from pathlib import Path
from uuid import uuid4

from app.config import Settings
from app.telegram_bot import ToonBotService

ROOT = Path(__file__).resolve().parents[1]


def _app_text() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "app").glob("*.py"))


def test_telegram_command_handlers_do_not_publish():
    text = (ROOT / "app" / "telegram_bot.py").read_text(encoding="utf-8").lower()

    assert "publish(" not in text
    assert "post_to_instagram" not in text
    assert "auto upload" not in text
    assert "fanout" not in text


def test_no_instagram_api_call_exists():
    text = _app_text().lower()

    assert "graph.instagram" not in text
    assert "instagram.com" not in text
    assert "instagrapi" not in text


def test_no_auto_sns_mutation_exists():
    text = _app_text().lower()

    assert "auto-sns" not in text
    assert "autosns" not in text


def test_no_notion_or_drive_mutation_exists():
    text = _app_text().lower()

    assert "notion" not in text
    assert "google drive" not in text
    assert "drive.files" not in text


def test_no_api_keys_printed():
    text = _app_text().lower()

    assert "print(" not in text


def test_raw_provider_payload_not_logged():
    text = _app_text().lower()

    assert "raw_response" in text
    assert "logger.info(raw_response" not in text
    assert "logger.debug(raw_response" not in text
    assert "logger.info(settings.openai_api_key" not in text
    assert "logger.info(self.settings.openai_api_key" not in text


def test_generate_creates_storyboard_only_before_image_render():
    output_dir = Path("outputs") / f"test-{uuid4().hex}"
    service = ToonBotService(Settings(output_dir=output_dir))
    state = service.session(7)
    state.idea = "정중한 허가 절차 풍자"
    state.panel_count = 4

    package = service.generate_storyboard_only(7)

    assert package.panels
    assert state.rendered_paths == []
    assert not list((output_dir / package.request_id).glob("slide_*.png"))
