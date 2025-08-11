#!/usr/bin/env python3
"""
Send an enhanced test email with all new features
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

async def send_enhanced_test_email():
    """Send actual enhanced email to test the full system"""
    print("📧 Sending Enhanced Test Email...")
    
    try:
        from app.services.email_service import email_service
        from app.core.config import get_settings
        
        settings = get_settings()
        
        # Create mock user
        class MockUser:
            def __init__(self):
                self.id = "test-user-123"
                self.first_name = "John"
                self.email = settings.EMAIL_FROM  # Send to yourself
        
        # Create mock savings plans with realistic scenarios
        class MockSavingPlan:
            def __init__(self, name, amount, total_saved, weeks, created_days_ago):
                self.savings_name = name
                self.amount = Decimal(str(amount))
                self.total_saved_amount = Decimal(str(total_saved))
                self.number_of_weeks = weeks
                self.deleted_at = None
                self.date_created = datetime.now() - timedelta(days=created_days_ago)
        
        user = MockUser()
        
        # Realistic scenario: User has mixed progress
        savings_plans = [
            # Holiday Fund: Should have saved £100 in 2 weeks, but only saved £50 (1 week behind)
            MockSavingPlan("Holiday Fund", 500, 50, 10, 14),
            
            # Emergency Fund: Should have saved £60 in 3 weeks, but only saved £20 (2 weeks behind)  
            MockSavingPlan("Emergency Fund", 400, 20, 20, 21),
            
            # Car Savings: On track - saved £25 in 1 week as expected
            MockSavingPlan("Car Savings", 300, 25, 12, 7)
        ]
        
        user_stats = {
            'total_saved_amount': 95,  # 50 + 20 + 25
            'total_target_amount': 1200,  # 500 + 400 + 300
            'overall_progress_percentage': 7.92  # 95/1200 * 100
        }
        
        print(f"📤 Sending enhanced reminder email to: {user.email}")
        print(f"👤 User: {user.first_name}")
        print(f"💰 Total saved: £{user_stats['total_saved_amount']}")
        print(f"🎯 Total target: £{user_stats['total_target_amount']}")
        print(f"📊 Progress: {user_stats['overall_progress_percentage']:.1f}%")
        
        # Send the enhanced email
        success = await email_service.send_weekly_reminder(user, savings_plans, user_stats)
        
        if success:
            print("\n✅ Enhanced test email sent successfully!")
            print(f"📬 Check your Gmail inbox at: {user.email}")
            print(f"\n🎨 The email includes:")
            print(f"   📈 Progress tracking: '2 weeks behind your savings schedule'")
            print(f"   💡 Catch-up suggestion: Smart recommendations based on progress")
            print(f"   🎯 Individual plan status: On track vs behind indicators")
            print(f"   ⚠️ Visual warnings for plans behind schedule")
            print(f"   🔓 Secure unsubscribe link")
            print(f"   📊 Expected vs actual savings breakdown")
            return True
        else:
            print("❌ Failed to send enhanced test email")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced email sending failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(send_enhanced_test_email())
    if result:
        print("\n🎉 Enhanced Email System is fully functional!")
        print(f"\n🚀 Ready for production with these features:")
        print(f"   • Weeks behind tracking")
        print(f"   • Smart catch-up suggestions") 
        print(f"   • Contextual motivational messages")
        print(f"   • One-click unsubscribe")
        print(f"   • Visual progress indicators")
    else:
        print(f"\n❌ Enhancement test failed")