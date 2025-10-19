from __future__ import annotations
from typing import Any, Dict, Optional
import time

class SessionState:
    """
    Простейшее in-memory хранилище произвольного состояния по session_id.
    Для продакшена можно заменить на Redis/DB.
    """
    def __init__(self, ttl_seconds: int = 60*60*12):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._ts: Dict[str, float] = {}
        self.ttl = ttl_seconds

    def _touch(self, sid: str):
        self._ts[sid] = time.time()

    def get(self, sid: str) -> Dict[str, Any]:
        # TTL очистка по требованию
        ts = self._ts.get(sid, 0.0)
        if ts and (time.time() - ts) > self.ttl:
            self._store.pop(sid, None)
        self._touch(sid)
        return self._store.setdefault(sid, {})

    def update(self, sid: str, patch: Dict[str, Any]) -> Dict[str, Any]:
        st = self.get(sid)
        st.update(patch or {})
        self._touch(sid)
        return st

    def clear(self, sid: str):
        self._store.pop(sid, None)
        self._ts.pop(sid, None)

state = SessionState()
