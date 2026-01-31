from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.config import get_settings
from app.database import SessionLocal
from app.services.scraper_service import scrape_and_save
from app.services.notification_service import check_and_notify
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

scheduler = BackgroundScheduler()

def run_scraper_job():
    """Job to scrape doctor schedules periodically."""
    logger.info("Running scheduled scraper job...")
    db = SessionLocal()
    try:
        result = scrape_and_save(db)
        logger.info(f"Scraper job completed: {result}")
    except Exception as e:
        logger.error(f"Scraper job failed: {str(e)}")
    finally:
        db.close()

def run_notification_job():
    """Job to check and send notifications."""
    logger.debug("Running notification check job...")
    db = SessionLocal()
    try:
        check_and_notify(db)
    except Exception as e:
        logger.error(f"Notification job failed: {str(e)}")
    finally:
        db.close()

def start_scheduler():
    """Initialize and start the scheduler."""
    logger.info("Starting APScheduler...")
    
    # Add scraper job - runs every N hours
    scheduler.add_job(
        run_scraper_job,
        trigger=IntervalTrigger(hours=settings.SCRAPER_INTERVAL_HOURS),
        id="scraper_job",
        name="Scrape doctor schedules",
        replace_existing=True
    )
    
    # Add notification job - runs every N minutes
    scheduler.add_job(
        run_notification_job,
        trigger=IntervalTrigger(minutes=settings.NOTIFICATION_INTERVAL_MINUTES),
        id="notification_job",
        name="Check upcoming doctors and notify",
        replace_existing=True
    )
    
    # Run scraper immediately on startup
    run_scraper_job()
    
    scheduler.start()
    logger.info("Scheduler started successfully")

def stop_scheduler():
    """Stop the scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
