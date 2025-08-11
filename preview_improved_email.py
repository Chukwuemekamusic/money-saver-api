#!/usr/bin/env python3
"""
Preview the improved email formatting
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

async def preview_improved_email():
    """Preview the improved email formatting"""
    print("📧 Previewing Improved Email Formatting...\n")
    
    try:
        from app.services.email_service import email_service
        
        # Create mock user and plans (same as before)
        class MockUser:
            def __init__(self):
                self.id = "test-user-123"
                self.first_name = "John"
                self.email = "test@example.com"
        
        class MockSavingPlan:
            def __init__(self, name, amount, total_saved, weeks, created_days_ago):
                self.savings_name = name
                self.amount = Decimal(str(amount))
                self.total_saved_amount = Decimal(str(total_saved))
                self.number_of_weeks = weeks
                self.deleted_at = None
                self.date_created = datetime.now() - timedelta(days=created_days_ago)
        
        user = MockUser()
        
        savings_plans = [
            MockSavingPlan("Holiday Fund", 500, 50, 10, 14),
            MockSavingPlan("Emergency Fund", 400, 20, 20, 21),
            MockSavingPlan("Car Savings", 300, 25, 12, 7)
        ]
        
        user_stats = {
            'total_saved_amount': 95,
            'total_target_amount': 1200,
            'overall_progress_percentage': 7.92
        }
        
        # Generate email context and render text template
        context = email_service._prepare_reminder_context(user, savings_plans, user_stats)
        text_content = email_service._render_template("weekly_reminder.txt", context)
        
        print("📝 IMPROVED EMAIL TEXT PREVIEW:")
        print("=" * 60)
        print(text_content)
        print("=" * 60)
        
        print(f"\n✨ Key Improvements:")
        print(f"   📏 Proper line spacing and breaks")
        print(f"   📊 Visual section separators with ═══")
        print(f"   🎯 Clear section headers")
        print(f"   📱 Emojis for better visual appeal")
        print(f"   📈 Organized information hierarchy")
        print(f"   🔍 Easy to scan layout")
        
        return True
            
    except Exception as e:
        print(f"❌ Preview failed: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(preview_improved_email())