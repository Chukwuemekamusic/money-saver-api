"""
User-related Pydantic schemas

These schemas define the request/response models for user data.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class UserResponse(BaseModel):
    """Response model for user data"""
    id: str = Field(..., description="User UUID from Supabase")
    email: str = Field(..., description="User email address")
    first_name: str = Field(..., description="User first name")
    last_name: str = Field(..., description="User last name")
    is_active: bool = Field(..., description="Whether user account is active")
    provider: Optional[str] = Field(default="email", description="Authentication provider")
    created_at: datetime = Field(..., description="User creation timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True,
                "provider": "google",
                "created_at": "2025-08-06T00:00:00Z"
            }
        }
    )


class UserUpdate(BaseModel):
    """Request model for updating user profile"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="User first name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="User last name")

    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "John",
                "last_name": "Doe"
            }
        }
    }