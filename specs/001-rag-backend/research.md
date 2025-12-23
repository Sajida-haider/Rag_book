# Research: Live Deployed Book RAG Backend (Cohere + Qdrant)

## Overview
This research document addresses technical unknowns and best practices for implementing the RAG backend that ingests content from a live deployed Docusaurus book and stores embeddings in Qdrant for question answering.

## Decision: URL Discovery Strategy
**Rationale**: Need to identify all accessible pages from the deployed Docusaurus book at https://rag-book-cwq3n6mkx-sajida-haiders-projects.vercel.app
**Approach**: Use web scraping to discover all accessible URLs from the site. Two main strategies:
1. Sitemap parsing: Check if the site has a sitemap.xml
2. Web crawling: Follow internal links from the homepage

**Decision**: Implement both strategies - first check for sitemap.xml, then fall back to crawling internal links.

## Decision: HTML Content Extraction
**Rationale**: Need to extract clean, readable text from HTML pages while removing navigation, headers, and other non-content elements
**Approach**: Use BeautifulSoup4 to parse HTML and extract content from specific elements that contain the book content
**Best Practices**:
- Target main content containers (e.g., `main`, `article`, `#content`, `.markdown`)
- Remove navigation, headers, footers, sidebars
- Preserve text structure and hierarchy

## Decision: Text Chunking Strategy
**Rationale**: Need to split extracted text into appropriately sized chunks for embedding generation
**Approach**: Implement recursive text splitting that maintains semantic boundaries
**Best Practices**:
- Use sentence boundaries for splitting
- Overlap chunks slightly to preserve context
- Limit chunk size to ~500-1000 tokens (roughly 200-400 words)
- Preserve document context in metadata

## Decision: Cohere Embedding Model
**Rationale**: Need to select an appropriate embedding model from Cohere
**Approach**: Use Cohere's embed-multilingual-v3.0 model which works well for various content types
**Best Practices**:
- Use the latest version of Cohere's embedding model
- Handle rate limiting appropriately
- Cache embeddings to avoid redundant API calls

## Decision: Qdrant Collection Setup
**Rationale**: Need to create and configure the Qdrant collection named "rag_embedding"
**Approach**: Create collection with appropriate vector size for Cohere embeddings (1024 dimensions)
**Best Practices**:
- Use cosine similarity for semantic search
- Configure proper payload schema for metadata
- Implement proper error handling for collection creation

## Decision: API Framework
**Rationale**: Need to implement a question answering endpoint
**Approach**: Use FastAPI for the web framework due to its excellent support for async operations and automatic API documentation
**Best Practices**:
- Implement proper error handling
- Add request/response validation
- Include health check endpoints
- Use async functions for I/O operations

## Decision: Error Handling Strategy
**Rationale**: Need to handle various failure scenarios (Cohere API, Qdrant, website unavailable)
**Approach**: Implement graceful degradation with appropriate error messages
**Best Practices**:
- Use try-catch blocks for external API calls
- Provide meaningful error messages to users
- Implement retry logic for transient failures
- Log errors appropriately for debugging

## Decision: Configuration Management
**Rationale**: Need to handle API keys and configuration without hardcoding
**Approach**: Use environment variables for configuration
**Best Practices**:
- Store API keys in environment variables
- Provide default values where appropriate
- Validate required environment variables at startup
- Create .env.example file for documentation

## Decision: Dependency Management
**Rationale**: Need to manage Python dependencies
**Approach**: Use uv for dependency management as specified in user requirements
**Best Practices**:
- Create requirements.txt with exact versions
- Pin dependency versions for reproducibility
- Separate runtime and development dependencies if needed