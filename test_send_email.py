#!/usr/bin/env python3
"""
Test script to send actual email
"""
import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

async def test_send_email():
    """Test sending an actual email"""
    print("📧 Testing Email Sending...")
    
    try:
        from app.services.email_service import email_service
        from app.core.config import get_settings
        
        settings = get_settings()
        
        # Test sending a simple test email
        recipient = settings.EMAIL_FROM  # Send to yourself
        print(f"📤 Sending test email to: {recipient}")
        
        success = await email_service.send_test_email(recipient)
        
        if success:
            print("✅ Test email sent successfully!")
            print(f"📬 Check your inbox at: {recipient}")
            return True
        else:
            print("❌ Failed to send test email")
            return False
            
    except Exception as e:
        print(f"❌ Email test failed: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_send_email())
    if result:
        print("\n🎉 Email system is fully functional!")
        print("📝 Next steps:")
        print("   1. Check your Gmail inbox for the test email")
        print("   2. The system will send weekly reminders every Monday at 9 AM")
        print("   3. Users can manage their email preferences via the API")
    else:
        print("\n❌ Email test failed. Check your Gmail app password.")