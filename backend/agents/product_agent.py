from typing import Any, Dict
from backend.rag.retriever import Retriever
from openai import OpenAI
import httpx
from backend.utils.settings import settings

RAG_SYSTEM_PROMPT = """You are a banking product expert. Use ONLY the provided context to answer.
If information is missing, ask 1-2 clarifying questions. Keep answers concise and practical.
"""

class ProductAgent:
    name = "product_recommendation"

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

        from backend.nlp.intent_llm import summarize_history
        history_note = summarize_history(history, max_chars=600)

        hits = self.retriever.retrieve(query if not history_note else f"{history_note}\n\ncurrent: {query}")
        ctx = self.retriever.format_context(hits)

        messages = [
            {"role": "system", "content": RAG_SYSTEM_PROMPT},
            {"role": "system", "content": f"CONTEXT:\n{ctx or '(no relevant context)'}"},
            {"role": "system", "content": f"RECENT TURNS:\n{history_note}" if history_note else "RECENT TURNS: (none)"},
            {"role": "user", "content": query},
        ]
        resp = self.client.chat.completions.create(
            model=self.model, temperature=0.2,
            messages=messages
        )
        answer = resp.choices[0].message.content.strip()
        return {
            "answer": answer,
            "used_docs": [{"source": h["meta"].get("source"), "chunk": h["meta"].get("chunk"), "score": h["score"]} for h in hits]
        }
