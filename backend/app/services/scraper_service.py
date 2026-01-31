from sqlalchemy.orm import Session
from app.database import Schedule
from app.scraper.extract_schedule import extract_schedule
import logging

logger = logging.getLogger(__name__)

def scrape_and_save(db: Session) -> dict:
    """
    Runs the scraper and saves results to database.
    Returns: dict with status and count
    """
    try:
        logger.info("Starting scraper...")
        data = extract_schedule()
        
        if not data:
            logger.warning("No data returned from scraper")
            return {"status": "warning", "message": "No data scraped", "count": 0}
        
        # Clear existing schedules (or implement smart update logic)
        # For simplicity, we'll delete all and re-insert
        db.query(Schedule).delete()
        
        # Insert new schedules
        for item in data:
            schedule = Schedule(
                date=item.get("date", ""),
                name=item.get("name", ""),
                timing=item.get("timing", ""),
                category=item.get("category", ""),
                room=item.get("room", "")
            )
            db.add(schedule)
        
        db.commit()
        logger.info(f"Saved {len(data)} schedules to database")
        
        return {
            "status": "success",
            "message": f"Scraped and saved {len(data)} doctor schedules",
            "count": len(data)
        }
        
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        db.rollback()
        return {
            "status": "error",
            "message": f"Scraping failed: {str(e)}",
            "count": 0
        }
