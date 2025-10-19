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

    USE_VECTOR_API: bool = os.getenv("USE_VECTOR_API", "0") in ("1", "true", "True")
    VECTOR_STORE_ID: str = os.getenv("VECTOR_STORE_ID", "").strip()
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "900"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "150"))

    QT_ENABLE: bool = os.getenv("QT_ENABLE", "1") in ("1", "true", "True")
    QT_MULTI: bool = os.getenv("QT_MULTI", "1") in ("1", "true", "True")
    QT_HYDE: bool = os.getenv("QT_HYDE", "0") in ("1", "true", "True")
    QT_MULTI_K: int = int(os.getenv("QT_MULTI_K", "3"))
    QT_LANG_MIRROR: bool = os.getenv("QT_LANG_MIRROR", "1") in ("1", "true", "True")

    PRICE_PROMPT_PER_1K: float = float(os.getenv("PRICE_PROMPT_PER_1K", "0"))
    PRICE_COMPLETION_PER_1K: float = float(os.getenv("PRICE_COMPLETION_PER_1K", "0"))

settings = Settings()
