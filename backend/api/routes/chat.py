from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from agents.orchestrator import AgentOrchestrator
from models.schemas import ChatMessage, ChatResponse

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    user_id: str
    conversation_id: Optional[str] = None
    context: Optional[dict] = None

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Основной эндпоинт для чата"""
    try:
        orchestrator = AgentOrchestrator(user_id=request.user_id)
        response = await orchestrator.process_message(
            message=request.message,
            conversation_id=request.conversation_id,
            context=request.context
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{conversation_id}")
async def get_history(conversation_id: str):
    """Получить историю диалога"""
    # TODO: Реализовать получение из БД
    pass