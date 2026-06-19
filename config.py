import os
from dotenv import load_dotenv

load_dotenv()

# API Auth
API_KEY_SECRET: str = os.getenv("API_KEY_SECRET", "test-key")

# Supabase
SUPABASE_URL: str | None = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str | None = os.getenv("SUPABASE_KEY")

# OpenRouter
OPENROUTER_API_KEY: str | None = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL: str = "openai/gpt-oss-120b:free"

# Scraper
SCRAPER_TIMEOUT_SECONDS: int = 10
SCRAPER_MAX_CHARS_PER_PAGE: int = 5000
LLM_MAX_INPUT_CHARS: int = 8000
LLM_MAX_TOKENS: int = 500

PRIVACY_PAGE_PATHS: list[str] = [
    "/privacy",
    "/privacy-policy",
    "/terms",
    "/security",
    "/legal",
    "/trust",
    "/compliance",
]