from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class ToonRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(default_factory=lambda: uuid4().hex)
    user_id: int
    idea: str
    administrative_topic: str | None = None
    character_setup: str | None = None
    tone: str = "괴짜 행정툰"
    panel_count: int = 6
    source_url_optional: HttpUrl | None = None
    official_source_attached: bool = False
    source_needed: bool = True
    output_language: str = "ko"
    manual_instagram_upload_only: bool = True
    review_only: bool = True
    publish_ready: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("panel_count")
    @classmethod
    def panel_count_range(cls, value: int) -> int:
        if value < 4 or value > 8:
            raise ValueError("panel_count must be between 4 and 8")
        return value

    @field_validator("source_needed", mode="before")
    @classmethod
    def infer_source_needed(cls, value: Any, info: Any) -> bool:
        source_url = info.data.get("source_url_optional") if info.data else None
        attached = info.data.get("official_source_attached", False) if info.data else False
        return bool(value) if value is not None else not bool(source_url or attached)

    def model_post_init(self, __context: Any) -> None:
        if self.source_url_optional or self.official_source_attached:
            object.__setattr__(self, "source_needed", False)


class Panel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    panel_number: int
    scene: str
    character_expression: str
    dialogue: str
    caption: str
    legal_or_admin_point: str
    image_prompt: str
    safety_notes: list[str] = Field(default_factory=list)


class ToonPackage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    toon_package_id: str = Field(default_factory=lambda: uuid4().hex)
    request_id: str
    toon_title: str
    logline: str
    character_setup: str
    absurd_scenario: str
    administrative_problem: str
    procedure_checkpoints: list[str]
    caution_or_disclaimer: str
    panel_count: int
    panels: list[Panel]
    image_prompt_summaries: list[str]
    source_needed: bool
    source_limitations: str
    legal_safety_notes: list[str]
    review_only: bool = True
    instagram_manual_upload_only: bool = True
    publish_ready: bool = False
    provider_call_metadata_sanitized: bool = True

    @field_validator("panel_count")
    @classmethod
    def panel_count_range(cls, value: int) -> int:
        if value < 4 or value > 8:
            raise ValueError("panel_count must be between 4 and 8")
        return value

    def model_post_init(self, __context: Any) -> None:
        if len(self.panels) != self.panel_count:
            raise ValueError("panel_count must match panels length")
        if any(panel.panel_number != index + 1 for index, panel in enumerate(self.panels)):
            raise ValueError("panel numbers must be sequential starting at 1")
