from fastapi import APIRouter, HTTPException, Depends
from ..services.local_storage import storage
from ..utils.auth import get_current_user_id
from ..services.job_scraper import scrape_job_url
from ..models.job import ScrapeJobRequest, PasteJobRequest

try:
    from langdetect import detect
    from langdetect.lang_detect_exception import LanguageDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/scrape")
async def scrape_job(
    request: ScrapeJobRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Scrape a job posting URL using crawl4ai."""
    try:
        scraped_data = await scrape_job_url(request.source_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

    job_data = {
        "user_id": user_id,
        "source_url": request.source_url,
        "title": scraped_data.get("title"),
        "company": scraped_data.get("company"),
        "raw_content": scraped_data.get("raw_content", ""),
        "detected_language": _detect_job_language(scraped_data.get("raw_content", "")),
        "parsed_data": scraped_data.get("parsed_data"),
    }

    job = storage.insert("job_postings", job_data)
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

    job = storage.insert("job_postings", job_data)
    return {"job": job, "message": "Job posting saved successfully"}


@router.get("/{job_id}")
async def get_job(
    job_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get a specific job posting."""
    job = storage.get("job_postings", job_id)

    if not job or job.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Job posting not found")

    return {"job": job}


@router.get("")
async def list_jobs(
    user_id: str = Depends(get_current_user_id)
):
    """List all job postings for the current user."""
    return {"jobs": storage.list_by_user("job_postings", user_id)}


@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a job posting."""
    job = storage.get("job_postings", job_id)

    if not job or job.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Job posting not found")

    storage.delete("job_postings", job_id)
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
