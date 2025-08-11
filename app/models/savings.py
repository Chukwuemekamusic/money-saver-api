from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import (
    String, Integer, DECIMAL, Boolean, DateTime, ForeignKey,
    CheckConstraint, Index, func, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SavingPlan(Base):
    """Saving plan model with business constraints"""
    __tablename__ = "saving_plans"
    
    # Primary key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Saving plan unique identifier"
    )
    
    # Foreign key to User (Supabase UUID)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to user who owns this saving plan"
    )
    
    # Saving plan details
    savings_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Name/description of the saving goal"
    )
    amount: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2),
        nullable=False,
        comment="Target amount to save"
    )
    number_of_weeks: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Number of weeks to complete the saving plan"
    )
    total_saved_amount: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2),
        default=Decimal('0.00'),
        nullable=False,
        comment="Current total amount saved"
    )
    
    # Timestamps
    date_created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Plan creation timestamp"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="Plan last update timestamp"
    )
    
    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Soft delete timestamp"
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="saving_plans",
        lazy="select"
    )
    weekly_amounts: Mapped[List["WeeklyAmount"]] = relationship(
        "WeeklyAmount",
        back_populates="saving_plan",
        cascade="all, delete-orphan",
        lazy="select",
        order_by="WeeklyAmount.week_index"
    )
    
    # Constraints and Indexes
    __table_args__ = (
        # Business constraints
        CheckConstraint('amount > 0', name='ck_saving_plan_amount_positive'),
        CheckConstraint('number_of_weeks > 0', name='ck_saving_plan_weeks_positive'),
        CheckConstraint('number_of_weeks <= 104', name='ck_saving_plan_weeks_max_2_years'),
        CheckConstraint('total_saved_amount >= 0', name='ck_saving_plan_total_saved_non_negative'),
        CheckConstraint('total_saved_amount <= amount', name='ck_saving_plan_total_saved_not_exceed_target'),
        
        # Indexes for performance
        Index('idx_saving_plans_user_id', 'user_id'),
        Index('idx_saving_plans_user_created', 'user_id', 'date_created'),
        Index('idx_saving_plans_deleted_at', 'deleted_at'),
        Index('idx_saving_plans_user_active', 'user_id', 'deleted_at'),
    )
    
    def __repr__(self) -> str:
        return f"<SavingPlan(id={self.id}, name={self.savings_name}, amount={self.amount})>"
    
    @property
    def is_deleted(self) -> bool:
        """Check if saving plan is soft deleted"""
        return self.deleted_at is not None
    
    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage"""
        if self.amount == 0:
            return 0.0
        return float((self.total_saved_amount / self.amount) * 100)
    
    @property
    def is_completed(self) -> bool:
        """Check if saving plan is completed"""
        return self.total_saved_amount >= self.amount
    
    @property
    def remaining_amount(self) -> Decimal:
        """Calculate remaining amount to save"""
        return max(Decimal('0.00'), self.amount - self.total_saved_amount)
    
    def soft_delete(self) -> None:
        """Soft delete the saving plan"""
        self.deleted_at = func.now()


class WeeklyAmount(Base):
    """Weekly amount model for saving plans"""
    __tablename__ = "weekly_amounts"
    
    # Primary key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Weekly amount unique identifier"
    )
    
    # Foreign key to SavingPlan
    saving_plan_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("saving_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to the saving plan"
    )
    
    # Weekly amount details
    amount: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2),
        nullable=False,
        comment="Amount to save for this week"
    )
    selected: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether this week's amount has been saved"
    )
    week_index: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Week number in the saving plan (1-based)"
    )
    date_selected: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When this week's amount was marked as saved"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Weekly amount creation timestamp"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="Weekly amount last update timestamp"
    )
    
    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Soft delete timestamp"
    )
    
    # Relationships
    saving_plan: Mapped["SavingPlan"] = relationship(
        "SavingPlan",
        back_populates="weekly_amounts",
        lazy="select"
    )
    
    # Constraints and Indexes
    __table_args__ = (
        # Business constraints
        CheckConstraint('amount > 0', name='ck_weekly_amount_positive'),
        CheckConstraint('week_index IS NULL OR week_index > 0', name='ck_weekly_amount_week_index_positive'),
        
        # Indexes for performance
        Index('idx_weekly_amounts_saving_plan_id', 'saving_plan_id'),
        Index('idx_weekly_amounts_plan_week', 'saving_plan_id', 'week_index'),
        Index('idx_weekly_amounts_selected', 'selected'),
        Index('idx_weekly_amounts_date_selected', 'date_selected'),
        Index('idx_weekly_amounts_deleted_at', 'deleted_at'),
        
        # Unique constraint: one weekly amount per week per plan (nulls allowed)
        Index('idx_weekly_amounts_plan_week_unique', 'saving_plan_id', 'week_index', unique=True, postgresql_where=text('week_index IS NOT NULL')),
    )
    
    def __repr__(self) -> str:
        return f"<WeeklyAmount(id={self.id}, plan_id={self.saving_plan_id}, week={self.week_index}, amount={self.amount})>"
    
    @property
    def is_deleted(self) -> bool:
        """Check if weekly amount is soft deleted"""
        return self.deleted_at is not None
    
    def mark_as_saved(self) -> None:
        """Mark this weekly amount as saved"""
        self.selected = True
        self.date_selected = func.now()
    
    def unmark_as_saved(self) -> None:
        """Unmark this weekly amount as saved"""
        self.selected = False
        self.date_selected = None
    
    def soft_delete(self) -> None:
        """Soft delete the weekly amount"""
        self.deleted_at = func.now()