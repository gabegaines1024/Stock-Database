from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./stock-tracker.db"

#create the database engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

#create session local class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#create base class for models
Base = declarative_base()