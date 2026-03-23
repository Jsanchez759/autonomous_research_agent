"""LLM Service for managing language model interactions with OpenRouter"""
import logging
from typing import Optional
from langchain_openai import ChatOpenAI
from app.core.config import settings

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
            if not settings.OPENROUTER_API_KEY:
                logger.warning("OPENROUTER_API_KEY not set. LLM features may not work.")
            
            self._llm = ChatOpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url=settings.OPENROUTER_BASE_URL,
                model=settings.OPENROUTER_CHAT_MODEL,
            )
            logger.info("LLM Service initialized with model: %s", settings.OPENROUTER_CHAT_MODEL)

    def get_llm(self):
        """Get LLM instance"""
        return self._llm

    def invoke(self, messages: list, **kwargs):
        """Invoke LLM with messages"""
        if not self._llm:
            raise RuntimeError("LLM not initialized")
        return self._llm.invoke(messages, **kwargs)

    async def ainvoke(self, messages: list, **kwargs):
        """Invoke LLM asynchronously with messages."""
        if not self._llm:
            raise RuntimeError("LLM not initialized")
        return await self._llm.ainvoke(messages, **kwargs)
