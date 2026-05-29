from app.toon_models import ToonRequest


def test_request_model_defaults_review_only_and_not_publish_ready():
    request = ToonRequest(user_id=1, idea="정중한 행정 풍자")

    assert request.review_only is True
    assert request.manual_instagram_upload_only is True
    assert request.publish_ready is False


def test_source_needed_true_when_no_official_source():
    request = ToonRequest(user_id=1, idea="허가 절차를 배우는 만화")

    assert request.source_needed is True
