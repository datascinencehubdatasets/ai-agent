from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.nlp.intent_llm import LLMIntentClassifier
from backend.utils.logger import get_logger
from backend.memory.session import memory

router = APIRouter(prefix="/intent", tags=["intent"])
log = get_logger("intent")
clf = LLMIntentClassifier()

class IntentRequest(BaseModel):
    text: str = Field(..., min_length=1)
    language: str | None = None
    session_id: str | None = Field(default="default")   # <-- NEW

class IntentResponse(BaseModel):
    intent: str
    confidence: float
    matched_reasons: list[str] = []
    llm: str | None = None
    fallback: str | None = None

@router.post("/classify", response_model=IntentResponse)
def classify(req: IntentRequest):
    try:
        sid = req.session_id or "default"

        memory.append(sid, "user", req.text, meta={"endpoint":"intent"})
        result = clf.predict(req.text, language=req.language, session_messages=memory.get_messages(sid))

        memory.append(sid, "assistant", f"[intent: {result['intent']}]", meta={"endpoint":"intent"})
        return result
    except Exception as e:
        log.exception("intent classify failed")
        raise HTTPException(status_code=500, detail=str(e))
