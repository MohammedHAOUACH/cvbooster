from supabase import create_client, Client
from .config import get_settings


def get_supabase() -> Client:
    """Get Supabase client with service role key (backend admin access)."""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_service_key)


def get_supabase_anon() -> Client:
    """Get Supabase client with anon key (user-level access)."""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_anon_key)
