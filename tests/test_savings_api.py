"""
Tests for savings API endpoints
"""

import pytest
from decimal import Decimal

from app.api.dependencies import get_current_user
from tests.conftest import mock_get_current_user


class TestSavingsAPI:
    """Test savings plan API endpoints"""
    
    def test_create_saving_plan(self, client, test_user):
        """Test creating a new saving plan"""
        # Mock authentication
        client.app.dependency_overrides[get_current_user] = mock_get_current_user(test_user)
        
        plan_data = {
            "savings_name": "Emergency Fund",
            "amount": "5000.00",
            "number_of_weeks": 26
        }
        
        response = client.post("/api/v1/savings/plans", json=plan_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["savings_name"] == "Emergency Fund"
        assert data["amount"] == "5000.00"
        assert data["number_of_weeks"] == 26
        assert data["user_id"] == test_user.id
        assert data["total_saved_amount"] == "0"
        assert "id" in data
        assert "date_created" in data
    
    def test_create_saving_plan_with_weekly_amounts(self, client, test_user):
        """Test creating a saving plan with weekly amounts"""
        client.app.dependency_overrides[get_current_user] = mock_get_current_user(test_user)
        
        plan_data = {
            "savings_name": "Vacation Fund",
            "amount": "1000.00",
            "number_of_weeks": 10,
            "weekly_amounts": [
                {"amount": "100.00", "week_index": 1, "selected": True},
                {"amount": "100.00", "week_index": 2, "selected": False}
            ]
        }
        
        response = client.post("/api/v1/savings/plans", json=plan_data)
        
        assert response.status_code == 201
        data = response.json()
        assert len(data["weekly_amounts"]) == 2
        assert data["weekly_amounts"][0]["selected"] == True
        assert data["weekly_amounts"][1]["selected"] == False
    
    def test_get_saving_plans(self, client, test_user, test_saving_plan):
        """Test getting user's saving plans"""
        client.app.dependency_overrides[get_current_user] = mock_get_current_user(test_user)
        
        response = client.get("/api/v1/savings/plans")
        
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        assert "total" in data
        assert data["total"] >= 1
        assert len(data["plans"]) >= 1
        assert data["plans"][0]["id"] == test_saving_plan.id
    
    def test_get_saving_plan_by_id(self, client, test_user, test_saving_plan):
        """Test getting a specific saving plan"""
        client.app.dependency_overrides[get_current_user] = mock_get_current_user(test_user)
        
        response = client.get(f"/api/v1/savings/plans/{test_saving_plan.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_saving_plan.id
        assert data["savings_name"] == test_saving_plan.savings_name
        assert data["user_id"] == test_user.id
    
    def test_get_nonexistent_saving_plan(self, client, test_user):
        """Test getting a non-existent saving plan"""
        client.app.dependency_overrides[get_current_user] = mock_get_current_user(test_user)
        
        response = client.get("/api/v1/savings/plans/99999")
        
        assert response.status_code == 404
        response_data = response.json()
        if "detail" in response_data:
            assert "not found" in response_data["detail"].lower()
        else:
            # Handle other error response formats
            assert response.status_code == 404
    
    def test_update_saving_plan(self, client, test_user, test_saving_plan):
        """Test updating a saving plan"""
        client.app.dependency_overrides[get_current_user] = mock_get_current_user(test_user)
        
        update_data = {
            "savings_name": "Updated Savings Plan",
            "amount": "2000.00"
        }
        
        response = client.put(f"/api/v1/savings/plans/{test_saving_plan.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["savings_name"] == "Updated Savings Plan"
        assert data["amount"] == "2000.00"
        assert data["number_of_weeks"] == test_saving_plan.number_of_weeks  # Unchanged
    
    def test_delete_saving_plan(self, client, test_user, test_saving_plan):
        """Test deleting a saving plan"""
        client.app.dependency_overrides[get_current_user] = mock_get_current_user(test_user)
        
        response = client.delete(f"/api/v1/savings/plans/{test_saving_plan.id}")
        
        assert response.status_code == 204
        
        # Verify plan is soft deleted
        get_response = client.get(f"/api/v1/savings/plans/{test_saving_plan.id}")
        assert get_response.status_code == 404
    
    def test_update_weekly_amount(self, client, test_user, test_weekly_amount):
        """Test updating a weekly amount"""
        client.app.dependency_overrides[get_current_user] = mock_get_current_user(test_user)
        
        update_data = {
            "amount": "75.00",
            "selected": True
        }
        
        response = client.put(f"/api/v1/savings/weekly-amounts/{test_weekly_amount.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == "75.00"
        assert data["selected"] == True
        assert data["date_selected"] is not None
    
    def test_select_weekly_amount(self, client, test_user, test_weekly_amount):
        """Test selecting a weekly amount"""
        client.app.dependency_overrides[get_current_user] = mock_get_current_user(test_user)
        
        select_data = {"selected": True}
        
        response = client.post(f"/api/v1/savings/weekly-amounts/{test_weekly_amount.id}/select", json=select_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["selected"] == True
        assert data["date_selected"] is not None
    
    def test_get_savings_stats(self, client, test_user, test_saving_plan):
        """Test getting savings statistics"""
        client.app.dependency_overrides[get_current_user] = mock_get_current_user(test_user)
        
        response = client.get("/api/v1/savings/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_plans" in data
        assert "active_plans" in data
        assert "completed_plans" in data
        assert "total_target_amount" in data
        assert "total_saved_amount" in data
        assert "completion_percentage" in data
        assert data["total_plans"] >= 1
    
    def test_unauthorized_access(self, client):
        """Test that endpoints require authentication"""
        # Test without authentication
        response = client.get("/api/v1/savings/plans")
        assert response.status_code == 401 or response.status_code == 422
        
        response = client.post("/api/v1/savings/plans", json={"savings_name": "Test", "amount": "100", "number_of_weeks": 1})
        assert response.status_code == 401 or response.status_code == 422