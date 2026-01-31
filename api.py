from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from extract_schedule import extract_schedule
import uvicorn
from contextlib import asynccontextmanager
import threading
import time
import threading

# Simple in-memory cache
cached_schedule = []

def update_schedule_background():
    """Function to run in background and update schedule."""
    global cached_schedule
    print("Updating schedule...")
    try:
        data = extract_schedule()
        if data:
            cached_schedule = data
            print("Schedule updated successfully.")
        else:
            print("No data returned during update.")
    except Exception as e:
        print(f"Failed to update schedule: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load initial data
    update_schedule_background()
    yield
    # Shutdown logic if needed

app = FastAPI(title="IITJ Health Center Schedule API", lifespan=lifespan)


# Add CORS Middleware to allow requests from local HTML file
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Removed original lifespan def


# app = FastAPI(lifespan=lifespan)  <- REMOVE THIS DUPLICATE

@app.get("/")
def read_root():
    return {"message": "Welcome to IITJ Doctor Schedule API", "endpoints": ["/schedule", "/refresh"]}

@app.get("/schedule")
def get_schedule():
    """Returns the cached doctor schedule."""
    if not cached_schedule:
        # Try one immediate fetch if cache is empty
        update_schedule_background()
        
    return {"count": len(cached_schedule), "data": cached_schedule}

@app.post("/refresh")
def refresh_schedule():
    """Forces a refresh of the schedule data."""
    update_schedule_background()
    return {"status": "Refresh triggered", "current_count": len(cached_schedule)}

from notification_logic import check_upcoming_doctors
import datetime

@app.get("/notifications")
def get_notifications():
    """Checks for doctors arriving in the next 60 minutes."""
    if not cached_schedule:
        update_schedule_background()
        
    # Mock time for demo if needed, otherwise use real time
    # For demo purposes, since the schedule might be in 2026 (based on sheet), 
    # and "now" is 2026-01-31.
    now = datetime.datetime.now()
    
    upcoming = check_upcoming_doctors(cached_schedule, now)
    
    return {
        "timestamp": now.isoformat(),
        "upcoming_count": len(upcoming),
        "alerts": upcoming,
        "message": "These doctors are arriving soon!" if upcoming else "No doctors arriving in the next hour."
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
