from typing import List, Dict
import pandas as pd

class AnalyticsAgent:
    """Агент анализа расходов и доходов"""
    
    def __init__(self, llm):
        self.llm = llm
        
        self.prompt = ChatPromptTemplate.from_template("""
        Ты - аналитик данных ZAMAN Bank.
        
        Проанализируй финансовые данные клиента и дай инсайты:
        
        Расходы по категориям за месяц:
        {spending_breakdown}
        
        Доходы: {income}
        
        Сравнение с похожими пользователями:
        {peer_comparison}
        
        Запрос клиента: {message}
        
        Дай конкретные, действенные советы по оптимизации.
        Покажи, сколько можно сэкономить и на что направить.
        """)
    
    async def process(
        self,
        message: str,
        user_id: str,
        rag_context: List[str],
        conversation_context: Optional[dict] = None
    ):
        """Проанализировать расходы пользователя"""
        
        # Получить транзакции из MongoDB
        transactions = await self._get_transactions(user_id)
        
        # Категоризировать расходы
        spending_breakdown = self._categorize_spending(transactions)
        
        # Сравнить с peer group
        peer_comparison = await self._compare_with_peers(user_id, spending_breakdown)
        
        # Сформировать промпт
        prompt_input = {
            "message": message,
            "spending_breakdown": self._format_breakdown(spending_breakdown),
            "income": "500 000 ₸",  # TODO: из БД
            "peer_comparison": self._format_comparison(peer_comparison)
        }
        
        response = await self.llm.ainvoke(
            self.prompt.format(**prompt_input)
        )
        
        return {
            "message": response.content,
            "agent": "analytics",
            "data": {
                "spending": spending_breakdown,
                "comparison": peer_comparison
            }
        }
    
    async def _get_transactions(self, user_id: str) -> List[Dict]:
        """Получить транзакции из MongoDB"""
        # TODO: Запрос к MongoDB
        return [
            {"category": "Рестораны", "amount": 120000, "date": "2025-01-15"},
            {"category": "Продукты", "amount": 80000, "date": "2025-01-10"}
        ]
    
    def _categorize_spending(self, transactions: List[Dict]) -> Dict:
        """Категоризировать расходы"""
        df = pd.DataFrame(transactions)
        breakdown = df.groupby('category')['amount'].sum().to_dict()
        return breakdown
    
    async def _compare_with_peers(self, user_id: str, spending: Dict) -> Dict:
        """Сравнить с похожими пользователями"""
        # TODO: Реальное сравнение
        return {
            "savings_rate": {"user": 0.15, "peers_avg": 0.25, "percentile": 40},
            "restaurant_spending": {"user": 120000, "peers_avg": 80000}
        }
    
    def _format_breakdown(self, breakdown: Dict) -> str:
        """Форматировать разбивку расходов"""
        total = sum(breakdown.values())
        lines = []
        for category, amount in breakdown.items():
            percent = (amount / total) * 100
            lines.append(f"- {category}: {amount:,} ₸ ({percent:.1f}%)")
        return "\n".join(lines)
    
    def _format_comparison(self, comparison: Dict) -> str:
        """Форматировать сравнение"""
        return f"""
        Ваш уровень накоплений: {comparison['savings_rate']['user']*100:.0f}%
        Средний среди похожих: {comparison['savings_rate']['peers_avg']*100:.0f}%
        Вы в топ-{comparison['savings_rate']['percentile']}% по накоплениям
        """
