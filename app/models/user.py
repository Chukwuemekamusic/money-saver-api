from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Boolean, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    """User model synced with Supabase Auth"""
    __tablename__ = "users"
    
    # Use Supabase auth.users.id as primary key (UUID string)
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True,
        comment="Supabase auth user UUID"
    )
    
    # User information
    email: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        index=True,
        comment="User email address"
    )
    first_name: Mapped[str] = mapped_column(
        String(100),
        comment="User first name"
    )
    last_name: Mapped[str] = mapped_column(
        String(100),
        comment="User last name"
    )
    
    # Authentication info
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True,
        comment="Whether user account is active"
    )
    provider: Mapped[Optional[str]] = mapped_column(
        String(50),
        default="email",
        comment="Authentication provider (email, google, etc.)"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="User creation timestamp"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="User last update timestamp"
    )
    
    # Email notification preferences
    email_notifications: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="Whether user wants to receive email notifications"
    )
    last_reminder_sent: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp of last reminder email sent"
    )
    
    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Soft delete timestamp"
    )
    
    # Relationships
    saving_plans: Mapped[List["SavingPlan"]] = relationship(
        "SavingPlan",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_users_email_active', 'email', 'is_active'),
        Index('idx_users_provider', 'provider'),
        Index('idx_users_created_at', 'created_at'),
        Index('idx_users_deleted_at', 'deleted_at'),
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, provider={self.provider})>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_deleted(self) -> bool:
        """Check if user is soft deleted"""
        return self.deleted_at is not None
    
    def soft_delete(self) -> None:
        """Soft delete the user"""
        self.deleted_at = func.now()
        self.is_active = False