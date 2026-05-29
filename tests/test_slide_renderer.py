from pathlib import Path
from uuid import uuid4

from app.toon_models import ToonRequest
from app.toon_slide_renderer import render_slides
from app.toon_storyboard_generator import sample_package_for_request


def test_slide_renderer_creates_expected_output_filenames():
    output_dir = Path("outputs") / f"test-{uuid4().hex}"
    package = sample_package_for_request(ToonRequest(user_id=1, idea="허가 절차", panel_count=4))

    paths = render_slides(package, output_dir)

    assert [path.name for path in paths] == [
        "slide_01.png",
        "slide_02.png",
        "slide_03.png",
        "slide_04.png",
        "contact_sheet.png",
    ]
    assert all(path.exists() for path in paths)
