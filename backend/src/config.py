from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Supabase
    supabase_url: str = "https://siekxlkhsppcqwyoxrvn.supabase.co"
    supabase_anon_key: str = ""
    supabase_service_key: str = ""

    # LLM (OpenRouter via litellm)
    openrouter_api_key: str = ""

    # App
    app_name: str = "CVBooster"
    app_env: str = "development"
    cors_origins: str = "http://localhost:3000,http://localhost:80"
    debug: bool = False

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
