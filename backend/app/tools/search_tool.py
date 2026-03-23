"""Web search tool for agent"""
import logging
import re
import html
from urllib.parse import quote_plus
import requests

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

    if not query.strip():
        return []

    url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Search failed for query '%s': %s", query, exc)
        return []

    # DuckDuckGo HTML SERP snippets are in anchors with class result__a and
    # snippets in adjacent anchors with class result__snippet.
    title_matches = re.findall(
        r'<a[^>]*class="[^"]*result__a[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
        response.text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    snippet_matches = re.findall(
        r'<a[^>]*class="[^"]*result__snippet[^"]*"[^>]*>(.*?)</a>',
        response.text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    results: list[dict] = []
    for idx, (href, raw_title) in enumerate(title_matches):
        if len(results) >= max_results:
            break

        title = _clean_html(raw_title)
        snippet = _clean_html(snippet_matches[idx]) if idx < len(snippet_matches) else ""
        parsed_url = _extract_ddg_redirect_url(href)
        if not parsed_url:
            continue

        results.append(
            {
                "title": title,
                "url": parsed_url,
                "snippet": snippet,
            }
        )

    return results


def _extract_ddg_redirect_url(raw_href: str) -> str:
    """Extract final URL from DuckDuckGo redirect links."""
    if raw_href.startswith("http://") or raw_href.startswith("https://"):
        return raw_href

    match = re.search(r"uddg=([^&]+)", raw_href)
    if not match:
        return ""

    encoded = match.group(1)
    return requests.utils.unquote(encoded)


def _clean_html(text: str) -> str:
    """Remove HTML tags and compress whitespace."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()
