from __future__ import annotations
from typing import List, Dict, Any, Optional
from openai import OpenAI
import httpx, json, re

from backend.utils.settings import settings
from backend.utils.logger import get_logger

log = get_logger("query-transform")

_SYS_REWRITE = """You rewrite the user's message into a single standalone search query for retrieving knowledge base passages.
- Keep it concise and specific.
- Include key entities, dates, amounts, currencies, domain terms.
- If the user writes in Russian, keep Russian. If in English, keep English.
- Do not add explanations; return ONLY the rewritten query text.
"""

_SYS_MULTI = """Generate up to {k} alternative phrasings or keyword-style variants for the following query.
- Cover synonyms, domain terms, and likely KB wording.
- Prefer short, retrieval-friendly strings (no extra punctuation).
Return a JSON object: {"queries": ["q1","q2",...]}"""

_SYS_HYDE = """Write a short hypothetical answer/passage (5-7 lines) likely to appear in the KB for the query below.
Neutral, factual tone. No hallucinated brand claims. Return plain text only (no JSON)."""

def _lang_mirror(q: str) -> Optional[str]:
    """Простая эвристика RU<->EN — генерим зеркальную подсказку для перевода модели."""
    if not settings.QT_LANG_MIRROR:
        return None
    has_cyr = bool(re.search(r"[А-Яа-яЁё]", q))
    if has_cyr:
        return f"English equivalent of: {q}"
    return f"Русский эквивалент запроса: {q}"

class QueryTransformer:
    """Историо-осознанный rewrite + multi-query expansion + (опц.) HyDE."""
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            timeout=settings.REQUEST_TIMEOUT_SECONDS,
            max_retries=2,
            http_client=httpx.Client(timeout=settings.REQUEST_TIMEOUT_SECONDS),
        )
        self.model = settings.INTENT_MODEL

    def history_aware_rewrite(self, query: str, history_note: str = "") -> str:
        sys = _SYS_REWRITE + (f"\n\nConversation context:\n{history_note}" if history_note else "")
        r = self.client.chat.completions.create(
            model=self.model, temperature=0.0,
            messages=[{"role":"system","content":sys},{"role":"user","content":query}]
        )
        return (r.choices[0].message.content or "").strip()


    def multi_expand(self, rewritten: str, k: int) -> List[str]:
        sys = _SYS_MULTI.format(k=k)
        r = self.client.chat.completions.create(
            model=self.model, temperature=0.2,
            response_format={"type":"json_object"},
            messages=[{"role":"system","content":sys},{"role":"user","content":rewritten}]
        )
        raw = (r.choices[0].message.content or "").strip()
        try:
            data = json.loads(raw)
            qs = data.get("queries")
            if not isinstance(qs, list):
                raise ValueError("'queries' not a list")
            out = [q.strip() for q in qs if isinstance(q, str) and q.strip()]
            if out:
                return out
            raise ValueError("empty queries")
        except Exception:
        
            guess = [ln.strip("-• ").strip() for ln in raw.splitlines() if ln.strip()]
            guess = [g for g in guess if len(g) > 1]
            if len(guess) <= 1 and raw:
                parts = [p.strip() for p in raw.split(",") if p.strip()]
                if len(parts) > 1:
                    guess = parts
            # ограничим k
            guess = guess[:k]
            return guess

    # def multi_expand(self, rewritten: str, k: int) -> List[str]:
        sys = _SYS_MULTI.format(k=k)
        r = self.client.chat.completions.create(
            model=self.model, temperature=0.2,
            response_format={"type":"json_object"},
            messages=[{"role":"system","content":sys},{"role":"user","content":rewritten}]
        )
        try:
            data = json.loads(r.choices[0].message.content)
        except Exception:
            return []
        qs = [q.strip() for q in data.get("queries", []) if isinstance(q, str) and q.strip()]
        return qs

    def hyde(self, rewritten: str) -> str:
        r = self.client.chat.completions.create(
            model=self.model, temperature=0.2,
            messages=[{"role":"system","content":_SYS_HYDE},{"role":"user","content":rewritten}]
        )
        return (r.choices[0].message.content or "").strip()

    def transform(self, query: str, history_note: str = "") -> Dict[str, Any]:
        """
        Returns:
          {
            "primary": str,
            "alternatives": [str],
            "mirror": Optional[str],
            "hyde": Optional[str]
          }
        """
        primary = self.history_aware_rewrite(query, history_note=history_note)
        alts: List[str] = []
        if settings.QT_MULTI and settings.QT_MULTI_K > 0:
            try:
                alts = self.multi_expand(primary, settings.QT_MULTI_K)
            except Exception as e:
                log.warning(f"multi_expand failed: {e}")
        mirror = _lang_mirror(primary)
        hyde_text = None
        if settings.QT_HYDE:
            try:
                hyde_text = self.hyde(primary)
            except Exception as e:
                log.warning(f"hyde failed: {e}")
        return {"primary": primary, "alternatives": alts, "mirror": mirror, "hyde": hyde_text}
