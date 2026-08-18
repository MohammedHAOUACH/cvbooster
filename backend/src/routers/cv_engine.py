import asyncio
import os
import uuid
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse

from ..services.sqlite_storage import storage
from ..services.cv_templates import is_valid_template
from ..utils.auth import get_current_user_id
from ..models.cv import GenerateCVRequest, RetemplateCVRequest
from ..services.llm_service import optimize_cv_for_job
from ..services.ats_optimizer import calculate_ats_score
from ..services.pdf_generator import generate_cv_pdf

router = APIRouter(prefix="/api/cv", tags=["cv-generation"])

# Uploads directory - use environment variable or default
UPLOADS_DIR = os.environ.get("UPLOADS_DIR", "/app/uploads")
GENERATED_CVS_DIR = os.path.join(UPLOADS_DIR, "generated-cvs")
ORIGINAL_CVS_DIR = os.path.join(UPLOADS_DIR, "original-cvs")
os.makedirs(GENERATED_CVS_DIR, exist_ok=True)
os.makedirs(ORIGINAL_CVS_DIR, exist_ok=True)


@router.post("/generate")
async def generate_cv(
    request: GenerateCVRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Generate an ATS-optimized CV tailored to a job posting."""
    original_cv = storage.get_original_cv(request.original_cv_id)
    if not original_cv or original_cv.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Original CV not found")

    job_posting = storage.get_job_posting(request.job_posting_id)
    if not job_posting or job_posting.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Job posting not found")

    output_language = job_posting.get("detected_language") or "en"
    original_cv_style = original_cv.get("detected_style") or "clean"
    template_name = request.template_name or original_cv_style

    if not is_valid_template(template_name):
        raise HTTPException(status_code=400, detail=f"Unknown template: {template_name}")

    # 3. Generate optimized CV content via LLM
    try:
        optimized_cv = await optimize_cv_for_job(
            original_cv_data=original_cv.get("extracted_data", {}),
            job_posting_data=job_posting,
            output_language=output_language,
        )
    except Exception as e:
        print(f"[CV Engine] LLM generation failed: {e}")
        raise HTTPException(status_code=500, detail="LLM generation failed. Please try again.")

    # 4. Calculate ATS score
    ats_result = calculate_ats_score(
        cv_data=optimized_cv,
        job_posting_data=job_posting,
    )

    # 5. Generate PDF directly at its final location (CPU-bound: off the event loop)
    generated_id = str(uuid.uuid4())
    file_id = f"{generated_id}.pdf"
    dest_path = os.path.join(GENERATED_CVS_DIR, file_id)

    try:
        await asyncio.to_thread(
            generate_cv_pdf,
            optimized_cv,
            template_name,
            output_language,
            original_cv_style,
            dest_path,
        )
    except Exception as e:
        print(f"[CV Engine] PDF generation failed: {e}")
        raise HTTPException(status_code=500, detail="PDF generation failed. Please try again.")

    file_url = f"/api/files/generated-cvs/{file_id}"

    # 7. Save to SQLite storage
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

    generated_cv = storage.insert_generated_cv(gen_cv_data)
    return {
        "generated_cv": generated_cv,
        "message": "CV generated successfully",
    }


@router.get("/{cv_id}")
async def get_generated_cv(
    cv_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get a generated CV details."""
    generated_cv = storage.get_generated_cv(cv_id)

    if not generated_cv or generated_cv.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Generated CV not found")

    return {"generated_cv": generated_cv}


@router.get("/{cv_id}/download")
async def download_cv(
    cv_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Download the generated PDF."""
    generated_cv = storage.get_generated_cv(cv_id)

    if not generated_cv or generated_cv.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Generated CV not found")

    file_url = generated_cv.get("file_url")
    file_path = os.path.join(GENERATED_CVS_DIR, os.path.basename(file_url)) if file_url else None

    if not file_path or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="PDF not found")

    return FileResponse(file_path, media_type="application/pdf")


@router.delete("/{cv_id}")
async def delete_generated_cv(
    cv_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a generated CV and its PDF file."""
    generated_cv = storage.get_generated_cv(cv_id)

    if not generated_cv or generated_cv.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Generated CV not found")

    deleted = storage.delete_generated_cv(cv_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Generated CV not found")

    file_url = deleted.get("file_url")
    if file_url:
        path = os.path.join(GENERATED_CVS_DIR, os.path.basename(file_url))
        if os.path.isfile(path):
            os.remove(path)

    return {"message": "Generated CV deleted successfully"}


@router.get("")
async def list_generated_cvs(
    user_id: str = Depends(get_current_user_id)
):
    """List all generated CVs for the current user."""
    return {"generated_cvs": storage.list_generated_cvs(user_id)}


@router.post("/{cv_id}/retemplate")
async def regenerate_with_template(
    cv_id: str,
    request: RetemplateCVRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Regenerate the CV with a different template."""
    generated_cv = storage.get_generated_cv(cv_id)

    if not generated_cv or generated_cv.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Generated CV not found")

    if not is_valid_template(request.template_name):
        raise HTTPException(status_code=400, detail=f"Unknown template: {request.template_name}")

    output_language = generated_cv.get("output_language") or "en"
    original_cv_style = generated_cv.get("original_cv_style") or "clean"

    # Regenerate PDF with new template (directly at its final location)
    file_id = f"{uuid.uuid4().hex}.pdf"
    dest_path = os.path.join(GENERATED_CVS_DIR, file_id)

    try:
        await asyncio.to_thread(
            generate_cv_pdf,
            generated_cv.get("llm_output", {}),
            request.template_name,
            output_language,
            original_cv_style,
            dest_path,
        )
    except Exception as e:
        print(f"[CV Engine] PDF generation failed: {e}")
        raise HTTPException(status_code=500, detail="PDF generation failed. Please try again.")

    new_url = f"/api/files/generated-cvs/{file_id}"

    # Update SQLite storage
    updated = storage.update_generated_cv(cv_id, {
        "template_name": request.template_name,
        "file_url": new_url,
    })

    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update generated CV")

    # Remove the superseded PDF file (only once the DB points at the new one)
    old_file_url = generated_cv.get("file_url")
    if old_file_url:
        old_path = os.path.join(GENERATED_CVS_DIR, os.path.basename(old_file_url))
        if os.path.isfile(old_path):
            os.remove(old_path)

    return {"generated_cv": updated, "message": "Template updated"}
