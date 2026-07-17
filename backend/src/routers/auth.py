from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from typing import Optional

from ..services.sqlite_storage import storage
from ..services.google_auth import google_auth
from ..models.user import UserUpdate, UserProfile
from ..utils.auth import get_current_user_id

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/session")
async def get_session(
    user_id: str = Depends(get_current_user_id)
):
    """Get current user profile."""
    profile = storage.get_profile(user_id)
    
    if not profile:
        # Auto-create profile for existing users
        profile = storage.create_profile(
            user_id=user_id,
            provider="local"
        )
    
    return {"user": profile}


@router.put("/profile")
async def update_profile(
    update: UserUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """Update current user profile."""
    profile = storage.get_profile(user_id)
    
    if not profile:
        profile = storage.create_profile(user_id=user_id)
    
    updated = storage.create_profile(
        user_id=user_id,
        full_name=update.full_name or profile["full_name"],
        avatar_url=update.avatar_url or profile["avatar_url"]
    )
    
    return {"user": updated}


@router.get("/google")
async def google_login():
    """Initiate Google OAuth flow."""
    result = google_auth.get_google_auth_url()
    
    # Store state in session/cookie (simplified - in production use proper session)
    # For now, redirect directly to Google
    return RedirectResponse(url=result.get("auth_url", ""))


@router.get("/google/callback")
async def google_callback(code: str, state: Optional[str] = None):
    """Handle Google OAuth callback."""
    if not code:
        return RedirectResponse(url="/login?error=no_code")
    
    # Verify Google token and get user info
    auth_result = await google_auth.verify_google_token(code)
    
    if not auth_result:
        return RedirectResponse(url="/login?error=auth_failed")
    
    # Redirect to frontend with token
    # In production, set cookie or use proper auth flow
    return RedirectResponse(
        url=f"/login?token={auth_result['access_token']}&name={auth_result['user'].get('full_name', '')}"
    )


@router.post("/logout")
async def logout():
    """Logout (client-side token removal)."""
    return {"message": "Logged out successfully"}
