# Book RAG System - Physical AI & Humanoid Robotics

This project implements a Retrieval-Augmented Generation (RAG) system for the "Physical AI & Humanoid Robotics" book content. The system allows users to ask questions about book content and get relevant answers based on the stored documentation.

## Features

- **Content Ingestion**: Automatically crawl and ingest book content from sitemaps
- **Embedding Generation**: Create vector embeddings of book content using Cohere
- **Vector Storage**: Store embeddings in Qdrant vector database
- **Semantic Search**: Find relevant content based on semantic similarity
- **RAG Interface**: Query the system to get answers based on book content

## About This Project

This RAG system provides AI-powered access to the comprehensive guide covering the intersection of artificial intelligence and robotics, focusing on how AI systems can function in the physical world. The documentation covers:

- **Module 1**: The Robotic Nervous System (ROS 2)
  - ROS 2 Fundamentals
  - Python Agents with ROS 2 (rclpy)
  - Humanoid Robot Description with URDF
- **Module 2**: The Digital Twin (Gazebo & Unity)
  - Physics Simulation in Gazebo
  - High Fidelity Simulation in Unity
  - Sensor Simulation
- **Module 3**: The AI-Robot Brain (NVIDIA Isaac™)
  - NVIDIA Isaac Sim
  - Isaac ROS Perception
  - Nav2 Navigation
- **Module 4**: Vision-Language-Action (VLA)
  - Voice to Action
  - Cognitive Planning with LLMs
  - Capstone: Autonomous Humanoid

## Architecture

The system consists of several key components:

- `ingest_from_sitemap.py`: Crawls sitemap and ingests documentation pages
- `services/rag_service.py`: Main RAG service for querying book content
- `services/web_scraper.py`: Scrapes content from web pages (with JS support)
- `services/content_extractor.py`: Extracts meaningful content from HTML
- `services/embedding_generator.py`: Generates embeddings using Cohere API
- `services/vector_storage.py`: Stores and retrieves embeddings from Qdrant
- `api.py`: Flask API for querying the RAG system

## Setup

1. Install dependencies:
```bash
pip install -r backend/requirements.txt
playwright install chromium
```

2. Set up environment variables in `.env`:
```
COHERE_API_KEY=your_cohere_api_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
COLLECTION_NAME=humanoid_ai_book
```

3. Run the ingestion script:
```bash
python backend/ingest_from_sitemap.py
```

## Usage

### Query the RAG System

```python
from services.rag_service import RAGService

rag_service = RAGService()

# Get relevant results for a question
results = rag_service.query("What is RAG?", top_k=5)

# Get context for generation
context = rag_service.get_context_for_generation("Explain RAG systems", max_context_length=2000)

# Get full answer
answer = rag_service.answer_question("How does RAG work?")
```

### Using the API

Start the API server:
```bash
python backend/api.py
```

Query the API:
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?", "top_k": 5}'
```

### Run the Demo

```bash
python backend/simple_demo.py
```

## Components

### Ingestion Pipeline
1. Crawl sitemap to find documentation pages
2. Scrape content from each page (with JavaScript rendering support)
3. Extract and clean meaningful content
4. Chunk content into appropriate sizes
5. Generate embeddings using Cohere
6. Store in Qdrant vector database

### Retrieval System
1. Receive user query
2. Generate embedding for query
3. Search for similar content in vector database
4. Return top-k relevant results
5. Format results for generation

## Environment Variables

- `COHERE_API_KEY`: API key for Cohere embedding service
- `QDRANT_URL`: URL for Qdrant vector database
- `QDRANT_API_KEY`: API key for Qdrant database
- `COLLECTION_NAME`: Name of the Qdrant collection (default: humanoid_ai_book)
- `SITEMAP_URL`: URL of the sitemap to crawl (default: https://rag-book-ten.vercel.app/sitemap.xml)

## Troubleshooting

- If content extraction fails, ensure Playwright browsers are installed: `playwright install chromium`
- Check that all environment variables are properly set
- Verify Qdrant connection and credentials
- For large sites, consider adjusting the `max_pages` parameter in ingestion

## Status

The system has successfully ingested content from the sitemap at `https://rag-book-ten.vercel.app/sitemap.xml`, including:
- All module chapters (Module 1-4)
- All tutorial pages
- All guide pages
- All documentation pages

The ingestion processed 21 pages successfully with 1 failure (due to empty content), creating 21 vector embeddings stored in the Qdrant database.
