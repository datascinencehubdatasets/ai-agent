from typing import List, Optional

class WellnessAgent:
    """Агент эмоциональной поддержки и wellness советов"""
    
    def __init__(self, llm):
        self.llm = llm
        
        self.prompt = ChatPromptTemplate.from_template("""
        Ты - эмпатичный психолог и коуч по финансовому благополучию.
        
        Клиент испытывает эмоциональные трудности или импульс потратить деньги.
        
        Сообщение клиента: {message}
        
        Его текущая цель: {goal}
        Прогресс: {progress}%
        
        Помоги клиенту:
        1. Признай его эмоции, проявив эмпатию
        2. Предложи 3-4 альтернативы тратам (спорт, хобби, социальное)
        3. Напомни о его цели и мотивируй
        4. Дай практичный совет, как справиться прямо сейчас
        
        Тон: тёплый, поддерживающий, без осуждения.
        """)
    
    async def process(
        self,
        message: str,
        user_id: str,
        rag_context: List[str],
        conversation_context: Optional[dict] = None
    ):
        """Дать эмоциональную поддержку"""
        
        # Получить цели пользователя
        user_goals = await self._get_user_goals(user_id)
        
        goal = user_goals[0] if user_goals else {"name": "финансовая стабильность", "progress": 0}
        
        prompt_input = {
            "message": message,
            "goal": goal["name"],
            "progress": goal.get("progress", 0)
        }
        
        response = await self.llm.ainvoke(
            self.prompt.format(**prompt_input)
        )
        
        return {
            "message": response.content,
            "agent": "wellness",
            "alternatives": self._extract_alternatives(response.content)
        }
    
    async def _get_user_goals(self, user_id: str) -> List[Dict]:
        """Получить цели пользователя"""
        # TODO: Запрос к БД
        return [
            {"name": "Квартира", "progress": 15, "target": 50000000}
        ]
    
    def _extract_alternatives(self, response: str) -> List[str]:
        """Извлечь альтернативы тратам"""
        # TODO: Парсинг
        return ["Медитация 15 минут", "Прогулка в парке", "Позвонить другу"]