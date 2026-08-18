"""
Job posting scraper using crawl4ai.
Scrapes job URLs from LinkedIn, Indeed, Glassdoor, etc.
"""
from typing import Any, Dict


async def scrape_job_url(url: str) -> Dict[str, Any]:
    """
    Scrape a job posting URL and extract structured data.

    Args:
        url: The job posting URL to scrape.

    Returns:
        Dict with title, company, raw_content, parsed_data.
    """
    from crawl4ai import AsyncWebCrawler

    # page_timeout (ms) is a CrawlerRunConfig option in crawl4ai >= 0.5
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, page_timeout=60000)

        if not result.success:
            raise RuntimeError(f"Failed to scrape {url}: {result.error_message}")

        # Get cleaned markdown text
        raw_content = result.markdown or result.cleaned_html or ""

        # Prefer the real page title (og:title / <title>) from the metadata;
        # on JS-heavy pages the text heuristics may pick a loading placeholder
        meta = result.metadata or {}
        meta_title = (meta.get("title") or "").strip()
        if meta_title and len(meta_title) >= 3 and "chargement" not in meta_title.lower():
            title = meta_title
        else:
            title = _extract_title(raw_content)
        company = _extract_company(raw_content)

        return {
            "title": title,
            "company": company,
            "raw_content": raw_content,
            "parsed_data": {
                "skills": [],
                "requirements": [],
                "responsibilities": [],
            },
        }


def _extract_title(content: str) -> str:
    """Extract job title from scraped content."""
    import re

    # Look for common title patterns
    patterns = [
        r'(?:Job Title|Title|Position|Role)[:\s]+(.{3,100})',
        r'<h1[^>]*>(.{3,100})</h1>',
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    # Fallback: first line that looks like a title
    lines = content.strip().split("\n")
    for line in lines[:10]:
        line = line.strip()
        if 10 < len(line) < 100 and not line.startswith(("http", "#", "-")):
            return line

    return "Job Title"


def _extract_company(content: str) -> str:
    """Extract company name from scraped content."""
    import re

    patterns = [
        r'(?:Company|Employer|Organization)[:\s]+(.{3,80})',
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return "Company"
