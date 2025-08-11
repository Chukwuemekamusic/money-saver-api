#!/usr/bin/env python3
"""
Test script for email service functionality
"""
import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

async def test_email_service():
    """Test the email service configuration and basic functionality"""
    print("🧪 Testing Email Service Configuration...")
    
    try:
        from app.services.email_service import email_service
        from app.core.config import get_settings
        
        settings = get_settings()
        
        print(f"✅ Email service imported successfully")
        print(f"📧 Email enabled: {settings.EMAIL_ENABLED}")
        print(f"📧 Email username: {settings.EMAIL_USERNAME or 'Not configured'}")
        print(f"📧 Email from: {settings.EMAIL_FROM or 'Not configured'}")
        print(f"📧 Email host: {settings.EMAIL_HOST}")
        print(f"📧 Email port: {settings.EMAIL_PORT}")
        
        # Test email configuration
        if not settings.EMAIL_ENABLED:
            print("⚠️  Email service is disabled")
            return False
            
        if not all([settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD, settings.EMAIL_FROM]):
            print("❌ Email service not configured - missing credentials")
            print("   Please set EMAIL_USERNAME, EMAIL_PASSWORD, and EMAIL_FROM in your .env file")
            return False
        
        print("✅ Email service configuration looks good!")
        
        # Test template rendering (without sending email)
        print("\n🧪 Testing Template Rendering...")
        try:
            # Mock data for template testing
            context = {
                'user_name': 'Test User',
                'total_plans': 2,
                'total_target_this_week': 50.00,
                'total_saved_amount': 150.00,
                'total_target_amount': 500.00,
                'overall_progress_percentage': 30.0,
                'plan_summaries': [
                    {
                        'name': 'Holiday Fund',
                        'target_amount': 300.00,
                        'saved_amount': 100.00,
                        'weekly_target': 25.00,
                        'progress_percentage': 33.3,
                        'remaining_amount': 200.00
                    },
                    {
                        'name': 'Emergency Fund',
                        'target_amount': 200.00,
                        'saved_amount': 50.00,
                        'weekly_target': 25.00,
                        'progress_percentage': 25.0,
                        'remaining_amount': 150.00
                    }
                ],
                'motivation_message': "You're building great savings habits! Every pound counts! 🎯",
                'app_url': 'http://localhost:3000',
                'unsubscribe_url': 'http://localhost:3000/unsubscribe?token=test'
            }
            
            html_content = email_service._render_template("weekly_reminder.html", context)
            text_content = email_service._render_template("weekly_reminder.txt", context)
            
            if html_content and text_content:
                print("✅ Email templates rendered successfully")
                print(f"   HTML content length: {len(html_content)} characters")
                print(f"   Text content length: {len(text_content)} characters")
            else:
                print("❌ Failed to render email templates")
                return False
                
        except Exception as e:
            print(f"❌ Template rendering failed: {str(e)}")
            return False
        
        print("\n✅ All email service tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Email service test failed: {str(e)}")
        return False

async def test_scheduler_service():
    """Test the scheduler service"""
    print("\n🧪 Testing Scheduler Service...")
    
    try:
        from app.services.scheduler_service import scheduler_service
        from app.core.config import get_settings
        
        settings = get_settings()
        
        print(f"✅ Scheduler service imported successfully")
        print(f"📅 Scheduler running: {scheduler_service.scheduler.running}")
        print(f"📅 Reminder day: {settings.REMINDER_DAY}")
        print(f"📅 Reminder time: {settings.REMINDER_HOUR:02d}:{settings.REMINDER_MINUTE:02d}")
        
        # Get job status
        job_status = scheduler_service.get_job_status('weekly_savings_reminder')
        if job_status:
            print(f"✅ Weekly reminder job found:")
            print(f"   Job ID: {job_status['id']}")
            print(f"   Job Name: {job_status['name']}")
            print(f"   Next Run: {job_status['next_run_time']}")
            print(f"   Trigger: {job_status['trigger']}")
        else:
            print("⚠️  Weekly reminder job not found (may be disabled)")
        
        print("✅ Scheduler service test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Scheduler service test failed: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Email Reminder System Tests...\n")
    
    email_test = await test_email_service()
    scheduler_test = await test_scheduler_service()
    
    print(f"\n📊 Test Results:")
    print(f"   Email Service: {'✅ PASS' if email_test else '❌ FAIL'}")
    print(f"   Scheduler Service: {'✅ PASS' if scheduler_test else '❌ FAIL'}")
    
    if email_test and scheduler_test:
        print(f"\n🎉 All tests passed! Email reminder system is ready.")
        print(f"\n📝 Next steps:")
        print(f"   1. Set up Gmail app password in your .env file")
        print(f"   2. Run the migration: alembic upgrade head")
        print(f"   3. Start the FastAPI server: uvicorn app.main:app --reload")
        print(f"   4. Test the API endpoints at http://localhost:8000/docs")
    else:
        print(f"\n❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())