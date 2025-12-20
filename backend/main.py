from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI(
    title="RAG Chatbot Backend",
    description="Backend service for the Docusaurus-based RAG chatbot",
    version="0.1.0"
)

# Import and include routers
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.endpoints.health import router as health_router
from app.endpoints.chat import router as chat_router

app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(chat_router, prefix="/api", tags=["chat"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )