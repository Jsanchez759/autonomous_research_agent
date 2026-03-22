"""Research request/response schemas"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ResearchRequest(BaseModel):
    """Research request from frontend"""
    topic: str
    max_iterations: Optional[int] = 5


class ResearchStep(BaseModel):
    """Individual agent step"""
    step_number: int
    action: str
    status: str  # running, completed, failed
    message: str
    timestamp: datetime


class ResearchFinding(BaseModel):
    """Research finding/insight"""
    title: str
    content: str
    source: Optional[str] = None
    confidence: float = 0.8


class ResearchReport(BaseModel):
    """Final research report"""
    topic: str
    summary: str
    findings: List[ResearchFinding]
    conclusion: str
    generated_at: datetime


class ResearchRunResponse(BaseModel):
    """Response for research run"""
    run_id: str
    topic: str
    status: str  # pending, running, completed, failed
    steps: List[ResearchStep]
    report: Optional[ResearchReport] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
