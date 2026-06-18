import os
import uuid
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from supabase import Client
from ..database import get_supabase
from ..utils.auth import get_current_user_id
from ..models.cv import GenerateCVRequest, RetemplateCVRequest
from ..services.llm_service import optimize_cv_for_job
from ..services.ats_optimizer import calculate_ats_score
from ..services.pdf_generator import generate_cv_pdf

router = APIRouter(prefix="/api/cv", tags=["cv-generation"])

UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "uploads")
GENERATED_CVS_DIR = os.path.join(UPLOADS_DIR, "generated-cvs")
os.makedirs(GENERATED_CVS_DIR, exist_ok=True)


@router.post("/generate")
async def generate_cv(
    request: GenerateCVRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Generate an ATS-optimized CV tailored to a job posting."""
    supabase: Client = get_supabase()

    # 1. Get original CV
    cv_result = (
        supabase.table("original_cvs")
        .select("*")
        .eq("id", request.original_cv_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not cv_result.data:
        raise HTTPException(status_code=404, detail="Original CV not found")
    original_cv = cv_result.data[0]

    # 2. Get job posting
    job_result = (
        supabase.table("job_postings")
        .select("*")
        .eq("id", request.job_posting_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not job_result.data:
        raise HTTPException(status_code=404, detail="Job posting not found")
    job_posting = job_result.data[0]

    output_language = job_posting.get("detected_language") or "en"
    original_cv_style = original_cv.get("extracted_data", {}).get("detected_style") or "clean"
    template_name = request.template_name or original_cv_style

    # 3. Generate optimized CV content via LLM
    try:
        optimized_cv = await optimize_cv_for_job(
            original_cv_data=original_cv.get("extracted_data", {}),
            job_posting_data=job_posting,
            output_language=output_language,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")

    # 4. Calculate ATS score
    ats_result = calculate_ats_score(
        cv_data=optimized_cv,
        job_posting_data=job_posting,
    )

    # 5. Generate PDF
    pdf_path = generate_cv_pdf(
        cv_data=optimized_cv,
        template_name=template_name,
        output_language=output_language,
        original_cv_style=original_cv_style,
    )

    # 6. Store PDF locally
    generated_id = str(uuid.uuid4())
    file_id = f"{generated_id}.pdf"
    dest_path = os.path.join(GENERATED_CVS_DIR, file_id)
    
    # Move/copy the generated PDF to our storage
    import shutil
    if pdf_path != dest_path:
        shutil.copy2(pdf_path, dest_path)

    file_url = f"/api/files/generated-cvs/{file_id}"

    # 7. Save to database
    gen_cv_data = {
        "user_id": user_id,
        "original_cv_id": request.original_cv_id,
        "job_posting_id": request.job_posting_id,
        "template_name": template_name,
        "output_language": output_language,
        "original_cv_style": original_cv_style,
        "file_url": file_url,
        "llm_output": optimized_cv,
        "ats_score": ats_result.get("score"),
        "keywords_matched": ats_result.get("keywords_matched"),
        "keywords_total": ats_result.get("keywords_total"),
    }

    result = supabase.table("generated_cvs").insert(gen_cv_data).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to save generated CV")

    return {
        "generated_cv": result.data[0],
        "message": "CV generated successfully",
    }


@router.get("/{cv_id}")
async def get_generated_cv(
    cv_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get a generated CV details."""
    supabase: Client = get_supabase()

    result = (
        supabase.table("generated_cvs")
        .select("*")
        .eq("id", cv_id)
        .eq("user_id", user_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Generated CV not found")

    return {"generated_cv": result.data[0]}


@router.get("/{cv_id}/download")
async def download_cv(
    cv_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Download the generated PDF."""
    supabase: Client = get_supabase()

    result = (
        supabase.table("generated_cvs")
        .select("file_url")
        .eq("id", cv_id)
        .eq("user_id", user_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Generated CV not found")

    file_url = result.data[0]["file_url"]
    return {"download_url": file_url}


@router.get("")
async def list_generated_cvs(
    user_id: str = Depends(get_current_user_id)
):
    """List all generated CVs for the current user."""
    supabase: Client = get_supabase()

    result = (
        supabase.table("generated_cvs")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )

    return {"generated_cvs": result.data or []}


@router.post("/{cv_id}/retail")
async def regenerate_with_template(
    cv_id: str,
    request: RetemplateCVRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Regenerate the CV with a different template."""
    supabase: Client = get_supabase()

    # Get existing generated CV
    result = (
        supabase.table("generated_cvs")
        .select("*")
        .eq("id", cv_id)
        .eq("user_id", user_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Generated CV not found")

    existing = result.data[0]

    output_language = existing.get("output_language") or "en"
    original_cv_style = existing.get("original_cv_style") or "clean"

    # Regenerate PDF with new template
    pdf_path = generate_cv_pdf(
        cv_data=existing.get("llm_output", {}),
        template_name=request.template_name,
        output_language=output_language,
        original_cv_style=original_cv_style,
    )

    file_id = f"{uuid.uuid4().hex}.pdf"
    dest_path = os.path.join(GENERATED_CVS_DIR, file_id)
    
    import shutil
    if pdf_path != dest_path:
        shutil.copy2(pdf_path, dest_path)

    new_url = f"/api/files/generated-cvs/{file_id}"

    # Update database
    updated = (
        supabase.table("generated_cvs")
        .update({"template_name": request.template_name, "file_url": new_url})
        .eq("id", cv_id)
        .execute()
    )

    return {"generated_cv": updated.data[0], "message": "Template updated"}
