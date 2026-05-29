from app.toon_models import ToonRequest
from app.toon_storyboard_generator import FakeTextProvider, generate_storyboard, parse_storyboard_response


def test_storyboard_output_validates_against_schema():
    request = ToonRequest(user_id=1, idea="예수님이 주류 무한 제조 허가를 만들려면?", panel_count=4)
    package = generate_storyboard(request, FakeTextProvider())

    assert package.request_id == request.request_id
    assert package.panel_count == 4
    assert len(package.panels) == 4
    assert package.review_only is True
    assert package.publish_ready is False


def test_parse_storyboard_response_validates_schema():
    request = ToonRequest(user_id=1, idea="허가 절차", panel_count=5)
    raw = FakeTextProvider().generate_json(
        "Request JSON: " + request.model_dump_json() + "\nOutput schema shape: {}"
    )

    assert parse_storyboard_response(raw).panel_count == 5
