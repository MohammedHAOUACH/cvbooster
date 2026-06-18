"""
PDF parsing service using LiteParse.
Extracts structured text from CV PDFs and detects dominant style/format.
"""
from typing import Any, Dict
import tempfile
import os

TEMPLATE_STYLES = [
    "clean", "modern", "minimal", "corporate", "tech", "creative", "academic", "executive",
]


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

        # LiteParse v2 returns ParseResult object with .text attribute
        raw_text = getattr(result, "text", "") or getattr(result, "markdown", "") or str(result)

        # Basic structuring of extracted text
        extracted = {
            "raw_text": raw_text,
            "personal_info": _extract_personal_info(raw_text),
            "sections": _split_into_sections(raw_text),
            "detected_style": _detect_cv_style(raw_text, pdf_content),
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


def _detect_cv_style(raw_text: str, pdf_content: bytes = b"") -> str:
    """Detect dominant CV style/format based on parsed text and raw PDF hints."""
    text = raw_text or ""
    sections = _split_into_sections(text)
    section_headers = [s.get("header", "").strip().lower() for s in sections]

    # Academic/research cues
    academic_cues = {"publications", "research", "certificates"}
    if sum(1 for h in section_headers if h in academic_cues) >= 2:
        return "academic"

    # Executive/leadership cues
    executive_cues = {"leadership", "management", "certifications", "awards", "honors"}
    executive_score = sum(1 for h in section_headers if h in executive_cues)
    leadership_score = sum(1 for line in text.splitlines() if any(word in line.lower() for word in ["director", "manager", "head of", "vp", "ceo", "cto"]))
    if executive_score >= 2 or leadership_score >= 3:
        return "executive"

    # Tech cues
    tech_cues = {"technologies", "tools", "projects", "frameworks"}
    if sum(1 for h in section_headers if h in tech_cues) >= 1:
        tech_words = ["python", "javascript", "typescript", "docker", "aws", "api", "rest", "react"]
        if sum(1 for w in tech_words if w in text.lower()) >= 2:
            return "tech"

    # Creative cues
    creative_cues = {"portfolio", "creative", "design", "media"}
    if sum(1 for h in section_headers if h in creative_cues) >= 1:
        return "creative"

    # Corporate cues
    corporate_cues = {"professional experience", "employment history", "qualifications"}
    if any(h in corporate_cues for h in section_headers):
        return "corporate"

    # Minimal cues: fewer section headers, shorter text, simple structure
    if len(sections) <= 3 and len(text.splitlines()) < 40:
        return "minimal"

    # Modern cues: explicit skills/tools/projects beyond basics
    if len(sections) >= 4:
        return "modern"

    return "clean"
