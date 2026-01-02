# Data Model: Connect Chatbot UI with RAG Backend

## Entities

### Chat Session
**Description**: Represents a conversation context with unique identifier, message history, and metadata
**Fields**:
- `id` (string): Unique identifier for the session
- `created_at` (timestamp): When the session was created
- `updated_at` (timestamp): When the session was last updated
- `messages` (array): List of messages in the conversation
- `user_id` (string, optional): Identifier for the user (if tracking is needed)

### User Message
**Description**: Text input from the user with timestamp and session association
**Fields**:
- `id` (string): Unique identifier for the message
- `session_id` (string): Reference to the chat session
- `content` (string): The actual message text
- `timestamp` (timestamp): When the message was sent
- `role` (string): "user" to identify the sender

### AI Response
**Description**: AI-generated response based on retrieved content with source references
**Fields**:
- `id` (string): Unique identifier for the response
- `session_id` (string): Reference to the chat session
- `content` (string): The AI-generated response text
- `timestamp` (timestamp): When the response was generated
- `role` (string): "assistant" to identify the sender
- `sources` (array): List of source documents/references used in generation
- `retrieved_content` (array): The content retrieved from vector database that influenced the response

### Backend Service Connection
**Description**: Configuration for connecting to the backend service
**Fields**:
- `endpoint_url` (string): The URL of the backend API
- `api_key` (string, optional): Authentication key if required
- `timeout` (number): Request timeout in milliseconds
- `max_retries` (number): Number of retry attempts for failed requests

## Validation Rules

### Chat Session
- Session ID must be unique across all sessions
- Session must have a creation timestamp
- Session cannot have more than 100 messages (to prevent memory issues)
- Session must be updated when a new message is added

### User Message
- Content must not be empty
- Content must be less than 10,000 characters
- Must have a valid session ID reference
- Timestamp must be current or past (not future)

### AI Response
- Content must not be empty
- Must have a valid session ID reference
- Sources array can be empty but must exist
- Retrieved content should be used to generate the response

## State Transitions

### Chat Session
- `created` → `active`: When first message is sent
- `active` → `active`: When additional messages are exchanged
- `active` → `ended`: When session expires or is closed by user
- `ended` → `archived`: After a period of inactivity (optional)

### Backend Service Connection
- `initialized` → `connected`: When connection is established
- `connected` → `disconnected`: When connection fails
- `disconnected` → `reconnecting`: When attempting to reconnect
- `reconnecting` → `connected`: When reconnection succeeds