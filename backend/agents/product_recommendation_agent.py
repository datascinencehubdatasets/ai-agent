from typing import List, Optional

class ProductRecommendationAgent:
    """Агент подбора банковских продуктов"""
    
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever
        
        self.prompt = ChatPromptTemplate.from_template("""
        Ты - эксперт по продуктам ZAMAN Bank.
        
        Подбери 2-3 наиболее подходящих продукта для клиента:
        
        Профиль клиента:
        - Цель: {goal}
        - Сумма: {amount} ₸
        - Срок: {timeline}
        - Доход: {income} ₸/мес
        
        Доступные продукты:
        {products_context}
        
        Для каждого продукта объясни:
        1. Почему он подходит
        2. Конкретные цифры (платёж, доходность)
        3. Как поможет достичь цели
        
        Сравни варианты и дай рекомендацию.
        """)
    
    async def process(
        self,
        message: str,
        user_id: str,
        rag_context: List[str],
        conversation_context: Optional[dict] = None
    ):
        """Подобрать продукты"""
        
        # Извлечь параметры из контекста разговора
        goal = conversation_context.get("goal", "не указана")
        amount = conversation_context.get("amount", 0)
        timeline = conversation_context.get("timeline", "не указан")
        
        # Получить информацию о пользователе
        user_profile = await self._get_user_profile(user_id)
        
        # Сформировать промпт
        prompt_input = {
            "goal": goal,
            "amount": amount,
            "timeline": timeline,
            "income": user_profile.get("income", "не указан"),
            "products_context": "\n\n".join(rag_context)
        }
        
        response = await self.llm.ainvoke(
            self.prompt.format(**prompt_input)
        )
        
        # Извлечь структурированные рекомендации
        recommendations = await self._parse_recommendations(response.content)
        
        return {
            "message": response.content,
            "agent": "product_recommendation",
            "recommendations": recommendations
        }
    
    async def _get_user_profile(self, user_id: str) -> Dict:
        """Получить профиль пользователя"""
        # TODO: Запрос к PostgreSQL
        return {"income": 500000, "age": 28, "city": "Астана"}
    
    async def _parse_recommendations(self, response: str) -> List[Dict]:
        """Парсинг рекомендаций из ответа LLM"""
        # TODO: Извлечь структурированные данные
        return [
            {
                "product": "Депозит Вакала Zaman",
                "rate": "20%",
                "reason": "Высокая доходность для накоплений"
            }
        ]