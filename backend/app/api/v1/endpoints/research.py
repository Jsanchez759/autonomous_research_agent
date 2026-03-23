"""Research endpoints"""
import logging
import asyncio
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.core.config import settings
from app.schemas.research import ResearchRequest, ResearchRunResponse, ResearchStep, ResearchReport
from app.services.research_service import research_service
from app.agents.research_agent import ResearchAgent

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/research", tags=["research"])


@router.post("/start", response_model=ResearchRunResponse)
async def start_research(request: ResearchRequest):
    """Start a new research task"""
    # Create run record and schedule async execution without blocking request.
    run_id = await research_service.create_research_run(request)
    task = research_service.submit_task(_run_research_background_sync, run_id, request.model_dump())
    research_service.register_task(run_id, task)

    run = research_service.get_run(run_id)
    return {
        "run_id": run_id,
        "topic": request.topic,
        "status": run["status"],
        "steps": [],
        "summary": "",
        "findings": [],
        "report": None,
        "error": None,
        "created_at": run["created_at"],
        "completed_at": None,
    }


@router.get("/run/{run_id}", response_model=ResearchRunResponse)
async def get_run_status(run_id: str):
    """Get status of a research run"""
    run = research_service.get_run(run_id)
    
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return {
        "run_id": run_id,
        "topic": run["topic"],
        "status": run["status"],
        "steps": [step.model_dump() if hasattr(step, "model_dump") else step for step in run["steps"]],
        "summary": run.get("summary", ""),
        "findings": run.get("findings", []),
        "report": run.get("report"),
        "error": run.get("error"),
        "created_at": run["created_at"],
        "completed_at": run.get("completed_at"),
    }


@router.get("/report/{run_id}", response_model=ResearchReport)
async def get_run_report(run_id: str):
    """Get final report payload for a completed run."""
    run = research_service.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    report = run.get("report")
    if not report:
        raise HTTPException(status_code=404, detail="Report not available yet")
    return report


@router.get("/report/{run_id}/pdf")
async def download_run_report_pdf(run_id: str):
    """Download generated report PDF."""
    run = research_service.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    report = run.get("report") or {}
    pdf_path = report.get("pdf_path")
    if not pdf_path:
        raise HTTPException(status_code=404, detail="PDF not available for this run")

    safe_path = _resolve_pdf_path(pdf_path)
    if not safe_path.exists() or not safe_path.is_file():
        raise HTTPException(status_code=404, detail="PDF file not found on disk")

    return FileResponse(
        path=safe_path,
        filename=safe_path.name,
        media_type="application/pdf",
    )


async def _run_research_background(run_id: str, request: ResearchRequest) -> None:
    """Execute one research run in background task."""
    try:
        research_service.update_run_status(run_id, "running")
        agent = ResearchAgent()

        result = await agent.run_research(
            topic=request.topic,
            max_iterations=request.max_iterations,
        )

        for step_data in result.get("steps", []):
            if isinstance(step_data, ResearchStep):
                step_obj = step_data
            else:
                step_obj = ResearchStep(**step_data)
            research_service.add_step(run_id, step_obj)

        research_service.set_run_result(
            run_id=run_id,
            summary=result.get("summary", ""),
            findings=result.get("findings", []),
            report=result.get("report"),
        )
        research_service.complete_run(run_id)
        research_service.update_run_status(run_id, "completed")
    except Exception as exc:
        logger.error("Background research failed for run %s: %s", run_id, exc)
        research_service.update_run_status(run_id, "failed")
        research_service.set_run_error(run_id, str(exc))
    finally:
        research_service.clear_task(run_id)


def _run_research_background_sync(run_id: str, request_data: dict) -> None:
    """Run async research flow inside worker thread."""
    request = ResearchRequest(**request_data)
    asyncio.run(_run_research_background(run_id, request))


def _resolve_pdf_path(pdf_path: str) -> Path:
    """Resolve and validate report PDF path against reports directory."""
    candidate = Path(pdf_path).expanduser().resolve()
    reports_root = settings.reports_dir_path.resolve()
    if reports_root not in candidate.parents and candidate != reports_root:
        raise HTTPException(status_code=400, detail="Invalid PDF path")
    return candidate
