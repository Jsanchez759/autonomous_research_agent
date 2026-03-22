"""Research Service for managing research operations"""
import logging
import uuid
from datetime import datetime
from typing import Optional, List
from ..schemas.research import ResearchRequest, ResearchRunResponse, ResearchStep

logger = logging.getLogger(__name__)


class ResearchService:
    """Service for managing research operations"""

    def __init__(self):
        """Initialize research service"""
        self.active_runs = {}

    async def create_research_run(self, request: ResearchRequest) -> str:
        """Create a new research run"""
        run_id = str(uuid.uuid4())
        
        self.active_runs[run_id] = {
            "topic": request.topic,
            "status": "pending",
            "steps": [],
            "created_at": datetime.now(),
            "completed_at": None,
        }
        
        logger.info(f"Created research run: {run_id} for topic: {request.topic}")
        return run_id

    def add_step(self, run_id: str, step: ResearchStep) -> None:
        """Add a step to a research run"""
        if run_id in self.active_runs:
            self.active_runs[run_id]["steps"].append(step)
            logger.info(f"Added step to run {run_id}: {step.action}")

    def update_run_status(self, run_id: str, status: str) -> None:
        """Update research run status"""
        if run_id in self.active_runs:
            self.active_runs[run_id]["status"] = status
            logger.info(f"Updated run {run_id} status to: {status}")

    def complete_run(self, run_id: str) -> None:
        """Mark research run as completed"""
        if run_id in self.active_runs:
            self.active_runs[run_id]["completed_at"] = datetime.now()
            logger.info(f"Completed research run: {run_id}")

    def get_run(self, run_id: str) -> Optional[dict]:
        """Get research run details"""
        return self.active_runs.get(run_id)

    def get_all_runs(self) -> List[dict]:
        """Get all research runs"""
        return list(self.active_runs.values())


# Global instance
research_service = ResearchService()
