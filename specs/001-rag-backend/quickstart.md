# Quickstart Guide: Live Deployed Book RAG Backend (Cohere + Qdrant)

## Overview
This guide provides instructions for setting up and running the RAG backend that ingests content from a live deployed Docusaurus book and stores embeddings in Qdrant for question answering.

## Prerequisites
- Python 3.11 or higher
- uv package manager
- Cohere API key
- Qdrant API key and URL
- Access to the deployed book at https://rag-book-cwq3n6mkx-sajida-haiders-projects.vercel.app

## Setup Instructions

### 1. Clone and Navigate to Project
```bash
# Navigate to your project directory
cd your-project-root
```

### 2. Create Backend Directory
```bash
mkdir ragbot_backend
```

### 3. Install Dependencies
```bash
# Install required packages
pip install requests beautifulsoup4 cohere qdrant-client fastapi uvicorn python-dotenv
```

### 4. Environment Configuration
Create a `.env` file in the project root with the following variables:
```env
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=your_qdrant_cluster_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
BOOK_URL=https://rag-book-cwq3n6mkx-sajida-haiders-projects.vercel.app
```

## Running the Application

### 1. Start the Ingestion Process
```bash
cd ragbot_backend
python main.py --ingest
```

### 2. Start the API Server
```bash
cd ragbot_backend
uvicorn main:app --reload --port 8000
```

### 3. Query the API
Once the server is running, you can query it:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "Your question here"}'
```

## Key Endpoints
- `POST /query` - Submit a question and receive an answer
- `GET /health` - Check the health status of the service
- `POST /ingest` - Trigger content ingestion from the book

## Configuration Options
- `BOOK_URL`: The URL of the deployed Docusaurus book
- `CHUNK_SIZE`: Size of text chunks (default: 300 words)
- `OVERLAP_SIZE`: Overlap between chunks (default: 50 words)
- `MODEL_NAME`: Cohere embedding model to use (default: embed-multilingual-v3.0)

## Troubleshooting
- If ingestion fails, check that the BOOK_URL is accessible
- If embeddings fail, verify your Cohere API key
- If Qdrant operations fail, verify your Qdrant credentials
- Check logs for specific error messages