"""Content summarization tool"""
import logging

logger = logging.getLogger(__name__)


def summarize_content(content: str, max_length: int = 300) -> str:
    """
    Summarize content.
    
    Args:
        content: Content to summarize
        max_length: Maximum length of summary
        
    Returns:
        Summarized content
    """
    logger.info(f"Summarizing content (length: {len(content)})")
    
    # TODO: Implement with LLM or extractive summarization
    if len(content) > max_length:
        return content[:max_length] + "..."
    return content
