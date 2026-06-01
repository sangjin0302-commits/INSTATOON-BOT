from __future__ import annotations

import logging

from app.config import load_settings
from app.telegram_bot import create_application


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    settings = load_settings()
    if not settings.telegram_toon_bot_token:
        raise RuntimeError("TELEGRAM_TOON_BOT_TOKEN is required to run the Telegram bot.")
    logging.getLogger(__name__).info("telegram_bot_starting image_generation_enabled=%s", settings.enable_image_generation)
    create_application(settings).run_polling()


if __name__ == "__main__":
    main()
