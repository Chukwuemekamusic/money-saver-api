from typing import Optional
from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.supabase import verify_supabase_token
from app.core.database import get_db
from app.services.supabase_service import SupabaseService
from app.models.user import User


async def get_authorization_header(authorization: Optional[str] = Header(None)) -> str:
    """Extract and validate authorization header"""
    if not authorization:
        raise HTTPException(
            status_code=401, 
            detail="Authorization header is required"
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format. Expected: Bearer <token>"
        )
    
    return authorization.split(" ")[1]


async def get_current_user_info(
    token: str = Depends(get_authorization_header)
) -> dict:
    """Verify token and return user info from Supabase"""
    return await verify_supabase_token(token)


async def get_current_user(
    user_info: dict = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get or create user in local database from Supabase user info"""
    try:
        supabase_service = SupabaseService()
        
        # Try to get user from local database first
        user = await supabase_service.get_user_by_id(db, user_info["user_id"])
        
        if not user:
            # User doesn't exist in local DB, create from Supabase info
            user = await supabase_service.sync_user_to_db(db, user_info)
        
        return user
        
    except Exception as e:
        # If database operations fail, log error but still allow user through
        # This prevents database issues from blocking authenticated users
        print(f"Warning: Database operation failed for user {user_info.get('user_id', 'unknown')}: {e}")
        
        # Create a minimal user object from Supabase info for this request
        # This allows the API to work even if the local database is having issues
        from app.models.user import User
        user = User(
            id=user_info["user_id"],
            email=user_info["email"],
            provider=user_info.get("provider", "email")
        )
        return user


async def get_optional_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current user if token is provided, otherwise return None"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        token = authorization.split(" ")[1]
        user_info = await verify_supabase_token(token)
        
        supabase_service = SupabaseService()
        user = await supabase_service.get_user_by_id(db, user_info["user_id"])
        
        if not user:
            # Create user if doesn't exist
            user = await supabase_service.sync_user_to_db(db, user_info)
            
        return user
        
    except Exception:
        # If token verification fails, just return None
        return None