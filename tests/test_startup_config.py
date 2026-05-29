import pytest

from app.main import main


def test_main_fails_clearly_without_telegram_token(monkeypatch):
    monkeypatch.delenv("TELEGRAM_TOON_BOT_TOKEN", raising=False)

    with pytest.raises(RuntimeError, match="TELEGRAM_TOON_BOT_TOKEN is required"):
        main()
