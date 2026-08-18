"""
PDF file serving (original + generated CVs).
Files are only served to their owner: the DB record is looked up by file
name and compared against the authenticated user.
"""
import os
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse

from ..services.sqlite_storage import storage
from ..utils.auth import get_current_user_id

router = APIRouter(prefix="/api/files", tags=["files"])

# Uploads directory - use environment variable or default
UPLOADS_DIR = os.environ.get("UPLOADS_DIR", "/app/uploads")
ORIGINAL_CVS_DIR = os.path.join(UPLOADS_DIR, "original-cvs")
GENERATED_CVS_DIR = os.path.join(UPLOADS_DIR, "generated-cvs")


@router.get("/original-cvs/{file_path:path}")
async def serve_original_cv(
    file_path: str,
    user_id: str = Depends(get_current_user_id)
):
    """Serve the owner's original CV PDF files."""
    safe_name = os.path.basename(file_path)
    record = storage.find_original_cv_by_file_name(safe_name)

    if not record or record.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="File not found")

    full_path = os.path.join(ORIGINAL_CVS_DIR, safe_name)
    if not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(full_path, media_type="application/pdf")


@router.get("/generated-cvs/{file_path:path}")
async def serve_generated_cv(
    file_path: str,
    user_id: str = Depends(get_current_user_id)
):
    """Serve the owner's generated CV PDF files."""
    safe_name = os.path.basename(file_path)
    record = storage.find_generated_cv_by_file_name(safe_name)

    if not record or record.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="File not found")

    full_path = os.path.join(GENERATED_CVS_DIR, safe_name)
    if not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(full_path, media_type="application/pdf")
