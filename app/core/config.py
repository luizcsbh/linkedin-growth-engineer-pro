import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
    LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
    HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
    DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", 5000))
    DATABASE_PATH = os.getenv("DATABASE_PATH", "data/growth.db")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Safe Automation Rules
    MAX_ACTIONS_PER_DAY = 20
    MAX_LIKES = 6
    MAX_PROFILE_VISITS = 5
    
    # AI Learning Engine
    MIN_ACTIONS_BEFORE_OPTIMIZATION = int(os.getenv("MIN_ACTIONS_BEFORE_OPTIMIZATION", 50))
    OPTIMIZATION_INTERVAL_DAYS = int(os.getenv("OPTIMIZATION_INTERVAL_DAYS", 7))
