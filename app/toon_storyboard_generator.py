from __future__ import annotations

import json
import re
from typing import Protocol

from app.character_registry import character_registry_text
from app.safety_filter import assert_safe_or_raise, check_text_safety
from app.toon_models import ToonPackage, ToonRequest
from app.toon_prompt_builder import build_storyboard_prompt
from app.toon_style_bible import DEFAULT_DEPARTMENT, DEFAULT_FICTIONAL_AGENCY, TAGLINE


class TextProvider(Protocol):
    def generate_json(self, prompt: str) -> str: ...


class FakeTextProvider:
    def generate_json(self, prompt: str) -> str:
        request_data = json.loads(prompt.split("Request JSON: ", 1)[1].split("\n", 1)[0])
        request_id = request_data["request_id"]
        panel_count = request_data["panel_count"]
        panels = [
            {
                "panel_number": i,
                "scene": f"{DEFAULT_FICTIONAL_AGENCY} {DEFAULT_DEPARTMENT} 상담창구 장면 {i}",
                "character_expression": "백절차는 피곤하지만 정확하고, 나민원은 궁금해하며 메모한다.",
                "dialogue": "백절차: 기적이어도 절차표부터 봅니다. 나민원: 몬스터 훈련장도요?",
                "caption": f"{i}단계: 이상한 설정을 실제 행정 체크포인트로 번역한다.",
                "legal_or_admin_point": "허가 가능성은 사실관계와 공식 기준 검토가 필요하다.",
                "image_prompt": (
                    "Square comic panel, Weird Phenomena Permit Office, Baek Jeolcha, "
                    "Na Minwon, respectful fictional applicant, no text."
                ),
                "safety_notes": ["fictional framing", "no guaranteed approval"],
            }
            for i in range(1, panel_count + 1)
        ]
        return json.dumps(
            {
                "request_id": request_id,
                "toon_title": "이상현상 행정청: 기적도 접수번호가 필요합니다",
                "logline": TAGLINE,
                "character_setup": character_registry_text(),
                "absurd_scenario": "기적, 마법, 몬스터 같은 허구 설정을 행정 절차 교육용으로 다룬다.",
                "administrative_problem": "관할, 허가 유형, 시설, 표시, 세무, 안전 기준 확인",
                "procedure_checkpoints": ["관할 기관 확인", "허가 유형 분류", "시설 기준", "표시와 세무", "안전 점검"],
                "caution_or_disclaimer": "요건은 사안과 관할에 따라 달라 공식 출처 검토가 필요합니다.",
                "panel_count": panel_count,
                "panels": panels,
                "image_prompt_summaries": ["respectful Weird Phenomena Permit Office panel"] * panel_count,
                "source_needed": True,
                "source_limitations": "No official source was attached.",
                "legal_safety_notes": ["No guarantee", "No evasion", "No invented legal authority"],
                "review_only": True,
                "instagram_manual_upload_only": True,
                "publish_ready": False,
                "provider_call_metadata_sanitized": True,
            },
            ensure_ascii=False,
        )


class OpenAITextProvider:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def generate_json(self, prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is required for live text generation.")
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        response = client.responses.create(
            model=self.model,
            input=prompt,
            text={"format": {"type": "json_object"}},
        )
        return response.output_text


def parse_storyboard_response(raw_response: str) -> ToonPackage:
    cleaned = raw_response.strip()
    fence_match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", cleaned, flags=re.DOTALL)
    if fence_match:
        cleaned = fence_match.group(1).strip()
    data = json.loads(cleaned)
    return ToonPackage.model_validate(data)


def validate_toon_package(package: ToonPackage) -> ToonPackage:
    if not package.review_only or package.publish_ready:
        raise ValueError("Toon package must remain review-only and not publish-ready.")
    for panel in package.panels:
        safety = check_text_safety(" ".join([panel.scene, panel.dialogue, panel.caption]))
        if not safety.allowed:
            raise ValueError(f"Unsafe panel {panel.panel_number}: {safety.reasons}")
    return package


def generate_storyboard(request: ToonRequest, provider: TextProvider | None = None) -> ToonPackage:
    assert_safe_or_raise(request.idea)
    prompt = build_storyboard_prompt(request)
    raw_response = (provider or FakeTextProvider()).generate_json(prompt)
    package = parse_storyboard_response(raw_response)
    return validate_toon_package(package)


def sample_package_for_request(request: ToonRequest) -> ToonPackage:
    return generate_storyboard(request, FakeTextProvider())
