from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import logging
from datetime import datetime
import json

# Import services (will be implemented in subsequent steps)
from ..services.rag_service import RAGService
from ..services.vector_storage import VectorStorageService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot Backend",
    description="Backend service for RAG-powered chatbot integration with Docusaurus book",
    version="1.0.0"
)

# Request/Response models based on the API contract
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class RetrievedContent(BaseModel):
    content: str
    source: str
    score: float

class ChatResponse(BaseModel):
    response: str
    sources: List[str]
    session_id: str
    retrieved_content: List[RetrievedContent]

class ErrorResponse(BaseModel):
    error: str
    code: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str

# Initialize services
rag_service = RAGService()
vector_storage = VectorStorageService()

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint for basic health check"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )

@app.post("/chat", response_model=ChatResponse, responses={
    400: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def chat_endpoint(request: ChatRequest):
    """
    Process user message and return AI-generated response based on book content.

    This endpoint handles chat requests by:
    1. Using the provided session_id or generating a new one
    2. Querying the vector database for relevant content
    3. Generating an AI response based on retrieved content
    4. Returning the response with source attribution
    """
    try:
        # Validate input
        if not request.message or len(request.message.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Message cannot be empty",
                    "code": "INVALID_REQUEST"
                }
            )

        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        logger.info(f"Processing chat request for session: {session_id}")

        # Check if services are available
        if not await rag_service.validate_connection():
            logger.warning("Required services are not available")
            return ChatResponse(
                response="The chat service is temporarily unavailable. Please try again later.",
                sources=[],
                session_id=session_id,
                retrieved_content=[]
            )

        # Use RAG service to generate response
        result = await rag_service.process_message(
            message=request.message,
            session_id=session_id
        )

        return ChatResponse(
            response=result["response"],
            sources=result["sources"],
            session_id=session_id,
            retrieved_content=result["retrieved_content"]
        )

    except HTTPException:
        # Re-raise HTTP exceptions as they are
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Error processing chat request",
                "code": "AI_GENERATION_ERROR"
            }
        )

@app.post("/chat/stream", response_class=StreamingResponse)
async def chat_stream_endpoint(request: ChatRequest):
    """
    Streamed version of the chat endpoint that returns responses in chunks.
    This provides a more responsive user experience with real-time text generation.
    """
    async def generate_stream():
        try:
            # Validate input
            if not request.message or len(request.message.strip()) == 0:
                yield json.dumps({
                    "error": "Message cannot be empty",
                    "code": "INVALID_REQUEST"
                }) + "\n"
                return

            # Generate session ID if not provided
            session_id = request.session_id or str(uuid.uuid4())
            logger.info(f"Processing streaming chat request for session: {session_id}")

            # Check if services are available
            if not await rag_service.validate_connection():
                logger.warning("Required services are not available")
                yield json.dumps({
                    "response": "The chat service is temporarily unavailable. Please try again later.",
                    "sources": [],
                    "session_id": session_id,
                    "retrieved_content": [],
                    "done": True
                }) + "\n"
                return

            # For now, we'll simulate streaming by returning the full response in chunks
            # In a production implementation, this would use an actual streaming LLM API
            result = await rag_service.process_message(
                message=request.message,
                session_id=session_id
            )

            # Simulate streaming by breaking the response into chunks
            response_text = result["response"]
            chunk_size = 20  # characters per chunk

            for i in range(0, len(response_text), chunk_size):
                chunk = response_text[i:i+chunk_size]
                yield json.dumps({
                    "chunk": chunk,
                    "done": False
                }) + "\n"

            # Send completion message with full response details
            yield json.dumps({
                "response": result["response"],
                "sources": result["sources"],
                "session_id": session_id,
                "retrieved_content": [
                    {
                        "content": item.content,
                        "source": item.source,
                        "score": item.score
                    } for item in result["retrieved_content"]
                ],
                "done": True
            }) + "\n"

        except Exception as e:
            logger.error(f"Error processing streaming chat request: {str(e)}")
            yield json.dumps({
                "error": "Error processing chat request",
                "code": "AI_GENERATION_ERROR"
            }) + "\n"

    return StreamingResponse(generate_stream(), media_type="application/json")


@app.get("/api/health")
async def api_health():
    """Additional health check endpoint"""
    return {"status": "ok", "service": "chatbot-backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)