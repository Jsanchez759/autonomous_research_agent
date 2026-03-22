"""Main research agent using LangChain"""
import logging
from datetime import datetime
from typing import Optional
from langchain.tools import Tool
from langchain_core.messages import HumanMessage, SystemMessage
from ..services.llm_service import LLMService
from ..schemas.research import ResearchStep

logger = logging.getLogger(__name__)


class ResearchAgent:
    """Main research agent for autonomous research"""

    def __init__(self):
        """Initialize research agent"""
        self.llm_service = LLMService()
        self.tools = self._create_tools()
        self.steps: list[ResearchStep] = []

    def _create_tools(self) -> list[Tool]:
        """Create tools for the agent"""
        # TODO: Create LangChain tools from our tool functions
        tools = []
        return tools

    async def run_research(
        self,
        topic: str,
        max_iterations: int = 5,
    ) -> dict:
        """
        Run research on a topic.
        
        Args:
            topic: Research topic
            max_iterations: Maximum iterations
            
        Returns:
            Research results
        """
        logger.info(f"Starting research on topic: {topic}")
        
        # Initialize system message
        system_prompt = self._get_system_prompt()
        
        # Create messages for agent
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Research the following topic: {topic}"),
        ]
        
        try:
            # Get response from LLM
            llm = self.llm_service.get_llm()
            response = llm.invoke(messages)
            
            # Add step
            step = ResearchStep(
                step_number=1,
                action="initial_analysis",
                status="completed",
                message=str(response.content),
                timestamp=datetime.now(),
            )
            self.steps.append(step)
            
            return {
                "topic": topic,
                "steps": [step.dict()],
                "summary": str(response.content),
            }
        
        except Exception as e:
            logger.error(f"Error during research: {e}")
            raise

    def _get_system_prompt(self) -> str:
        """Get system prompt for research"""
        return """You are a thorough research assistant. 
            Conduct comprehensive research providing detailed analysis, multiple perspectives, 
            and well-sourced information."""
