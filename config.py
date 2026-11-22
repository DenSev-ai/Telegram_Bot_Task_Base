"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings required by the bot."""

    bot_token: str
    db_path: Path


def load_settings() -> Settings:
    """Read settings from .env or environment variables.

    Raises:
        RuntimeError: If BOT_TOKEN is not configured.
    """
    load_dotenv()
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "BOT_TOKEN is not set. Copy .env.example to .env and paste the token."
        )
    db_path = Path(os.getenv("DB_PATH", "data/tasks.db"))
    return Settings(bot_token=token, db_path=db_path)
