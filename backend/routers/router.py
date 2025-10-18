from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict
from backend.utils.logger import get_logger
from backend.nlp.intent_llm import LLMIntentClassifier
from backend.agents.base import make_agent

router = APIRouter(prefix="/route", tags=["router"])
log = get_logger("processing-router")
clf = LLMIntentClassifier()

class RouteRequest(BaseModel):
    text: str = Field(..., min_length=1)
    language: str | None = Field(default=None, description="ru/en (optional)")
    # опционально: контекст пользователя (id, профиль, и т.д.)
    context: Dict[str, Any] | None = None

class RouteResponse(BaseModel):
    intent: str
    confidence: float
    agent: str
    answer: str
    llm: str | None = None
    fallback: str | None = None
    extra: Dict[str, Any] | None = None

@router.post("", response_model=RouteResponse)
def route(req: RouteRequest):
    try:
        # 1) Intent (через LLM)
        intent_result = clf.predict(req.text, language=req.language)
        intent = intent_result["intent"]
        confidence = float(intent_result["confidence"])
        llm_model = intent_result.get("llm")
        fallback = intent_result.get("fallback")

        # 2) Агент по интенту
        agent = make_agent(intent)
        agent_output = agent.run(req.text, context=req.context or {})

        answer = str(agent_output.get("answer", ""))
        extra = {k: v for k, v in agent_output.items() if k != "answer"}

        log.info(f"intent={intent} conf={confidence:.2f} agent={agent.name}")

        return RouteResponse(
            intent=intent,
            confidence=confidence,
            agent=agent.name,
            answer=answer,
            llm=llm_model,
            fallback=fallback,
            extra=extra or None
        )
    except Exception as e:
        log.exception("route failed")
        raise HTTPException(status_code=500, detail=str(e))
