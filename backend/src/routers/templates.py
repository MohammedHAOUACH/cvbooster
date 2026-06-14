from fastapi import APIRouter, HTTPException
from ..models.response import MessageResponse

router = APIRouter(prefix="/api/templates", tags=["templates"])

# Available CV templates
TEMPLATES = [
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


@router.get("")
async def list_templates():
    """List all available CV templates."""
    return {"templates": TEMPLATES}


@router.get("/{template_name}")
async def get_template(template_name: str):
    """Get details for a specific template."""
    template = next((t for t in TEMPLATES if t["name"] == template_name), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"template": template}
