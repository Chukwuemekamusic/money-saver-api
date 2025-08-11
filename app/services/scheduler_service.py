import logging
from datetime import datetime
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

from app.core.config import get_settings
from .reminder_service import reminder_service

logger = logging.getLogger(__name__)
settings = get_settings()

class SchedulerService:
    def __init__(self):
        # Configure scheduler
        jobstores = {
            'default': MemoryJobStore(),
        }
        executors = {
            'default': ThreadPoolExecutor(20),
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )
        
        self._setup_weekly_reminder_job()
        
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started successfully")
        else:
            logger.info("Scheduler is already running")
    
    def shutdown(self, wait: bool = True):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            logger.info("Scheduler shutdown successfully")
    
    def _setup_weekly_reminder_job(self):
        """Setup the weekly reminder job"""
        if not settings.EMAIL_ENABLED:
            logger.info("Weekly reminder job not scheduled - email disabled")
            return
            
        # Parse day of week (monday = 0, sunday = 6)
        day_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        day_of_week = day_map.get(settings.REMINDER_DAY.lower(), 0)
        
        # Add the weekly reminder job
        self.scheduler.add_job(
            reminder_service.send_weekly_reminders,
            trigger=CronTrigger(
                day_of_week=day_of_week,
                hour=settings.REMINDER_HOUR,
                minute=settings.REMINDER_MINUTE,
                timezone='UTC'
            ),
            id='weekly_savings_reminder',
            name='Weekly Savings Reminder',
            replace_existing=True
        )
        
        logger.info(
            f"Weekly reminder job scheduled for {settings.REMINDER_DAY} "
            f"at {settings.REMINDER_HOUR:02d}:{settings.REMINDER_MINUTE:02d} UTC"
        )
    
    def get_job_status(self, job_id: str) -> Optional[dict]:
        """Get status of a specific job"""
        job = self.scheduler.get_job(job_id)
        if job:
            return {
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time,
                'trigger': str(job.trigger)
            }
        return None
    
    def trigger_job_now(self, job_id: str) -> bool:
        """Manually trigger a job for testing"""
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                job.modify(next_run_time=datetime.utcnow())
                logger.info(f"Job {job_id} triggered manually")
                return True
            else:
                logger.warning(f"Job {job_id} not found")
                return False
        except Exception as e:
            logger.error(f"Failed to trigger job {job_id}: {str(e)}")
            return False

# Global scheduler service instance
scheduler_service = SchedulerService()