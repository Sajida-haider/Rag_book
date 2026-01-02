from typing import Dict, List, Any, Optional
import logging
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from openai import OpenAI
from .vector_storage import VectorStorageService, RetrievedContent
from .session_service import SessionService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGService:
    """
    Service for handling Retrieval-Augmented Generation (RAG) operations
    """

    def __init__(self):
        # Initialize dependencies
        self.vector_storage = VectorStorageService()
        self.session_service = SessionService()
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Validate required configuration
        if not os.getenv("OPENAI_API_KEY"):
            logger.warning("OPENAI_API_KEY not found in environment. RAG functionality may not work properly.")

    async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """
        Process a user message using RAG approach:
        1. Search for relevant content in the vector database
        2. Generate an AI response based on the retrieved content and user message
        3. Return the response with source attribution

        Args:
            message: The user's message/query
            session_id: The session identifier for conversation context

        Returns:
            Dictionary containing the response, sources, and retrieved content
        """
        try:
            logger.info(f"Processing message for session {session_id}: {message[:50]}...")

            # Add user message to session
            self.session_service.add_message(session_id, "user", message)

            # Retrieve relevant content from vector database
            retrieved_content = await self.vector_storage.search_by_text(message, limit=5)

            if not retrieved_content:
                logger.warning(f"No relevant content found for query: {message[:50]}...")
                # Return a helpful response when no content is found
                response_text = "I couldn't find specific information about that topic in the book. Please try rephrasing your question or ask about a different topic."

                # Add assistant response to session
                self.session_service.add_message(session_id, "assistant", response_text)

                return {
                    "response": response_text,
                    "sources": [],
                    "retrieved_content": []
                }

            # Prepare context for AI generation
            context_text = "\n\n".join([item.content for item in retrieved_content])
            sources = list(set([item.source for item in retrieved_content]))  # Remove duplicates

            # Generate AI response using OpenAI
            response = await self._generate_response(message, context_text)

            # Add assistant response to session
            self.session_service.add_message(session_id, "assistant", response)

            logger.info(f"Generated response for session {session_id}")

            return {
                "response": response,
                "sources": sources,
                "retrieved_content": retrieved_content
            }

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            # Return a fallback response
            response_text = "I'm having trouble processing your request right now. Please try again later."

            # Add assistant response to session even in error case
            if hasattr(self, 'session_service'):
                self.session_service.add_message(session_id, "assistant", response_text)

            return {
                "response": response_text,
                "sources": [],
                "retrieved_content": []
            }

    async def _generate_response(self, user_message: str, context: str) -> str:
        """
        Generate an AI response based on user message and retrieved context

        Args:
            user_message: The original user message
            context: Retrieved context from the vector database

        Returns:
            Generated AI response
        """
        try:
            # Create a prompt that includes the context and user message
            prompt = f"""
            You are a helpful assistant for a technical book. Use the following context to answer the user's question.
            If the context doesn't contain relevant information, say so politely.
            Base your response only on the provided context, and be concise and helpful.

            Context:
            {context}

            User's question: {user_message}

            Assistant's response:
            """

            # Call OpenAI API to generate response
            completion = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # You can change this to gpt-4 if preferred
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant for a technical book. Answer questions based on the provided context."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )

            response = completion.choices[0].message.content.strip()
            return response

        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            raise

    async def validate_connection(self) -> bool:
        """
        Validate that all required services are available

        Returns:
            True if all services are available, False otherwise
        """
        try:
            # Check if Qdrant collection exists
            if not self.vector_storage.collection_exists():
                logger.error(f"Qdrant collection '{self.vector_storage.collection_name}' does not exist")
                return False

            # Check if OpenAI API key is available and working
            if not os.getenv("OPENAI_API_KEY"):
                logger.warning("OpenAI API key not configured")
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating connection: {str(e)}")
            return False