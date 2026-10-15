"""Application settings loaded from environment variables."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "Aegis"
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql://rag:ragsecret@localhost:5433/ragdb"
    )
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")


settings = Settings()
