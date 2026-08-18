"""
CV upload endpoint: validates, parses and stores original CV PDFs.
"""
import asyncio
import os
import re
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from ..services.sqlite_storage import storage
from ..utils.auth import get_current_user_id
from ..services.pdf_parser import parse_cv_pdf

router = APIRouter(prefix="/api/upload", tags=["upload"])

# Uploads directory - use environment variable or default
UPLOADS_DIR = os.environ.get("UPLOADS_DIR", "/app/uploads")
ORIGINAL_CVS_DIR = os.path.join(UPLOADS_DIR, "original-cvs")
os.makedirs(ORIGINAL_CVS_DIR, exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def _sanitize_filename(filename: str) -> str:
    """Reduce a client-provided file name to a safe on-disk file name."""
    base = os.path.basename(filename or "cv.pdf")
    base = re.sub(r"[^A-Za-z0-9._-]", "_", base)
    if len(base) > 100:
        name, ext = os.path.splitext(base)
        base = f"{name[:100 - len(ext)]}{ext}"
    return base or "cv.pdf"


@router.post("/cv")
async def upload_cv(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id)
):
    """Upload a CV PDF file, parse it with LiteParse, and store locally."""
    if not file.content_type or file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Read with a hard size cap (chunked, so oversized uploads abort early)
    chunks = []
    total = 0
    while chunk := await file.read(1024 * 1024):
        total += len(chunk)
        if total > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File size must be under 10MB")
        chunks.append(chunk)
    content = b"".join(chunks)
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="File does not look like a valid PDF")

    # Parse the PDF with LiteParse (CPU-bound: run outside the event loop)
    try:
        extracted_data = await asyncio.to_thread(parse_cv_pdf, content)
    except Exception:
        print("[Upload] PDF parsing failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to parse PDF. Try another file.")

    # Store file locally with a sanitized file name
    safe_name = _sanitize_filename(file.filename)
    file_id = f"{uuid.uuid4().hex}_{safe_name}"
    file_path = os.path.join(ORIGINAL_CVS_DIR, file_id)
    await asyncio.to_thread(_write_file, file_path, content)

    # Save metadata to SQLite storage (persist the detected style)
    cv_data = {
        "user_id": user_id,
        "file_url": f"/api/files/original-cvs/{file_id}",
        "file_name": safe_name,
        "file_size": len(content),
        "extracted_data": extracted_data,
        "detected_style": extracted_data.get("detected_style", "clean"),
    }

    cv = storage.insert_original_cv(cv_data)
    return {"cv": cv, "message": "CV uploaded and parsed successfully"}


def _write_file(path: str, content: bytes) -> None:
    with open(path, "wb") as f:
        f.write(content)


def _local_path_for_file_url(file_url: Optional[str]) -> Optional[str]:
    """Map a stored file_url to its on-disk location."""
    if not file_url:
        return None
    name = os.path.basename(file_url)
    if "original-cvs" in file_url:
        return os.path.join(ORIGINAL_CVS_DIR, name)
    return os.path.join(os.path.join(UPLOADS_DIR, "generated-cvs"), name)


@router.get("/cv/{cv_id}")
async def get_cv(
    cv_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get a specific original CV."""
    cv = storage.get_original_cv(cv_id)
    if not cv or cv.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="CV not found")

    return {"cv": cv}


@router.get("/cvs")
async def list_cvs(
    user_id: str = Depends(get_current_user_id)
):
    """List all original CVs for the current user."""
    return {"cvs": storage.list_original_cvs(user_id)}


@router.delete("/cv/{cv_id}")
async def delete_cv(
    cv_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete an original CV, its PDF file, and the CVs generated from it."""
    cv = storage.get_original_cv(cv_id)
    if not cv or cv.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="CV not found")

    deleted = storage.delete_original_cv(cv_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="CV not found")

    # Remove PDF files (original + cascaded generated CVs)
    to_remove = [cv.get("file_url")] + [g.get("file_url") for g in deleted.get("deleted_generated_cvs", [])]
    for file_url in to_remove:
        path = _local_path_for_file_url(file_url)
        if path and os.path.isfile(path):
            os.remove(path)

    return {"message": "CV deleted successfully"}
