"""Data models for the book embeddings RAG system based on data-model.md"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class BookContent:
    """Represents the extracted text content from book pages, including cleaned text and structural information"""
    url: str
    title: str
    content: str
    section: str
    created_at: datetime
    updated_at: datetime


@dataclass
class Embedding:
    """Vector representation of book content chunks, generated using Cohere embedding models"""
    vector: List[float]
    chunk_id: str
    model: str
    created_at: datetime


@dataclass
class Metadata:
    """Information about the source of content including URL, page title, section, and timestamp"""
    source_url: str
    page_title: str
    section_info: str
    chunk_index: int
    total_chunks: int
    created_at: datetime


@dataclass
class VectorRecord:
    """Combined entity of embedding vectors and metadata stored in the Qdrant database"""
    id: str
    payload: Dict[str, Any]  # Contains url, title, section, content, chunk_index
    vector: List[float]
    created_at: datetime