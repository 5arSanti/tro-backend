from __future__ import annotations

from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parents[4]
BACKEND_ROOT: Path = REPO_ROOT / "tro-backend"
YOLO_MODEL_PATH: Path = REPO_ROOT / "yolo-train-routes-optimization" / "my_model" / "my_model.pt"
VIDEO_ASSETS_PATH: Path = BACKEND_ROOT / "src" / "app" / "assets"
