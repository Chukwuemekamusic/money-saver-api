"""
Service layer for savings-related operations
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, select, update, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.savings import SavingPlan, WeeklyAmount
from app.schemas.savings import (
    SavingPlanCreate, 
    SavingPlanUpdate, 
    WeeklyAmountCreate,
    WeeklyAmountUpdate,
    SavingPlanStats,
    ScheduleStatus
)

logger = logging.getLogger(__name__)


class SavingsService:
    """Service for managing savings plans and weekly amounts"""
    
    @staticmethod
    async def create_saving_plan(
        db: AsyncSession, 
        user_id: str, 
        plan_data: SavingPlanCreate
    ) -> SavingPlan:
        """Create a new saving plan with optional weekly amounts"""
        try:
            # Create the saving plan
            db_plan = SavingPlan(
                user_id=user_id,
                savings_name=plan_data.savings_name,
                amount=plan_data.amount,
                number_of_weeks=plan_data.number_of_weeks,
                total_saved_amount=Decimal('0')
            )
            
            db.add(db_plan)
            await db.flush()  # Get the plan ID
            
            # Create weekly amounts if provided
            if plan_data.weekly_amounts:
                for week_data in plan_data.weekly_amounts:
                    # Validate week_index is within the plan's number_of_weeks (only if week_index is not null)
                    if week_data.week_index is not None and week_data.week_index > plan_data.number_of_weeks:
                        raise ValueError(f"Week index {week_data.week_index} exceeds plan duration of {plan_data.number_of_weeks} weeks")
                    
                    db_week = WeeklyAmount(
                        saving_plan_id=db_plan.id,
                        amount=week_data.amount,
                        week_index=week_data.week_index,
                        selected=week_data.selected,
                        date_selected=datetime.utcnow() if week_data.selected else None
                    )
                    db.add(db_week)
            
            await db.commit()
            await db.refresh(db_plan, ['weekly_amounts'])
            
            logger.info(f"Created saving plan {db_plan.id} for user {user_id}")
            return db_plan
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating saving plan for user {user_id}: {str(e)}")
            raise
    
    @staticmethod
    async def get_user_saving_plans(
        db: AsyncSession,
        user_id: str,
        skip: int = 0,
        limit: int = 10,
        include_deleted: bool = False
    ) -> Tuple[List[SavingPlan], int]:
        """Get paginated list of user's saving plans"""
        try:
            # Base query
            query = select(SavingPlan).where(SavingPlan.user_id == user_id)
            
            # Filter out deleted plans unless requested
            if not include_deleted:
                query = query.where(SavingPlan.deleted_at.is_(None))
            
            # Include weekly amounts
            query = query.options(selectinload(SavingPlan.weekly_amounts))
            
            # Get total count
            count_query = select(func.count(SavingPlan.id)).where(SavingPlan.user_id == user_id)
            if not include_deleted:
                count_query = count_query.where(SavingPlan.deleted_at.is_(None))
            
            total_result = await db.execute(count_query)
            total = total_result.scalar() or 0
            
            # Get paginated results
            query = query.order_by(SavingPlan.date_created.desc()).offset(skip).limit(limit)
            result = await db.execute(query)
            plans = result.scalars().all()
            
            return list(plans), total
            
        except Exception as e:
            logger.error(f"Error fetching saving plans for user {user_id}: {str(e)}")
            raise
    
    @staticmethod
    async def get_saving_plan_by_id(
        db: AsyncSession,
        plan_id: int,
        user_id: str
    ) -> Optional[SavingPlan]:
        """Get a specific saving plan by ID for a user"""
        try:
            query = select(SavingPlan).where(
                and_(
                    SavingPlan.id == plan_id,
                    SavingPlan.user_id == user_id,
                    SavingPlan.deleted_at.is_(None)
                )
            ).options(selectinload(SavingPlan.weekly_amounts))
            
            result = await db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error fetching saving plan {plan_id} for user {user_id}: {str(e)}")
            raise
    
    @staticmethod
    async def update_saving_plan(
        db: AsyncSession,
        plan_id: int,
        user_id: str,
        plan_data: SavingPlanUpdate
    ) -> Optional[SavingPlan]:
        """Update a saving plan"""
        try:
            # Get the existing plan
            db_plan = await SavingsService.get_saving_plan_by_id(db, plan_id, user_id)
            if not db_plan:
                return None
            
            # Update fields
            update_data = plan_data.model_dump(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(db_plan, field, value)
                
                db_plan.updated_at = datetime.utcnow()
                await db.commit()
                await db.refresh(db_plan, ['weekly_amounts'])
            
            logger.info(f"Updated saving plan {plan_id} for user {user_id}")
            return db_plan
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating saving plan {plan_id} for user {user_id}: {str(e)}")
            raise
    
    @staticmethod
    async def delete_saving_plan(
        db: AsyncSession,
        plan_id: int,
        user_id: str
    ) -> bool:
        """Soft delete a saving plan"""
        try:
            # Get the existing plan
            db_plan = await SavingsService.get_saving_plan_by_id(db, plan_id, user_id)
            if not db_plan:
                return False
            
            # Soft delete the plan and its weekly amounts
            now = datetime.utcnow()
            db_plan.deleted_at = now
            db_plan.updated_at = now
            
            # Also soft delete associated weekly amounts
            await db.execute(
                update(WeeklyAmount)
                .where(WeeklyAmount.saving_plan_id == plan_id)
                .values(deleted_at=now, updated_at=now)
            )
            
            await db.commit()
            logger.info(f"Deleted saving plan {plan_id} for user {user_id}")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting saving plan {plan_id} for user {user_id}: {str(e)}")
            raise
    
    @staticmethod
    async def update_weekly_amount(
        db: AsyncSession,
        weekly_amount_id: int,
        user_id: str,
        update_data: WeeklyAmountUpdate
    ) -> Optional[WeeklyAmount]:
        """Update a weekly amount"""
        try:
            # Get the weekly amount and verify ownership
            query = select(WeeklyAmount).join(SavingPlan).where(
                and_(
                    WeeklyAmount.id == weekly_amount_id,
                    SavingPlan.user_id == user_id,
                    WeeklyAmount.deleted_at.is_(None),
                    SavingPlan.deleted_at.is_(None)
                )
            )
            
            result = await db.execute(query)
            db_weekly = result.scalar_one_or_none()
            
            if not db_weekly:
                return None
            
            # Update fields
            update_fields = update_data.model_dump(exclude_unset=True)
            if update_fields:
                selection_changed = False
                for field, value in update_fields.items():
                    setattr(db_weekly, field, value)
                    if field == 'selected':
                        selection_changed = True
                
                # Update date_selected if selection status changed
                if 'selected' in update_fields:
                    db_weekly.date_selected = datetime.utcnow() if update_fields['selected'] else None
                
                db_weekly.updated_at = datetime.utcnow()
                await db.commit()
                
                # If selection status changed, recalculate week indices and update total_saved_amount
                if selection_changed:
                    await SavingsService.recalculate_week_indices(
                        db=db, 
                        saving_plan_id=db_weekly.saving_plan_id, 
                        user_id=user_id
                    )
                    # Update the plan's total_saved_amount
                    await SavingsService.update_plan_total_saved(
                        db=db,
                        saving_plan_id=db_weekly.saving_plan_id,
                        user_id=user_id
                    )
                
                await db.refresh(db_weekly)
            
            logger.info(f"Updated weekly amount {weekly_amount_id} for user {user_id}")
            return db_weekly
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating weekly amount {weekly_amount_id} for user {user_id}: {str(e)}")
            raise
    
    @staticmethod
    async def recalculate_week_indices(
        db: AsyncSession,
        saving_plan_id: int,
        user_id: str
    ) -> List[WeeklyAmount]:
        """Recalculate week indices based on date_selected order"""
        try:
            # Get all selected weekly amounts for this plan, ordered by date_selected
            selected_query = select(WeeklyAmount).join(SavingPlan).where(
                and_(
                    WeeklyAmount.saving_plan_id == saving_plan_id,
                    SavingPlan.user_id == user_id,
                    WeeklyAmount.selected == True,
                    WeeklyAmount.deleted_at.is_(None),
                    SavingPlan.deleted_at.is_(None)
                )
            ).order_by(WeeklyAmount.date_selected.asc())
            
            result = await db.execute(selected_query)
            selected_amounts = list(result.scalars().all())
            
            # Assign week indices based on selection order
            for index, weekly_amount in enumerate(selected_amounts):
                weekly_amount.week_index = index + 1
                weekly_amount.updated_at = datetime.utcnow()
            
            # Get all unselected amounts and set their week_index to null
            unselected_query = select(WeeklyAmount).join(SavingPlan).where(
                and_(
                    WeeklyAmount.saving_plan_id == saving_plan_id,
                    SavingPlan.user_id == user_id,
                    WeeklyAmount.selected == False,
                    WeeklyAmount.deleted_at.is_(None),
                    SavingPlan.deleted_at.is_(None)
                )
            )
            
            result = await db.execute(unselected_query)
            unselected_amounts = list(result.scalars().all())
            
            # Set week_index to null for unselected amounts
            for weekly_amount in unselected_amounts:
                weekly_amount.week_index = None
                weekly_amount.updated_at = datetime.utcnow()
            
            await db.commit()
            
            # Return all weekly amounts for this plan
            all_query = select(WeeklyAmount).where(
                and_(
                    WeeklyAmount.saving_plan_id == saving_plan_id,
                    WeeklyAmount.deleted_at.is_(None)
                )
            ).order_by(
                # Selected items first (by week_index), then unselected items
                WeeklyAmount.week_index.asc().nulls_last(),
                WeeklyAmount.amount.asc()
            )
            
            result = await db.execute(all_query)
            return list(result.scalars().all())
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error recalculating week indices for plan {saving_plan_id}: {str(e)}")
            raise

    @staticmethod
    async def get_user_savings_stats(
        db: AsyncSession,
        user_id: str
    ) -> SavingPlanStats:
        """Get user's savings statistics"""
        try:
            # Get basic plan counts
            stats_query = select(
                func.count(SavingPlan.id).label('total_plans'),
                func.sum(
                    case(
                        (SavingPlan.total_saved_amount >= SavingPlan.amount, 1),
                        else_=0
                    )
                ).label('completed_plans'),
                func.sum(SavingPlan.amount).label('total_target'),
                func.sum(SavingPlan.total_saved_amount).label('total_saved')
            ).where(
                and_(
                    SavingPlan.user_id == user_id,
                    SavingPlan.deleted_at.is_(None)
                )
            )
            
            result = await db.execute(stats_query)
            row = result.first()
            
            total_plans = row.total_plans or 0
            completed_plans = row.completed_plans or 0
            total_target = row.total_target or Decimal('0')
            total_saved = row.total_saved or Decimal('0')
            
            active_plans = total_plans - completed_plans
            completion_percentage = float(
                (total_saved / total_target * 100) if total_target > 0 else 0
            )
            
            return SavingPlanStats(
                total_plans=total_plans,
                active_plans=active_plans,
                completed_plans=completed_plans,
                total_target_amount=total_target,
                total_saved_amount=total_saved,
                completion_percentage=round(completion_percentage, 2)
            )
            
        except Exception as e:
            logger.error(f"Error fetching savings stats for user {user_id}: {str(e)}")
            raise

    @staticmethod
    async def update_plan_total_saved(
        db: AsyncSession,
        saving_plan_id: int,
        user_id: str
    ) -> None:
        """Update the total_saved_amount for a saving plan based on selected weekly amounts"""
        try:
            # Get the saving plan to verify ownership
            plan_query = select(SavingPlan).where(
                and_(
                    SavingPlan.id == saving_plan_id,
                    SavingPlan.user_id == user_id,
                    SavingPlan.deleted_at.is_(None)
                )
            )
            
            result = await db.execute(plan_query)
            db_plan = result.scalar_one_or_none()
            
            if not db_plan:
                return
            
            # Calculate total saved amount from selected weekly amounts
            total_query = select(
                func.coalesce(func.sum(WeeklyAmount.amount), 0).label('total_saved')
            ).where(
                and_(
                    WeeklyAmount.saving_plan_id == saving_plan_id,
                    WeeklyAmount.selected == True,
                    WeeklyAmount.deleted_at.is_(None)
                )
            )
            
            result = await db.execute(total_query)
            total_saved = result.scalar() or Decimal('0')
            
            # Update the plan's total_saved_amount
            db_plan.total_saved_amount = total_saved
            db_plan.updated_at = datetime.utcnow()
            
            await db.commit()
            
            logger.info(f"Updated total_saved_amount to {total_saved} for plan {saving_plan_id}")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating total_saved_amount for plan {saving_plan_id}: {str(e)}")
            raise

    @staticmethod
    async def get_plan_schedule_status(
        db: AsyncSession,
        plan_id: int,
        user_id: str
    ) -> Optional[ScheduleStatus]:
        """Get the weekly savings schedule status for a plan"""
        try:
            # Get the saving plan
            db_plan = await SavingsService.get_saving_plan_by_id(db, plan_id, user_id)
            if not db_plan:
                return None
            
            # Calculate time-based metrics
            now = datetime.utcnow().replace(tzinfo=db_plan.date_created.tzinfo)
            plan_start = db_plan.date_created
            time_diff = now - plan_start
            weeks_elapsed = max(0, time_diff.days // 7)  # Full weeks elapsed since plan creation
            
            # Count paid weeks
            weeks_paid = len([w for w in db_plan.weekly_amounts if w.selected and not w.deleted_at])
            
            # Calculate required weeks (don't exceed plan duration)
            weeks_required = min(weeks_elapsed, db_plan.number_of_weeks)
            
            # Check if plan is completed
            if weeks_paid >= db_plan.number_of_weeks:
                return ScheduleStatus(
                    status="completed",
                    weeks_elapsed=weeks_elapsed,
                    weeks_required=weeks_required,
                    weeks_paid=weeks_paid,
                    weeks_behind=0,
                    weeks_ahead=0,
                    message="Savings plan completed!",
                    next_due_date=None
                )
            
            # Determine status and calculate metrics
            if weeks_paid >= weeks_required:
                # On track or ahead
                weeks_ahead = weeks_paid - weeks_required
                if weeks_ahead > 0:
                    return ScheduleStatus(
                        status="ahead",
                        weeks_elapsed=weeks_elapsed,
                        weeks_required=weeks_required,
                        weeks_paid=weeks_paid,
                        weeks_behind=0,
                        weeks_ahead=weeks_ahead,
                        message=f"Great! You're {weeks_ahead} week{'s' if weeks_ahead != 1 else ''} ahead of schedule",
                        next_due_date=plan_start.replace(hour=0, minute=0, second=0, microsecond=0) + 
                                     timedelta(days=(weeks_paid + 1) * 7) if weeks_paid < db_plan.number_of_weeks else None
                    )
                else:
                    return ScheduleStatus(
                        status="on-track",
                        weeks_elapsed=weeks_elapsed,
                        weeks_required=weeks_required,
                        weeks_paid=weeks_paid,
                        weeks_behind=0,
                        weeks_ahead=0,
                        message="Perfect! You're on track with your savings schedule",
                        next_due_date=plan_start.replace(hour=0, minute=0, second=0, microsecond=0) + 
                                     timedelta(days=(weeks_paid + 1) * 7) if weeks_paid < db_plan.number_of_weeks else None
                    )
            else:
                # Behind schedule
                weeks_behind = weeks_required - weeks_paid
                return ScheduleStatus(
                    status="behind",
                    weeks_elapsed=weeks_elapsed,
                    weeks_required=weeks_required,
                    weeks_paid=weeks_paid,
                    weeks_behind=weeks_behind,
                    weeks_ahead=0,
                    message=f"You're {weeks_behind} week{'s' if weeks_behind != 1 else ''} behind schedule. Catch up when you can!",
                    next_due_date=plan_start.replace(hour=0, minute=0, second=0, microsecond=0) + 
                                 datetime.timedelta(days=(weeks_paid + 1) * 7) if weeks_paid < db_plan.number_of_weeks else None
                )
            
        except Exception as e:
            logger.error(f"Error getting schedule status for plan {plan_id}: {str(e)}")
            raise