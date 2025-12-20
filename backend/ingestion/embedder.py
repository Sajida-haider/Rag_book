import os
import openai
from typing import List, Dict
import logging
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class OpenAIEmbedder:
    """
    Module to generate embeddings using OpenAI embeddings API
    """

    def __init__(self):
        # Set up OpenAI API key from environment variables
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        openai.api_key = api_key

        # Use a default model, but allow override
        self.model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")

        # Track API usage for rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum time between requests in seconds

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of text chunks using OpenAI API
        """
        if not texts:
            return []

        # Rate limiting: ensure minimum interval between requests
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)

        try:
            # Call OpenAI API to generate embeddings
            response = openai.embeddings.create(
                input=texts,
                model=self.model
            )

            # Extract embeddings from response
            embeddings = []
            for item in response.data:
                embeddings.append(item.embedding)

            # Update last request time
            self.last_request_time = time.time()

            logger.info(f"Generated embeddings for {len(texts)} text chunks using model {self.model}")
            return embeddings

        except openai.AuthenticationError:
            logger.error("OpenAI API authentication failed. Check your API key.")
            raise
        except openai.RateLimitError:
            logger.error("OpenAI API rate limit exceeded. Consider upgrading your plan or implementing more aggressive rate limiting.")
            raise
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during embedding generation: {e}")
            raise

    def generate_single_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        """
        embeddings = self.generate_embeddings([text])
        return embeddings[0] if embeddings else []

    def validate_embeddings(self, texts: List[str], embeddings: List[List[float]]) -> bool:
        """
        Validate that embeddings match the expected count and dimensions
        """
        if len(texts) != len(embeddings):
            logger.error(f"Mismatch: {len(texts)} texts but {len(embeddings)} embeddings")
            return False

        # Check that all embeddings have the same dimension
        if embeddings:
            expected_dim = len(embeddings[0])
            for i, embedding in enumerate(embeddings):
                if len(embedding) != expected_dim:
                    logger.error(f"Embedding {i} has dimension {len(embedding)}, expected {expected_dim}")
                    return False

        logger.info(f"Validated {len(embeddings)} embeddings successfully")
        return True

    def get_model_info(self) -> Dict:
        """
        Get information about the embedding model being used
        """
        return {
            "model": self.model,
            "dimensions": self.get_embedding_dimensions(),
            "api_provider": "OpenAI"
        }

    def get_embedding_dimensions(self) -> int:
        """
        Get the expected dimension of embeddings for the current model
        """
        # Different models have different dimensions
        model_dims = {
            "text-embedding-ada-002": 1536,
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072
        }
        return model_dims.get(self.model, 1536)  # Default to ada-002 dimensions


class EmbeddingCache:
    """
    Simple cache to avoid regenerating embeddings for the same content
    """

    def __init__(self):
        self.cache = {}

    def get(self, text: str) -> List[float]:
        """
        Get embedding from cache if available
        """
        text_hash = hash(text)
        return self.cache.get(text_hash)

    def put(self, text: str, embedding: List[float]):
        """
        Put embedding in cache
        """
        text_hash = hash(text)
        self.cache[text_hash] = embedding

    def has(self, text: str) -> bool:
        """
        Check if embedding is in cache
        """
        text_hash = hash(text)
        return text_hash in self.cache


# Example usage
if __name__ == "__main__":
    # This would require a valid OpenAI API key to run
    try:
        embedder = OpenAIEmbedder()

        sample_texts = [
            "This is the first chunk of text.",
            "This is the second chunk with different content.",
            "Final chunk for testing purposes."
        ]

        print("Generating embeddings...")
        embeddings = embedder.generate_embeddings(sample_texts)

        print(f"Generated {len(embeddings)} embeddings")
        print(f"First embedding has {len(embeddings[0])} dimensions")

        # Validate embeddings
        is_valid = embedder.validate_embeddings(sample_texts, embeddings)
        print(f"Embeddings validation: {'Passed' if is_valid else 'Failed'}")

    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Embeddings generation requires a valid OPENAI_API_KEY in environment variables")