# backend/utils/settings.py
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://openai-hub.neuraldeep.tech/v1")
    INTENT_MODEL: str = os.getenv("INTENT_MODEL", "gpt-4o-mini")
    SERVICE_ENV: str = os.getenv("SERVICE_ENV", "dev")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    USE_RERANK: bool = os.getenv("USE_RERANK", "0") in ("1", "true", "True")
    RERANK_TOP_K: int = int(os.getenv("RERANK_TOP_K", "4"))
    RERANK_MODEL: str = os.getenv("RERANK_MODEL", "default")

# ВАЖНО: именно это имя экспортируется и импортируется далее
settings = Settings()
