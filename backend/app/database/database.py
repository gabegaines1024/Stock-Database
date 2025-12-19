from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL

# Create the database engine using DATABASE_URL from config
# SQLite requires check_same_thread=False, PostgreSQL doesn't need it
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Create session local class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)