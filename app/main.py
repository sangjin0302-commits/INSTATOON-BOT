from __future__ import annotations

import logging

from app.config import load_settings
from app.telegram_bot import create_application


def main() -> None:
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s:%(name)s:%(message)s")
    logging.getLogger("app").setLevel(logging.INFO)
    logging.getLogger("__main__").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    settings = load_settings()
    logging.getLogger(__name__).info("instatoon bot booting")
    logging.getLogger(__name__).info(
        "config_summary TELEGRAM_TOON_BOT_TOKEN_present=%s OPENAI_API_KEY_present=%s ENABLE_IMAGE_GENERATION=%s",
        bool(settings.telegram_toon_bot_token),
        bool(settings.openai_api_key),
        settings.enable_image_generation,
    )
    if not settings.telegram_toon_bot_token:
        raise RuntimeError("TELEGRAM_TOON_BOT_TOKEN is required to run the Telegram bot.")
    logging.getLogger(__name__).info("telegram_bot_starting image_generation_enabled=%s", settings.enable_image_generation)
    logging.getLogger(__name__).info("telegram polling starting")
    try:
        create_application(settings).run_polling(drop_pending_updates=False)
    finally:
        logging.getLogger(__name__).info("telegram polling stopped")


if __name__ == "__main__":
    main()
