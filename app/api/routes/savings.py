"""
API routes for savings plans management
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.savings import (
    SavingPlanCreate,
    SavingPlanResponse, 
    SavingPlanUpdate,
    SavingPlanListResponse,
    WeeklyAmountUpdate,
    WeeklyAmountResponse,
    WeeklyAmountSelectRequest,
    SavingPlanStats,
    ScheduleStatus
)
from app.services.savings_service import SavingsService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/plans",
    response_model=SavingPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new saving plan",
    description="Create a new saving plan with optional weekly amounts"
)
async def create_saving_plan(
    plan_data: SavingPlanCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new saving plan for the authenticated user"""
    try:
        plan = await SavingsService.create_saving_plan(
            db=db,
            user_id=current_user.id,
            plan_data=plan_data
        )
        return plan
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating saving plan for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create saving plan"
        )


@router.get(
    "/plans",
    response_model=SavingPlanListResponse,
    summary="Get user's saving plans",
    description="Get paginated list of user's saving plans"
)
async def get_saving_plans(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    include_deleted: bool = Query(False, description="Include soft-deleted plans"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get paginated list of user's saving plans"""
    try:
        plans, total = await SavingsService.get_user_saving_plans(
            db=db,
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            include_deleted=include_deleted
        )
        
        return SavingPlanListResponse(
            plans=plans,
            total=total,
            page=(skip // limit) + 1,
            size=limit,
            has_next=(skip + limit) < total,
            has_prev=skip > 0
        )
    except Exception as e:
        logger.error(f"Error fetching saving plans for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch saving plans"
        )


@router.get(
    "/plans/{plan_id}",
    response_model=SavingPlanResponse,
    summary="Get a specific saving plan",
    description="Get detailed information about a specific saving plan"
)
async def get_saving_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific saving plan by ID"""
    try:
        plan = await SavingsService.get_saving_plan_by_id(
            db=db,
            plan_id=plan_id,
            user_id=current_user.id
        )
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saving plan not found"
            )
        
        return plan
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching saving plan {plan_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch saving plan"
        )


@router.put(
    "/plans/{plan_id}",
    response_model=SavingPlanResponse,
    summary="Update a saving plan",
    description="Update an existing saving plan"
)
async def update_saving_plan(
    plan_id: int,
    plan_data: SavingPlanUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a specific saving plan"""
    try:
        plan = await SavingsService.update_saving_plan(
            db=db,
            plan_id=plan_id,
            user_id=current_user.id,
            plan_data=plan_data
        )
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saving plan not found"
            )
        
        return plan
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating saving plan {plan_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update saving plan"
        )


@router.delete(
    "/plans/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a saving plan",
    description="Soft delete a saving plan and its associated weekly amounts"
)
async def delete_saving_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a specific saving plan"""
    try:
        success = await SavingsService.delete_saving_plan(
            db=db,
            plan_id=plan_id,
            user_id=current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saving plan not found"
            )
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting saving plan {plan_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete saving plan"
        )


@router.put(
    "/weekly-amounts/{weekly_amount_id}",
    response_model=WeeklyAmountResponse,
    summary="Update a weekly amount",
    description="Update a specific weekly amount (amount or selection status)"
)
async def update_weekly_amount(
    weekly_amount_id: int,
    update_data: WeeklyAmountUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a specific weekly amount"""
    try:
        weekly_amount = await SavingsService.update_weekly_amount(
            db=db,
            weekly_amount_id=weekly_amount_id,
            user_id=current_user.id,
            update_data=update_data
        )
        
        if not weekly_amount:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Weekly amount not found"
            )
        
        return weekly_amount
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating weekly amount {weekly_amount_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update weekly amount"
        )


@router.post(
    "/weekly-amounts/{weekly_amount_id}/select",
    response_model=WeeklyAmountResponse,
    summary="Select/deselect a weekly amount",
    description="Quick endpoint to select or deselect a weekly amount"
)
async def select_weekly_amount(
    weekly_amount_id: int,
    select_data: WeeklyAmountSelectRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Select or deselect a weekly amount"""
    try:
        update_data = WeeklyAmountUpdate(selected=select_data.selected)
        weekly_amount = await SavingsService.update_weekly_amount(
            db=db,
            weekly_amount_id=weekly_amount_id,
            user_id=current_user.id,
            update_data=update_data
        )
        
        if not weekly_amount:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Weekly amount not found"
            )
        
        return weekly_amount
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error selecting weekly amount {weekly_amount_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update weekly amount selection"
        )


@router.get(
    "/stats",
    response_model=SavingPlanStats,
    summary="Get user's savings statistics",
    description="Get comprehensive statistics about user's savings plans"
)
async def get_savings_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's savings statistics"""
    try:
        stats = await SavingsService.get_user_savings_stats(
            db=db,
            user_id=current_user.id
        )
        return stats
    except Exception as e:
        logger.error(f"Error fetching savings stats for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch savings statistics"
        )


@router.get(
    "/plans/{plan_id}/schedule-status",
    response_model=ScheduleStatus,
    summary="Get plan's weekly schedule status",
    description="Get the current schedule status for a savings plan (on-track, behind, ahead, or completed)"
)
async def get_plan_schedule_status(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the weekly savings schedule status for a specific plan"""
    try:
        schedule_status = await SavingsService.get_plan_schedule_status(
            db=db,
            plan_id=plan_id,
            user_id=current_user.id
        )
        
        if not schedule_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saving plan not found"
            )
        
        return schedule_status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching schedule status for plan {plan_id} and user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch plan schedule status"
        )