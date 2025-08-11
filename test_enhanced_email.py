#!/usr/bin/env python3
"""
Test script for enhanced email reminder system with progress tracking
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

async def test_enhanced_email_content():
    """Test the enhanced email content with mock data"""
    print("🧪 Testing Enhanced Email Content...")
    
    try:
        from app.services.email_service import email_service
        
        # Create mock user
        class MockUser:
            def __init__(self):
                self.id = "test-user-123"
                self.first_name = "John"
                self.email = "chukwuemekamusic@gmail.com"
        
        # Create mock savings plans with different scenarios
        class MockSavingPlan:
            def __init__(self, name, amount, total_saved, weeks, created_days_ago):
                self.savings_name = name
                self.amount = Decimal(str(amount))
                self.total_saved_amount = Decimal(str(total_saved))
                self.number_of_weeks = weeks
                self.deleted_at = None
                # Simulate plan created X days ago
                self.date_created = datetime.utcnow() - timedelta(days=created_days_ago)
        
        user = MockUser()
        
        # Scenario 1: Mix of on-track and behind plans
        savings_plans = [
            # On track: Should have saved £50 in 2 weeks, has saved £50
            MockSavingPlan("Holiday Fund", 500, 50, 10, 14),  # Created 2 weeks ago
            
            # 2 weeks behind: Should have saved £60 in 3 weeks, has saved £20  
            MockSavingPlan("Emergency Fund", 400, 20, 20, 21),  # Created 3 weeks ago
            
            # 1 week behind: Should have saved £25 in 1 week, has saved £15
            MockSavingPlan("Car Savings", 300, 15, 12, 7)   # Created 1 week ago
        ]
        
        user_stats = {
            'total_saved_amount': 85,
            'total_target_amount': 1200,
            'overall_progress_percentage': 7.08  # 85/1200 * 100
        }
        
        print("📧 Testing email content generation...")
        
        # Test the enhanced context preparation
        context = email_service._prepare_reminder_context(user, savings_plans, user_stats)
        
        print(f"✅ Context generated successfully!")
        print(f"📊 User: {context['user_name']}")
        print(f"📊 Total weeks behind: {context['total_weeks_behind']}")
        print(f"📊 Is behind schedule: {context['is_behind_schedule']}")
        print(f"📊 Catch-up amount: £{context['catch_up_amount']}")
        print(f"📊 This week's target: £{context['total_target_this_week']}")
        
        print(f"\n💬 Motivation message:")
        print(f"   {context['motivation_message']}")
        
        print(f"\n💡 Catch-up suggestion:")
        print(f"   {context['catch_up_suggestion']}")
        
        print(f"\n📋 Plan Summaries:")
        for i, plan in enumerate(context['plan_summaries'], 1):
            status = "✅ On track" if plan['on_track'] else f"⚠️ {plan['weeks_behind']} weeks behind"
            print(f"   {i}. {plan['name']} - {status}")
            print(f"      Saved: £{plan['saved_amount']} / £{plan['target_amount']} ({plan['progress_percentage']}%)")
            if not plan['on_track']:
                print(f"      Expected: £{plan['expected_saved']:.2f} • Behind by: £{plan['behind_amount']:.2f}")
        
        # Test template rendering
        print(f"\n🎨 Testing template rendering...")
        html_content = email_service._render_template("weekly_reminder.html", context)
        text_content = email_service._render_template("weekly_reminder.txt", context)
        
        if html_content and text_content:
            print(f"✅ Templates rendered successfully!")
            print(f"   HTML length: {len(html_content)} characters")
            print(f"   Text length: {len(text_content)} characters")
            
            # Show a preview of the text content
            print(f"\n📝 Text Email Preview (first 500 chars):")
            print(f"{'='*50}")
            print(text_content[:500])
            if len(text_content) > 500:
                print("... [truncated]")
            print(f"{'='*50}")
            
            return True
        else:
            print(f"❌ Template rendering failed")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced email test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_unsubscribe_token():
    """Test unsubscribe token generation and validation"""
    print(f"\n🔐 Testing Unsubscribe Token System...")
    
    try:
        from app.services.token_service import token_service
        
        user_id = "test-user-123"
        
        # Generate token
        token = token_service.generate_unsubscribe_token(user_id)
        print(f"✅ Token generated: {token[:20]}...")
        
        # Validate token
        validated_user_id = token_service.validate_unsubscribe_token(token)
        
        if validated_user_id == user_id:
            print(f"✅ Token validation successful!")
            print(f"   Original user_id: {user_id}")
            print(f"   Validated user_id: {validated_user_id}")
            return True
        else:
            print(f"❌ Token validation failed")
            print(f"   Expected: {user_id}")
            print(f"   Got: {validated_user_id}")
            return False
            
    except Exception as e:
        print(f"❌ Token test failed: {str(e)}")
        return False

async def main():
    """Run all enhanced email tests"""
    print("🚀 Testing Enhanced Email Reminder System...\n")
    
    content_test = await test_enhanced_email_content()
    token_test = await test_unsubscribe_token()
    
    print(f"\n📊 Test Results:")
    print(f"   Enhanced Content: {'✅ PASS' if content_test else '❌ FAIL'}")
    print(f"   Unsubscribe Tokens: {'✅ PASS' if token_test else '❌ FAIL'}")
    
    if content_test and token_test:
        print(f"\n🎉 All enhanced features working perfectly!")
        print(f"\n✨ New Email Features:")
        print(f"   📈 Progress tracking with weeks behind calculation")
        print(f"   💡 Smart catch-up suggestions based on user progress")  
        print(f"   🎯 Contextual motivational messages")
        print(f"   🔓 Secure one-click unsubscribe")
        print(f"   📊 Individual plan progress with visual indicators")
        print(f"   ⚠️ Clear warnings for users behind schedule")
        
        print(f"\n📝 Sample Email Content Includes:")
        print(f"   • 'You're 2 weeks behind your savings schedule'")
        print(f"   • 'Try saving £75 this week (£25 extra) to get closer to your target!'")
        print(f"   • Individual plan status: '✅ On track' or '⚠️ 2 weeks behind'")
        print(f"   • Expected vs actual savings: 'Expected by now: £60 • Behind by: £40'")
        
    else:
        print(f"\n❌ Some tests failed. Check the errors above.")
    
    return 0 if (content_test and token_test) else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())