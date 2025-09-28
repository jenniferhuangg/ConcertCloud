# app/db.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()  # loads DATABASE_URL from .env

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://concertcloud:devpass@localhost:5432/concertcloud"
)

# Create a single Engine for the whole app
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Factory that gives you a Session for one request
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    """
    FastAPI dependency.
    Yields a SQLAlchemy Session and guarantees close() after the request.
    Commit inside your route/service when you actually change data.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()