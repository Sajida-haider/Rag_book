# Quickstart Guide: Book Embeddings for RAG System

## Prerequisites

- Python 3.11 or higher
- `uv` package manager installed
- Access to Cohere API (API key)
- Access to Qdrant Cloud (URL and API key)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Create Backend Directory
```bash
mkdir backend
cd backend
```

### 3. Initialize Python Environment with uv
```bash
# Install uv if not already installed
pip install uv

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 4. Create Requirements File
Create `requirements.txt` with the following dependencies:
```
requests==2.31.0
beautifulsoup4==4.12.2
cohere==4.4.3
qdrant-client==1.8.0
python-dotenv==1.0.0
```

Install the dependencies:
```bash
uv pip install -r requirements.txt
```

### 5. Set Up Environment Variables
Create a `.env` file in the backend directory with your API keys:
```
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=your_qdrant_cloud_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
BOOK_URL=https://rag-book.vercel.app
```

**Note**: Never commit the `.env` file to version control. Add it to `.gitignore`.

### 6. Create the Main Application File
Create `main.py` with the complete ingestion pipeline implementation.

### 7. Run the Ingestion Pipeline
```bash
cd backend
python main.py
```

## Expected Output

The system will:
1. Fetch content from the specified book URL
2. Extract and clean text content from all accessible pages
3. Generate embeddings for each content chunk
4. Store embeddings with metadata in Qdrant Cloud
5. Report ingestion statistics and completion status

## Configuration Options

- `BOOK_URL`: The URL of the deployed Docusaurus book website
- `CHUNK_SIZE`: Size of content chunks for embedding (default: 1000 characters)
- `EMBEDDING_MODEL`: Cohere model to use for embeddings (default: multilingual-v3.0)
- `QDRANT_COLLECTION`: Name of the Qdrant collection to store vectors

## Troubleshooting

- If content extraction fails, verify the book URL is accessible
- If embeddings fail, check Cohere API key validity
- If Qdrant storage fails, verify Qdrant credentials and collection exists
- For large books, consider breaking the ingestion into batches