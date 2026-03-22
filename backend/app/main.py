"""FastAPI application factory"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import ALLOWED_ORIGINS, API_V1_STR, PROJECT_NAME, PROJECT_VERSION
from .core.logging_config import setup_logging
from .api.v1.router import api_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=PROJECT_NAME,
    version=PROJECT_VERSION,
    description="Autonomous Research Agent API",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=API_V1_STR)


@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info(f"{PROJECT_NAME} started (v{PROJECT_VERSION})")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    logger.info("Application shutdown")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Autonomous Research Agent API",
        "version": PROJECT_VERSION,
        "docs": "/docs",
    }
