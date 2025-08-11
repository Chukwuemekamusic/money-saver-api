import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.supabase import get_supabase_client, get_user_from_supabase
from app.models.user import User

logger = logging.getLogger(__name__)


class SupabaseService:
    """Service for Supabase integration and user management"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def get_user_by_id(self, db: AsyncSession, user_id: str) -> Optional[User]:
        """Get user from local database by ID"""
        try:
            stmt = select(User).where(
                User.id == user_id,
                User.deleted_at.is_(None)  # Only active users
            )
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user {user_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting user {user_id}: {e}")
            return None
    
    async def sync_user_to_db(self, db: AsyncSession, user_info: dict) -> User:
        """Create or update user in local database from Supabase user info"""
        
        try:
            # Validate required fields
            required_fields = ["user_id", "email"]
            for field in required_fields:
                if not user_info.get(field):
                    raise ValueError(f"Missing required field: {field}")
            
            user_id = user_info["user_id"]
            logger.info(f"Syncing user {user_id} to local database")
            
            # Check if user already exists
            existing_user = await self.get_user_by_id(db, user_id)
            
            if existing_user:
                logger.info(f"Updating existing user {user_id}")
                # Update existing user
                existing_user.email = user_info["email"]
                existing_user.provider = user_info.get("provider", "email")
                existing_user.is_active = True  # Reactivate if was inactive
                
                # Update names from user_metadata
                self._update_user_names(existing_user, user_info)
                
                await db.commit()
                await db.refresh(existing_user)
                logger.info(f"Successfully updated user {user_id}")
                return existing_user
            
            # Create new user if doesn't exist
            return await self._create_new_user(db, user_info)
            
        except ValueError as e:
            logger.error(f"Validation error syncing user: {e}")
            raise
        except IntegrityError as e:
            logger.error(f"Database integrity error syncing user: {e}")
            await db.rollback()
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error syncing user: {e}")
            await db.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error syncing user: {e}")
            await db.rollback()
            raise
    
    def _update_user_names(self, user: User, user_info: dict) -> None:
        """Update user names from Supabase user metadata"""
        metadata = user_info.get("user_metadata", {})
        
        # Update first_name and last_name if available
        if "first_name" in metadata:
            user.first_name = metadata["first_name"]
        if "last_name" in metadata:
            user.last_name = metadata["last_name"]
        
        # Parse full_name if first_name not available
        if "full_name" in metadata and not user.first_name:
            full_name_parts = metadata["full_name"].split(" ", 1)
            user.first_name = full_name_parts[0]
            user.last_name = full_name_parts[1] if len(full_name_parts) > 1 else ""
        
        # Fallback: use email prefix if no names available
        if not user.first_name:
            user.first_name = user_info["email"].split("@")[0]
    
    async def _create_new_user(self, db: AsyncSession, user_info: dict) -> User:
        """Create a new user in the local database"""
        user_id = user_info["user_id"]
        logger.info(f"Creating new user {user_id}")
        
        # Prepare user data
        user_data = {
            "id": user_id,
            "email": user_info["email"],
            "provider": user_info.get("provider", "email"),
            "is_active": True,
            "first_name": "",
            "last_name": ""
        }
        
        # Create user object and update names
        new_user = User(**user_data)
        self._update_user_names(new_user, user_info)
        
        # Save to database
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        logger.info(f"Successfully created new user {user_id}")
        return new_user
    
    async def get_supabase_user_details(self, user_id: str) -> Optional[dict]:
        """Get user details from Supabase (requires service key)"""
        return await get_user_from_supabase(user_id)