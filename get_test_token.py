#!/usr/bin/env python3
"""
Script to create a test user and get JWT token for API testing
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_test_token():
    """Create a test user and get JWT token"""
    
    # Initialize Supabase client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return None
    
    supabase: Client = create_client(url, key)
    
    # Test user credentials
    email = "test@example.com"
    password = "testpassword123"
    
    try:
        # Try to sign up (will fail if user exists)
        print(f"🔐 Attempting to create test user: {email}")
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if response.user:
            print("✅ Test user created successfully")
        else:
            print("⚠️  User might already exist, trying to sign in...")
    
    except Exception as e:
        print(f"⚠️  Signup failed (user might exist): {e}")
        print("Trying to sign in instead...")
    
    try:
        # Sign in to get token
        print(f"🔑 Signing in as: {email}")
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user and response.session:
            token = response.session.access_token
            print("✅ Successfully obtained JWT token!")
            print(f"📋 Token (first 50 chars): {token[:50]}...")
            print(f"📋 Full token: {token}")
            return token
        else:
            print("❌ Failed to get token")
            return None
            
    except Exception as e:
        print(f"❌ Sign in failed: {e}")
        return None

if __name__ == "__main__":
    print("🧪 Getting test token for API testing...")
    token = get_test_token()
    
    if token:
        print("\n🎉 Success! You can now test protected endpoints:")
        print(f"curl -H 'Authorization: Bearer {token}' http://localhost:8000/api/v1/savings/plans")
        print(f"\nOr update test_api.py with:")
        print(f"tester.set_token('{token[:50]}...')")
    else:
        print("\n❌ Failed to get test token")
        print("💡 You'll need to get a token from your React frontend instead")