from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def _resolve_path(value: str, default: str) -> Path:
    raw = Path(os.getenv(value, default))
    return raw if raw.is_absolute() else PROJECT_ROOT / raw


@dataclass(frozen=True, slots=True)
class Settings:
    db_path: Path = _resolve_path(
        "SUPPORT_AGENT_DB_PATH", "data/mock/support_agent.db"
    )
    seed_dir: Path = _resolve_path(
        "SUPPORT_AGENT_SEED_DIR", "data/seeds"
    )
    return_window_days: int = int(
        os.getenv("SUPPORT_AGENT_RETURN_WINDOW_DAYS", "7")
    )
    log_level: str = os.getenv("SUPPORT_AGENT_LOG_LEVEL", "INFO")


settings = Settings()
