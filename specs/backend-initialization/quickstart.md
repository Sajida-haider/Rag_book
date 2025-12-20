# Quickstart: RAG Chatbot Backend

## Prerequisites
- Python 3.11 or higher
- pip package manager

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
Copy the .env file to set up your local configuration:
```bash
cp .env .env.local  # if you want to customize settings
```

### 7. Run the Application
```bash
# Using uvicorn directly
uvicorn main:app --reload

# Or run the main.py file directly
python main.py
```

## API Endpoints

Once the server is running (default: http://localhost:8000):

### Health Check
```
GET /api/health
```
Returns the health status of the service.

### Chat Endpoint
```
POST /api/chat
Content-Type: application/json

{
  "message": "Your message here",
  "history": []
}
```
Sends a message to the chatbot and receives a response.

## Testing the Backend

### Manual Testing
1. Start the server: `uvicorn main:app --reload`
2. Open your browser to http://localhost:8000/docs to access the interactive API documentation
3. Test the endpoints using the built-in Swagger UI

### API Documentation
The backend automatically generates API documentation at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)
- http://localhost:8000/openapi.json (OpenAPI specification)

## Configuration

The backend can be configured using environment variables in the `.env` file:
- `HOST`: Server host address (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `LOG_LEVEL`: Logging level (default: INFO)
- `DEBUG`: Debug mode (default: false)