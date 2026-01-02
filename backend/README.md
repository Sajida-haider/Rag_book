# Book Embeddings RAG System with Chatbot Backend

This system fetches content from deployed Docusaurus book websites, processes it, generates vector embeddings using Cohere models, and stores the embeddings with metadata in Qdrant Cloud. It also includes a RAG chatbot backend that allows users to ask questions about the book content and receive AI-generated responses.

## Architecture

The system consists of several services:

### Content Ingestion Services:
- `web_scraper.py`: Fetches HTML content from web pages
- `content_extractor.py`: Extracts relevant content from HTML
- `content_cleaner.py`: Cleans and preprocesses extracted content
- `url_crawler.py`: Discovers all pages in a book website
- `content_chunker.py`: Splits content into appropriate sizes for embedding
- `embedding_generator.py`: Generates vector embeddings using Cohere
- `vector_storage.py`: Stores embeddings in Qdrant vector database
- `change_detector.py`: Detects changes in book content
- `re_ingestion.py`: Handles re-ingestion of updated content
- `models.py`: Data models for the system
- `main.py`: Main ingestion pipeline orchestrator

### RAG Chatbot Backend Services:
- `src/api/main.py`: FastAPI application with chat endpoints
- `src/services/rag_service.py`: Core RAG logic for processing queries
- `src/services/vector_storage.py`: Qdrant integration for content retrieval
- `src/services/session_service.py`: Session management for conversations

## Setup

1. Install Python 3.11+
2. Install uv package manager: `pip install uv`
3. Create virtual environment: `uv venv`
4. Activate virtual environment: `source .venv/bin/activate` (Linux/Mac) or `.venv\Scripts\activate` (Windows)
5. Install dependencies: `uv pip install -r requirements.txt`
6. Set up environment variables in `.env` file

## RAG Chatbot Backend Setup

The RAG chatbot backend provides API endpoints for the Docusaurus book's chat interface.

### Backend Requirements:
- Python 3.11+
- FastAPI
- uvicorn
- OpenAI API key
- Qdrant vector database access

### Environment Variables for Chatbot Backend:
```
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
OPENAI_API_KEY=your_openai_api_key
QDRANT_COLLECTION_NAME=book_embeddings
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

### Running the Backend:
```bash
cd backend
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### API Endpoints:
- `POST /chat`: Process user message and return AI-generated response
- `POST /chat/stream`: Streamed version of the chat endpoint
- `GET /health`: Health check endpoint

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=your_qdrant_cloud_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
BOOK_URL=https://rag-book.vercel.app
COLLECTION_NAME=humanoid_ai_book
```

## Usage

### Initial Ingestion
```bash
cd backend
python main.py
```

### Re-ingestion (to update with changed content)
```bash
cd backend
python main.py reingest
```

## Features

- Fetches content from Docusaurus-based book websites
- Discovers all pages using crawling and sitemap detection
- Extracts and cleans content while preserving document structure
- Chunks content into appropriate sizes for embedding
- Generates embeddings using Cohere's latest stable model
- Stores embeddings with metadata in Qdrant Cloud
- Detects content changes and supports re-ingestion
- Preserves source metadata for attribution
- Comprehensive logging and error handling

## Configuration

- `BOOK_URL`: The URL of the deployed Docusaurus book website
- `COLLECTION_NAME`: Name of the Qdrant collection to store vectors
- `CHUNK_SIZE`: Size of content chunks for embedding (default: 1000 characters)
- `EMBEDDING_MODEL`: Cohere model to use for embeddings (default: multilingual-v3.0)

## Troubleshooting

- If content extraction fails, verify the book URL is accessible
- If embeddings fail, check Cohere API key validity
- If Qdrant storage fails, verify Qdrant credentials and collection exists
- For large books, the system automatically processes content in batches