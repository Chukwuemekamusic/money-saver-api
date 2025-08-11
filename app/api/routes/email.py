from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.email_service import email_service
from app.services.reminder_service import reminder_service
from app.services.scheduler_service import scheduler_service
from app.services.token_service import token_service

router = APIRouter(prefix="/email", tags=["Email"])

class EmailPreferencesResponse(BaseModel):
    email_notifications: bool
    last_reminder_sent: str = None

class UpdateEmailPreferences(BaseModel):
    email_notifications: bool

class TestEmailRequest(BaseModel):
    recipient_email: EmailStr

@router.get("/preferences", response_model=EmailPreferencesResponse)
async def get_email_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's email notification preferences"""
    return EmailPreferencesResponse(
        email_notifications=current_user.email_notifications,
        last_reminder_sent=current_user.last_reminder_sent.isoformat() if current_user.last_reminder_sent else None
    )

@router.put("/preferences", response_model=EmailPreferencesResponse)
async def update_email_preferences(
    preferences: UpdateEmailPreferences,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user's email notification preferences"""
    current_user.email_notifications = preferences.email_notifications
    await db.commit()
    await db.refresh(current_user)
    
    return EmailPreferencesResponse(
        email_notifications=current_user.email_notifications,
        last_reminder_sent=current_user.last_reminder_sent.isoformat() if current_user.last_reminder_sent else None
    )

@router.post("/test")
async def send_test_email(
    request: TestEmailRequest,
    current_user: User = Depends(get_current_user)
):
    """Send test email (for development/testing)"""
    success = await email_service.send_test_email(request.recipient_email)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send test email"
        )
    
    return {"message": f"Test email sent successfully to {request.recipient_email}"}

@router.post("/send-reminder")
async def send_test_reminder(
    current_user: User = Depends(get_current_user)
):
    """Send test weekly reminder to current user"""
    success = await reminder_service.send_test_reminder(current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send test reminder"
        )
    
    return {"message": f"Test reminder sent successfully to {current_user.email}"}

@router.get("/scheduler/status")
async def get_scheduler_status():
    """Get scheduler job status"""
    job_status = scheduler_service.get_job_status('weekly_savings_reminder')
    
    if not job_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weekly reminder job not found"
        )
    
    return job_status

@router.post("/scheduler/trigger")
async def trigger_weekly_reminders():
    """Manually trigger weekly reminders (for testing)"""
    success = scheduler_service.trigger_job_now('weekly_savings_reminder')
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger weekly reminders"
        )
    
    return {"message": "Weekly reminders triggered successfully"}

@router.get("/unsubscribe")
async def unsubscribe_from_emails(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Unsubscribe user from email notifications using token"""
    # Validate token
    user_id = token_service.validate_unsubscribe_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired unsubscribe token"
        )
    
    # Find user and disable email notifications
    from sqlalchemy import select
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Disable email notifications
    user.email_notifications = False
    await db.commit()
    
    return {
        "message": f"Successfully unsubscribed {user.email} from email notifications",
        "user_email": user.email,
        "status": "unsubscribed"
    }