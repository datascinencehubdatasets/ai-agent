from typing import Dict, List
from openai import OpenAI
import httpx
from ..utils.settings import settings
from ..utils.logger import get_logger
from .intent_regex import fallback_predict

log = get_logger("intent-llm")

# Имена интентов фиксируем явно (удобно для роутинга)
INTENTS: List[str] = [
    "goal_planning",
    "analytics",
    "product_recommendation",
    "wellness",
    "general_knowledge",
]

SYSTEM_PROMPT = """You are an intent classifier for a bilingual (ru/en) financial assistant.
Return a STRICT JSON object with fields:
- intent: one of ["goal_planning","analytics","product_recommendation","wellness","general_knowledge"]
- confidence: float between 0 and 1 (0.0..1.0)
- matched_reasons: short array of strings (why you chose the intent)

Decision policy:
- Prefer "product_recommendation" for queries about bank products (deposits, cards, loans, Islamic products).
- Prefer "analytics" for spending/transactions/category summaries.
- Prefer "goal_planning" for saving plans, budgets, future targets.
- Prefer "wellness" for emotional support (sad, anxious, stress).
- Else "general_knowledge" (e.g., Islamic finance concepts, FAQs).
Do NOT include any extra keys or prose.
"""

# несколько демонстрационных примеров повышают устойчивость
FEW_SHOTS = [
    {"role": "user", "content": "Хочу открыть вклад под 14% и карту без комиссии"},
    {"role": "assistant", "content": '{"intent":"product_recommendation","confidence":0.92,"matched_reasons":["вклад","карта","процентная ставка"]}'},
    {"role": "user", "content": "Покажи расходы за сентябрь по категориям"},
    {"role": "assistant", "content": '{"intent":"analytics","confidence":0.9,"matched_reasons":["расходы","категории","месяц"]}'},
    {"role": "user", "content": "How can I save for a vacation and plan a budget?"},
    {"role": "assistant", "content": '{"intent":"goal_planning","confidence":0.9,"matched_reasons":["save","plan","budget"]}'},
    {"role": "user", "content": "Мне тревожно из-за денег"},
    {"role": "assistant", "content": '{"intent":"wellness","confidence":0.8,"matched_reasons":["эмоциональная поддержка"]}'},
    {"role": "user", "content": "Что такое мурабаха в исламском финансировании?"},
    {"role": "assistant", "content": '{"intent":"general_knowledge","confidence":0.85,"matched_reasons":["исламское финансирование","термин"]}'},
]

class LLMIntentClassifier:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            timeout=settings.REQUEST_TIMEOUT_SECONDS,
            max_retries=2,
            http_client=httpx.Client(timeout=settings.REQUEST_TIMEOUT_SECONDS)
        )
        self.model = settings.INTENT_MODEL

    def predict(self, text: str, language: str | None = None, session_messages: Optional[List[Dict]] = None) -> Dict:
        if not text or not text.strip():
            return {"intent":"general_knowledge","confidence":0.1,"matched_reasons":[],"llm":self.model}

        try:
            messages = [{"role":"system","content": SYSTEM_PROMPT}]
            messages += FEW_SHOTS
            messages.append({"role":"user","content": text})

            resp = self.client.chat.completions.create(
                model=self.model,
                temperature=0.0,
                response_format={"type":"json_object"},
                messages=messages
            )
            # OpenAI python SDK v1.x: content строковый JSON, parsed недоступен всегда
            raw = resp.choices[0].message.content
            import json
            data = json.loads(raw)

            intent = data.get("intent","general_knowledge")
            conf = float(data.get("confidence", 0.7))
            reasons = data.get("matched_reasons", [])
            if intent not in INTENTS:
                intent = "general_knowledge"

            return {
                "intent": intent,
                "confidence": max(0.0, min(conf, 1.0)),
                "matched_reasons": reasons,
                "llm": self.model
            }

        except Exception as e:
            log.warning(f"LLM intent failed: {e}. Falling back to regex.")
            fb = fallback_predict(text, language=language)
            fb["llm"] = None
            fb["fallback"] = "regex"
            return fb
