"""
PDF parsing service using LiteParse.
Extracts structured text from CV PDFs.
"""
from typing import Any, Dict
import tempfile
import os


def parse_cv_pdf(pdf_content: bytes) -> Dict[str, Any]:
    """
    Parse a CV PDF file and extract structured content using LiteParse.

    Args:
        pdf_content: Raw PDF bytes from uploaded file.

    Returns:
        Dict with extracted CV data (personal info, experience, education, skills).
    """
    # Write PDF to temp file for LiteParse
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_content)
        tmp_path = tmp.name

    try:
        from liteparse import LiteParse

        parser = LiteParse()
        result = parser.parse(tmp_path)

        # LiteParse returns text content with layout info
        raw_text = result.get("text", "")

        # Basic structuring of extracted text
        extracted = {
            "raw_text": raw_text,
            "personal_info": _extract_personal_info(raw_text),
            "sections": _split_into_sections(raw_text),
        }

        return extracted

    except ImportError:
        # Fallback: basic text extraction if liteparse not available
        raise RuntimeError(
            "LiteParse not installed. Install with: pip install liteparse"
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def _extract_personal_info(text: str) -> Dict[str, str]:
    """Extract personal info from raw text (name, email, phone, etc.)."""
    import re

    info = {}

    # Email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        info["email"] = email_match.group()

    # Phone
    phone_match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}', text)
    if phone_match:
        info["phone"] = phone_match.group()

    # LinkedIn
    linkedin_match = re.search(r'linkedin\.com/in/[\w\-]+', text)
    if linkedin_match:
        info["linkedin"] = linkedin_match.group()

    # Location (basic)
    lines = text.split("\n")
    for line in lines[:5]:
        if any(city in line.lower() for city in ["paris", "london", "new york", "tokyo", "berlin"]):
            info["location"] = line.strip()
            break

    return info


def _split_into_sections(text: str) -> list[Dict[str, str]]:
    """Split text into logical sections based on common CV headers."""
    import re

    section_headers = [
        "experience", "work experience", "professional experience", "emploi",
        "education", "education & training", "formation", "etudes",
        "skills", "competences", "technologies", "tools",
        "projects", "publications", "certifications", "certificates",
        "languages", "summary", "profile", "about", "objective",
        "volunteer", "awards", "honors", "references",
    ]

    sections = []
    lines = text.split("\n")
    current_section = None
    current_content = []

    for line in lines:
        line_lower = line.strip().lower()
        matched = False
        for header in section_headers:
            if header in line_lower and len(line.strip()) < 60:
                if current_section:
                    sections.append({
                        "header": current_section,
                        "content": "\n".join(current_content).strip(),
                    })
                current_section = line.strip()
                current_content = []
                matched = True
                break
        if not matched and current_section:
            current_content.append(line)

    if current_section and current_content:
        sections.append({
            "header": current_section,
            "content": "\n".join(current_content).strip(),
        })

    return sections
