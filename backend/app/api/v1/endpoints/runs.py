"""Research runs history endpoints"""
import logging
from fastapi import APIRouter
from app.services.research_service import research_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/runs", tags=["runs"])


@router.get("/")
async def list_runs():
    """Get list of all research runs"""
    runs = research_service.get_all_runs()
    
    return {
        "total": len(runs),
        "runs": [
            {
                "run_id": list(research_service.active_runs.keys())[i] if i < len(research_service.active_runs) else "",
                "topic": run["topic"],
                "status": run["status"],
                "created_at": run["created_at"],
                "completed_at": run.get("completed_at"),
            }
            for i, run in enumerate(runs)
        ],
    }
