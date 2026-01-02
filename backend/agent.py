"""
OpenRouter Agent with Qdrant Retrieval Integration
This file implements an intelligent agent that can answer book-related queries
using retrieved context from Qdrant vector database via OpenRouter API.
"""

import os
import logging
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
import openai

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set up OpenRouter API
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")

# Initialize OpenAI with OpenRouter
openai.base_url = "https://openrouter.ai/api/v1"
openai.api_key = OPENROUTER_API_KEY

# Initialize Qdrant client
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
collection_name = os.getenv("COLLECTION_NAME", "humanoid_ai_book")


@dataclass
class AgentConfig:
    model: str = "mistralai/devstral-2512:free"  # Using OpenRouter model
    max_tokens: int = 1000
    temperature: float = 0.3
    top_k: int = 5
    max_context_length: int = 2000


class QdrantRetriever:
    """Class to handle retrieval from Qdrant database"""

    def __init__(self, collection_name: str = collection_name):
        if qdrant_url and qdrant_api_key:
            self.client = QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key,
                prefer_grpc=True
            )
        else:
            # Fallback to local instance if cloud config not available
            host = os.getenv("QDRANT_HOST", "localhost")
            port = int(os.getenv("QDRANT_PORT", 6333))
            self.client = QdrantClient(host=host, port=port)

        self.collection_name = collection_name

    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for the query using OpenRouter"""
        try:
            # Call OpenRouter embeddings API using requests
            import json
            headers = {
                "Authorization": f"Bearer {openai.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "text-embedding-ada-002",  # Using OpenAI embedding model via OpenRouter
                "input": query
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/embeddings",
                headers=headers,
                json=data
            )

            if response.status_code == 200:
                response_data = response.json()
                if 'data' in response_data and len(response_data['data']) > 0:
                    embedding = response_data['data'][0]['embedding']
                    # Check if the embedding dimension matches Qdrant expectation (1024)
                    if len(embedding) != 1024:
                        # If dimensions don't match, we need to handle this appropriately
                        # For now, let's try to resize or use a different approach
                        if len(embedding) == 1536:
                            # If it's the standard OpenAI embedding size, truncate to 1024
                            return embedding[:1024]
                        else:
                            # For other sizes, return a zero-filled vector of the right size
                            result = [0.0] * 1024
                            min_len = min(len(embedding), 1024)
                            for i in range(min_len):
                                result[i] = embedding[i]
                            return result
                    return embedding
                else:
                    # Fallback to 1024-dim vector
                    return [0.0] * 1024
            else:
                logger.error(f"OpenRouter embeddings API error: {response.status_code} - {response.text}")
                # Fallback to 1024-dim vector
                return [0.0] * 1024
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Fallback: raise an error to stop ingestion
            raise RuntimeError("Embedding failed — stop ingestion")

    def retrieve_context(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant context from Qdrant based on the query"""
        try:
            query_embedding = self.embed_query(query)

            # Search for similar content in Qdrant using query_points method
            search_result = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=top_k,
                with_payload=True,
                with_vectors=False
            )

            # Format results - query_points returns a QueryResponse object
            # Extract the points from the response
            points = search_result.points if hasattr(search_result, 'points') else search_result

            formatted_results = []
            for result in points:
                # Check the type and structure of the result
                if hasattr(result, 'payload') and hasattr(result, 'score'):
                    # It's a ScoredPoint object
                    payload = result.payload
                    score = result.score
                elif isinstance(result, tuple):
                    # It might be a tuple of (payload, vector, score) or similar
                    if len(result) >= 2:
                        payload = result[0] if isinstance(result[0], dict) else {}
                        score = result[2] if len(result) > 2 else 0
                    else:
                        continue
                elif isinstance(result, dict):
                    # It's a dictionary
                    payload = result.get('payload', result)
                    score = result.get('score', result.get('score', 0))
                else:
                    # Unknown format, skip
                    continue

                # Ensure payload is a dict
                if not isinstance(payload, dict):
                    payload = {}

                formatted_results.append({
                    'content': payload.get('content', ''),
                    'title': payload.get('title', ''),
                    'url': payload.get('url', ''),
                    'section': payload.get('section', ''),
                    'score': score,
                    'chunk_index': payload.get('chunk_index', 0)
                })

            logger.info(f"Retrieved {len(formatted_results)} results from Qdrant")
            return formatted_results

        except Exception as e:
            logger.error(f"Error retrieving context from Qdrant: {e}")
            import traceback
            traceback.print_exc()
            return []


