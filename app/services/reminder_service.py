import logging
from typing import List
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.user import User
from app.models.savings import SavingPlan
from app.services.email_service import email_service
from app.services.savings_service import SavingsService

logger = logging.getLogger(__name__)

class ReminderService:
    def __init__(self):
        self.savings_service = SavingsService()

    async def send_weekly_reminders(self):
        """Send weekly reminder emails to all eligible users"""
        logger.info("Starting weekly reminder email process")
        
        try:
            async for session in get_db():
                # Get all active users with email notifications enabled
                users = await self._get_eligible_users(session)
                logger.info(f"Found {len(users)} eligible users for weekly reminders")
                
                success_count = 0
                error_count = 0
                
                for user in users:
                    try:
                        success = await self._send_user_reminder(session, user)
                        if success:
                            success_count += 1
                        else:
                            error_count += 1
                            
                    except Exception as e:
                        logger.error(f"Error processing reminder for user {user.email}: {str(e)}")
                        error_count += 1
                
                logger.info(
                    f"Weekly reminder process completed. "
                    f"Sent: {success_count}, Errors: {error_count}"
                )
                
        except Exception as e:
            logger.error(f"Failed to complete weekly reminder process: {str(e)}")

    async def _get_eligible_users(self, db: AsyncSession) -> List[User]:
        """Get users eligible for weekly reminders"""
        from sqlalchemy import select
        
        # Query active users with email notifications enabled and active savings plans
        query = (
            select(User)
            .where(
                and_(
                    User.is_active == True,
                    User.deleted_at.is_(None),
                    User.email_notifications == True,  # Will be added in database migration
                    User.email.isnot(None)
                )
            )
            .options(selectinload(User.saving_plans))
        )
        
        result = await db.execute(query)
        all_users = result.scalars().all()
        
        # Filter users who have at least one active saving plan
        eligible_users = []
        for user in all_users:
            active_plans = [
                plan for plan in user.saving_plans 
                if plan.deleted_at is None
            ]
            if active_plans:
                eligible_users.append(user)
        
        return eligible_users

    async def _send_user_reminder(self, db: AsyncSession, user: User) -> bool:
        """Send reminder email to a specific user"""
        try:
            # Get user's active saving plans
            savings_plans = await self.savings_service.get_user_saving_plans(
                db=db, 
                user_id=user.id,
                skip=0,
                limit=100  # Get all plans
            )
            
            # Get user statistics
            user_stats = await self.savings_service.get_user_savings_stats(
                db=db, 
                user_id=user.id
            )
            
            # Send the email
            success = await email_service.send_weekly_reminder(
                user=user,
                savings_plans=savings_plans.get('plans', []),
                user_stats=user_stats
            )
            
            if success:
                logger.info(f"Weekly reminder sent successfully to {user.email}")
            else:
                logger.warning(f"Failed to send weekly reminder to {user.email}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending reminder to {user.email}: {str(e)}")
            return False

    async def send_test_reminder(self, user_id: str) -> bool:
        """Send test reminder to a specific user (for development/testing)"""
        try:
            async for session in get_db():
                from sqlalchemy import select
                
                # Get the user
                query = select(User).where(User.id == user_id)
                result = await session.execute(query)
                user = result.scalar_one_or_none()
                
                if not user:
                    logger.error(f"User {user_id} not found for test reminder")
                    return False
                
                return await self._send_user_reminder(session, user)
                
        except Exception as e:
            logger.error(f"Error sending test reminder to user {user_id}: {str(e)}")
            return False

# Global reminder service instance
reminder_service = ReminderService()