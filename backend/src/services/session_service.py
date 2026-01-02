from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Message(BaseModel):
    id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime

class ChatSession(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    messages: List[Message] = []
    user_id: Optional[str] = None

class SessionService:
    """
    Service for managing chat sessions in memory
    In production, this would use a persistent storage solution like Redis or PostgreSQL
    """

    def __init__(self, session_timeout_minutes: int = 30):
        self.sessions: Dict[str, ChatSession] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)

    def create_session(self, user_id: Optional[str] = None) -> ChatSession:
        """
        Create a new chat session

        Args:
            user_id: Optional user identifier

        Returns:
            Created ChatSession object
        """
        session_id = str(uuid.uuid4())
        now = datetime.now()

        session = ChatSession(
            id=session_id,
            created_at=now,
            updated_at=now,
            user_id=user_id
        )

        self.sessions[session_id] = session
        logger.info(f"Created new session: {session_id}")

        return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Get a chat session by ID

        Args:
            session_id: The session identifier

        Returns:
            ChatSession object if found, None otherwise
        """
        session = self.sessions.get(session_id)

        if session:
            # Check if session has expired
            if datetime.now() - session.updated_at > self.session_timeout:
                logger.info(f"Session {session_id} has expired, removing it")
                del self.sessions[session_id]
                return None

            return session

        return None

    def add_message(self, session_id: str, role: str, content: str) -> Optional[Message]:
        """
        Add a message to a chat session

        Args:
            session_id: The session identifier
            role: The role of the message sender ("user" or "assistant")
            content: The message content

        Returns:
            Created Message object if successful, None otherwise
        """
        session = self.get_session(session_id)
        if not session:
            logger.warning(f"Cannot add message to non-existent session: {session_id}")
            return None

        message = Message(
            id=str(uuid.uuid4()),
            role=role,
            content=content,
            timestamp=datetime.now()
        )

        # Limit the number of messages to prevent memory issues
        if len(session.messages) >= 100:
            # Remove the oldest messages to keep only the most recent 90
            session.messages = session.messages[-90:]
            logger.info(f"Trimmed messages for session {session_id}")

        session.messages.append(message)
        session.updated_at = datetime.now()

        logger.info(f"Added message to session {session_id}, total messages: {len(session.messages)}")

        return message

    def get_session_history(self, session_id: str) -> Optional[List[Message]]:
        """
        Get the message history for a session

        Args:
            session_id: The session identifier

        Returns:
            List of messages if session exists, None otherwise
        """
        session = self.get_session(session_id)
        if session:
            return session.messages
        return None

    def clear_session(self, session_id: str) -> bool:
        """
        Clear a chat session

        Args:
            session_id: The session identifier

        Returns:
            True if session was cleared, False if it didn't exist
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared session: {session_id}")
            return True
        return False

    def cleanup_expired_sessions(self):
        """
        Remove all expired sessions from memory
        """
        current_time = datetime.now()
        expired_sessions = []

        for session_id, session in self.sessions.items():
            if current_time - session.updated_at > self.session_timeout:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self.sessions[session_id]
            logger.info(f"Cleaned up expired session: {session_id}")

        return len(expired_sessions)