def retrieve_book_context(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Retrieve relevant book content from Qdrant vector database based on the query."""
    try:
        retriever = QdrantRetriever()
        results = retriever.retrieve_context(query, top_k)
        logger.info(f"Retrieved {len(results)} results from Qdrant for query: {query}")
        return results
    except Exception as e:
        logger.error(f"Error in retrieve_book_context: {e}")
        return []


class BookQAAgent:
    """OpenRouter Agent for answering book-related questions using retrieved context."""

    def __init__(self, config: AgentConfig = None):
        self.config = config or AgentConfig()
        self.retriever = QdrantRetriever()

    def _format_context(self, results: List[Dict[str, Any]]) -> str:
        """Format retrieved context for the LLM"""
        if not results:
            return "No relevant information found in the book."

        formatted_context = "Relevant book content:\n\n"
        for i, result in enumerate(results, 1):
            formatted_context += f"Source {i}: {result['title']} ({result['url']})\n"
            formatted_context += f"Content: {result['content']}\n"
            formatted_context += f"Relevance Score: {result['score']:.3f}\n\n"

        return formatted_context

    def answer_query(self, query: str) -> str:
        """Answer a query using OpenRouter with retrieved context."""
        try:
            logger.info(f"Processing query: {query}")

            # Retrieve relevant context from Qdrant
            retrieved_results = self.retriever.retrieve_context(query, top_k=self.config.top_k)

            # Format the context
            context = self._format_context(retrieved_results)

            # Prepare the prompt with context
            system_prompt = """
            You are a helpful assistant that answers questions based on book content.
            You must only use information that is provided in the context to answer questions.
            Do not make up information or use knowledge that is not in the provided context.
            If the answer is not available in the context, clearly state that the information is not available in the book.
            Always cite the source when providing information.
            """

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ]

            # Call OpenRouter API using requests
            import json
            headers = {
                "Authorization": f"Bearer {openai.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.config.model,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            )

            if response.status_code == 200:
                response_data = response.json()
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    result = response_data['choices'][0]['message']['content']
                else:
                    result = "Unable to get response from the model"
            else:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                result = "Unable to get response from the model"

            logger.info(f"Agent response generated successfully")
            return result

        except Exception as e:
            logger.error(f"Error processing query with OpenRouter: {e}")
            return f"An error occurred while processing your query: {str(e)}"

    async def answer_query_async(self, query: str) -> str:
        """Answer a query asynchronously using OpenRouter with retrieved context."""
        # For simplicity, just call the sync version
        # In a real implementation, you would use an async HTTP client
        return self.answer_query(query)

    def close(self):
        """Clean up resources"""
        logger.info("OpenRouter Agent resources cleaned up")


def main():
    """Main function to demonstrate the OpenRouter Agent implementation"""
    logger.info("Initializing Book QA Agent with OpenRouter...")

    try:
        # Create the agent
        agent = BookQAAgent()

        # Example queries
        example_queries = [
            "What is ROS 2?",
            "Explain Python agents with ROS 2",
            "What is Isaac ROS?",
            "How is humanoid robotics covered in this book?"
        ]

        print("Book QA Agent with OpenRouter initialized successfully!")
        print("=" * 50)

        for query in example_queries:
            print(f"\nQuery: {query}")
            print("-" * 30)

            response = agent.answer_query(query)
            print(f"Response: {response}")
            print("=" * 50)

        # Interactive mode
        print("\nInteractive mode (type 'quit' to exit):")
        while True:
            user_query = input("\nEnter your question: ").strip()
            if user_query.lower() in ['quit', 'exit', 'q']:
                break

            if user_query:
                response = agent.answer_query(user_query)
                print(f"Response: {response}")

    except Exception as e:
        logger.error(f"Error in main function: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if 'agent' in locals():
            agent.close()


if __name__ == "__main__":
    main()