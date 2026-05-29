from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _bool_env(value: str | None, default: bool = False) -> bool:
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    telegram_toon_bot_token: str = ""
    openai_api_key: str = ""
    openai_text_model: str = "gpt-4.1-mini"
    openai_image_model: str = "gpt-image-1"
    output_dir: Path = Path("outputs")
    default_panel_count: int = 6
    enable_image_generation: bool = False
    max_daily_generations: int | None = None
    admin_user_ids: tuple[int, ...] = ()


def load_settings() -> Settings:
    load_dotenv()
    admin_ids = tuple(
        int(item.strip())
        for item in os.getenv("ADMIN_USER_IDS", "").split(",")
        if item.strip().isdigit()
    )
    max_daily = os.getenv("MAX_DAILY_GENERATIONS", "").strip()
    return Settings(
        telegram_toon_bot_token=os.getenv("TELEGRAM_TOON_BOT_TOKEN", ""),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_text_model=os.getenv("OPENAI_TEXT_MODEL", "gpt-4.1-mini"),
        openai_image_model=os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1"),
        output_dir=Path(os.getenv("OUTPUT_DIR", "outputs")),
        default_panel_count=int(os.getenv("DEFAULT_PANEL_COUNT", "6")),
        enable_image_generation=_bool_env(os.getenv("ENABLE_IMAGE_GENERATION"), False),
        max_daily_generations=int(max_daily) if max_daily else None,
        admin_user_ids=admin_ids,
    )
