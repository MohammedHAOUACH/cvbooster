from fastapi import APIRouter, HTTPException, Depends
from ..services.sqlite_storage import storage
from ..utils.auth import get_current_user_id
from ..utils.validators import is_safe_url_for_scraping
from ..services.job_scraper import scrape_job_url
from ..models.job import ScrapeJobRequest, PasteJobRequest

try:
    from langdetect import detect
    from langdetect.lang_detect_exception import LanguageDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

import os

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

# Uploads directory - use environment variable or default
UPLOADS_DIR = os.environ.get("UPLOADS_DIR", "/app/uploads")
GENERATED_CVS_DIR = os.path.join(UPLOADS_DIR, "generated-cvs")


@router.post("/scrape")
async def scrape_job(
    request: ScrapeJobRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Scrape a job posting URL using crawl4ai."""
    # SSRF guard: only public http(s) URLs, never internal addresses
    if not is_safe_url_for_scraping(request.source_url):
        raise HTTPException(
            status_code=400,
            detail="Invalid or unsafe URL. Only public http(s) job posting links are allowed.",
        )

    try:
        scraped_data = await scrape_job_url(request.source_url)
    except Exception as e:
        error_msg = str(e)
        print(f"[Scraper] Failed to scrape {request.source_url}: {error_msg}")
        # Check for common anti-bot protection errors
        if "Cloudflare" in error_msg or "anti-bot" in error_msg.lower() or "blocked" in error_msg.lower():
            raise HTTPException(
                status_code=403,
                detail="This website is protected by Cloudflare or similar anti-bot protection. Please use 'Paste Text' mode instead to copy and paste the job description manually."
            )
        raise HTTPException(status_code=500, detail="Scraping failed. Please use 'Paste Text' mode instead.")

    raw_content = scraped_data.get("raw_content", "") or ""
    job_data = {
        "user_id": user_id,
        "source_url": request.source_url,
        "title": scraped_data.get("title"),
        "company": scraped_data.get("company"),
        "raw_content": raw_content,
        "detected_language": _detect_job_language(raw_content),
        "parsed_data": scraped_data.get("parsed_data"),
    }

    job = storage.insert_job_posting(job_data)
    return {"job": job, "message": "Job scraped and saved successfully"}


@router.post("/paste")
async def paste_job(
    request: PasteJobRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Submit a job posting by pasting the text directly."""
    job_data = {
        "user_id": user_id,
        "title": request.title,
        "company": request.company,
        "raw_content": request.raw_content,
        "detected_language": _detect_job_language(request.raw_content or ""),
    }

    job = storage.insert_job_posting(job_data)
    return {"job": job, "message": "Job posting saved successfully"}


@router.get("/{job_id}")
async def get_job(
    job_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get a specific job posting."""
    job = storage.get_job_posting(job_id)

    if not job or job.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Job posting not found")

    return {"job": job}


@router.get("")
async def list_jobs(
    user_id: str = Depends(get_current_user_id)
):
    """List all job postings for the current user."""
    return {"jobs": storage.list_job_postings(user_id)}


@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a job posting and the CVs generated from it."""
    job = storage.get_job_posting(job_id)

    if not job or job.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Job posting not found")

    deleted = storage.delete_job_posting(job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job posting not found")

    # Remove generated PDF files (cascade)
    for g in deleted.get("deleted_generated_cvs", []):
        file_url = g.get("file_url")
        if file_url:
            path = os.path.join(GENERATED_CVS_DIR, os.path.basename(file_url))
            if os.path.isfile(path):
                os.remove(path)

    return {"message": "Job posting deleted successfully"}


def _detect_job_language(raw_content: str) -> str:
    """Detect the dominant language of a job posting, defaulting to English."""
    text = raw_content.strip() if raw_content else ""
    if not text:
        return "en"

    if LANGDETECT_AVAILABLE:
        try:
            return detect(text[:10000])
        except (LanguageDetectException, Exception):
            pass

    # Fallback heuristic: common French characters/words
    lower = text.lower()
    fr_cues = ["é", "è", "ê", "à", "ù", "ç", "expérience", "compétences", "formation", "recherche"]
    if any(cue in lower for cue in fr_cues):
        return "fr"

    return "en"
