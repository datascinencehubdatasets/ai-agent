# from typing import List, Dict, Any
# from backend.rag.embedder import Embedder
# from backend.rag.store import LocalVectorStore

# class Retriever:
#     def __init__(self, store: LocalVectorStore | None = None, embedder: Embedder | None = None,
#                  top_k: int = 4, min_score: float = 0.2):
#         self.store = store or LocalVectorStore()
#         self.embedder = embedder or Embedder()
#         self.top_k = top_k
#         self.min_score = min_score

#     def retrieve(self, query: str) -> List[Dict[str, Any]]:
#         qv = self.embedder.encode([query])[0]
#         results = self.store.search(qv, top_k=self.top_k)
#         # отфильтруем по минимальному порогу релевантности
#         results = [r for r in results if r.get("score", 0.0) >= self.min_score]
#         return results

#     @staticmethod
#     def format_context(chunks: List[Dict[str, Any]], max_chars: int = 3000) -> str:
#         """Собираем один строковый контекст из фрагментов, не превышая лимит символов."""
#         acc = []
#         size = 0
#         for i, ch in enumerate(chunks, 1):
#             piece = f"[Doc {i} | score={ch.get('score',0):.2f}]\n{ch['text'].strip()}\n\n"
#             if size + len(piece) > max_chars:
#                 break
#             acc.append(piece)
#             size += len(piece)
#         return "".join(acc).strip()

from typing import List, Dict, Any
from backend.rag.embedder import Embedder
from backend.rag.store import LocalVectorStore
from backend.rag.reranker import Reranker
from backend.utils.settings import settings

class Retriever:
    def __init__(self, store: LocalVectorStore | None = None, embedder: Embedder | None = None,
                 top_k: int = 4, min_score: float = 0.2):
        self.store = store or LocalVectorStore()
        self.embedder = embedder or Embedder()
        self.top_k = top_k
        self.min_score = min_score
        self.use_rerank = settings.USE_RERANK
        self.reranker = Reranker() if self.use_rerank else None

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        # 1) векторный поиск (быстрый и дешёвый черновой recall)
        qv = self.embedder.encode([query])[0]
        initial = self.store.search(qv, top_k=max(self.top_k, 8))   # берём чуть больше на вход rerank
        if not initial:
            return []

        # 2) фильтр по порогу до rerank (слабый, чтобы не потерять кандидатов)
        prefiltered = [d for d in initial if d.get("score", 0.0) >= max(self.min_score * 0.75, 0.05)]
        candidates = prefiltered or initial

        # 3) (опц.) rerank
        if self.reranker:
            docs = [c["text"] for c in candidates]
            ranking = self.reranker.rerank(query, docs, top_k=self.top_k)
            if ranking:
                # собрать выдачу по новому порядку
                ordered: List[Dict[str, Any]] = []
                for r in ranking:
                    item = dict(candidates[r["index"]])  # копия
                    item["rerank_score"] = r["score"]
                    ordered.append(item)
                return ordered[: self.top_k]

        # 4) без rerank — просто отсечь по косинусу и топ-k
        return candidates[: self.top_k]

    @staticmethod
    def format_context(chunks: List[Dict[str, Any]], max_chars: int = 3000) -> str:
        acc, size = [], 0
        for i, ch in enumerate(chunks, 1):
            score = ch.get("rerank_score", ch.get("score", 0.0))
            piece = f"[Doc {i} | score={score:.2f}]\n{ch['text'].strip()}\n\n"
            if size + len(piece) > max_chars:
                break
            acc.append(piece); size += len(piece)
        return "".join(acc).strip()
