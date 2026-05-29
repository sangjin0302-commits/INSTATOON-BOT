from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.toon_models import ToonPackage


SLIDE_SIZE = 1080


def _font(size: int) -> ImageFont.ImageFont:
    for name in ("malgun.ttf", "NanumGothic.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _draw_wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font: ImageFont.ImageFont, width: int) -> None:
    line_height = max(28, int(getattr(font, "size", 24) * 1.35))
    y = xy[1]
    for raw_line in text.splitlines():
        for line in textwrap.wrap(raw_line, width=width) or [""]:
            draw.text((xy[0], y), line, fill="#16202a", font=font)
            y += line_height


def render_slides(
    package: ToonPackage,
    output_dir: Path,
    panel_image_paths: list[Path] | None = None,
    create_contact_sheet: bool = True,
) -> list[Path]:
    target_dir = output_dir / package.request_id
    target_dir.mkdir(parents=True, exist_ok=True)
    title_font = _font(42)
    body_font = _font(30)
    small_font = _font(24)
    slide_paths: list[Path] = []

    for index, panel in enumerate(package.panels):
        background_path = panel_image_paths[index] if panel_image_paths and index < len(panel_image_paths) else None
        if background_path and background_path.exists():
            slide = Image.open(background_path).convert("RGB").resize((SLIDE_SIZE, SLIDE_SIZE))
        else:
            slide = Image.new("RGB", (SLIDE_SIZE, SLIDE_SIZE), "#f6efe2")
        draw = ImageDraw.Draw(slide)
        draw.rectangle((0, 0, SLIDE_SIZE, 112), fill="#203846")
        draw.text((42, 32), f"{panel.panel_number}. {package.toon_title}", fill="#ffffff", font=title_font)
        draw.rounded_rectangle((48, 690, 1032, 848), radius=28, fill="#ffffff", outline="#203846", width=4)
        draw.rounded_rectangle((48, 866, 1032, 1028), radius=18, fill="#e7f0ed", outline="#51766f", width=3)
        _draw_wrapped(draw, (84, 718), panel.dialogue, body_font, 34)
        _draw_wrapped(draw, (84, 886), f"{panel.caption}\n행정 포인트: {panel.legal_or_admin_point}", small_font, 42)
        path = target_dir / f"slide_{panel.panel_number:02}.png"
        slide.save(path)
        slide_paths.append(path)

    if create_contact_sheet:
        thumbs = [Image.open(path).resize((270, 270)) for path in slide_paths]
        sheet = Image.new("RGB", (1080, 540 if len(thumbs) <= 4 else 810), "#ffffff")
        for i, thumb in enumerate(thumbs):
            sheet.paste(thumb, ((i % 4) * 270, (i // 4) * 270))
        sheet_path = target_dir / "contact_sheet.png"
        sheet.save(sheet_path)
        slide_paths.append(sheet_path)
    return slide_paths
