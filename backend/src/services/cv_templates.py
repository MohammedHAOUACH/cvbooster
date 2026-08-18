"""
Catalog of available CV templates.
Single source of truth shared by the API (routers/templates.py)
and the generation pipeline (routers/cv_engine.py).
"""
from typing import Dict, List, Optional

TEMPLATES: List[Dict[str, str]] = [
    {
        "name": "clean",
        "display_name": "Clean",
        "description": "Simple, elegant, lots of white space. Good for all sectors.",
        "category": "general",
    },
    {
        "name": "modern",
        "display_name": "Modern",
        "description": "Contemporary design with color accents. Great for tech and marketing.",
        "category": "tech",
    },
    {
        "name": "minimal",
        "display_name": "Minimal",
        "description": "Typography-only, no colors. For design and architecture roles.",
        "category": "creative",
    },
    {
        "name": "corporate",
        "display_name": "Corporate",
        "description": "Professional two-column layout. Finance and consulting.",
        "category": "corporate",
    },
    {
        "name": "tech",
        "display_name": "Tech",
        "description": "Developer-focused with skills bars. For engineers and data roles.",
        "category": "tech",
    },
    {
        "name": "creative",
        "display_name": "Creative",
        "description": "Bold design with vibrant colors. Marketing and design roles.",
        "category": "creative",
    },
    {
        "name": "academic",
        "display_name": "Academic",
        "description": "Publications-first layout. Research and academia.",
        "category": "academic",
    },
    {
        "name": "executive",
        "display_name": "Executive",
        "description": "Impact and leadership focus. C-Level and management.",
        "category": "executive",
    },
]


def get_template(template_name: str) -> Optional[Dict[str, str]]:
    """Return the template with the given name, or None."""
    return next((t for t in TEMPLATES if t["name"] == template_name), None)


def is_valid_template(template_name: str) -> bool:
    """Check whether a template name exists in the catalog."""
    return get_template(template_name) is not None
