from __future__ import annotations

from app.config import load_settings
from app.telegram_bot import create_application


def main() -> None:
    settings = load_settings()
    if not settings.telegram_toon_bot_token:
        raise RuntimeError("TELEGRAM_TOON_BOT_TOKEN is required to run the Telegram bot.")
    create_application(settings).run_polling()


if __name__ == "__main__":
    main()
