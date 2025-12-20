from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    message: str

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify the server is running
    """
    return HealthResponse(
        status="healthy",
        message="RAG Chatbot Backend is running"
    )