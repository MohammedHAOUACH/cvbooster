"""
SQLite database setup for CVBooster.
Uses SQLAlchemy for ORM with SQLite backend.
"""
from sqlalchemy import create_engine, Column, String, Text, DateTime, Float, JSON, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
import os
import sqlite3

# Database path from environment or default
DATABASE_PATH = os.environ.get("DATABASE_PATH", "/app/data/cvbooster.db")

# Ensure directory exists
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

# SQLite engine with proper settings for single-threaded access
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
    pool_size=1,
    max_overflow=0
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(String(36), primary_key=True)
    full_name = Column(String(255), default="")
    avatar_url = Column(String(500), default="")
    provider = Column(String(50), default="google")
    email = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class OriginalCV(Base):
    __tablename__ = "original_cvs"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    file_url = Column(String(500), nullable=False)
    file_name = Column(String(255))
    file_size = Column(BigInteger)
    extracted_data = Column(JSON, default=dict)
    detected_style = Column(String(50), default="clean")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class JobPosting(Base):
    __tablename__ = "job_postings"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    source_url = Column(String(500))
    title = Column(String(255))
    company = Column(String(255))
    raw_content = Column(Text)
    detected_language = Column(String(10), default="en")
    parsed_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class GeneratedCV(Base):
    __tablename__ = "generated_cvs"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    original_cv_id = Column(String(36), nullable=False, index=True)
    job_posting_id = Column(String(36), nullable=False, index=True)
    template_name = Column(String(50), nullable=False)
    output_language = Column(String(10), default="en")
    original_cv_style = Column(String(50), default="clean")
    file_url = Column(String(500), nullable=False)
    llm_output = Column(JSON, default=dict)
    ats_score = Column(Float)
    keywords_matched = Column(String(10))
    keywords_total = Column(String(10))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    print(f"[Database] SQLite initialized at {DATABASE_PATH}")


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
