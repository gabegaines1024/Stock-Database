#use this for SECRET_KEY and DATABASE_URL
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stock-tracker.db")

class Settings:
    secret_key: str = SECRET_KEY
    algorithm: str = "HS256"

settings = Settings()