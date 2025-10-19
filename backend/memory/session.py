from __future__ import annotations
from typing import Deque, Dict, List, Literal, Optional, Tuple
from collections import deque
import time

Role = Literal["user","assistant","system"]

class SessionMemory:
    """
    Простая in-memory память. Для продакшена замените на Redis/DB,
    сохранив публичные методы: append(), get_messages(), clear().
    """
    def __init__(self, max_messages: int = 16, ttl_seconds: int = 60*60*6):
        self._store: Dict[str, Tuple[float, Deque[Dict]]] = {}
        self.max_messages = max_messages
        self.ttl = ttl_seconds

    def _get_deque(self, session_id: str) -> Deque[Dict]:
        now = time.time()
        if session_id in self._store:
            ts, dq = self._store[session_id]
            # протухание
            if now - ts > self.ttl:
                dq = deque(maxlen=self.max_messages)
            self._store[session_id] = (now, dq)
            return dq
        dq = deque(maxlen=self.max_messages)
        self._store[session_id] = (now, dq)
        return dq

    def append(self, session_id: str, role: Role, content: str, meta: Optional[Dict]=None):
        dq = self._get_deque(session_id)
        dq.append({"role": role, "content": content, "meta": meta or {}})
        # обновим таймстемп активности
        self._store[session_id] = (time.time(), dq)

    def get_messages(self, session_id: str) -> List[Dict]:
        dq = self._get_deque(session_id)
        return list(dq)

    def clear(self, session_id: str):
        self._store.pop(session_id, None)

# Singleton на процесс приложения
memory = SessionMemory(max_messages=18, ttl_seconds=60*60*12)
