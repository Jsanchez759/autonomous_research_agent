"""Run history schemas"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RunHistory(BaseModel):
    """Run history record"""
    run_id: str
    topic: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    class Config:
        from_attributes = True


class RunsList(BaseModel):
    """List of runs"""
    total: int
    runs: list[RunHistory]
