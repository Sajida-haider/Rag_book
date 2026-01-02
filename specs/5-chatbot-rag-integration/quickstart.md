# Quickstart: Connect Chatbot UI with RAG Backend

## Prerequisites

- Node.js 18+ for Docusaurus frontend
- Python 3.11+ for FastAPI backend
- Access to Qdrant vector database (local or cloud)
- OpenAI API key (or alternative LLM provider)
- Git for version control

## Setup Instructions

### 1. Clone and Prepare Repository

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd book_ragbot

# Checkout the feature branch
git checkout 5-chatbot-rag-integration
```

### 2. Backend Setup

```bash
# Navigate to backend directory (create if it doesn't exist)
mkdir -p backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn python-dotenv qdrant-client openai Pydantic

# Create the backend structure
mkdir -p src/{models,services,api}
```

### 3. Frontend Setup

```bash
# Ensure Docusaurus is properly configured
cd book/my-book

# Install dependencies if not already installed
npm install

# Verify the chatbot component exists
# The chatbot UI should already be integrated in the Docusaurus site
```

### 4. Environment Configuration

Create `.env` file in the backend directory:

```env
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
OPENAI_API_KEY=your_openai_api_key
QDRANT_COLLECTION_NAME=book_embeddings
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

### 5. Start the Services

#### Backend:
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

#### Frontend:
```bash
cd book/my-book
npm run start
```

## API Endpoints

### Chat Endpoint
- **URL**: `POST /chat`
- **Request Body**:
  ```json
  {
    "message": "Your question here",
    "session_id": "unique-session-id"  // Optional, generated if not provided
  }
  ```
- **Response**:
  ```json
  {
    "response": "AI-generated response",
    "sources": ["source1", "source2"],
    "session_id": "session-id-used"
  }
  ```

## Testing the Integration

1. Start both backend and frontend services
2. Navigate to your Docusaurus site in the browser
3. Use the embedded chatbot UI to send a message
4. Verify that the message is sent to the backend
5. Check that you receive a response based on the book content
6. Confirm that the response appears in the chat UI

## Troubleshooting

### Common Issues:

1. **Backend not responding**:
   - Check that the backend service is running on the correct port
   - Verify environment variables are properly set
   - Confirm Qdrant connection details

2. **No responses from chatbot**:
   - Ensure the vector database has been populated with book content
   - Check that embeddings exist for the content being queried
   - Verify API endpoint is correctly configured in the frontend

3. **UI not updating**:
   - Check browser console for JavaScript errors
   - Verify API endpoint URL in frontend code
   - Confirm CORS settings allow frontend-backend communication