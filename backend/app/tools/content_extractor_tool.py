"""Content extraction tool"""
import logging
from typing import Optional
import re
import requests

logger = logging.getLogger(__name__)


def extract_content(url: str) -> Optional[str]:
    """
    Extract main content from a URL.
    
    Args:
        url: URL to extract content from
        
    Returns:
        Extracted content or None
    """
    logger.info(f"Extracting content from: {url}")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Failed to fetch URL '%s': %s", url, exc)
        return None

    html = response.text
    if not html:
        return None

    # Remove script/style/noscript blocks before stripping tags.
    html = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    html = re.sub(r"(?is)<style.*?>.*?</style>", " ", html)
    html = re.sub(r"(?is)<noscript.*?>.*?</noscript>", " ", html)

    # Extract paragraph-like blocks first; fall back to full tag stripping.
    paragraph_chunks = re.findall(r"(?is)<p[^>]*>(.*?)</p>", html)
    if paragraph_chunks:
        text = " ".join(paragraph_chunks)
    else:
        text = html

    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = (
        text.replace("&amp;", "&")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&nbsp;", " ")
    )
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return None

    # Keep payload bounded for downstream summarization/insight tools.
    return text[:12000]
