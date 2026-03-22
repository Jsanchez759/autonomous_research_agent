"""API v1 router"""
from fastapi import APIRouter
from .endpoints import health, research, runs

api_router = APIRouter()

# Include routers
api_router.include_router(health.router)
api_router.include_router(research.router)
api_router.include_router(runs.router)
