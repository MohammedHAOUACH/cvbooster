from fastapi import APIRouter, HTTPException, Depends

from ..services.local_storage import storage
from ..models.user import UserUpdate
from ..utils.auth import get_current_user_id

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/session")
async def get_session(
    user_id: str = Depends(get_current_user_id)
):
    """Get current user profile."""
    profile = storage.get("profiles", user_id)

    if not profile:
        profile = storage.insert("profiles", {
            "id": user_id,
            "full_name": "Local Test User",
            "avatar_url": "",
            "provider": "local",
        })

    return {"user": profile}


@router.put("/profile")
async def update_profile(
    update: UserUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """Update current user profile."""
    profile = storage.get("profiles", user_id)

    if not profile:
        profile = storage.insert("profiles", {"id": user_id})

    updated = storage.update("profiles", user_id, update.model_dump(exclude_unset=True))

    if not updated:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {"user": updated}
