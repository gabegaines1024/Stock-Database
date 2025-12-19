#use this for SECRET_KEY, DATABASE_URL, and other configuration
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stock-tracker.db")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")  # Vite dev server default
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_TO_FILE = os.getenv("LOG_TO_FILE", "true").lower() == "true"
LOG_TO_CONSOLE = os.getenv("LOG_TO_CONSOLE", "true").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # development, production

class Settings:
    secret_key: str = SECRET_KEY
    algorithm: str = "HS256"
    frontend_url: str = FRONTEND_URL
    log_level: str = LOG_LEVEL
    log_to_file: bool = LOG_TO_FILE
    log_to_console: bool = LOG_TO_CONSOLE
    environment: str = ENVIRONMENT
    is_production: bool = ENVIRONMENT.lower() == "production"

settings = Settings()