"""
Conversation Manager for AI Therapist

Owns conversation lifecycle and provides clean APIs for conversation operations.
Acts as the single source of truth for conversation state.
"""

import logging
import re
from typing import Optional, Dict, Any, List
from backend.database import Database

logger = logging.getLogger(__name__)


class ConversationManager:
    """
    Manages conversation lifecycle and state.
    
    Responsibilities:
    - Create new conversations
    - Generate conversation titles
    - Update conversation metadata
    - List conversations for user
    - Delete conversations
    """
    
    def __init__(self, database: Database):
        """Initialize conversation manager with database instance."""
        self.db = database
    
    def create_conversation(self, user_id: str, title: Optional[str] = None) -> str:
        """
        Create a new conversation.
        
        Args:
            user_id: User ID who owns the conversation
            title: Optional conversation title (will be auto-generated if not provided)
        
        Returns:
            conversation_id: ID of the created conversation
        """
        conversation_id = self.db.create_conversation(user_id, title)
        logger.info(f"Created conversation {conversation_id} for user {user_id}")
        return conversation_id
    
    def get_conversation(self, conversation_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a conversation by ID (scoped to user).
        
        Args:
            conversation_id: ID of the conversation
            user_id: User ID (for security scoping)
        
        Returns:
            Conversation dict or None if not found
        """
        return self.db.get_conversation(conversation_id, user_id)
    
    def list_conversations(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all conversations for a user, ordered by most recent first.
        
        Args:
            user_id: User ID
            limit: Maximum number of conversations to return
            offset: Offset for pagination
        
        Returns:
            List of conversation dicts
        """
        return self.db.list_conversations(user_id, limit, offset)
    
    def update_conversation_title(self, conversation_id: str, title: str) -> bool:
        """
        Update conversation title.
        
        Args:
            conversation_id: ID of the conversation
            title: New title
        
        Returns:
            True if updated successfully
        """
        success = self.db.update_conversation_title(conversation_id, title)
        if success:
            logger.info(f"Updated title for conversation {conversation_id}")
        return success
    
    def update_conversation_timestamp(self, conversation_id: str) -> bool:
        """
        Update conversation's updated_at timestamp to current time.
        
        Args:
            conversation_id: ID of the conversation
        
        Returns:
            True if updated successfully
        """
        return self.db.update_conversation_timestamp(conversation_id)
    
    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        Delete a conversation and all its messages.
        
        Args:
            conversation_id: ID of the conversation
            user_id: User ID (for security scoping)
        
        Returns:
            True if deleted successfully
        """
        success = self.db.delete_conversation(conversation_id, user_id)
        if success:
            logger.info(f"Deleted conversation {conversation_id} for user {user_id}")
        return success
    
    def generate_title_from_message(self, message: str, max_length: int = 50) -> str:
        """
        Generate a conversation title from the first user message.
        
        Uses simple heuristics to create a meaningful title:
        - Extract first sentence or clause
        - Truncate to max_length
        - Clean up formatting
        
        Args:
            message: First user message in the conversation
            max_length: Maximum title length
        
        Returns:
            Generated title string
        """
        if not message:
            return "New Conversation"
        
        # Clean the message
        cleaned = message.strip()
        
        # Remove common prefixes
        prefixes_to_remove = [
            "hi", "hello", "hey", "greetings",
            "i want to", "i need to", "can you", "could you",
            "please", "help me"
        ]
        
        lower_cleaned = cleaned.lower()
        for prefix in prefixes_to_remove:
            if lower_cleaned.startswith(prefix):
                # Remove prefix and any following punctuation/whitespace
                cleaned = re.sub(f"^{re.escape(prefix)}[,.:;!?\\s]*", "", cleaned, flags=re.IGNORECASE).strip()
                break
        
        # Extract first sentence or clause
        # Look for sentence-ending punctuation or natural breaks
        sentence_match = re.search(r'^([^.!?]+[.!?])', cleaned)
        if sentence_match:
            title = sentence_match.group(1).strip()
        else:
            # No sentence ending found, look for comma or use whole message
            comma_match = re.search(r'^([^,]+)', cleaned)
            if comma_match:
                title = comma_match.group(1).strip()
            else:
                title = cleaned
        
        # Truncate to max_length
        if len(title) > max_length:
            title = title[:max_length].rsplit(' ', 1)[0] + "..."
        
        # Remove trailing punctuation if it's just a period
        title = re.sub(r'\.$', '', title)
        
        # Capitalize first letter
        if title:
            title = title[0].upper() + title[1:]
        
        # Fallback if title is empty or too short
        if not title or len(title) < 3:
            title = "New Conversation"
        
        return title
    
    def get_conversation_message_count(self, conversation_id: str) -> int:
        """
        Get the number of messages in a conversation.
        
        Args:
            conversation_id: ID of the conversation
        
        Returns:
            Number of messages
        """
        messages = self.db.get_messages_for_conversation(conversation_id, limit=10000)
        return len(messages)
