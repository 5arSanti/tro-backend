from __future__ import annotations

from pathlib import Path

PROJECT_ROOT: Path = Path(__file__).resolve().parents[3]
YOLO_MODEL_PATH: Path = PROJECT_ROOT / "yolo-train-routes-optimization" / "my_model" / "my_model.pt"
VIDEO_ASSETS_PATH: Path = PROJECT_ROOT / "yolo-train-routes-optimization" / "assets"
