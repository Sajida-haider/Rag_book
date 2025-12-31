# OpenAI Agent with Qdrant Retrieval

This directory contains the implementation for an intelligent agent that answers book-related queries using retrieved context from Qdrant vector database, as specified in the feature spec for `008-openai-agent-qdrant`.

## Components

### 1. OpenAI Agent (`backend/agent.py`)
- Creates and manages an OpenAI assistant using the Assistants API
- Handles conversation threads and runs
- Processes user queries and generates responses

### 2. Qdrant Retriever (`backend/agent.py`)
- Connects to Qdrant vector database
- Performs semantic search using embeddings
- Formats retrieved context for the agent

### 3. Context Management (`backend/agent.py`)
- Structures retrieved content for agent consumption
- Manages context length and relevance
- Ensures responses are grounded in retrieved content

## Setup

### Prerequisites
- Python 3.8+
- OpenAI API key
- Qdrant database access (cloud or local)

### Environment Configuration
Make sure your `.env` file in the backend directory has the following variables:
```
OPENAI_API_KEY=your_openai_api_key_here
QDRANT_URL=your_qdrant_cloud_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
COLLECTION_NAME=humanoid_ai_book
```

### Installation
```bash
pip install openai qdrant-client python-dotenv
```

## Usage

### Running the Agent
```bash
python backend/agent.py
```

This will start the agent in interactive mode where you can ask questions about the book content.

### Example Queries
- "What is ROS 2?"
- "Explain Python agents with ROS 2"
- "What is Isaac ROS?"
- "How is humanoid robotics covered in this book?"

### Using the Agent Programmatically
```python
from backend.agent import BookQAAgent

# Create the agent
agent = BookQAAgent()

# Ask a question
response = agent.answer_query("What is ROS 2?")
print(response)

# Close the agent when done
agent.close()
```

## Architecture

The system follows this workflow:
1. User submits a query
2. Agent generates an embedding for the query
3. Agent searches for similar content in Qdrant
4. Retrieved context is formatted and provided to the OpenAI agent
5. Agent generates a response grounded only in the retrieved content
6. Response is returned to the user

## Features

- **Grounded Responses**: The agent only uses information from retrieved context
- **Source Citations**: Responses include citations to the source content
- **Error Handling**: Proper error handling and fallback mechanisms
- **Performance Monitoring**: Logging and performance metrics
- **Configurable**: Agent parameters can be customized

## Configuration

The agent can be configured using the `AgentConfig` class:
- `model`: OpenAI model to use (default: gpt-4-turbo-preview)
- `max_tokens`: Maximum tokens for responses (default: 1000)
- `temperature`: Response randomness (default: 0.3)
- `top_k`: Number of results to retrieve from Qdrant (default: 5)
- `max_context_length`: Maximum context length (default: 2000)

## Testing

To run the test suite:
```bash
python backend/test_agent.py
```

## Requirements

All required dependencies are included in the main project requirements and include:
- openai
- qdrant-client
- python-dotenv