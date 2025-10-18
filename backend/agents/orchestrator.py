from typing import Optional
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from config import get_settings
from core.rag.retriever import RAGRetriever
from agents.goal_planning_agent import GoalPlanningAgent
from agents.analytics_agent import AnalyticsAgent
from agents.product_recommendation_agent import ProductRecommendationAgent
from agents.wellness_agent import WellnessAgent
from agents.general_agent import GeneralAgent

settings = get_settings()

class AgentOrchestrator:
    """Координирует работу всех агентов"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.openai_base_url
        )
        self.retriever = RAGRetriever()
        
        # Инициализация агентов
        self.agents = {
            "goal_planning": GoalPlanningAgent(self.llm, self.retriever),
            "analytics": AnalyticsAgent(self.llm),
            "product_recommendation": ProductRecommendationAgent(self.llm, self.retriever),
            "wellness": WellnessAgent(self.llm),
            "general": GeneralAgent(self.llm, self.retriever)
        }
    
    async def process(
        self,
        message: str,
        user_id: str,
        rag_context: List[str],
        conversation_context: Optional[dict] = None
    ):
        """Обработать запрос о финансовой цели"""
        
        # Получить контекст пользователя из БД
        user_context = await self._get_user_context(user_id)
        
        # Сформировать промпт
        prompt_input = {
            "message": message,
            "rag_context": "\n".join(rag_context),
            "user_context": user_context
        }
        
        # Получить ответ от LLM
        response = await self.llm.ainvoke(
            self.prompt.format(**prompt_input)
        )
        
        return {
            "message": response.content,
            "agent": "goal_planning",
            "suggestions": await self._extract_suggestions(response.content)
        }
    
    async def _get_user_context(self, user_id: str) -> str:
        """Получить контекст пользователя"""
        # TODO: Запрос к БД
        return "Доход: 500 000 ₸/мес, Возраст: 28 лет"
    
    async def _extract_suggestions(self, response: str) -> List[dict]:
        """Извлечь рекомендации продуктов"""
        # TODO: Парсинг предложенных продуктов
        return []