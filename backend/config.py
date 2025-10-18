from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = "sk-roG3OusRr0TLCHAADks6lw"
    openai_base_url: str = "https://openai-hub.neuraldeep.tech"
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    whisper_model: str = "whisper-1"
    
    # Database
    database_url: str
    mongodb_url: str
    redis_url: str
    
    # Vector Store
    chroma_url: str = "http://localhost:8001"
    chroma_collection: str = "zaman_knowledge_base"
    
    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 86400
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()