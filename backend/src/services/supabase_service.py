"""
Supabase operations wrapper.
Centralized DB operations for the backend.
"""
from supabase import Client
from ..database import get_supabase


def create_profile_on_signup(user_id: str, email: str = "") -> bool:
    """Create a profile entry when a new user signs up (trigger handler)."""
    supabase: Client = get_supabase()

    result = supabase.table("profiles").insert({
        "id": user_id,
        "full_name": "",
        "avatar_url": "",
        "provider": "",
    }).execute()

    return bool(result.data)
