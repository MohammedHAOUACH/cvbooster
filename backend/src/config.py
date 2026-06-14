import os
from functools import lru_cache
from dotenv import load_dotenv

# Load .env from project root (one level up from backend/)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


class Settings:
    def __init__(self):
        self.supabase_url: str = os.getenv("SUPABASE_URL", "https://siekxlkhsppcqwyoxrvn.supabase.co")
        self.supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
        self.supabase_service_key: str = os.getenv("SUPABASE_SERVICE_KEY", "")
        self.openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
        self.app_name: str = os.getenv("APP_NAME", "CVBooster")
        self.app_env: str = os.getenv("APP_ENV", "development")
        self.cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:80")
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"
        self.skip_auth: bool = os.getenv("SKIP_AUTH", "false").lower() == "true"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
