from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from ..database import get_supabase
from ..models.user import UserProfile, UserUpdate
from ..utils.auth import get_current_user_id, verify_supabase_jwt

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


@router.get("/session")
async def get_session(
    user_id: str = Depends(get_current_user_id)
):
    """Get current user profile from Supabase JWT token."""
    supabase: Client = get_supabase()

    profile = (
        supabase.table("profiles")
        .select("*")
        .eq("id", user_id)
        .execute()
    )

    if not profile.data:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {"user": profile.data[0]}


@router.put("/profile")
async def update_profile(
    update: UserUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """Update current user profile."""
    supabase: Client = get_supabase()

    result = (
        supabase.table("profiles")
        .update(update.model_dump(exclude_unset=True))
        .eq("id", user_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {"user": result.data[0]}
