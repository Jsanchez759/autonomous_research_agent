"""Configuration for the application using Pydantic Settings."""
from pathlib import Path
from typing import Any, Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    PROJECT_NAME: str = "Autonomous Research Agent"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # CORS defaults for local development.
    ALLOWED_ORIGINS: Annotated[list[str], NoDecode] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]
    ALLOWED_ORIGIN_REGEX: str = (
        r"^https?://(localhost|127\.0\.0\.1|0\.0\.0\.0)(:\d+)?$"
        r"|^https://([a-zA-Z0-9-]+\.)*vercel\.app$"
    )

    # OpenRouter-compatible OpenAI client settings.
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_CHAT_MODEL: str = "openrouter/free"
    OPENROUTER_EMBEDDING_MODEL: str = "nvidia/llama-nemotron-embed-vl-1b-v2:free"
    LLM_TEMPERATURE: float = 0.7
    LLM_TIMEOUT_SECONDS: float = 45.0
    LLM_MAX_RETRIES: int = 0

    # Storage/database settings.
    STORAGE_DIR: str = "storage"
    DB_DIR: str = "storage/db"
    REPORTS_DIR: str = "storage/reports"
    DATABASE_URL: str = ""

    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: Any) -> list[str]:
        """Support comma-separated env var values for ALLOWED_ORIGINS."""
        if isinstance(value, str):
            cleaned = [origin.strip() for origin in value.split(",") if origin.strip()]
            return cleaned
        if isinstance(value, list):
            return value
        return []

    @property
    def base_dir(self) -> Path:
        """Project backend directory (contains app/, storage/, .env)."""
        return Path(__file__).resolve().parent.parent.parent

    @property
    def storage_dir_path(self) -> Path:
        """Absolute path for storage directory."""
        storage = Path(self.STORAGE_DIR)
        if not storage.is_absolute():
            storage = self.base_dir / storage
        return storage

    @property
    def db_dir_path(self) -> Path:
        """Absolute path for db directory."""
        db_dir = Path(self.DB_DIR)
        if not db_dir.is_absolute():
            db_dir = self.base_dir / db_dir
        return db_dir

    @property
    def database_url(self) -> str:
        """Database URL resolved from env or default sqlite path."""
        if self.DATABASE_URL.strip():
            return self.DATABASE_URL.strip()
        return f"sqlite:///{self.db_dir_path / 'research_agent.db'}"

    @property
    def reports_dir_path(self) -> Path:
        """Absolute path for generated reports."""
        reports = Path(self.REPORTS_DIR)
        if not reports.is_absolute():
            reports = self.base_dir / reports
        return reports

    def ensure_directories(self) -> None:
        """Create storage/db directories when using local sqlite paths."""
        self.storage_dir_path.mkdir(parents=True, exist_ok=True)
        self.db_dir_path.mkdir(parents=True, exist_ok=True)
        self.reports_dir_path.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
