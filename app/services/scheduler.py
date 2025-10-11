"""Scheduler service for automated daily news refresh and user briefing delivery."""

import asyncio
from datetime import datetime
from typing import List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.config import settings
from app.services.selection import news_selection_service
from app.services.summarizer import summarizer_service
from app.database import get_async_session_factory
from app.models import TelegramUser
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

class SchedulerService:
    """Service for managing scheduled tasks."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone=settings.SCHEDULER_TIMEZONE)
        self.is_running = False
    
    async def daily_news_refresh(self):
        """Daily task to refresh news for all categories."""
        try:
            logger.info("Starting daily news refresh...")
            start_time = datetime.utcnow()
            
            # Fetch articles for all available categories
            category_articles = await news_selection_service.select_articles_for_categories(
                settings.AVAILABLE_CATEGORIES
            )
            
            if not category_articles:
                logger.warning("No articles found during daily refresh")
                return
            
            # Process and save articles
            saved_articles = await summarizer_service.process_and_save_articles(category_articles)
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(
                f"Daily news refresh completed successfully! "
                f"Processed {len(saved_articles)} articles in {duration:.2f} seconds"
            )
            
        except Exception as e:
            logger.error(f"Error during daily news refresh: {e}")
            # In a production environment, you might want to send alerts here
    
    def start_scheduler(self):
        """Start the scheduler with daily news refresh job."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            # Add daily refresh job
            self.scheduler.add_job(
                func=self.daily_news_refresh,
                trigger=CronTrigger(
                    hour=settings.DAILY_REFRESH_HOUR,
                    minute=settings.DAILY_REFRESH_MINUTE,
                    timezone=settings.SCHEDULER_TIMEZONE
                ),
                id='daily_news_refresh',
                name='Daily News Refresh',
                replace_existing=True,
                max_instances=1  # Prevent overlapping executions
            )
            
            self.scheduler.start()
            self.is_running = True
            
            logger.info(
                f"Scheduler started successfully! "
                f"Daily refresh scheduled for {settings.DAILY_REFRESH_HOUR:02d}:{settings.DAILY_REFRESH_MINUTE:02d} "
                f"{settings.SCHEDULER_TIMEZONE}"
            )
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise e
    
    def stop_scheduler(self):
        """Stop the scheduler."""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        try:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("Scheduler stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    def get_scheduler_status(self):
        """Get current scheduler status and job information."""
        if not self.is_running:
            return {
                "status": "stopped",
                "jobs": []
            }
        
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "status": "running",
            "timezone": settings.SCHEDULER_TIMEZONE,
            "jobs": jobs
        }
    
    async def trigger_manual_refresh(self):
        """Manually trigger a news refresh (for testing/admin purposes)."""
        logger.info("Manual news refresh triggered")
        await self.daily_news_refresh()
    
    def add_one_time_job(self, func, run_date, job_id=None, **kwargs):
        """Add a one-time job to the scheduler."""
        if not self.is_running:
            logger.error("Cannot add job: scheduler is not running")
            return False
        
        try:
            self.scheduler.add_job(
                func=func,
                trigger='date',
                run_date=run_date,
                id=job_id,
                **kwargs
            )
            logger.info(f"One-time job added: {job_id or 'unnamed'}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add one-time job: {e}")
            return False

    async def send_briefing_to_user(self, user_id: int):
        """Send a personalized briefing to a specific user."""
        try:
            # Import here to avoid circular imports
            from app.services.telegram_bot import telegram_bot_service
            
            session_factory = get_async_session_factory()
            async with session_factory() as session:
                # Get user data
                result = await session.execute(
                    select(TelegramUser).where(TelegramUser.telegram_id == user_id)
                )
                user = result.scalar_one_or_none()
                
                if not user or not user.selected_categories or not user.is_active:
                    logger.warning(f"User {user_id} not found, inactive, or has no categories")
                    return
                
                # Generate personalized briefing
                briefing = await telegram_bot_service._generate_briefing(
                    categories=user.selected_categories,
                    user_name=user.first_name,
                    is_scheduled=True
                )
                
                if briefing and telegram_bot_service.application:
                    await telegram_bot_service.application.bot.send_message(
                        chat_id=user.telegram_id,
                        text=briefing,
                        parse_mode="Markdown"
                    )
                    logger.info(
                        f"✅ Sent scheduled briefing to {user.first_name or "Unknown"} "
                        f"(ID: {user.telegram_id}) at {datetime.utcnow().strftime("%H:%M UTC")} "
                        f"- Scheduled for: {user.daily_time}"
                    )
                else:
                    logger.error(f"Failed to generate briefing or bot not initialized for user {user_id}")
                    
        except Exception as e:
            logger.error(f"Error sending briefing to user {user_id}: {e}")
    
    def schedule_user_briefing(self, user_id: int, daily_time: str, timezone: str = "UTC"):
        """Schedule a daily briefing for a specific user."""
        try:
            # Parse time (format: "HH:MM")
            hour, minute = map(int, daily_time.split(":"))
            
            job_id = f"briefing_user_{user_id}"
            
            # Remove existing job if it exists
            try:
                self.scheduler.remove_job(job_id)
                logger.info(f"Removed existing briefing job for user {user_id}")
            except:
                pass  # Job didnt exist
            
            # Add new job
            self.scheduler.add_job(
                func=self.send_briefing_to_user,
                args=[user_id],
                trigger=CronTrigger(
                    hour=hour,
                    minute=minute,
                    timezone=timezone
                ),
                id=job_id,
                name=f"Daily Briefing for User {user_id}",
                replace_existing=True,
                max_instances=1
            )
            
            logger.info(f"📅 Scheduled daily briefing for user {user_id} at {daily_time} {timezone}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule briefing for user {user_id}: {e}")
            return False
    
    def remove_user_briefing(self, user_id: int):
        """Remove scheduled briefing for a specific user."""
        try:
            job_id = f"briefing_user_{user_id}"
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed briefing schedule for user {user_id}")
            return True
        except:
            logger.warning(f"No briefing schedule found for user {user_id}")
            return False
    
    async def sync_user_briefing_schedules(self):
        """Sync all user briefing schedules from database."""
        try:
            session_factory = get_async_session_factory()
            async with session_factory() as session:
                # Get all active users with daily_time set
                result = await session.execute(
                    select(TelegramUser).where(
                        TelegramUser.is_active == True,
                        TelegramUser.daily_time.isnot(None)
                    )
                )
                users = result.scalars().all()
                
                scheduled_count = 0
                for user in users:
                    if self.schedule_user_briefing(
                        user_id=user.telegram_id,
                        daily_time=user.daily_time,
                        timezone=user.timezone or "UTC"
                    ):
                        scheduled_count += 1
                
                logger.info(f"✅ Synced {scheduled_count} user briefing schedules")
                return scheduled_count
                
        except Exception as e:
            logger.error(f"Error syncing user briefing schedules: {e}")
            return 0

# Global scheduler service instance
scheduler_service = SchedulerService()

# Convenience functions for FastAPI integration
async def start_background_scheduler():
    """Start the scheduler in the background."""
    try:
        scheduler_service.start_scheduler()
        logger.info("Background scheduler started")
    except Exception as e:
        logger.error(f"Failed to start background scheduler: {e}")

async def stop_background_scheduler():
    """Stop the background scheduler."""
    try:
        scheduler_service.stop_scheduler()
        logger.info("Background scheduler stopped")
    except Exception as e:
        logger.error(f"Failed to stop background scheduler: {e}")

def get_scheduler_info():
    """Get scheduler information for API endpoints."""
    return scheduler_service.get_scheduler_status()
