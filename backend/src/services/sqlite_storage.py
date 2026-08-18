"""
SQLite storage service for CVBooster.
Persistent storage replacing in-memory LocalStorage.
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from ..database import (
    get_db, Profile, OriginalCV, JobPosting, GeneratedCV
)


class SQLiteStorage:
    """Storage service using SQLite backend."""
    
    def __init__(self):
        pass
    
    def _now(self) -> str:
        return datetime.now().isoformat()
    
    def _get_db(self) -> Session:
        return next(get_db())
    
    # Profile operations
    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile by ID."""
        db = self._get_db()
        try:
            profile = db.query(Profile).filter(Profile.id == user_id).first()
            if profile:
                return {
                    "id": profile.id,
                    "full_name": profile.full_name,
                    "avatar_url": profile.avatar_url,
                    "provider": profile.provider,
                    "email": profile.email,
                    "created_at": profile.created_at.isoformat() if profile.created_at else None,
                    "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
                }
            return None
        finally:
            db.close()
    
    def create_profile(self, user_id: str, full_name: str = "", avatar_url: str = "", 
                       provider: str = "google", email: str = None) -> Dict[str, Any]:
        """Create or update user profile."""
        db = self._get_db()
        try:
            profile = db.query(Profile).filter(Profile.id == user_id).first()
            if profile:
                profile.full_name = full_name or profile.full_name
                profile.avatar_url = avatar_url or profile.avatar_url
                profile.email = email or profile.email
            else:
                profile = Profile(
                    id=user_id,
                    full_name=full_name,
                    avatar_url=avatar_url,
                    provider=provider,
                    email=email
                )
                db.add(profile)
            db.commit()
            db.refresh(profile)
            return {
                "id": profile.id,
                "full_name": profile.full_name,
                "avatar_url": profile.avatar_url,
                "provider": profile.provider,
                "email": profile.email,
                "created_at": profile.created_at.isoformat() if profile.created_at else None,
                "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
            }
        finally:
            db.close()
    
    # Original CV operations
    def insert_original_cv(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert original CV record."""
        db = self._get_db()
        try:
            cv = OriginalCV(
                id=data.get("id") or str(uuid.uuid4()),
                user_id=data["user_id"],
                file_url=data["file_url"],
                file_name=data.get("file_name"),
                file_size=data.get("file_size"),
                extracted_data=data.get("extracted_data", {}),
                detected_style=data.get("detected_style", "clean"),
            )
            db.add(cv)
            db.commit()
            db.refresh(cv)
            return self._original_cv_to_dict(cv)
        finally:
            db.close()
    
    def get_original_cv(self, cv_id: str) -> Optional[Dict[str, Any]]:
        """Get original CV by ID."""
        db = self._get_db()
        try:
            cv = db.query(OriginalCV).filter(OriginalCV.id == cv_id).first()
            return self._original_cv_to_dict(cv) if cv else None
        finally:
            db.close()
    
    def list_original_cvs(self, user_id: str) -> List[Dict[str, Any]]:
        """List all original CVs for a user."""
        db = self._get_db()
        try:
            cvs = db.query(OriginalCV).filter(OriginalCV.user_id == user_id).all()
            return [self._original_cv_to_dict(cv) for cv in cvs]
        finally:
            db.close()
    
    def list_generated_cvs_by_original_cv(self, original_cv_id: str) -> List[Dict[str, Any]]:
        """List generated CVs produced from a given original CV."""
        db = self._get_db()
        try:
            cvs = (
                db.query(GeneratedCV)
                .filter(GeneratedCV.original_cv_id == original_cv_id)
                .all()
            )
            return [self._generated_cv_to_dict(cv) for cv in cvs]
        finally:
            db.close()

    def delete_original_cv(self, cv_id: str) -> Optional[Dict[str, Any]]:
        """Delete an original CV and cascade-delete its generated CVs.

        Returns the deleted original CV dict, or None if not found.
        Callers are responsible for removing PDF files from disk.
        """
        db = self._get_db()
        try:
            cv = db.query(OriginalCV).filter(OriginalCV.id == cv_id).first()
            if not cv:
                return None

            deleted_generated = (
                db.query(GeneratedCV)
                .filter(GeneratedCV.original_cv_id == cv_id)
                .all()
            )
            result = self._original_cv_to_dict(cv)
            generated_results = [self._generated_cv_to_dict(g) for g in deleted_generated]
            for g in deleted_generated:
                db.delete(g)
            db.delete(cv)
            db.commit()
            result["deleted_generated_cvs"] = generated_results
            return result
        finally:
            db.close()

    def find_original_cv_by_file_name(self, file_name: str) -> Optional[Dict[str, Any]]:
        """Find an original CV record by the stored file name (basename of file_url)."""
        db = self._get_db()
        try:
            cv = db.query(OriginalCV).filter(OriginalCV.file_url.endswith(f"/{file_name}")).first()
            return self._original_cv_to_dict(cv) if cv else None
        finally:
            db.close()

    def _original_cv_to_dict(self, cv: OriginalCV) -> Dict[str, Any]:
        return {
            "id": cv.id,
            "user_id": cv.user_id,
            "file_url": cv.file_url,
            "file_name": cv.file_name,
            "file_size": cv.file_size,
            "extracted_data": cv.extracted_data or {},
            "detected_style": cv.detected_style,
            "created_at": cv.created_at.isoformat() if cv.created_at else None,
        }
    
    # Job posting operations
    def insert_job_posting(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert job posting record."""
        db = self._get_db()
        try:
            job = JobPosting(
                id=data.get("id") or str(uuid.uuid4()),
                user_id=data["user_id"],
                source_url=data.get("source_url"),
                title=data.get("title"),
                company=data.get("company"),
                raw_content=data.get("raw_content"),
                detected_language=data.get("detected_language", "en"),
                parsed_data=data.get("parsed_data", {}),
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            return self._job_posting_to_dict(job)
        finally:
            db.close()
    
    def get_job_posting(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job posting by ID."""
        db = self._get_db()
        try:
            job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
            return self._job_posting_to_dict(job) if job else None
        finally:
            db.close()
    
    def list_job_postings(self, user_id: str) -> List[Dict[str, Any]]:
        """List all job postings for a user."""
        db = self._get_db()
        try:
            jobs = db.query(JobPosting).filter(JobPosting.user_id == user_id).all()
            return [self._job_posting_to_dict(job) for job in jobs]
        finally:
            db.close()
    
    def delete_job_posting(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Delete a job posting and cascade-delete its generated CVs.

        Returns the deleted job dict, or None if not found.
        Callers are responsible for removing generated PDF files from disk.
        """
        db = self._get_db()
        try:
            job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
            if not job:
                return None

            deleted_generated = (
                db.query(GeneratedCV)
                .filter(GeneratedCV.job_posting_id == job_id)
                .all()
            )
            result = self._job_posting_to_dict(job)
            generated_results = [self._generated_cv_to_dict(g) for g in deleted_generated]
            for g in deleted_generated:
                db.delete(g)
            db.delete(job)
            db.commit()
            result["deleted_generated_cvs"] = generated_results
            return result
        finally:
            db.close()

    def find_generated_cv_by_file_name(self, file_name: str) -> Optional[Dict[str, Any]]:
        """Find a generated CV record by the stored file name (basename of file_url)."""
        db = self._get_db()
        try:
            cv = db.query(GeneratedCV).filter(GeneratedCV.file_url.endswith(f"/{file_name}")).first()
            return self._generated_cv_to_dict(cv) if cv else None
        finally:
            db.close()

    def _job_posting_to_dict(self, job: JobPosting) -> Dict[str, Any]:
        return {
            "id": job.id,
            "user_id": job.user_id,
            "source_url": job.source_url,
            "title": job.title,
            "company": job.company,
            "raw_content": job.raw_content,
            "detected_language": job.detected_language,
            "parsed_data": job.parsed_data or {},
            "created_at": job.created_at.isoformat() if job.created_at else None,
        }
    
    # Generated CV operations
    def insert_generated_cv(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert generated CV record."""
        db = self._get_db()
        try:
            cv = GeneratedCV(
                id=data.get("id") or str(uuid.uuid4()),
                user_id=data["user_id"],
                original_cv_id=data["original_cv_id"],
                job_posting_id=data["job_posting_id"],
                template_name=data["template_name"],
                output_language=data.get("output_language", "en"),
                original_cv_style=data.get("original_cv_style", "clean"),
                file_url=data["file_url"],
                llm_output=data.get("llm_output", {}),
                ats_score=data.get("ats_score"),
                keywords_matched=data.get("keywords_matched"),
                keywords_total=data.get("keywords_total"),
            )
            db.add(cv)
            db.commit()
            db.refresh(cv)
            return self._generated_cv_to_dict(cv)
        finally:
            db.close()
    
    def get_generated_cv(self, cv_id: str) -> Optional[Dict[str, Any]]:
        """Get generated CV by ID."""
        db = self._get_db()
        try:
            cv = db.query(GeneratedCV).filter(GeneratedCV.id == cv_id).first()
            return self._generated_cv_to_dict(cv) if cv else None
        finally:
            db.close()
    
    def list_generated_cvs(self, user_id: str) -> List[Dict[str, Any]]:
        """List all generated CVs for a user."""
        db = self._get_db()
        try:
            cvs = db.query(GeneratedCV).filter(GeneratedCV.user_id == user_id).all()
            return [self._generated_cv_to_dict(cv) for cv in cvs]
        finally:
            db.close()
    
    def delete_generated_cv(self, cv_id: str) -> Optional[Dict[str, Any]]:
        """Delete a generated CV record. Returns the deleted dict or None."""
        db = self._get_db()
        try:
            cv = db.query(GeneratedCV).filter(GeneratedCV.id == cv_id).first()
            if not cv:
                return None
            result = self._generated_cv_to_dict(cv)
            db.delete(cv)
            db.commit()
            return result
        finally:
            db.close()

    def update_generated_cv(self, cv_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update generated CV record."""
        db = self._get_db()
        try:
            cv = db.query(GeneratedCV).filter(GeneratedCV.id == cv_id).first()
            if not cv:
                return None
            
            for key, value in data.items():
                if hasattr(cv, key):
                    setattr(cv, key, value)
            
            db.commit()
            db.refresh(cv)
            return self._generated_cv_to_dict(cv)
        finally:
            db.close()
    
    def _generated_cv_to_dict(self, cv: GeneratedCV) -> Dict[str, Any]:
        return {
            "id": cv.id,
            "user_id": cv.user_id,
            "original_cv_id": cv.original_cv_id,
            "job_posting_id": cv.job_posting_id,
            "template_name": cv.template_name,
            "output_language": cv.output_language,
            "original_cv_style": cv.original_cv_style,
            "file_url": cv.file_url,
            "llm_output": cv.llm_output or {},
            "ats_score": cv.ats_score,
            "keywords_matched": cv.keywords_matched,
            "keywords_total": cv.keywords_total,
            "created_at": cv.created_at.isoformat() if cv.created_at else None,
            "updated_at": cv.updated_at.isoformat() if cv.updated_at else None,
        }


# Singleton instance
storage = SQLiteStorage()
