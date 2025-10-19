from __future__ import annotations
from typing import List, Dict, Any, Optional
import httpx
from backend.utils.settings import settings
from backend.utils.logger import get_logger

log = get_logger("reranker")

class Reranker:

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, timeout: Optional[int] = None):

        base = (base_url or settings.OPENAI_BASE_URL).rstrip("/")
        self.base_url = base[:-3] if base.endswith("/v1") else base
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.timeout = timeout or settings.REQUEST_TIMEOUT_SECONDS
        self.http = httpx.Client(timeout=self.timeout)

    def rerank(self, query: str, documents: List[str], top_k: Optional[int] = None, model: Optional[str] = None):
        url = f"{self.base_url}/rerank"
        payload: Dict[str, Any] = {
            "query": query,
            "documents": documents,
            "top_k": top_k if top_k is not None else settings.RERANK_TOP_K,
        }
        if model or settings.RERANK_MODEL:
            payload["model"] = model or settings.RERANK_MODEL

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        try:
            r = self.http.post(url, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
            results = data.get("results") or data.get("data") or []

            normalized = []
            for item in results:
                idx = item.get("index")
                score = float(item.get("score", 0.0))
                if isinstance(idx, int) and 0 <= idx < len(documents):
                    normalized.append({"index": idx, "score": score})
            return normalized or None
        except Exception as e:
            log.warning(f"Rerank failed: {e}")
            return None
