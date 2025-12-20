"""
Book Content Ingestion Package

This package contains modules for ingesting Docusaurus book content,
generating embeddings, and storing them in Qdrant and Neon Postgres.
"""

__version__ = "0.1.0"

# Import main classes for easy access
from .content_reader import ContentReader
from .cleaner import ContentCleaner
from .chunker import ContentChunker
from .embedder import OpenAIEmbedder
from .vector_store import QdrantVectorStore
from .metadata_store import NeonPostgresMetadataStore
from .main import BookIngestionPipeline

__all__ = [
    "ContentReader",
    "ContentCleaner",
    "ContentChunker",
    "OpenAIEmbedder",
    "QdrantVectorStore",
    "NeonPostgresMetadataStore",
    "BookIngestionPipeline"
]