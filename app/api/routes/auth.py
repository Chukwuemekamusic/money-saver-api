"""
Authentication endpoints for Money Saver API

These endpoints handle Supabase auth integration:
- User sync from Supabase to local database
- Current user retrieval
- Token verification
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies import get_current_user_info, get_current_user
from app.services.supabase_service import SupabaseService
from app.schemas.user import UserResponse
from app.schemas.auth import UserSyncResponse, TokenVerifyResponse
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/sync-user", response_model=UserSyncResponse)
async def sync_user_to_database(
    user_info: dict = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db)
) -> UserSyncResponse:
    """
    Sync Supabase user to local database
    
    This endpoint is called after successful authentication with Supabase
    to ensure the user exists in our local database.
    """
    try:
        logger.info(f"Syncing user {user_info['user_id']} to database")
        
        supabase_service = SupabaseService()
        user = await supabase_service.sync_user_to_db(db, user_info)
        
        return UserSyncResponse(
            success=True,
            message="User synchronized successfully",
            user=UserResponse(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_active=user.is_active,
                provider=user.provider,
                created_at=user.created_at
            )
        )
        
    except ValueError as e:
        logger.error(f"Validation error syncing user: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error syncing user to database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync user to database"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get current authenticated user profile
    
    Returns the user profile information from the local database.
    Automatically syncs user if not found locally.
    """
    try:
        logger.info(f"Getting profile for user {current_user.id}")
        
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            is_active=current_user.is_active,
            provider=current_user.provider,
            created_at=current_user.created_at
        )
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )


@router.post("/verify-token", response_model=TokenVerifyResponse)
async def verify_token(
    user_info: dict = Depends(get_current_user_info)
) -> TokenVerifyResponse:
    """
    Verify Supabase token and return user information
    
    This endpoint can be used by the frontend to verify if a token is still valid
    without syncing the user to the database.
    """
    try:
        logger.info(f"Verifying token for user {user_info['user_id']}")
        
        return TokenVerifyResponse(
            valid=True,
            user_id=user_info["user_id"],
            email=user_info["email"],
            provider=user_info.get("provider", "email")
        )
        
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify token"
        )


@router.post("/logout")
async def logout() -> Dict[str, Any]:
    """
    Logout endpoint
    
    Note: Actual logout is handled by Supabase client on frontend.
    This endpoint can be used for any server-side cleanup if needed.
    """
    logger.info("Logout endpoint called")
    
    return {
        "success": True,
        "message": "Logout successful. Please clear the token on the client side."
    }