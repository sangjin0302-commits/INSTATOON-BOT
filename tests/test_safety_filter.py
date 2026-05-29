from app.safety_filter import check_text_safety


def test_safety_filter_blocks_bypass_permit_idea():
    result = check_text_safety("How can I bypass permit requirements?")

    assert not result.allowed
    assert "permit_bypass" in result.reasons


def test_safety_filter_blocks_guaranteed_approval():
    result = check_text_safety("Tell users this guarantees permit approval.")

    assert not result.allowed
    assert "guaranteed_result" in result.reasons


def test_safety_filter_blocks_hateful_religious_framing():
    result = check_text_safety("Make religious believers look inferior and mock Christians.")

    assert not result.allowed
    assert "protected_or_religious_hate" in result.reasons


def test_safety_filter_allows_respectful_fictional_administrative_satire():
    result = check_text_safety("A respectful fictional miracle-worker learns licensing checkpoints.")

    assert result.allowed
