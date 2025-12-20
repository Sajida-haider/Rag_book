# RAG Content Ingestion Pipeline

This pipeline fetches content from a deployed Docusaurus book, generates embeddings using Cohere, and stores them in Qdrant for RAG (Retrieval Augmented Generation) functionality.

## Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Then edit `.env` and add your:
- `COHERE_API_KEY` - Your Cohere API key for embeddings generation
- `QDRANT_API_KEY` - Your Qdrant API key (if using cloud service)
- `BOOK_URL` - The URL of your deployed book (default is provided)

### 3. Run the Ingestion Pipeline
```bash
python ingestion_pipeline.py
```

## Features

- **URL Discovery**: Automatically discovers all pages from the deployed book
- **Text Extraction**: Extracts clean text content from each page
- **Text Chunking**: Splits content into logical sections for RAG
- **Embedding Generation**: Creates vector embeddings using Cohere
- **Qdrant Integration**: Stores embeddings with metadata in Qdrant

## Pipeline Functions

The ingestion pipeline includes these main functions:

- `get_urls()` - Fetches all URLs from the deployed book
- `extract_text_from_url(url)` - Extracts and cleans text from a URL
- `chunk_text(text)` - Chunks text into logical sections
- `embed(chunks)` - Generates embeddings for text chunks
- `create_collection(name)` - Creates Qdrant collection for storage
- `upsert_to_qdrant(chunks, embeddings, urls)` - Stores data in Qdrant

## Collection Schema

The pipeline creates a Qdrant collection named `rag_embeddings` with the following payload structure:

```json
{
  "text": "The chunked text content",
  "url": "Source URL",
  "chunk_id": "Sequential ID of the chunk",
  "module": "Book module (placeholder)",
  "chapter": "Book chapter (placeholder)"
}
```

## Troubleshooting

- If you get API key errors, ensure your `.env` file is properly configured
- If URL discovery fails, check that the BOOK_URL is accessible
- If Qdrant connection fails, verify your QDRANT_URL and API key
- For large books, the pipeline may take several minutes to complete

## Next Steps

After running the ingestion pipeline, you can query the stored embeddings from your RAG chatbot backend.