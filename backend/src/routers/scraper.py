from fastapi import APIRouter, HTTPException, Depends
from supabase import Client
from ..database import get_supabase
from ..utils.auth import get_current_user_id
from ..services.job_scraper import scrape_job_url
from ..models.job import JobPosting, ScrapeJobRequest, PasteJobRequest

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

    supabase: Client = get_supabase()

    job_data = {
        "user_id": user_id,
        "source_url": request.source_url,
        "title": scraped_data.get("title"),
        "company": scraped_data.get("company"),
        "raw_content": scraped_data.get("raw_content", ""),
        "parsed_data": scraped_data.get("parsed_data"),
    }

    result = supabase.table("job_postings").insert(job_data).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to save job posting")

    return {"job": result.data[0], "message": "Job scraped and saved successfully"}


@router.post("/paste")
async def paste_job(
    request: PasteJobRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Submit a job posting by pasting the text directly."""
    supabase: Client = get_supabase()

    job_data = {
        "user_id": user_id,
        "title": request.title,
        "company": request.company,
        "raw_content": request.raw_content,
    }

    result = supabase.table("job_postings").insert(job_data).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to save job posting")

    return {"job": result.data[0], "message": "Job posting saved successfully"}


@router.get("/{job_id}")
async def get_job(
    job_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get a specific job posting."""
    supabase: Client = get_supabase()

    result = (
        supabase.table("job_postings")
        .select("*")
        .eq("id", job_id)
        .eq("user_id", user_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Job posting not found")

    return {"job": result.data[0]}


@router.get("")
async def list_jobs(
    user_id: str = Depends(get_current_user_id)
):
    """List all job postings for the current user."""
    supabase: Client = get_supabase()

    result = (
        supabase.table("job_postings")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )

    return {"jobs": result.data or []}


@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a job posting."""
    supabase: Client = get_supabase()

    result = (
        supabase.table("job_postings")
        .delete()
        .eq("id", job_id)
        .eq("user_id", user_id)
        .execute()
    )

    return {"message": "Job posting deleted successfully"}
