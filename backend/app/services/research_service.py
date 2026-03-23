"""Research Service for managing research operations with SQLite persistence."""
from concurrent.futures import Future, ThreadPoolExecutor
import json
import logging
import uuid
from datetime import datetime
from typing import Optional, List, Callable, Any

from app.db.models import ResearchRunModel
from app.db.session import SessionLocal, init_db
from app.schemas.research import ResearchRequest, ResearchStep

logger = logging.getLogger(__name__)


class ResearchService:
    """Service for managing research operations."""

    def __init__(self):
        """Initialize research service."""
        init_db()
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="research-worker")
        self._tasks: dict[str, Future] = {}

    async def create_research_run(self, request: ResearchRequest) -> str:
        """Create a new research run."""
        run_id = str(uuid.uuid4())
        now = datetime.now()

        with SessionLocal() as db:
            row = ResearchRunModel(
                run_id=run_id,
                topic=request.topic,
                status="pending",
                steps_json="[]",
                summary="",
                findings_json="[]",
                report_json="null",
                error=None,
                created_at=now,
                completed_at=None,
            )
            db.add(row)
            db.commit()

        logger.info("Created research run: %s for topic: %s", run_id, request.topic)
        return run_id

    def add_step(self, run_id: str, step: ResearchStep) -> None:
        """Add a step to a research run."""
        with SessionLocal() as db:
            row = self._get_row(db, run_id)
            if not row:
                return
            steps = self._loads_list(row.steps_json)
            steps.append(step.model_dump(mode="json"))
            row.steps_json = json.dumps(steps)
            db.commit()
        logger.info("Added step to run %s: %s", run_id, step.action)

    def update_run_status(self, run_id: str, status: str) -> None:
        """Update research run status."""
        with SessionLocal() as db:
            row = self._get_row(db, run_id)
            if not row:
                return
            row.status = status
            db.commit()
        logger.info("Updated run %s status to: %s", run_id, status)

    def complete_run(self, run_id: str) -> None:
        """Mark research run as completed."""
        with SessionLocal() as db:
            row = self._get_row(db, run_id)
            if not row:
                return
            row.completed_at = datetime.now()
            db.commit()
        logger.info("Completed research run: %s", run_id)

    def set_run_result(
        self,
        run_id: str,
        summary: str,
        findings: list[dict],
        report: Optional[dict] = None,
    ) -> None:
        """Store final research outputs for a run."""
        with SessionLocal() as db:
            row = self._get_row(db, run_id)
            if not row:
                return
            row.summary = summary
            row.findings_json = json.dumps(findings)
            row.report_json = json.dumps(report) if report is not None else "null"
            row.error = None
            db.commit()
        logger.info("Stored final output for run %s", run_id)

    def set_run_error(self, run_id: str, error: str) -> None:
        """Store run execution error."""
        with SessionLocal() as db:
            row = self._get_row(db, run_id)
            if not row:
                return
            row.error = error
            row.completed_at = datetime.now()
            db.commit()
        logger.info("Stored error for run %s", run_id)

    def get_run(self, run_id: str) -> Optional[dict]:
        """Get research run details."""
        with SessionLocal() as db:
            row = self._get_row(db, run_id)
            if not row:
                return None
            return self._serialize_row(row)

    def get_all_runs(self) -> List[dict]:
        """Get all research runs."""
        with SessionLocal() as db:
            rows = db.query(ResearchRunModel).order_by(ResearchRunModel.created_at.desc()).all()
            return [self._serialize_row(row) for row in rows]

    def delete_run(self, run_id: str) -> Optional[dict]:
        """Delete a run from persistence and return deleted record."""
        with SessionLocal() as db:
            row = self._get_row(db, run_id)
            if not row:
                return None
            serialized = self._serialize_row(row)
            db.delete(row)
            db.commit()
            return serialized

    def register_task(self, run_id: str, task: Future) -> None:
        """Register background task for a run."""
        self._tasks[run_id] = task

    def clear_task(self, run_id: str) -> None:
        """Remove background task reference for a run."""
        self._tasks.pop(run_id, None)

    def get_task(self, run_id: str) -> Optional[Future]:
        """Get background task for a run."""
        return self._tasks.get(run_id)

    def submit_task(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Future:
        """Submit work to the internal background executor."""
        return self._executor.submit(fn, *args, **kwargs)

    def _get_row(self, db, run_id: str) -> Optional[ResearchRunModel]:
        """Get DB row for run id."""
        return db.query(ResearchRunModel).filter(ResearchRunModel.run_id == run_id).first()

    def _loads_list(self, payload: str) -> list:
        """Safe JSON list decode helper."""
        try:
            decoded = json.loads(payload) if payload else []
            return decoded if isinstance(decoded, list) else []
        except json.JSONDecodeError:
            return []

    def _serialize_row(self, row: ResearchRunModel) -> dict:
        """Convert ORM row to API-friendly dictionary."""
        try:
            findings = json.loads(row.findings_json) if row.findings_json else []
        except json.JSONDecodeError:
            findings = []

        try:
            report = json.loads(row.report_json) if row.report_json else None
        except json.JSONDecodeError:
            report = None

        return {
            "run_id": row.run_id,
            "topic": row.topic,
            "status": row.status,
            "steps": self._loads_list(row.steps_json),
            "summary": row.summary or "",
            "findings": findings if isinstance(findings, list) else [],
            "report": report if isinstance(report, dict) else None,
            "error": row.error,
            "created_at": row.created_at,
            "completed_at": row.completed_at,
        }


# Global instance
research_service = ResearchService()
