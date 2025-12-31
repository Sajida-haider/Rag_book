"""Service for implementing Retrieval-Augmented Generation (RAG) functionality with book content"""

import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import sys
import os
# Add the backend directory to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from models import Embedding
from services.embedding_generator import EmbeddingGeneratorService
from services.vector_storage import VectorStorageService

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.embedding_service = EmbeddingGeneratorService()
        self.storage_service = VectorStorageService()

    def query(self, question: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Query the RAG system with a question and return relevant book content

        Args:
            question: The user's question
            top_k: Number of top results to return

        Returns:
            List of dictionaries containing relevant content and metadata
        """
        logger.info(f"Processing query: {question}")

        try:
            # Generate embedding for the question
            question_embedding = self.embedding_service.generate_embedding(
                text=question,
                chunk_id="query"
            )

            # Search for similar content in the vector database
            similar_results = self.storage_service.search_similar(
                query_vector=question_embedding.vector,
                limit=top_k
            )

            logger.info(f"Found {len(similar_results)} similar results")

            # Format and return the results
            formatted_results = []
            for result in similar_results:
                formatted_results.append({
                    'content': result['payload'].get('content', ''),
                    'title': result['payload'].get('title', ''),
                    'url': result['payload'].get('url', ''),
                    'section': result['payload'].get('section', ''),
                    'score': result['score'],
                    'chunk_index': result['payload'].get('chunk_index', 0)
                })

            return formatted_results

        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            raise

    def get_context_for_generation(self, question: str, max_context_length: int = 2000) -> str:
        """
        Get relevant context for a question to use in generation

        Args:
            question: The user's question
            max_context_length: Maximum length of context to return

        Returns:
            Formatted context string
        """
        results = self.query(question, top_k=10)  # Get more results to have more options

        context_parts = []
        current_length = 0

        for result in results:
            content = result['content']
            if current_length + len(content) <= max_context_length:
                context_parts.append(f"Source: {result['title']} ({result['url']})\nContent: {content}\n---\n")
                current_length += len(content) + len(context_parts[-1]) - len(content)  # Add overhead for formatting
            else:
                # Add partial content if we have space
                remaining_space = max_context_length - current_length
                if remaining_space > 100:  # Only add if we have significant space
                    partial_content = content[:remaining_space]
                    context_parts.append(f"Source: {result['title']} ({result['url']})\nContent: {partial_content}...\n---\n")
                break

        return "".join(context_parts)

    def answer_question(self, question: str, max_context_length: int = 2000) -> str:
        """
        Generate an answer to a question using the RAG approach

        Args:
            question: The user's question
            max_context_length: Maximum length of context to use for generation

        Returns:
            Generated answer based on retrieved context
        """
        # For now, return the context that would be used
        # In a full implementation, this would call an LLM with the context
        context = self.get_context_for_generation(question, max_context_length)

        return f"Context for question '{question}':\n\n{context}"

    def search_by_keywords(self, keywords: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for content using keywords instead of semantic similarity

        Args:
            keywords: Keywords to search for
            top_k: Number of top results to return

        Returns:
            List of matching content
        """
        # For keyword search, we'll use the same semantic approach but with keywords
        # In a production system, you might want to add traditional keyword search as well
        return self.query(keywords, top_k)

    def get_all_documentation(self) -> List[Dict[str, Any]]:
        """
        Retrieve all stored documentation content

        Returns:
            List of all stored content
        """
        try:
            all_records = self.storage_service.get_all_records()

            formatted_records = []
            for record in all_records:
                formatted_records.append({
                    'id': record.id,
                    'content': record.payload.get('content', ''),
                    'title': record.payload.get('title', ''),
                    'url': record.payload.get('url', ''),
                    'section': record.payload.get('section', ''),
                    'chunk_index': record.payload.get('chunk_index', 0),
                    'created_at': record.payload.get('created_at', '')
                })

            return formatted_records
        except Exception as e:
            logger.error(f"Error retrieving all documentation: {e}")
            raise