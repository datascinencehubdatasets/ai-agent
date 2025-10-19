from __future__ import annotations
from typing import List, Dict, Any
import os, json, uuid
import numpy as np

class LocalVectorStore:
    def __init__(self, dir_path: str = "data/embeddings"):
        self.dir = dir_path
        os.makedirs(self.dir, exist_ok=True)
        self.meta_path = os.path.join(self.dir, "store.jsonl")
        self.npy_path = os.path.join(self.dir, "embeddings.npy")
        self._meta: List[Dict[str, Any]] = []
        self._emb: np.ndarray | None = None
        self._load()

    def _load(self):
        if os.path.exists(self.meta_path):
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self._meta = [json.loads(line) for line in f if line.strip()]
        else:
            self._meta = []

        if os.path.exists(self.npy_path):
            self._emb = np.load(self.npy_path)
        else:
            self._emb = None

    def _save(self):
        with open(self.meta_path, "w", encoding="utf-8") as f:
            for rec in self._meta:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if self._emb is not None:
            np.save(self.npy_path, self._emb)

    def add_texts(self, texts: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]] | None = None) -> List[str]:
        metadatas = metadatas or [{} for _ in texts]
        ids = []
        vecs = np.array(embeddings, dtype=np.float32)

        if self._emb is None:
            self._emb = vecs
        else:
            self._emb = np.vstack([self._emb, vecs])

        for t, m in zip(texts, metadatas):
            _id = m.get("id") or str(uuid.uuid4())
            ids.append(_id)
            self._meta.append({"id": _id, "text": t, "meta": m})

        self._save()
        return ids

    def search(self, query_vec: List[float], top_k: int = 4) -> List[Dict[str, Any]]:
        if self._emb is None or len(self._meta) == 0:
            return []

        V = self._emb
        q = np.array(query_vec, dtype=np.float32)

        Vn = V / (np.linalg.norm(V, axis=1, keepdims=True) + 1e-12)
        qn = q / (np.linalg.norm(q) + 1e-12)
        sims = Vn @ qn

        idx = np.argsort(-sims)[:top_k]
        out: List[Dict[str, Any]] = []
        for i in idx:
            rec = dict(self._meta[int(i)])
            rec["score"] = float(sims[int(i)])
            out.append(rec)
        return out
