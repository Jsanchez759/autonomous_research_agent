"""Configuration for the application"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "storage"
DB_DIR = STORAGE_DIR / "db"

# Ensure directories exist
STORAGE_DIR.mkdir(exist_ok=True)
DB_DIR.mkdir(exist_ok=True)

# Database
DATABASE_URL = f"sqlite:///{DB_DIR / 'research_agent.db'}"

# OpenRouter Configuration (OpenAI-compatible endpoint)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_CHAT_MODEL = os.getenv("OPENROUTER_CHAT_MODEL", "openrouter/free")
OPENROUTER_EMBEDDING_MODEL = os.getenv("OPENROUTER_EMBEDDING_MODEL", "nvidia/llama-nemotron-embed-vl-1b-v2:free")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

# Agent Configuration

# API Configuration
API_V1_STR = "/api/v1"
PROJECT_NAME = "Autonomous Research Agent"
PROJECT_VERSION = "0.1.0"

# CORS
ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
