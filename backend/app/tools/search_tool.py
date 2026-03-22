"""Web search tool for agent"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web for information.
    
    Args:
        query: Search query
        max_results: Maximum number of results
        
    Returns:
        List of search results
    """
    logger.info(f"Searching web for: {query}")
    
    # TODO: Implement with DuckDuckGo or similar service
    # For now, return mock results
    return [
        {
            "title": f"Result for {query}",
            "url": f"https://example.com/search?q={query}",
            "snippet": f"This is a search result for {query}",
        }
    ]
