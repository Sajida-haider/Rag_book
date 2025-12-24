# API Contract: RAG Backend Question Answering

## Overview
This document defines the API contract for the question answering functionality of the RAG backend system.

## Base URL
`http://localhost:8000` (or deployed URL)

## Endpoints

### POST /query
Submit a question and receive an answer based on the ingested book content.

#### Request
```json
{
  "question": "string (required) - The question to answer",
  "max_sources": "integer (optional) - Maximum number of sources to reference (default: 3)"
}
```

#### Response
**Success (200 OK)**
```json
{
  "question": "string - The original question",
  "answer": "string - The generated answer",
  "sources": [
    {
      "url": "string - Source URL",
      "title": "string - Source title",
      "excerpt": "string - Relevant excerpt from source"
    }
  ],
  "confidence": "number - Confidence score between 0 and 1"
}
```

**Error (400 Bad Request)**
```json
{
  "error": "string - Error message",
  "details": "string - Additional error details"
}
```

**Error (500 Internal Server Error)**
```json
{
  "error": "string - Error message"
}
```

### POST /ingest
Trigger the content ingestion process from the live book.

#### Request
```json
{
  "force": "boolean (optional) - Whether to force re-ingestion of all content (default: false)"
}
```

#### Response
**Success (200 OK)**
```json
{
  "status": "string - Operation status",
  "processed_urls": "integer - Number of URLs processed",
  "indexed_chunks": "integer - Number of text chunks indexed",
  "message": "string - Additional status message"
}
```

### GET /health
Check the health status of the service.

#### Response
**Success (200 OK)**
```json
{
  "status": "string - Health status (ok)",
  "timestamp": "string - ISO 8601 timestamp",
  "dependencies": {
    "cohere": "string - Status of Cohere connection",
    "qdrant": "string - Status of Qdrant connection",
    "book_source": "string - Status of book source accessibility"
  }
}
```

### GET /stats
Get statistics about the indexed content.

#### Response
**Success (200 OK)**
```json
{
  "total_documents": "integer - Total number of documents indexed",
  "total_chunks": "integer - Total number of text chunks",
  "total_tokens": "integer - Approximate total tokens indexed",
  "last_ingestion": "string - ISO 8601 timestamp of last ingestion"
}
```

## Error Handling
All API endpoints follow standard HTTP status codes:
- 200: Success
- 400: Bad request (client error)
- 404: Resource not found
- 500: Internal server error

## Authentication
No authentication required for this initial implementation.

## Rate Limiting
No rate limiting implemented in this version.