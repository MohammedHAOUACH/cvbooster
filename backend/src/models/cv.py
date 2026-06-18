from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class OriginalCVBase(BaseModel):
    file_name: Optional[str] = None
    file_size: Optional[int] = None


class OriginalCV(OriginalCVBase):
    id: str
    user_id: str
    file_url: str
    extracted_data: Optional[dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class GeneratedCVBase(BaseModel):
    original_cv_id: str
    job_posting_id: str
    template_name: str


class GeneratedCV(GeneratedCVBase):
    id: str
    user_id: str
    file_url: str
    output_language: Optional[str] = "en"
    original_cv_style: Optional[str] = "clean"
    llm_output: Optional[dict[str, Any]] = None
    ats_score: Optional[float] = None
    keywords_matched: Optional[int] = None
    keywords_total: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GenerateCVRequest(BaseModel):
    original_cv_id: str
    job_posting_id: str
    template_name: str


class RetemplateCVRequest(BaseModel):
    template_name: str
