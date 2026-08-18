from fastapi import APIRouter, HTTPException
from ..services.cv_templates import TEMPLATES, get_template

router = APIRouter(prefix="/api/templates", tags=["templates"])

@router.get("")
async def list_templates():
    """List all available CV templates."""
    return {"templates": TEMPLATES}


@router.get("/{template_name}")
async def get_template_endpoint(template_name: str):
    """Get details for a specific template."""
    template = get_template(template_name)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"template": template}
