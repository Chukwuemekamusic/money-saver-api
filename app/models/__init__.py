"""
Database models for the Money Saver API

This module contains all SQLAlchemy models for the application.
Models are designed to work with Supabase Auth and include:
- Soft delete functionality
- Business constraints
- Proper indexing for performance
- UUID primary keys for Supabase compatibility
"""

from app.models.user import User
from app.models.savings import SavingPlan, WeeklyAmount

__all__ = [
    "User",
    "SavingPlan", 
    "WeeklyAmount"
]