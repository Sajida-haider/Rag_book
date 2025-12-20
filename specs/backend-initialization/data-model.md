# Data Model: RAG Chatbot Backend

## Entities

### ChatRequest
**Description**: Represents a request to the chat endpoint
- **message** (string, required): The user's input message
- **history** (array of objects, optional): Conversation history for context

### ChatResponse
**Description**: Represents a response from the chat endpoint
- **response** (string, required): The bot's response to the user
- **context** (array of strings, optional): Context information used to generate the response

### HealthResponse
**Description**: Represents a response from the health check endpoint
- **status** (string, required): Health status of the service
- **message** (string, required): Human-readable status message

## API Contracts

### POST /api/chat
**Purpose**: Process a chat message and return a response
- **Request Body**: ChatRequest object
- **Response**: ChatResponse object
- **Error Responses**:
  - 422: Validation error if request body doesn't match ChatRequest schema

### GET /api/health
**Purpose**: Check the health status of the service
- **Request Body**: None
- **Response**: HealthResponse object
- **Error Responses**: None (should always return a response)

## Validation Rules
- The message field in ChatRequest must not be empty
- The history field in ChatRequest, if provided, must be an array of objects
- Response field in ChatResponse must be a string

## State Transitions
- None applicable for this initialization phase (stateless API)