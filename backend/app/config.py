from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./doctor_schedule.db"
    
    # CORS
    FRONTEND_URL: str = "http://localhost:5173"
    ALLOWED_ORIGINS: str = "*"  # Comma-separated list in production
    
    # SMTP Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""  # Gmail address
    SMTP_PASSWORD: str = ""  # Gmail App Password
    SMTP_FROM: str = ""  # Same as SMTP_USER usually
    
    # Web Push Notifications (VAPID keys)
    VAPID_PRIVATE_KEY: str = "yUOPEFAijliQeSus_vSnnW7REZRk06Z1zuYWyTYNeGQ="
    VAPID_PUBLIC_KEY: str = "BEJpKLwgDm7pKcIEA85xbHS9mKskZFU0Lujcm1fvcioxm7olRQydUIQ_I5hUYErA9kwHO6wnGKE_7XlGhvu8Cn0="
    VAPID_EMAIL: str = "mailto:admin@iitj.ac.in"
    
    # Firebase Configuration
    FIREBASE_CREDENTIALS_PATH: str = "./firebase-service-account.json"  # Path to firebase-service-account.json
    
    # Scheduler Settings
    SCRAPER_INTERVAL_HOURS: int = 6
    NOTIFICATION_INTERVAL_MINUTES: int = 1
    
    # App Settings
    APP_NAME: str = "IITJ Doctor Schedule API"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
