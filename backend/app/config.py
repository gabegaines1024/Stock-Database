#use this for SECRET_KEY, DATABASE_URL, and other configuration
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stock-tracker.db")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")  # Vite dev server default

class Settings:
    secret_key: str = SECRET_KEY
    algorithm: str = "HS256"
    frontend_url: str = FRONTEND_URL

settings = Settings()