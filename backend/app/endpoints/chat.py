from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str
    context: Optional[List[str]] = []

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint that accepts a message and returns a placeholder response
    Future implementation will include RAG logic
    """
    # Placeholder response - in future this will connect to RAG pipeline
    response_text = f"I received your message: '{request.message}'. This is a placeholder response. The RAG system will be implemented in future phases."

    return ChatResponse(
        response=response_text,
        context=["placeholder_context_1", "placeholder_context_2"]
    )