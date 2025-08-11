#!/usr/bin/env python3
"""
Simple API testing script for Money Saver FastAPI endpoints
"""

import requests
import json
from datetime import datetime


class APITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
    
    def set_token(self, token):
        """Set the authentication token"""
        self.token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def test_health(self):
        """Test the health endpoint"""
        print("🏥 Testing Health Endpoint")
        response = self.session.get(f"{self.base_url}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response
    
    def test_root(self):
        """Test the root endpoint"""
        print("\n🏠 Testing Root Endpoint")
        response = self.session.get(f"{self.base_url}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response
    
    def test_savings_plans_unauthorized(self):
        """Test savings plans without auth (should fail)"""
        print("\n🚫 Testing Savings Plans (Unauthorized)")
        # Temporarily remove auth header
        headers = self.session.headers.copy()
        if "Authorization" in headers:
            del headers["Authorization"]
        
        response = requests.get(f"{self.base_url}/api/v1/savings/plans", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response
    
    def test_create_saving_plan(self):
        """Test creating a saving plan (requires auth)"""
        print("\n💰 Testing Create Saving Plan")
        if not self.token:
            print("❌ Token required for this endpoint")
            return None
        
        data = {
            "savings_name": f"Test Plan {datetime.now().strftime('%H:%M:%S')}",
            "amount": "1000.00",
            "number_of_weeks": 20
        }
        
        response = self.session.post(f"{self.base_url}/api/v1/savings/plans", json=data)
        print(f"Status: {response.status_code}")
        if response.status_code < 400:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error: {response.text}")
        return response
    
    def test_get_savings_plans(self):
        """Test getting savings plans (requires auth)"""
        print("\n📋 Testing Get Savings Plans")
        if not self.token:
            print("❌ Token required for this endpoint")
            return None
        
        response = self.session.get(f"{self.base_url}/api/v1/savings/plans")
        print(f"Status: {response.status_code}")
        if response.status_code < 400:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error: {response.text}")
        return response
    
    def test_get_savings_stats(self):
        """Test getting savings statistics (requires auth)"""
        print("\n📊 Testing Get Savings Stats")
        if not self.token:
            print("❌ Token required for this endpoint")
            return None
        
        response = self.session.get(f"{self.base_url}/api/v1/savings/stats")
        print(f"Status: {response.status_code}")
        if response.status_code < 400:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error: {response.text}")
        return response
    
    def run_all_tests(self):
        """Run all available tests"""
        print("🧪 Running API Tests for Money Saver FastAPI")
        print("=" * 50)
        
        # Test public endpoints
        self.test_health()
        self.test_root()
        self.test_savings_plans_unauthorized()
        
        # Test protected endpoints (if token is available)
        if self.token:
            print(f"\n🔐 Testing with authentication token: {self.token[:20]}...")
            self.test_create_saving_plan()
            self.test_get_savings_plans()
            self.test_get_savings_stats()
        else:
            print("\n⚠️  No authentication token provided. Skipping protected endpoints.")
            print("💡 To test protected endpoints, set a token with: tester.set_token('your_jwt_token')")


if __name__ == "__main__":
    # Create tester instance
    tester = APITester()
    
    # Optional: Set your Supabase JWT token here for testing protected endpoints
    # tester.set_token("your_supabase_jwt_token_here")
    
    # Run all tests
    tester.run_all_tests()
    
    print("\n✅ API testing completed!")
    print("💡 For interactive testing, visit: http://localhost:8000/docs")