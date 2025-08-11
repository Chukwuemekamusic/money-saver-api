import jwt
import uuid
from datetime import datetime, timedelta
from typing import Optional

from app.core.config import get_settings

settings = get_settings()

class TokenService:
    """Service for generating and validating tokens for email unsubscribe"""
    
    @staticmethod
    def generate_unsubscribe_token(user_id: str) -> str:
        """Generate a secure token for email unsubscribe"""
        payload = {
            'user_id': user_id,
            'action': 'unsubscribe',
            'exp': datetime.utcnow() + timedelta(days=365),  # Token valid for 1 year
            'iat': datetime.utcnow(),
            'jti': str(uuid.uuid4())  # Unique token ID
        }
        
        return jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm='HS256'
        )
    
    @staticmethod
    def validate_unsubscribe_token(token: str) -> Optional[str]:
        """Validate unsubscribe token and return user_id if valid"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            # Check if token is for unsubscribe action
            if payload.get('action') != 'unsubscribe':
                return None
                
            return payload.get('user_id')
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

token_service = TokenService()