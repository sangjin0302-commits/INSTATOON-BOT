from __future__ import annotations

from app.character_registry import character_prompt_text
from app.toon_style_bible import DEFAULT_DEPARTMENT, DEFAULT_FICTIONAL_AGENCY
from app.toon_models import Panel, ToonPackage


STYLE_SUFFIX = (
    "Square 1:1 Instagram comic panel, clean Korean webtoon style, consistent character design, "
    "modern absurd administrative-law setting, expressive but respectful, blank speech bubble areas, "
    "no text, no embedded Korean letters, Korean dialogue will be overlaid later with Pillow, "
    "no offensive caricature of protected or religious groups, generic parody framing."
)


def image_prompt_for_panel(panel: Panel, character_setup: str) -> str:
    return (
        f"{STYLE_SUFFIX} Fictional agency mood: {DEFAULT_FICTIONAL_AGENCY}, {DEFAULT_DEPARTMENT}. "
        f"Recurring character continuity: {character_prompt_text()}. "
        f"Episode character continuity: {character_setup}. "
        f"Scene: {panel.scene}. Expression: {panel.character_expression}. "
        f"Administrative learning focus: {panel.legal_or_admin_point}."
    )


def generate_image_prompts(package: ToonPackage) -> list[str]:
    return [image_prompt_for_panel(panel, package.character_setup) for panel in package.panels]
