"""
PDF generation service using WeasyPrint + Jinja2.
Converts optimized CV data (JSON Resume format) into styled PDFs.
"""
import os
import shutil
import tempfile
from typing import Any, Dict, List, Optional

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")

CV_SECTION_LABELS = {
    "en": {
        "summary": "Professional Summary",
        "work": "Work Experience",
        "education": "Education",
        "skills": "Skills",
        "projects": "Projects",
        "certificates": "Certifications",
    },
    "fr": {
        "summary": "Profil Professionnel",
        "work": "Expérience Professionnelle",
        "education": "Formation",
        "skills": "Compétences",
        "projects": "Projets",
        "certificates": "Certifications",
    },
}


def generate_cv_pdf(
    cv_data: Dict[str, Any],
    template_name: str = "clean",
    output_language: Optional[str] = "en",
    original_cv_style: Optional[str] = None,
) -> str:
    """
    Generate a PDF from CV data using a named template.

    Args:
        cv_data: CV data in JSON Resume format.
        template_name: Template name (clean, modern, minimal, etc.)
        output_language: Target output language for section labels.
        original_cv_style: Detected original CV style/format.

    Returns:
        Path to the generated PDF file.
    """
    from jinja2 import Environment, FileSystemLoader
    from weasyprint import HTML

    # Setup Jinja2
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=True,
    )

    # Load template
    template_file = f"{template_name}.html"
    try:
        template = env.get_template(template_file)
    except Exception:
        # Fallback to clean template
        template = env.get_template("clean.html")

    labels = _get_section_labels(output_language)
    section_order = _detect_section_order(labels, cv_data)

    # Strip empty fields from basics to avoid rendering {'label': '', 'url': '', ...}
    if "basics" in cv_data and isinstance(cv_data["basics"], dict):
        for key in list(cv_data["basics"]):
            if cv_data["basics"][key] in (None, "", {}, []):
                del cv_data["basics"][key]

    # Render HTML
    html_content = template.render(
        cv=cv_data,
        section_labels=labels,
        section_order=section_order,
        original_cv_style=original_cv_style or template_name,
        lang=output_language or "en",
    )

    # Generate PDF with WeasyPrint
    pdf_path = tempfile.NamedTemporaryFile(
        suffix=".pdf", delete=False
    ).name

    HTML(string=html_content, base_url=STATIC_DIR).write_pdf(pdf_path)

    return pdf_path


def _get_section_labels(output_language: Optional[str]) -> Dict[str, str]:
    lang = (output_language or "en").strip().lower()
    return CV_SECTION_LABELS.get(lang, CV_SECTION_LABELS["en"])


def _detect_section_order(labels: Dict[str, str], cv_data: Dict[str, Any]) -> List[str]:
    """Return detected section order based on provided CV data, fallback to standard."""
    order = []
    if cv_data.get("basics") and cv_data.get("basics", {}).get("summary"):
        order.append("summary")
    if cv_data.get("work"):
        order.append("work")
    if cv_data.get("education"):
        order.append("education")
    if cv_data.get("skills"):
        order.append("skills")
    if cv_data.get("projects"):
        order.append("projects")
    if cv_data.get("certificates"):
        order.append("certificates")
    if not order:
        order = list(labels.keys())
    return order
