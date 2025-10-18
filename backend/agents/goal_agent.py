from typing import Any, Dict
from .base import BaseAgent

class GoalAgent(BaseAgent):
    name = "goal_planning"

    def run(self, query: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        # TODO: подключить RAG/аналитику целей
        return {
            "answer": "Понял: помогаю с финансовыми целями. Уточните срок и сумму накопления.",
            "steps": ["сбор целей", "оценка доходов/расходов", "план накоплений"]
        }
