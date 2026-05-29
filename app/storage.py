from __future__ import annotations

import json
from pathlib import Path

from app.toon_models import ToonPackage, ToonRequest


def request_dir(output_dir: Path, request_id: str) -> Path:
    path = output_dir / request_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_request(request: ToonRequest, output_dir: Path) -> Path:
    path = request_dir(output_dir, request.request_id) / "request.json"
    path.write_text(request.model_dump_json(indent=2), encoding="utf-8")
    return path


def save_package(package: ToonPackage, output_dir: Path) -> Path:
    path = request_dir(output_dir, package.request_id) / "toon_package.json"
    path.write_text(json.dumps(package.model_dump(mode="json"), ensure_ascii=False, indent=2), encoding="utf-8")
    return path
