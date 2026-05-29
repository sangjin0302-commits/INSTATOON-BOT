from app.character_registry import DEFAULT_CHARACTERS, character_registry_text
from app.toon_image_prompt_generator import image_prompt_for_panel
from app.toon_models import Panel, ToonRequest
from app.toon_prompt_builder import build_storyboard_prompt
from app.toon_storyboard_generator import FakeTextProvider, generate_storyboard
from app.toon_style_bible import DEFAULT_DEPARTMENT, DEFAULT_FICTIONAL_AGENCY, TAGLINE


def test_style_bible_concept_consistency_in_prompt():
    prompt = build_storyboard_prompt(ToonRequest(user_id=1, idea="dragon restaurant permit"))

    assert DEFAULT_FICTIONAL_AGENCY in prompt
    assert DEFAULT_DEPARTMENT in prompt
    assert TAGLINE in prompt
    assert "monster training center" in prompt
    assert "protected brand names" in prompt


def test_character_registry_consistency_in_prompt_and_fake_storyboard():
    request = ToonRequest(user_id=1, idea="alien street vendor permit", panel_count=4)
    prompt = build_storyboard_prompt(request)
    package = generate_storyboard(request, FakeTextProvider())

    for character in DEFAULT_CHARACTERS:
        assert character.name in character_registry_text()
        assert character.name in prompt
        assert character.name in package.character_setup
    assert "백절차" in package.panels[0].dialogue
    assert "나민원" in package.panels[0].dialogue


def test_image_prompt_keeps_korean_text_out_of_generated_image():
    panel = Panel(
        panel_number=1,
        scene="괴현상 허가과 접수창구",
        character_expression="백절차가 피곤하지만 정확하게 설명한다.",
        dialogue="백절차: 절차부터 봅니다.",
        caption="허가 체크포인트",
        legal_or_admin_point="공식 기준 검토 필요",
        image_prompt="",
    )

    prompt = image_prompt_for_panel(panel, "fictional wizard applicant")

    assert DEFAULT_FICTIONAL_AGENCY in prompt
    assert DEFAULT_DEPARTMENT in prompt
    assert "no embedded Korean letters" in prompt
    assert "overlaid later with Pillow" in prompt


def test_source_needed_behavior_without_official_source():
    request = ToonRequest(user_id=1, idea="time traveler building permit")
    package = generate_storyboard(request, FakeTextProvider())

    assert request.source_needed is True
    assert package.source_needed is True


def test_prompt_and_fake_package_keep_no_publishing_behavior():
    request = ToonRequest(user_id=1, idea="ghost landlord registration", panel_count=4)
    prompt = build_storyboard_prompt(request)
    package = generate_storyboard(request, FakeTextProvider())

    assert "auto-upload" in prompt
    assert package.review_only is True
    assert package.instagram_manual_upload_only is True
    assert package.publish_ready is False
