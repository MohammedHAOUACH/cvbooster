"""
PDF generation service using WeasyPrint + Jinja2.
Converts optimized CV data (JSON Resume format) into styled PDFs.
"""
import os
import tempfile
from typing import Any, Dict

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")


def generate_cv_pdf(
    cv_data: Dict[str, Any],
    template_name: str = "clean",
) -> str:
    """
    Generate a PDF from CV data using a named template.

    Args:
        cv_data: CV data in JSON Resume format.
        template_name: Template name (clean, modern, minimal, etc.)

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

    # Render HTML
    html_content = template.render(cv=cv_data)

    # Generate PDF with WeasyPrint
    pdf_path = tempfile.NamedTemporaryFile(
        suffix=".pdf", delete=False
    ).name

    HTML(string=html_content, base_url=STATIC_DIR).write_pdf(pdf_path)

    return pdf_path
