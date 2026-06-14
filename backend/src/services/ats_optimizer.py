"""
ATS optimization service.
Calculates ATS score and extracts keywords from job postings.
"""
from typing import Any, Dict


def extract_keywords_from_job(job_posting_data: Dict[str, Any]) -> Dict[str, list[str]]:
    """
    Extract keywords from a job posting.

    Returns categories of keywords:
    - hard_skills
    - soft_skills
    - tools
    - certifications
    - other
    """
    raw = job_posting_data.get("raw_content", "").lower()

    # Common tech/programming keywords
    tech_keywords = [
        "python", "javascript", "typescript", "java", "c++", "c#", "ruby", "go",
        "react", "angular", "vue", "node.js", "django", "flask", "fastapi",
        "docker", "kubernetes", "aws", "azure", "gcp", "terraform",
        "sql", "nosql", "mongodb", "postgresql", "mysql",
        "machine learning", "deep learning", "nlp", "computer vision",
        "agile", "scrum", "git", "ci/cd", "devops",
        "html", "css", "sass", "tailwind",
        "api", "rest", "graphql", "microservices",
    ]

    # Common soft skills
    soft_skills = [
        "leadership", "communication", "teamwork", "problem solving",
        "critical thinking", "creativity", "adaptability", "time management",
        "collaboration", "mentoring", "stakeholder management",
        "project management", "strategic thinking", "negotiation",
    ]

    # Find matches
    found_hard = [k for k in tech_keywords if k in raw]
    found_soft = [k for k in soft_skills if k in raw]

    return {
        "hard_skills": found_hard,
        "soft_skills": found_soft,
        "tools": [],
        "certifications": [],
    }


def calculate_ats_score(
    cv_data: Dict[str, Any],
    job_posting_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Calculate ATS compatibility score between CV and job posting.

    Returns:
        {
            "score": float (0-100),
            "keywords_matched": int,
            "keywords_total": int,
            "breakdown": { ... },
        }
    """
    # Extract job keywords
    job_keywords = extract_keywords_from_job(job_posting_data)
    all_job_keywords = []
    for category, keywords in job_keywords.items():
        all_job_keywords.extend(keywords)

    total_keywords = len(all_job_keywords)
    if total_keywords == 0:
        return {
            "score": 50.0,
            "keywords_matched": 0,
            "keywords_total": 0,
            "breakdown": {},
        }

    # Flatten CV text content
    cv_text = _flatten_cv_text(cv_data).lower()

    # Count keyword matches
    matched = 0
    matched_details = []
    for keyword in all_job_keywords:
        if keyword in cv_text:
            matched += 1
            matched_details.append(keyword)

    # Calculate score components
    keyword_match_rate = (matched / total_keywords) * 100

    # Final score (weighted)
    score = min(100, keyword_match_rate * 1.2)  # Scale up slightly

    return {
        "score": round(score, 1),
        "keywords_matched": matched,
        "keywords_total": total_keywords,
        "breakdown": {
            "keyword_match_rate": round(keyword_match_rate, 1),
            "matched_keywords": matched_details,
        },
    }


def _flatten_cv_text(cv_data: Dict[str, Any]) -> str:
    """Flatten CV data into searchable text."""
    parts = []
    
    # Handle extracted CV data (from LiteParse) - check first
    if "raw_text" in cv_data:
        parts.append(cv_data["raw_text"])
        return " ".join(parts)
    
    # Handle JSON Resume format
    if isinstance(cv_data, dict):
        basics = cv_data.get("basics", {})
        parts.append(basics.get("summary", ""))
        parts.append(basics.get("name", ""))

        for work in cv_data.get("work", []):
            parts.append(work.get("position", ""))
            parts.append(work.get("company", ""))
            parts.append(work.get("summary", ""))
            for highlight in work.get("highlights", []):
                parts.append(highlight)

        for edu in cv_data.get("education", []):
            parts.append(edu.get("area", ""))
            parts.append(edu.get("institution", ""))

        for skill in cv_data.get("skills", []):
            parts.append(skill.get("name", ""))
            for kw in skill.get("keywords", []):
                parts.append(kw)

        for project in cv_data.get("projects", []):
            parts.append(project.get("name", ""))
            parts.append(project.get("description", ""))
            for kw in project.get("keywords", []):
                parts.append(kw)

    return " ".join(parts)
