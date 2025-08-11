from functools import lru_cache
from typing import Optional

from supabase import create_client, Client
from fastapi import HTTPException

from app.core.config import get_settings

settings = get_settings()


@lru_cache()
def get_supabase_client() -> Client:
    """Create and cache Supabase client instance"""
    try:
        supabase: Client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_KEY
        )
        return supabase
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize Supabase client: {str(e)}"
        )


async def verify_supabase_token(token: str) -> dict:
    """Verify Supabase JWT token and return user info"""
    if not token:
        raise HTTPException(status_code=401, detail="Token is required")
    
    try:
        supabase = get_supabase_client()
        
        # Verify token with Supabase
        response = supabase.auth.get_user(token)
        
        if not response.user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
            
        return {
            "user_id": response.user.id,
            "email": response.user.email,
            "provider": response.user.app_metadata.get("provider", "email"),
            "user_metadata": response.user.user_metadata
        }
        
    except Exception as e:
        if "Invalid JWT" in str(e) or "JWT expired" in str(e):
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        raise HTTPException(status_code=500, detail=f"Token verification failed: {str(e)}")


async def get_user_from_supabase(user_id: str) -> Optional[dict]:
    """Get user details from Supabase by user ID"""
    try:
        supabase = get_supabase_client()
        
        # Get user from Supabase auth
        response = supabase.auth.admin.get_user_by_id(user_id)
        
        if response.user:
            return {
                "id": response.user.id,
                "email": response.user.email,
                "provider": response.user.app_metadata.get("provider", "email"),
                "user_metadata": response.user.user_metadata,
                "created_at": response.user.created_at,
                "updated_at": response.user.updated_at
            }
        return None
        
    except Exception as e:
        # This might fail without service key, which is okay for now
        print(f"Warning: Could not fetch user from Supabase admin API: {e}")
        return None