from __future__ import annotations

import base64
from pathlib import Path
from typing import Protocol

from PIL import Image, ImageDraw

from app.config import Settings
from app.toon_models import ToonPackage


class ImageProvider(Protocol):
    def generate_image(self, prompt: str, output_path: Path) -> Path: ...


class FakeImageProvider:
    def generate_image(self, prompt: str, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image = Image.new("RGB", (1080, 1080), "#f7f3e8")
        draw = ImageDraw.Draw(image)
        draw.rectangle((60, 60, 1020, 1020), outline="#243043", width=8)
        draw.text((100, 100), "PLACEHOLDER PANEL", fill="#243043")
        draw.text((100, 150), prompt[:120], fill="#243043")
        image.save(output_path)
        return output_path


class OpenAIImageProvider:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def generate_image(self, prompt: str, output_path: Path) -> Path:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is required for live image generation.")
        from openai import OpenAI

        output_path.parent.mkdir(parents=True, exist_ok=True)
        client = OpenAI(api_key=self.api_key)
        response = client.images.generate(model=self.model, prompt=prompt, size="1024x1024")
        image_bytes = base64.b64decode(response.data[0].b64_json)
        output_path.write_bytes(image_bytes)
        return output_path


def generate_panel_image(
    prompt: str,
    output_path: Path,
    settings: Settings,
    provider: ImageProvider | None = None,
) -> Path:
    if not settings.enable_image_generation and provider is None:
        raise RuntimeError("Image generation is disabled by default.")
    return (provider or OpenAIImageProvider(settings.openai_api_key, settings.openai_image_model)).generate_image(
        prompt,
        output_path,
    )


def generate_all_panel_images(
    package: ToonPackage,
    prompts: list[str],
    settings: Settings,
    provider: ImageProvider | None = None,
) -> list[Path]:
    output_dir = settings.output_dir / package.request_id
    return [
        generate_panel_image(prompt, output_dir / f"panel_{index:02}.png", settings, provider)
        for index, prompt in enumerate(prompts, start=1)
    ]
