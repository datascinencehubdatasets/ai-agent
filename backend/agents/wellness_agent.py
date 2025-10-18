from typing import Any, Dict
from .base import BaseAgent

class WellnessAgent(BaseAgent):
    name = "wellness"

    def run(self, query: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        # Замечание: это НЕ медицинские советы; мягкая поддержка + ресурсы
        return {
            "answer": "Я здесь, чтобы поддержать. Хотите поговорить о том, что вас тревожит?",
            "resources": ["советы по управлению стрессом", "планирование финансов снизит тревогу"]
        }
