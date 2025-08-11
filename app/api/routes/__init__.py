"""
API route modules

This package contains all API route handlers organized by functionality.
"""

from app.api.routes.auth import router as auth_router
from app.api.routes.savings import router as savings_router
from app.api.routes.email import router as email_router

__all__ = ["auth_router", "savings_router", "email_router"]