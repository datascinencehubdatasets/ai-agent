# backend/rag/reranker.py
from __future__ import annotations
from typing import List, Dict, Any
from openai import OpenAI
import httpx, json
from backend.utils.settings import settings
from backend.utils.logger import get_logger

log = get_logger("reranker")

class Reranker:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,  
            timeout=settings.REQUEST_TIMEOUT_SECONDS,
            max_retries=2,
            http_client=httpx.Client(timeout=settings.REQUEST_TIMEOUT_SECONDS),
        )
        self.model = getattr(settings, "RERANK_MODEL", "gpt-4o-mini")

    def rerank(self, query: str, docs: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
    
        if not docs:
            return []
        try:
            system_msg = (
                "You are a reranker model. "
                "Given a user query and several document passages, "
                "assign each document a relevance score from 0.0 to 1.0. "
                "Return a JSON array of objects: [{\"index\":int,\"score\":float}]. "
                "Score should reflect how relevant each passage is to the query."
            )
            joined_docs = "\n\n".join([f"[{i}] {t.strip()}" for i, t in enumerate(docs)])
            user_msg = f"Query: {query}\n\nDocuments:\n{joined_docs}"

            resp = self.client.chat.completions.create(
                model=self.model,
                temperature=0.0,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                response_format={"type": "json_object"},
            )

            raw = resp.choices[0].message.content or ""
            data = json.loads(raw)
            if isinstance(data, dict) and "ranking" in data:
                data = data["ranking"]
            if not isinstance(data, list):
                raise ValueError("no list in response")
            results = []
            for r in data:
                if isinstance(r, dict) and "index" in r and "score" in r:
                    results.append({"index": int(r["index"]), "score": float(r["score"])})

            results.sort(key=lambda x: -x["score"])
            return results[:top_k]
        except Exception as e:
            log.warning(f"Rerank failed: {e}")
            return []
