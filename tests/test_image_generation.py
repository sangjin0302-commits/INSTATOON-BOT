from pathlib import Path
from uuid import uuid4

import pytest

from app.config import Settings
from app.toon_image_generator import FakeImageProvider, generate_panel_image
from app.toon_image_prompt_generator import image_prompt_for_panel
from app.toon_models import Panel


def _test_dir() -> Path:
    path = Path("outputs") / f"test-{uuid4().hex}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_image_prompt_avoids_embedded_korean_text_requirement():
    panel = Panel(
        panel_number=1,
        scene="민원실",
        character_expression="당황",
        dialogue="안녕하세요",
        caption="절차 확인",
        legal_or_admin_point="공식 기준 확인",
        image_prompt="",
    )

    prompt = image_prompt_for_panel(panel, "fictional respectful character")

    assert "no text" in prompt
    assert "no embedded Korean letters" in prompt


def test_image_generation_disabled_by_default():
    output_dir = _test_dir()
    settings = Settings(output_dir=output_dir)

    with pytest.raises(RuntimeError, match="disabled"):
        generate_panel_image("prompt", output_dir / "panel.png", settings)


def test_fake_image_provider_works():
    output_dir = _test_dir()
    settings = Settings(output_dir=output_dir)
    path = generate_panel_image("prompt", output_dir / "panel.png", settings, FakeImageProvider())

    assert path.exists()
    assert path.name == "panel.png"
