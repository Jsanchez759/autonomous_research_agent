"""LLM Service for managing language model interactions with OpenRouter"""
import logging
from typing import Optional
from langchain_openai import ChatOpenAI
from app.core.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_CHAT_MODEL,
)

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM interactions using OpenRouter"""

    _instance: Optional["LLMService"] = None
    _llm: Optional[ChatOpenAI] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize LLM service with OpenRouter"""
        if self._llm is None:
            if not OPENROUTER_API_KEY:
                logger.warning("OPENROUTER_API_KEY not set. LLM features may not work.")
            
            self._llm = ChatOpenAI(
                api_key=OPENROUTER_API_KEY,
                base_url=OPENROUTER_BASE_URL,
                model=OPENROUTER_CHAT_MODEL,
            )
            logger.info(f"LLM Service initialized with model: {OPENROUTER_CHAT_MODEL}")

    def get_llm(self):
        """Get LLM instance"""
        return self._llm

    def invoke(self, messages: list, **kwargs):
        """Invoke LLM with messages"""
        if not self._llm:
            raise RuntimeError("LLM not initialized")
        return self._llm.invoke(messages, **kwargs)
