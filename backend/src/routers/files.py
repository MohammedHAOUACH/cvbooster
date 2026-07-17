import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/files", tags=["files"])

# Uploads directory - use environment variable or default
UPLOADS_DIR = os.environ.get("UPLOADS_DIR", "/app/uploads")


@router.get("/original-cvs/{file_path:path}")
async def serve_original_cv(file_path: str):
    """Serve original CV PDF files."""
    # Prevent directory traversal
    safe_path = os.path.basename(file_path)
    full_path = os.path.join(UPLOADS_DIR, "original-cvs", safe_path)
    
    if not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(full_path, media_type="application/pdf")


@router.get("/generated-cvs/{file_path:path}")
async def serve_generated_cv(file_path: str):
    """Serve generated CV PDF files."""
    # Prevent directory traversal
    safe_path = os.path.basename(file_path)
    full_path = os.path.join(UPLOADS_DIR, "generated-cvs", safe_path)
    
    if not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(full_path, media_type="application/pdf")
