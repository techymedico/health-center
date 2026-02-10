from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import get_settings
from app.database import init_db
from app.scheduler import start_scheduler, stop_scheduler
from app.routes import schedule, notifications
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting application...")
    init_db()  # Initialize database
    
    # Initialize Firebase
    from app.services.fcm_service import initialize_firebase
    initialize_firebase()
    
    start_scheduler()  # Start background scheduler
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    stop_scheduler()
    logger.info("Application shut down")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
origins = settings.ALLOWED_ORIGINS.split(",") if settings.ALLOWED_ORIGINS != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(schedule.router, tags=["Schedule"])
app.include_router(notifications.router, tags=["Notifications"])

# Import and include FCM router
from app.routes import fcm
app.include_router(fcm.router, tags=["FCM"])

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "message": "Health Center API is running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
