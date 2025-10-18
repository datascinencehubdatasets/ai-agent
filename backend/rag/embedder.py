from typing import List
from openai import OpenAI
import httpx
from backend.utils.settings import settings

class Embedder:
    def __init__(self, model: str = "text-embedding-3-small", timeout: int | None = None):
        self.model = model
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            timeout=timeout or settings.REQUEST_TIMEOUT_SECONDS,
            max_retries=2,
            http_client=httpx.Client(timeout=timeout or settings.REQUEST_TIMEOUT_SECONDS),
        )

    def encode(self, texts: List[str]) -> List[List[float]]:
        # OpenAI embeddings API поддерживает батчи
        resp = self.client.embeddings.create(model=self.model, input=texts)
        return [d.embedding for d in resp.data]
