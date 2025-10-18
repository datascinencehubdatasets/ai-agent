from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAgent(ABC):
    name: str = "base"

    @abstractmethod
    def run(self, query: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Возвращает словарь формата: {'answer': str, ...}"""
        raise NotImplementedError

# Фабрика агентов — по имени интента
def make_agent(intent: str) -> BaseAgent:
    from .goal_agent import GoalAgent
    from .analytics_agent import AnalyticsAgent
    from .product_agent import ProductAgent
    from .wellness_agent import WellnessAgent
    from .general_agent import GeneralAgent

    mapping = {
        "goal_planning": GoalAgent,
        "analytics": AnalyticsAgent,
        "product_recommendation": ProductAgent,
        "wellness": WellnessAgent,
        "general_knowledge": GeneralAgent,
    }
    agent_cls = mapping.get(intent, GeneralAgent)
    return agent_cls()
