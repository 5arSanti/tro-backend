import importlib
from pathlib import Path
from typing import Any

from src.app.common.constants import YOLO_MODEL_PATH

YOLOType = Any


class ModelService:
    _model: YOLOType | None = None
    _model_path: Path = YOLO_MODEL_PATH

    def set_model_path(self, model_path: Path) -> None:
        self._model_path = model_path

    def _load_model_class(self) -> Any:
        module = importlib.import_module("ultralytics")
        return module.YOLO

    def get_model(self) -> YOLOType:
        if self._model is None:
            if not self._model_path.exists():
                raise FileNotFoundError(f"Model not found at {self._model_path}")

            yolo_cls = self._load_model_class()
            self._model = yolo_cls(str(self._model_path), task="detect")
        return self._model

    def is_loaded(self) -> bool:
        return self._model is not None

    def reload(self) -> None:
        self._model = None
        if self._model_path.exists():
            yolo_cls = self._load_model_class()
            self._model = yolo_cls(str(self._model_path), task="detect")
