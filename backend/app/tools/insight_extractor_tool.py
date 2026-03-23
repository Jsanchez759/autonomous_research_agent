"""Insight extraction tool powered by LLM."""
import json
import logging
import re
from typing import List

from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import settings
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


def extract_insights(content: str) -> List[dict]:
    """
    Extract a single key insight from page content using LLM.

    Args:
        content: Raw extracted page content

    Returns:
        A list containing exactly one structured insight when possible.
    """
    logger.info("Extracting one insight from content")

    cleaned = re.sub(r"\s+", " ", content).strip()
    if not cleaned:
        return []

    # Bound context size for stable latency/cost.
    context = cleaned[:5000]

    if not settings.OPENROUTER_API_KEY:
        return [_fallback_insight(context)]

    try:
        llm_service = LLMService()
        response = llm_service.invoke(
            [
                SystemMessage(
                    content=(
                        "You extract exactly one high-value insight from a webpage text. "
                        "Return ONLY valid JSON with keys: "
                        '{"title":"string","description":"string","confidence":0.0}.'
                    )
                ),
                HumanMessage(
                    content=(
                        "From the content below, extract one key insight that is most relevant, "
                        "specific, and evidence-based.\n\n"
                        f"CONTENT:\n{context}"
                    )
                ),
            ]
        )

        payload = _parse_json(str(response.content))
        title = str(payload.get("title", "")).strip()
        description = str(payload.get("description", "")).strip()
        confidence = _safe_confidence(payload.get("confidence"))

        if not title or not description:
            return [_fallback_insight(context)]

        return [
            {
                "title": title,
                "description": description,
                "confidence": confidence,
            }
        ]
    except Exception as exc:
        logger.warning("LLM insight extraction failed, using fallback: %s", exc)
        return [_fallback_insight(context)]


def _parse_json(raw: str) -> dict:
    """Extract and parse JSON object from plain text/markdown."""
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw, flags=re.IGNORECASE | re.DOTALL)
    json_text = fenced.group(1) if fenced else raw

    obj_match = re.search(r"\{.*\}", json_text, flags=re.DOTALL)
    if obj_match:
        json_text = obj_match.group(0)

    return json.loads(json_text)


def _fallback_insight(content: str) -> dict:
    """Fallback heuristic insight when LLM is unavailable."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", content) if s.strip()]
    sentence = sentences[0] if sentences else (content[:240] or "No insight extracted.")
    title_words = sentence.split()[:8]
    title = " ".join(title_words).rstrip(".,;:") or "Key Insight"

    return {
        "title": title,
        "description": sentence[:700],
        "confidence": 0.6,
    }


def _safe_confidence(value) -> float:
    """Clamp confidence into valid [0, 1] range."""
    try:
        numeric = float(value)
    except Exception:
        numeric = 0.75
    return max(0.0, min(numeric, 1.0))
