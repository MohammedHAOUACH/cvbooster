import os
import uuid
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
from supabase import Client
from ..database import get_supabase
from ..utils.auth import get_current_user_id
from ..services.pdf_parser import parse_cv_pdf
from ..models.response import MessageResponse

router = APIRouter(prefix="/api/upload", tags=["upload"])

UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "uploads")
ORIGINAL_CVS_DIR = os.path.join(UPLOADS_DIR, "original-cvs")
os.makedirs(ORIGINAL_CVS_DIR, exist_ok=True)


@router.post("/cv")
async def upload_cv(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id)
):
    """Upload a CV PDF file, parse it with LiteParse, and store locally + in Supabase."""
    if not file.content_type or file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=400, detail="File size must be under 10MB")

    # Store file locally
    file_id = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(ORIGINAL_CVS_DIR, file_id)
    with open(file_path, "wb") as f:
        f.write(content)

    # Parse the PDF with LiteParse
    try:
        extracted_data = parse_cv_pdf(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse PDF: {str(e)}")

    # Save metadata to database
    cv_data = {
        "user_id": user_id,
        "file_url": f"/api/files/original-cvs/{file_id}",
        "file_name": file.filename,
        "file_size": len(content),
        "extracted_data": extracted_data,
    }

    supabase: Client = get_supabase()
    result = supabase.table("original_cvs").insert(cv_data).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to save CV")

    return {"cv": result.data[0], "message": "CV uploaded and parsed successfully"}


@router.get("/cv/{cv_id}")
async def get_cv(
    cv_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get a specific original CV."""
    supabase: Client = get_supabase()

    result = (
        supabase.table("original_cvs")
        .select("*")
        .eq("id", cv_id)
        .eq("user_id", user_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="CV not found")

    return {"cv": result.data[0]}


@router.get("/cvs")
async def list_cvs(
    user_id: str = Depends(get_current_user_id)
):
    """List all original CVs for the current user."""
    supabase: Client = get_supabase()

    result = (
        supabase.table("original_cvs")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )

    return {"cvs": result.data or []}


@router.delete("/cv/{cv_id}")
async def delete_cv(
    cv_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete an original CV."""
    supabase: Client = get_supabase()

    result = (
        supabase.table("original_cvs")
        .select("*")
        .eq("id", cv_id)
        .eq("user_id", user_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="CV not found")

    supabase.table("original_cvs").delete().eq("id", cv_id).execute()

    return MessageResponse(message="CV deleted successfully")
