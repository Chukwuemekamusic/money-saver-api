"""
Pydantic schemas for savings-related operations
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class WeeklyAmountBase(BaseModel):
    """Base schema for weekly amounts"""
    amount: Decimal = Field(..., gt=0, description="Amount for this week")
    week_index: Optional[int] = Field(None, ge=1, le=104, description="Week number (1-104), null if not yet selected")
    selected: bool = Field(default=False, description="Whether this week is selected")


class WeeklyAmountCreate(WeeklyAmountBase):
    """Schema for creating a weekly amount"""
    pass


class WeeklyAmountUpdate(BaseModel):
    """Schema for updating a weekly amount"""
    amount: Optional[Decimal] = Field(None, gt=0, description="Amount for this week")
    selected: Optional[bool] = Field(None, description="Whether this week is selected")


class WeeklyAmountResponse(WeeklyAmountBase):
    """Schema for weekly amount responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    saving_plan_id: int
    date_selected: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class SavingPlanBase(BaseModel):
    """Base schema for saving plans"""
    savings_name: str = Field(..., min_length=1, max_length=200, description="Name of the saving plan")
    amount: Decimal = Field(..., gt=0, description="Target amount to save")
    number_of_weeks: int = Field(..., ge=1, le=104, description="Number of weeks for this plan")


class SavingPlanCreate(SavingPlanBase):
    """Schema for creating a saving plan"""
    weekly_amounts: Optional[List[WeeklyAmountCreate]] = Field(
        default=None, 
        description="Optional list of weekly amounts to create with the plan"
    )


class SavingPlanUpdate(BaseModel):
    """Schema for updating a saving plan"""
    savings_name: Optional[str] = Field(None, min_length=1, max_length=200, description="Name of the saving plan")
    amount: Optional[Decimal] = Field(None, gt=0, description="Target amount to save")
    number_of_weeks: Optional[int] = Field(None, ge=1, le=104, description="Number of weeks for this plan")


class SavingPlanResponse(SavingPlanBase):
    """Schema for saving plan responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: str
    total_saved_amount: Decimal = Field(default=Decimal('0'), description="Amount saved so far")
    is_completed: bool = Field(default=False, description="Whether the plan is completed")
    date_created: datetime
    updated_at: datetime
    weekly_amounts: List[WeeklyAmountResponse] = Field(default=[], description="Associated weekly amounts")


class SavingPlanListResponse(BaseModel):
    """Schema for paginated saving plan lists"""
    plans: List[SavingPlanResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class WeeklyAmountSelectRequest(BaseModel):
    """Schema for selecting/deselecting weekly amounts"""
    selected: bool = Field(..., description="Whether to select or deselect this week")


class SavingPlanStats(BaseModel):
    """Schema for saving plan statistics"""
    total_plans: int
    active_plans: int
    completed_plans: int
    total_target_amount: Decimal
    total_saved_amount: Decimal
    completion_percentage: float = Field(ge=0, le=100)


class ScheduleStatus(BaseModel):
    """Schema for weekly savings schedule status"""
    status: str = Field(..., description="Schedule status: 'on-track', 'behind', 'ahead', or 'completed'")
    weeks_elapsed: int = Field(..., ge=0, description="Number of weeks since plan creation")
    weeks_required: int = Field(..., ge=0, description="Number of weeks that should have been paid by now")
    weeks_paid: int = Field(..., ge=0, description="Number of weeks actually paid")
    weeks_behind: int = Field(default=0, ge=0, description="Number of weeks behind schedule (0 if on track or ahead)")
    weeks_ahead: int = Field(default=0, ge=0, description="Number of weeks ahead of schedule (0 if behind or on track)")
    message: str = Field(..., description="Human-readable status message")
    next_due_date: Optional[datetime] = Field(None, description="When the next payment is due (if applicable)")