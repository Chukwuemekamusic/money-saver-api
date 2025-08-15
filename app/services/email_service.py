import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr

from app.core.config import get_settings
from app.models.user import User
from app.models.savings import SavingPlan
from app.services.token_service import token_service

logger = logging.getLogger(__name__)
settings = get_settings()

class EmailService:
    def __init__(self):
        if not settings.EMAIL_ENABLED:
            logger.info("Email service disabled via configuration")
            return
            
        if not all([settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD, settings.EMAIL_FROM]):
            logger.warning("Email service not configured - missing credentials")
            return
            
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.EMAIL_USERNAME,
            MAIL_PASSWORD=settings.EMAIL_PASSWORD,
            MAIL_FROM=settings.EMAIL_FROM,
            MAIL_FROM_NAME=settings.EMAIL_FROM_NAME,
            MAIL_PORT=settings.EMAIL_PORT,
            MAIL_SERVER=settings.EMAIL_HOST,
            MAIL_STARTTLS=settings.EMAIL_USE_TLS,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
        
        self.fastmail = FastMail(self.conf)
        
        # Setup Jinja2 template environment
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        self.template_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )
        
        logger.info("Email service initialized successfully")

    async def send_weekly_reminder(
        self, 
        user: User, 
        savings_plans: List[SavingPlan],
        user_stats: Dict[str, Any]
    ) -> bool:
        """Send weekly savings reminder email to user"""
        if not settings.EMAIL_ENABLED:
            return False
            
        try:
            # Prepare template context
            context = self._prepare_reminder_context(user, savings_plans, user_stats)
            
            # Render email content
            html_content = self._render_template("weekly_reminder.html", context)
            text_content = self._render_template("weekly_reminder.txt", context)
            
            # Create message
            subject = f"Your weekly savings reminder - £{context['total_target_this_week']} to go! 💰"
            
            # Create proper multipart message with both HTML and text
            # For better text formatting, send as plain text only
            message = MessageSchema(
                subject=subject,
                recipients=[user.email],
                body=text_content,
                subtype="plain",
                charset="utf-8"
            )
            
            # Send email
            await self.fastmail.send_message(message)
            logger.info(f"Weekly reminder sent successfully to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send weekly reminder to {user.email}: {str(e)}")
            return False

    def _prepare_reminder_context(
        self, 
        user: User, 
        savings_plans: List[SavingPlan],
        user_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare template context for reminder email with enhanced progress tracking"""
        from datetime import datetime, timedelta
        
        # Calculate weekly targets for active plans
        active_plans = [plan for plan in savings_plans if plan.deleted_at is None]
        
        total_target_this_week = 0
        total_weeks_behind = 0
        plan_summaries = []
        catch_up_amount = 0
        
        for plan in active_plans:
            # Calculate weekly target (total amount / number of weeks) - convert to float
            weekly_target = float(plan.amount / plan.number_of_weeks) if plan.number_of_weeks > 0 else 0.0
            total_target_this_week += weekly_target
            
            # Calculate progress percentage
            progress_percentage = (
                (float(plan.total_saved_amount) / float(plan.amount) * 100) 
                if plan.amount > 0 else 0
            )
            
            # Calculate weeks behind schedule
            weeks_elapsed = self._calculate_weeks_elapsed(plan.date_created)
            expected_saved = weekly_target * weeks_elapsed
            actual_saved = float(plan.total_saved_amount) if plan.total_saved_amount else 0.0
            behind_amount = max(0.0, expected_saved - actual_saved)
            weeks_behind = int(behind_amount / weekly_target) if weekly_target > 0 else 0
            
            # Track maximum weeks behind across all plans
            total_weeks_behind = max(total_weeks_behind, weeks_behind)
            catch_up_amount += behind_amount
            
            plan_summaries.append({
                'name': plan.savings_name,
                'target_amount': float(plan.amount),
                'saved_amount': float(plan.total_saved_amount),
                'weekly_target': weekly_target,
                'progress_percentage': round(progress_percentage, 1),
                'remaining_amount': float(plan.amount - plan.total_saved_amount),
                'weeks_behind': weeks_behind,
                'behind_amount': behind_amount,
                'on_track': weeks_behind == 0,
                'weeks_elapsed': weeks_elapsed,
                'expected_saved': expected_saved
            })
        
        # Determine motivational message based on progress and consistency
        overall_progress = user_stats.get('overall_progress_percentage', 0)
        motivation_message = self._get_enhanced_motivation_message(overall_progress, total_weeks_behind, len(active_plans))
        
        # Calculate catch-up suggestion
        catch_up_suggestion = self._get_catch_up_suggestion(total_weeks_behind, catch_up_amount, total_target_this_week)
        
        # Generate secure unsubscribe token
        unsubscribe_token = token_service.generate_unsubscribe_token(user.id)
        
        return {
            'user_name': user.first_name or 'Saver',
            'total_plans': len(active_plans),
            'total_target_this_week': round(total_target_this_week, 2),
            'total_saved_amount': user_stats.get('total_saved_amount', 0),
            'total_target_amount': user_stats.get('total_target_amount', 0),
            'overall_progress_percentage': round(overall_progress, 1),
            'plan_summaries': plan_summaries,
            'motivation_message': motivation_message,
            'catch_up_suggestion': catch_up_suggestion,
            'total_weeks_behind': total_weeks_behind,
            'catch_up_amount': round(catch_up_amount, 2),
            'is_behind_schedule': total_weeks_behind > 0,
            'app_url': settings.FRONTEND_URL,
            'unsubscribe_url': f'{settings.API_BASE_URL}/api/v1/email/unsubscribe?token={unsubscribe_token}'
        }
    
    def _calculate_weeks_elapsed(self, start_date) -> int:
        """Calculate how many weeks have elapsed since the plan started"""
        from datetime import datetime
        
        if not start_date:
            return 0
            
        # Convert to datetime if needed
        if hasattr(start_date, 'date'):
            start_date = start_date.date()
        
        today = datetime.utcnow().date()
        days_elapsed = (today - start_date).days
        weeks_elapsed = max(1, days_elapsed // 7)  # At least 1 week
        
        return weeks_elapsed

    def _get_motivation_message(self, progress_percentage: float) -> str:
        """Get motivational message based on progress (legacy method)"""
        if progress_percentage >= 80:
            return "You're crushing your savings goals! Keep up the amazing work! 🌟"
        elif progress_percentage >= 50:
            return "Great progress on your savings journey! You're more than halfway there! 💪"
        elif progress_percentage >= 25:
            return "You're building great savings habits! Every pound counts! 🎯"
        else:
            return "Every savings journey starts with a single step. You've got this! 🚀"
    
    def _get_enhanced_motivation_message(self, progress_percentage: float, weeks_behind: int, total_plans: int) -> str:
        """Get enhanced motivational message based on progress and consistency"""
        
        if weeks_behind == 0:
            # On track messages
            if progress_percentage >= 80:
                return "🌟 Fantastic! You're on track and crushing your savings goals! You're in the final stretch!"
            elif progress_percentage >= 50:
                return "💪 Great job staying on track! You're more than halfway to your goals!"
            elif progress_percentage >= 25:
                return "🎯 You're doing great! Staying consistent with your savings is the key to success!"
            else:
                return "🚀 Perfect start! You're building excellent savings habits by staying on schedule!"
                
        elif weeks_behind == 1:
            # 1 week behind
            return "⏰ You're just one week behind schedule - no worries! A small catch-up this week will get you right back on track!"
            
        elif weeks_behind == 2:
            # 2 weeks behind  
            return "📈 You've missed a couple of weeks, but you can still achieve your goals! Consider increasing this week's savings to catch up!"
            
        elif weeks_behind >= 3:
            # 3+ weeks behind
            return "💡 It's never too late to get back on track! Even small amounts saved consistently can make a big difference. Every step counts!"
            
        else:
            return "🎯 Keep building those savings habits! Consistency is key to reaching your financial goals!"
    
    def _get_catch_up_suggestion(self, weeks_behind: int, catch_up_amount: float, normal_weekly_target: float) -> str:
        """Generate catch-up suggestions based on how far behind the user is"""
        
        if weeks_behind == 0:
            return f"You're perfectly on track! Just save your regular £{normal_weekly_target:.0f} this week."
            
        elif weeks_behind == 1:
            suggested_amount = normal_weekly_target + (catch_up_amount * 0.5)  # Catch up 50% of missed amount
            return f"Try saving £{suggested_amount:.0f} this week (£{catch_up_amount * 0.5:.0f} extra) to get closer to your target!"
            
        elif weeks_behind == 2:
            suggested_amount = normal_weekly_target + (catch_up_amount * 0.3)  # Catch up 30% of missed amount
            return f"Consider saving £{suggested_amount:.0f} this week to start catching up gradually!"
            
        elif weeks_behind >= 3:
            # For very behind users, suggest a more reasonable catch-up
            suggested_amount = normal_weekly_target + min(normal_weekly_target * 0.5, catch_up_amount * 0.2)
            return f"Don't worry about catching up all at once! Try saving £{suggested_amount:.0f} this week - small consistent steps work best!"
            
        else:
            return f"Save whatever you can this week! Even £{normal_weekly_target * 0.5:.0f} is better than nothing!"

    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render email template with context"""
        try:
            template = self.template_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {str(e)}")
            return ""

    async def send_test_email(self, recipient_email: str) -> bool:
        """Send test email for development/debugging"""
        try:
            message = MessageSchema(
                subject="Money Saver App - Test Email",
                recipients=[recipient_email],
                body="This is a test email from Money Saver App email service.",
                subtype="plain"
            )
            
            await self.fastmail.send_message(message)
            logger.info(f"Test email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send test email to {recipient_email}: {str(e)}")
            return False

# Global email service instance
email_service = EmailService()