# API Contract: Chatbot RAG Backend

## Overview
This document defines the API contract for the RAG chatbot backend service that connects the Docusaurus UI with the content retrieval system.

## Base URL
`http://localhost:8000` (development) or your deployed backend URL

## Endpoints

### POST /chat
Process user message and return AI-generated response based on book content.

#### Request
```json
{
  "message": "string (required) - The user's message/query",
  "session_id": "string (optional) - Unique identifier for the chat session, generated if not provided"
}
```

#### Response (Success 200)
```json
{
  "response": "string - AI-generated response based on retrieved content",
  "sources": "array of strings - List of sources used to generate the response",
  "session_id": "string - The session ID used or generated for this conversation",
  "retrieved_content": [
    {
      "content": "string - The retrieved content chunk",
      "source": "string - Source document identifier",
      "score": "number - Relevance score of the content"
    }
  ]
}
```

#### Response (Error 400 - Bad Request)
```json
{
  "error": "string - Description of the error",
  "code": "string - Error code"
}
```

#### Response (Error 500 - Internal Server Error)
```json
{
  "error": "string - Description of the error",
  "code": "string - Error code"
}
```

### GET /health
Check the health status of the backend service.

#### Response (Success 200)
```json
{
  "status": "string - Health status (e.g., 'healthy')",
  "timestamp": "string - ISO 8601 timestamp"
}
```

## Error Codes
- `INVALID_REQUEST`: The request format is invalid
- `BACKEND_UNAVAILABLE`: The backend service is temporarily unavailable
- `VECTOR_DB_ERROR`: Error occurred while querying the vector database
- `AI_GENERATION_ERROR`: Error occurred during AI response generation
- `SESSION_ERROR`: Error related to session management

## Headers
- `Content-Type`: `application/json`
- `Accept`: `application/json`

## Example Request
```http
POST /chat
Content-Type: application/json

{
  "message": "What are the key concepts in this book?",
  "session_id": "session-12345"
}
```

## Example Response
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "response": "The key concepts in this book include Retrieval-Augmented Generation (RAG), vector databases, embedding models, and AI chatbot integration. These technologies work together to provide contextually relevant responses based on book content.",
  "sources": ["chapter_1_introduction.md", "chapter_3_rag_implementation.md"],
  "session_id": "session-12345",
  "retrieved_content": [
    {
      "content": "Retrieval-Augmented Generation (RAG) is a technique that combines retrieval-based and generative approaches...",
      "source": "chapter_1_introduction.md",
      "score": 0.92
    }
  ]
}
```