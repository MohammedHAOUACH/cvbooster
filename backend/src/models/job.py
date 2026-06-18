from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class JobPostingBase(BaseModel):
    source_url: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    raw_content: Optional[str] = None


class JobPosting(JobPostingBase):
    id: str
    user_id: str
    detected_language: Optional[str] = "en"
    parsed_data: Optional[dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ScrapeJobRequest(BaseModel):
    source_url: str


class PasteJobRequest(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    raw_content: str
