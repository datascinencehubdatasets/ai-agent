from typing import Any, Dict
from .base import BaseAgent

class AnalyticsAgent(BaseAgent):
    name = "analytics"

    def run(self, query: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        # TODO: подключить БД транзакций/аналитику
        return {
            "answer": "Готов сделать анализ расходов. Уточните период и категории.",
            "needs": ["period", "categories"]
        }
