"""Research runs history endpoints"""
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.core.config import settings
from app.services.research_service import research_service
from app.schemas.run import RunsList

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/runs", tags=["runs"])


@router.get("/", response_model=RunsList)
async def list_runs():
    """Get list of all research runs"""
    runs = research_service.get_all_runs()
    
    return {
        "total": len(runs),
        "runs": [
            {
                "run_id": run.get("run_id", ""),
                "topic": run["topic"],
                "status": run["status"],
                "created_at": run["created_at"],
                "completed_at": run.get("completed_at"),
            }
            for run in runs
        ],
    }


@router.delete("/{run_id}")
async def delete_run(run_id: str):
    """Delete a run and its PDF artifact (if any)."""
    run = research_service.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    status = run.get("status")
    if status in {"pending", "running"}:
        raise HTTPException(status_code=409, detail="Cannot delete a run while it is active")

    report = run.get("report") or {}
    pdf_path = report.get("pdf_path")
    if pdf_path:
        try:
            candidate = Path(pdf_path).expanduser().resolve()
            reports_root = settings.reports_dir_path.resolve()
            if reports_root in candidate.parents and candidate.exists() and candidate.is_file():
                candidate.unlink()
        except Exception as exc:
            logger.warning("Could not remove PDF for run %s: %s", run_id, exc)

    deleted = research_service.delete_run(run_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Run not found")

    return {"deleted": True, "run_id": run_id}
