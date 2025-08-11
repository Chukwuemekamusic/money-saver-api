"""
Authentication-related Pydantic schemas

These schemas define the request/response models for authentication endpoints.
"""

from typing import Optional
from pydantic import BaseModel, Field

from app.schemas.user import UserResponse


class UserSyncResponse(BaseModel):
    """Response model for user sync endpoint"""
    success: bool = Field(..., description="Whether the sync was successful")
    message: str = Field(..., description="Success or error message")
    user: UserResponse = Field(..., description="Synchronized user data")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "User synchronized successfully",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "is_active": True,
                    "provider": "google",
                    "created_at": "2025-08-06T00:00:00Z"
                }
            }
        }
    }


class TokenVerifyResponse(BaseModel):
    """Response model for token verification"""
    valid: bool = Field(..., description="Whether the token is valid")
    user_id: str = Field(..., description="User ID from Supabase")
    email: str = Field(..., description="User email")
    provider: Optional[str] = Field(default="email", description="Authentication provider")

    model_config = {
        "json_schema_extra": {
            "example": {
                "valid": True,
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "provider": "google"
            }
        }
    }


class AuthErrorResponse(BaseModel):
    """Error response model for authentication endpoints"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "INVALID_TOKEN",
                "message": "Token is invalid or expired",
                "detail": "JWT signature verification failed"
            }
        }
    }