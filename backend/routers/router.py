from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict
from backend.utils.logger import get_logger
from backend.nlp.intent_llm import LLMIntentClassifier
from backend.agents.base import make_agent
from backend.memory.session import memory

router = APIRouter(prefix="/route", tags=["router"])
log = get_logger("processing-router")
clf = LLMIntentClassifier()

class RouteRequest(BaseModel):
    text: str = Field(..., min_length=1)
    language: str | None = None
    context: Dict[str, Any] | None = None
    session_id: str | None = Field(default="default")   # <-- NEW

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
        sid = req.session_id or "default"

        memory.append(sid, "user", req.text, meta={"endpoint":"route"})

        history = memory.get_messages(sid)
        intent_result = clf.predict(req.text, language=req.language, session_messages=history)
        intent = intent_result["intent"]
        confidence = float(intent_result["confidence"])

        agent = make_agent(intent)
        agent_output = agent.run(req.text, context={"session_id": sid, "history": history, **(req.context or {})})

        answer = str(agent_output.get("answer", ""))
        extra = {k: v for k, v in agent_output.items() if k != "answer"}

        memory.append(sid, "assistant", answer, meta={"endpoint":"route","agent":agent.name,"intent":intent})

        return RouteResponse(
            intent=intent,
            confidence=confidence,
            agent=agent.name,
            answer=answer,
            llm=intent_result.get("llm"),
            fallback=intent_result.get("fallback"),
            extra=extra or None
        )
    except Exception as e:
        log.exception("route failed")
        raise HTTPException(status_code=500, detail=str(e))
