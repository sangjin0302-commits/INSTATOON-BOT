from app.toon_models import ToonRequest
from app.toon_prompt_builder import build_storyboard_prompt


def test_storyboard_prompt_includes_no_guarantee_rule():
    prompt = build_storyboard_prompt(ToonRequest(user_id=1, idea="허가 절차"))

    assert "No legal result guarantees" in prompt
    assert "Do not guarantee permits" in prompt


def test_storyboard_prompt_includes_no_illegal_bypass_rule():
    prompt = build_storyboard_prompt(ToonRequest(user_id=1, idea="허가 절차"))

    assert "No illegal bypass instructions" in prompt
    assert "evade permits" in prompt
