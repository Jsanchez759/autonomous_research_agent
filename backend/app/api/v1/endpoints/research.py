"""Research endpoints"""
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
from app.schemas.research import ResearchRequest, ResearchRunResponse, ResearchStep
from app.services.research_service import research_service
from app.agents.research_agent import ResearchAgent
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/research", tags=["research"])


@router.post("/start")
async def start_research(request: ResearchRequest):
    """Start a new research task"""
    try:
        # Create research run
        run_id = await research_service.create_research_run(request)
        
        # Initialize agent
        agent = ResearchAgent()
        
        # Update status
        research_service.update_run_status(run_id, "running")
        
        # Start research (in production, this would be async)
        result = await agent.run_research(
            topic=request.topic,
            max_iterations=request.max_iterations or 5,
        )
        
        # Update with results
        research_service.complete_run(run_id)
        research_service.update_run_status(run_id, "completed")
        
        return {
            "run_id": run_id,
            "topic": request.topic,
            "status": "completed",
            "steps": result.get("steps", []),
            "summary": result.get("summary", ""),
            "created_at": datetime.now(),
        }
    
    except Exception as e:
        logger.error(f"Error starting research: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/run/{run_id}")
async def get_run_status(run_id: str):
    """Get status of a research run"""
    run = research_service.get_run(run_id)
    
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return {
        "run_id": run_id,
        "topic": run["topic"],
        "status": run["status"],
        "steps": [step.dict() if hasattr(step, 'dict') else step for step in run["steps"]],
        "created_at": run["created_at"],
        "completed_at": run.get("completed_at"),
    }
