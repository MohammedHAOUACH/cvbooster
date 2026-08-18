import os
from functools import lru_cache
from dotenv import load_dotenv

# Load .env from project root (one level up from backend/)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


class Settings:
    def __init__(self):
        self.openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
        self.app_name: str = os.getenv("APP_NAME", "CVBooster")
        self.app_env: str = os.getenv("APP_ENV", "development")
        self.cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:80")
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"
        self.skip_auth: bool = os.getenv("SKIP_AUTH", "false").lower() == "true"
        self.use_openrouter: bool = os.getenv("USE_OPENROUTER", "false").lower() == "true"
        self.openrouter_model: str = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct")
        self.local_llm_url: str = os.getenv("LOCAL_LLM_URL", "http://localhost:1234")
        self.local_llm_model: str = os.getenv("LOCAL_LLM_MODEL", "")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
