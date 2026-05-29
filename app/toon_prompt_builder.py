from __future__ import annotations

import json

from app.character_registry import character_registry_text
from app.toon_models import ToonRequest
from app.toon_style_bible import style_bible_text


def build_storyboard_prompt(request: ToonRequest) -> str:
    source_note = (
        f"Official source provided: {request.source_url_optional}"
        if request.source_url_optional
        else "No official source provided. Set source_needed=true and include a caution."
    )
    schema = {
        "toon_package_id": "string",
        "request_id": request.request_id,
        "toon_title": "string",
        "logline": "string",
        "character_setup": "string",
        "absurd_scenario": "string",
        "administrative_problem": "string",
        "procedure_checkpoints": ["string"],
        "caution_or_disclaimer": "string",
        "panel_count": request.panel_count,
        "panels": [
            {
                "panel_number": 1,
                "scene": "string",
                "character_expression": "string",
                "dialogue": "string",
                "caption": "string",
                "legal_or_admin_point": "string",
                "image_prompt": "string",
                "safety_notes": ["string"],
            }
        ],
        "image_prompt_summaries": ["string"],
        "source_needed": request.source_needed,
        "source_limitations": "string",
        "legal_safety_notes": ["string"],
        "review_only": True,
        "instagram_manual_upload_only": True,
        "publish_ready": False,
        "provider_call_metadata_sanitized": True,
    }
    return "\n".join(
        [
            "Return structured JSON only. Do not wrap in Markdown.",
            "Use this modern absurd administrative-law series bible:",
            style_bible_text(),
            "Use these recurring characters consistently:",
            character_registry_text(),
            "Use the user idea as fictional educational framing for administrative-law satire.",
            "Default agency must be 이상현상 행정청 and default department must be 괴현상 허가과 unless user overrides.",
            "Include 백절차 as main explainer, 나민원 as common-sense questioner, and 꼼수요정 only as corrected safety foil when shortcuts arise.",
            "Episode applicants may include fictional miracle workers, monster trainers, dragons, ghosts, aliens, wizards, or time travelers.",
            "Prefer generic/parody phrasing for copyrighted franchises, such as monster training center instead of protected brand names.",
            "Religious, mythic, historical, or fictional characters must be respectful fictional framing.",
            "Do not mock, insult, or degrade protected/religious groups or believers.",
            "Never imply status, religion, miracles, money, influence, or fame bypass administrative procedures.",
            "No legal result guarantees. Do not guarantee permits, licenses, approvals, or outcomes.",
            "No illegal bypass instructions. Do not explain how to evade permits, licenses, taxes, inspections, or enforcement.",
            "Do not invent statutes, cases, precedents, adjudications, or official sources.",
            "Do not claim historical/legal accuracy without an official source.",
            "Do not include direct Instagram posting, publishing, auto-upload, fanout, or approval instructions.",
            "Create a 4-8 panel storyboard matching the requested panel count.",
            "Each panel must include scene, dialogue, caption, admin point, image prompt, and safety notes.",
            "Korean dialogue/captions are allowed, but must be overlaid locally with Pillow, not embedded in generated images.",
            source_note,
            f"Request JSON: {request.model_dump_json()}",
            f"Output schema shape: {json.dumps(schema, ensure_ascii=False)}",
        ]
    )
