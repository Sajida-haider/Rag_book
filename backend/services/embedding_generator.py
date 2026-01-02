"""Service for generating embeddings using Cohere API"""

import os
import cohere
from typing import List
from datetime import datetime
from dotenv import load_dotenv
import sys
import os
# Add the backend directory to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from models import Embedding

# Load environment variables
load_dotenv()

class EmbeddingGeneratorService:
    def __init__(self):
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            raise ValueError("COHERE_API_KEY environment variable is required")

        self.client = cohere.Client(api_key)
        self.model = "embed-multilingual-v3.0"  # Using Cohere's latest stable model

    def generate_embedding(self, text: str, chunk_id: str) -> Embedding:
        """Generate embedding for a single text chunk"""
        response = self.client.embed(
            texts=[text],
            model=self.model,
            input_type="search_document"
        )

        embedding_vector = response.embeddings[0]

        return Embedding(
            vector=embedding_vector,
            chunk_id=chunk_id,
            model=self.model,
            created_at=datetime.now()
        )

    def generate_embeddings_batch(self, texts: List[str]) -> List[Embedding]:
        """Generate embeddings for multiple text chunks"""
        if not texts:
            return []

        response = self.client.embed(
            texts=texts,
            model=self.model,
            input_type="search_document"
        )

        embeddings = []
        for i, embedding_vector in enumerate(response.embeddings):
            embeddings.append(
                Embedding(
                    vector=embedding_vector,
                    chunk_id=f"chunk_{i}",
                    model=self.model,
                    created_at=datetime.now()
                )
            )

        return embeddings