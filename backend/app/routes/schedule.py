from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db, Schedule
from app.services.scraper_service import scrape_and_save
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "IITJ Doctor Schedule API"
    }

@router.get("/schedules")
def get_schedules(
    date: Optional[str] = Query(None, description="Filter by date (format: DD/MM/YYYY)"),
    db: Session = Depends(get_db)
):
    """
    Get all doctor schedules, optionally filtered by date.
    """
    query = db.query(Schedule)
    
    if date:
        # Filter by date (partial match since our date includes day name)
        query = query.filter(Schedule.date.contains(date))
    
    schedules = query.all()
    
    # Convert to dict
    results = []
    for s in schedules:
        results.append({
            "id": s.id,
            "date": s.date,
            "name": s.name,
            "timing": s.timing,
            "category": s.category,
            "room": s.room,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None
        })
    
    return {
        "count": len(results),
        "data": results
    }

@router.post("/ingest-scraped-data")
def ingest_data(db: Session = Depends(get_db)):
    """
    Manually trigger the scraper and save data to database.
    Useful for GitHub Actions or manual refreshes.
    """
    logger.info("Manual scrape triggered via API")
    result = scrape_and_save(db)
    return result

@router.get("/")
def root():
    """API root with available endpoints."""
    return {
        "message": "IITJ Doctor Schedule API",
        "version": "1.0.0",
        "endpoints": {
            "schedules": "/schedules?date=DD/MM/YYYY",
            "ingest": "/ingest-scraped-data (POST)",
            "subscribe": "/subscribe (POST)",
            "health": "/health"
        }
    }
