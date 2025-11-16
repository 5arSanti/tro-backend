from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - import only for type checking
    from ultralytics import YOLO


class ModelService:
    _instance: ModelService | None = None
    _model: "YOLO" | None = None
    _model_path: Path | None = None

    def __new__(cls) -> ModelService:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def set_model_path(self, model_path: Path) -> None:
        self._model_path = model_path

    def get_model(self) -> "YOLO":
        if self._model is None:
            if self._model_path is None:
                raise RuntimeError("Model service not initialized. Call set_model_path() first.")
            if not self._model_path.exists():
                raise FileNotFoundError(f"Model not found at {self._model_path}")

            from ultralytics import YOLO  # Imported lazily to avoid heavy import at startup

            self._model = YOLO(str(self._model_path), task="detect")
        return self._model

    def is_loaded(self) -> bool:
        return self._model is not None

    def reload(self) -> None:
        self._model = None
        if self._model_path is not None:
            from ultralytics import YOLO  # Imported lazily to avoid heavy import at startup

            self._model = YOLO(str(self._model_path), task="detect")
