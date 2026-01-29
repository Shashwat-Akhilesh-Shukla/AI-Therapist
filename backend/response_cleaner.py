"""
Response Cleaner Module

Provides deterministic, code-based cleaning of LLM responses to remove
formatting artifacts like citations, markdown, hashtags, and excessive asterisks.

This module does NOT rely on the LLM to clean its own output. Instead, it uses
regex patterns and string manipulation to ensure clean, natural responses.
"""

import re
from typing import Optional


def remove_citations(text: str) -> str:
    """
    Remove citation markers like [1], [2], [1][2][3], etc.
    
    Handles:
    - Single citations: [1]
    - Multiple consecutive citations: [1][2][3]
    - Citations with spaces: [1] [2]
    - Citations in middle of text
    
    Args:
        text: Input text with potential citations
        
    Returns:
        Text with citations removed
    """
    # Remove citation patterns like [1], [2], [1][2], etc.
    # This pattern matches one or more occurrences of [digit(s)]
    text = re.sub(r'(\[\d+\])+', '', text)
    
    # Remove citation patterns with spaces between them
    text = re.sub(r'\[\d+\]\s*', '', text)
    
    return text


def remove_markdown_formatting(text: str) -> str:
    """
    Remove markdown formatting while preserving natural emphasis.
    
    Handles:
    - Bold: **text** or __text__
    - Italic: *text* or _text_
    - Headers: ### Header, ## Header, # Header
    - Inline code: `code`
    - Links: [text](url)
    
    Args:
        text: Input text with potential markdown
        
    Returns:
        Text with markdown removed, preserving the content
    """
    # Remove headers (###, ##, #) at start of lines
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Remove bold (**text** or __text__) - keep the text
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    
    # Remove italic (*text* or _text_) - keep the text
    # Be careful not to remove asterisks that are part of natural text
    text = re.sub(r'\*([^*]+?)\*', r'\1', text)
    text = re.sub(r'_([^_]+?)_', r'\1', text)
    
    # Remove inline code (`code`) - keep the text
    text = re.sub(r'`([^`]+?)`', r'\1', text)
    
    # Remove markdown links [text](url) - keep only the text
    text = re.sub(r'\[([^\]]+?)\]\([^\)]+?\)', r'\1', text)
    
    return text


def remove_hashtags(text: str) -> str:
    """
    Remove hashtags from text.
    
    Handles:
    - Hashtags at start of line: #hashtag
    - Hashtags in middle of text: some #hashtag text
    - Multiple hashtags: #tag1 #tag2
    
    Args:
        text: Input text with potential hashtags
        
    Returns:
        Text with hashtags removed
    """
    # Remove hashtags (word starting with #)
    # This pattern matches # followed by word characters
    text = re.sub(r'#\w+', '', text)
    
    return text


def remove_asterisk_emphasis(text: str) -> str:
    """
    Remove excessive asterisks used for emphasis.
    
    Handles patterns like:
    - **action** or *action*
    - Multiple asterisks: ***text***
    - Asterisks around words for emphasis
    
    Args:
        text: Input text with potential asterisk emphasis
        
    Returns:
        Text with asterisk emphasis removed
    """
    # Remove patterns like *word* or **word** that weren't caught by markdown removal
    # This is a more aggressive cleanup for any remaining asterisks
    text = re.sub(r'\*+([^*]+?)\*+', r'\1', text)
    
    # Remove standalone asterisks
    text = re.sub(r'\s\*+\s', ' ', text)
    
    return text


def normalize_spacing(text: str) -> str:
    """
    Normalize spacing while preserving natural paragraph breaks.
    
    Handles:
    - Multiple spaces -> single space
    - Multiple newlines -> max 2 newlines (paragraph break)
    - Trailing/leading whitespace
    
    Args:
        text: Input text with potential spacing issues
        
    Returns:
        Text with normalized spacing
    """
    # Replace multiple spaces with single space (but not newlines)
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Replace more than 2 consecutive newlines with exactly 2 (paragraph break)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove spaces at start/end of lines
    text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[ \t]+', '', text, flags=re.MULTILINE)
    
    # Remove trailing/leading whitespace from entire text
    text = text.strip()
    
    return text


def clean_response(text: str) -> str:
    """
    Main cleaning function that orchestrates all cleaning operations.
    
    Applies cleaning operations in a specific order to avoid conflicts:
    1. Remove citations
    2. Remove markdown formatting
    3. Remove hashtags
    4. Remove asterisk emphasis
    5. Normalize spacing
    
    Args:
        text: Raw LLM response text
        
    Returns:
        Cleaned, natural text suitable for display
    """
    if not text:
        return text
    
    # Apply cleaning operations in order
    text = remove_citations(text)
    text = remove_markdown_formatting(text)
    text = remove_hashtags(text)
    text = remove_asterisk_emphasis(text)
    text = normalize_spacing(text)
    
    return text


def clean_streaming_chunk(chunk: str, context: Optional[dict] = None) -> str:
    """
    Clean a streaming chunk of text.
    
    This is optimized for streaming scenarios where text arrives in chunks.
    It's more conservative than full cleaning to avoid breaking mid-word formatting.
    
    Args:
        chunk: A chunk of streaming text
        context: Optional context dict to maintain state across chunks
        
    Returns:
        Cleaned chunk
    """
    if not chunk:
        return chunk
    
    # For streaming, we do lighter cleaning to avoid breaking partial formatting
    # Full cleaning will happen on the complete response
    
    # Remove obvious citations
    chunk = re.sub(r'\[\d+\]', '', chunk)
    
    # Remove obvious markdown headers at start of chunk
    if chunk.startswith('#'):
        chunk = re.sub(r'^#{1,6}\s+', '', chunk)
    
    return chunk
