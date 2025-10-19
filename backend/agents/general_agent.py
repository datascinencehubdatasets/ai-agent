from __future__ import annotations
from typing import Any, Dict
from openai import OpenAI
import httpx

from backend.rag.retriever import Retriever
from backend.utils.settings import settings

RAG_SYSTEM_PROMPT = """You are a helpful assistant for banking & Islamic finance FAQs.
Use ONLY the provided context. If the answer is not in context, say you don't have that info and ask a clarifying question."""

class GeneralAgent:
    name = "general_knowledge"

    def __init__(self):
        self.retriever = Retriever()
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            timeout=settings.REQUEST_TIMEOUT_SECONDS,
            max_retries=2,
            http_client=httpx.Client(timeout=settings.REQUEST_TIMEOUT_SECONDS),
        )
        self.model = "gpt-4o-mini"

    def run(self, query: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        history = (context or {}).get("history") or []
        hits = self.retriever.retrieve(query, history=history)
        ctx = self.retriever.format_context(hits)

        messages = [
            {"role": "system", "content": RAG_SYSTEM_PROMPT},
            {"role": "system", "content": f"CONTEXT:\n{ctx or '(no relevant context)'}"},
            {"role": "user", "content": query},
        ]
        resp = self.client.chat.completions.create(
            model=self.model, temperature=0.2, messages=messages
        )
        answer = resp.choices[0].message.content.strip()

        return {
            "answer": answer,
            "used_docs": [
                {"source": h.get("meta", {}).get("source"), "chunk": h.get("meta", {}).get("chunk"), "score": h.get("score")}
                for h in hits
            ]
        }
