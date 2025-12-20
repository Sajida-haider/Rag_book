# Quickstart: Book Content Ingestion & Embeddings

## Overview
This guide explains how to set up and run the book content ingestion pipeline that prepares Docusaurus book content for Retrieval-Augmented Generation (RAG).

## Prerequisites
- Python 3.11+
- OpenAI API key
- Qdrant Cloud account and API key
- Neon Postgres database connection string
- Access to the Docusaurus book markdown files

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Navigate to Backend Directory
```bash
cd backend
```

### 3. Create Virtual Environment
```bash
python -m venv venv
```

### 4. Activate Virtual Environment
On Windows:
```bash
# Command Prompt
venv\Scripts\activate

# PowerShell
venv\Scripts\Activate.ps1
```

On macOS/Linux:
```bash
source venv/bin/activate
```

### 5. Install Dependencies
```bash
pip install -r requirements.txt
```

### 6. Configure Environment Variables
Create a `.env` file with the following variables:
```bash
OPENAI_API_KEY=your_openai_api_key
QDRANT_URL=your_qdrant_cluster_url
QDRANT_API_KEY=your_qdrant_api_key
NEON_DATABASE_URL=your_neon_postgres_connection_string
BOOK_PATH=path_to_your_book_markdown_files
```

### 7. Run the Ingestion Pipeline
```bash
python -m backend.ingestion.main
```

## Pipeline Components

The ingestion pipeline consists of several modules:

1. **content_reader.py**: Reads and parses markdown files from the book directory
2. **cleaner.py**: Cleans content while preserving headings hierarchy
3. **chunker.py**: Chunks content into logical sections optimized for embeddings
4. **embedder.py**: Generates embeddings using OpenAI embeddings API
5. **vector_store.py**: Stores vectors in Qdrant Cloud
6. **metadata_store.py**: Stores metadata in Neon Postgres

## Data Flow

1. **Read**: The pipeline identifies all markdown files in the specified book directory
2. **Clean**: Unnecessary formatting and HTML tags are removed while preserving headings hierarchy
3. **Chunk**: Content is split into logical sections based on document structure
4. **Embed**: Each chunk is sent to OpenAI embeddings API to generate vector representations
5. **Store**: Vectors are stored in Qdrant and metadata in Neon Postgres
6. **Verify**: The system verifies that embeddings and metadata are correctly stored

## Configuration Options

- **CHUNK_SIZE**: Maximum size of each content chunk (default: 1000 characters)
- **CHUNK_OVERLAP**: Overlap between chunks to maintain context (default: 100 characters)
- **EMBEDDING_MODEL**: OpenAI model to use for embeddings (default: text-embedding-ada-002)

## Verification

After running the pipeline, verify successful ingestion by:
1. Checking that the Qdrant collection contains the expected number of vectors
2. Confirming that metadata records exist in Neon Postgres
3. Testing retrieval with a sample query to ensure vectors are properly indexed