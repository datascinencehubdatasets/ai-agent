from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ..nlp.intent_llm import LLMIntentClassifier
from ..utils.logger import get_logger

router = APIRouter(prefix="/intent", tags=["intent"])
log = get_logger("intent-router")
clf = LLMIntentClassifier()

class IntentRequest(BaseModel):
    text: str = Field(..., min_length=1)
    language: str | None = Field(default=None, description="ru/en (optional)")

class IntentResponse(BaseModel):
    intent: str
    confidence: float
    matched_reasons: list[str] = []
    llm: str | None = None
    fallback: str | None = None

@router.post("/classify", response_model=IntentResponse)
def classify(req: IntentRequest):
    try:
        result = clf.predict(req.text, language=req.language)
        log.info(f"intent={result['intent']} conf={result['confidence']:.2f} text='{req.text[:80]}'")
        return result
    except Exception as e:
        log.exception("intent classify failed")
        raise HTTPException(status_code=500, detail=str(e))
