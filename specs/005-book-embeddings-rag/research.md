# Research Notes: Book Embeddings for RAG System

## Decision: Backend Structure and Technology Stack
**Rationale**: The system needs to fetch content from Docusaurus websites, generate embeddings using Cohere, and store them in Qdrant Cloud. Python is the ideal choice given its strong ecosystem for web scraping, NLP, and vector databases.
**Alternatives considered**: Node.js with JavaScript, but Python has better support for the required libraries (Cohere, Qdrant, BeautifulSoup).

## Decision: Single File Architecture (main.py)
**Rationale**: As specified in the requirements, a single main.py file will contain all ingestion functionality for simplicity and maintainability.
**Alternatives considered**: Multi-file modular approach, but the single file approach was explicitly requested.

## Decision: Package Manager (uv)
**Rationale**: uv is a fast Python package installer and resolver that will be used as specified in the requirements.
**Alternatives considered**: pip, poetry, but uv was specifically requested.

## Decision: Content Extraction from Docusaurus Sites
**Rationale**: Docusaurus sites have structured HTML with specific class names and elements that can be targeted for content extraction. BeautifulSoup4 will be used for parsing.
**Alternatives considered**: Selenium for dynamic content, but requests + BeautifulSoup is more efficient for static content.

## Decision: Embedding Model (Cohere)
**Rationale**: As specified in the requirements, Cohere's latest stable embedding model will be used for generating vector embeddings.
**Alternatives considered**: OpenAI embeddings, Hugging Face models, but Cohere was specifically requested.

## Decision: Vector Database (Qdrant Cloud)
**Rationale**: As specified in the requirements, Qdrant Cloud Free Tier will be used for storing embeddings with metadata.
**Alternatives considered**: Pinecone, Weaviate, but Qdrant was specifically requested.

## Decision: Content Chunking Strategy
**Rationale**: Content will be chunked into appropriate sizes (likely 512-1024 tokens) to optimize for embedding generation and retrieval performance.
**Alternatives considered**: Fixed character counts vs semantic chunking, but semantic chunking will be implemented to maintain context.

## Decision: Environment Configuration
**Rationale**: Using python-dotenv to manage API keys and configuration values securely without hardcoding them.
**Alternatives considered**: Direct environment variables, but .env files provide better management.