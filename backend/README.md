# RAG Chatbot Backend

This is the backend service for the Docusaurus-based RAG chatbot, built with FastAPI.

## Setup Instructions

### 1. Create Virtual Environment
```bash
cd backend
python -m venv venv
```

### 2. Activate Virtual Environment
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

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
# Using uvicorn directly
uvicorn main:app --reload

# Or run the main.py file directly
python main.py
```

## API Endpoints

- `GET /api/health` - Health check endpoint
- `POST /api/chat` - Chat endpoint (accepts a message and returns a response)

## Environment Variables

Copy the `.env.example` to `.env` and customize the values:

```bash
cp .env.example .env
```

Available environment variables:
- `HOST` - Host address (default: 0.0.0.0)
- `PORT` - Port number (default: 8000)
- `LOG_LEVEL` - Logging level (default: INFO)
- `DEBUG` - Debug mode (default: false)

## Project Structure

```
backend/
├── main.py                 # Main FastAPI application
├── endpoints/              # API endpoint modules
│   ├── health.py           # Health check endpoint
│   └── chat.py             # Chat endpoint
├── utils.py                # Utility functions
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
└── README.md               # This file
```