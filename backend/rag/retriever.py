from __future__ import annotations
from typing import List, Dict, Any, Optional

from backend.rag.embedder import Embedder
from backend.rag.store import LocalVectorStore
from backend.rag.reranker import Reranker
from backend.rag.query_transform import QueryTransformer
from backend.utils.settings import settings
from backend.utils.logger import get_logger

try:
    from backend.rag.vector_api import VectorStoreAPI
except Exception:  
    VectorStoreAPI = None 

from backend.nlp.intent_llm import summarize_history

log = get_logger("retriever")

class Retriever:
    def __init__(self, top_k: int = 4, min_score: float = 0.2):
        self.top_k = top_k
        self.min_score = min_score

        self.use_vector_api = getattr(settings, "USE_VECTOR_API", False)
        if self.use_vector_api and 'VectorStoreAPI' in globals() and VectorStoreAPI is not None:
            self.vs = VectorStoreAPI()
            self.embedder = None
            self.store = None
        else:
            self.vs = None
            self.store = LocalVectorStore()
            self.embedder = Embedder()

        self.use_rerank = getattr(settings, "USE_RERANK", False)
        self.reranker = Reranker() if self.use_rerank else None

        self.qt_enable = getattr(settings, "QT_ENABLE", False)
        self.qt = QueryTransformer() if self.qt_enable else None

    def _dedup(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        merged = []
        for c in sorted(candidates, key=lambda x: -float(x.get("score", 0.0))):
            meta = c.get("meta", {})
            key = (meta.get("source"), meta.get("chunk"))
            if key in seen:
                continue
            seen.add(key)
            merged.append(c)
        return merged

    def _prefilter(self, items: List[Dict[str, Any]], min_score: float) -> List[Dict[str, Any]]:
        return [d for d in items if float(d.get("score", 0.0)) >= min_score]

    def retrieve(self, query: str, history: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
       
        queries: List[str] = [query]
        hyde_vec = None

        if self.qt:
            hist_note = summarize_history(history or [], max_chars=400)
            qt = self.qt.transform(query, history_note=hist_note)
            queries = [qt["primary"]] + qt.get("alternatives", [])
            if qt.get("mirror"):
                queries.append(qt["mirror"])

            if settings.QT_HYDE and qt.get("hyde") and self.embedder is not None:
                try:
                    hyde_vec = self.embedder.encode([qt["hyde"]])[0]
                except Exception as e:
                    log.warning(f"hyde embedding failed: {e}")

        topk_candidates = max(self.top_k, 8)

        if self.vs is not None:
            all_candidates: List[Dict[str, Any]] = []
            for q in queries:
                try:
                    all_candidates += self.vs.search(q, top_k=topk_candidates)
                except Exception as e:
                    log.warning(f"VectorStore search failed for '{q}': {e}")
            if not all_candidates:
                return []

            merged = self._dedup(all_candidates)
            initial = merged[:topk_candidates]

        else:
            if self.embedder is None or self.store is None:
                log.warning("Local mode selected but embedder/store not initialized.")
                return []

            all_candidates: List[Dict[str, Any]] = []
            for q in queries:
                try:
                    qv = self.embedder.encode([q])[0]
                    all_candidates += self.store.search(qv, top_k=topk_candidates)
                except Exception as e:
                    log.warning(f"Local search failed for '{q}': {e}")

            if hyde_vec is not None:
                try:
                    all_candidates += self.store.search(hyde_vec, top_k=topk_candidates)
                except Exception as e:
                    log.warning(f"Local search (HyDE) failed: {e}")

            if not all_candidates:
                return []

            merged = self._dedup(all_candidates)
            initial = merged[:topk_candidates]

        pre_min = max(self.min_score * 0.75, 0.05)
        candidates = self._prefilter(initial, pre_min) or initial

        if self.reranker:
            docs = [c["text"] for c in candidates]
            ranking = self.reranker.rerank(query, docs, top_k=self.top_k)
            if ranking:
                ordered: List[Dict[str, Any]] = []
                for r in ranking:
                    idx = r.get("index")
                    if idx is None or not isinstance(idx, int) or idx < 0 or idx >= len(candidates):
                        continue
                    item = dict(candidates[idx])
                    item["rerank_score"] = float(r.get("score", 0.0))
                    ordered.append(item)
                return ordered[: self.top_k]

        return candidates[: self.top_k]

    @staticmethod
    def format_context(chunks: List[Dict[str, Any]], max_chars: int = 3000) -> str:
        acc, size = [], 0
        for i, ch in enumerate(chunks, 1):
            score = ch.get("rerank_score", ch.get("score", 0.0))
            src = (ch.get("meta") or {}).get("source", "")
            piece = f"[Doc {i} | score={score:.2f} | src={src}]\n{(ch.get('text') or '').strip()}\n\n"
            if size + len(piece) > max_chars:
                break
            acc.append(piece)
            size += len(piece)
        return "".join(acc).strip()
