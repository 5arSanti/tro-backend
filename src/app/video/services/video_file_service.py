from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from src.app.common.constants import VIDEO_ASSETS_PATH

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class VideoFileService:
    def __init__(self, assets_path: Path | None = None) -> None:
        self._assets_path: Path = assets_path or VIDEO_ASSETS_PATH
        self._video_extensions: set[str] = {".mp4", ".avi", ".mov", ".mkv", ".wmv"}

    def list_video_files(self) -> list[Path]:
        if not self._assets_path.exists():
            logger.warning("Assets path %s does not exist", self._assets_path)
            return []

        try:
            all_files = list[Path](self._assets_path.glob("*"))
        except Exception:
            logger.exception("Failed to read assets directory %s", self._assets_path)
            raise

        video_files = [
            file_path
            for file_path in all_files
            if file_path.is_file() and file_path.suffix.lower() in self._video_extensions
        ]
        video_files.sort(key=lambda path: path.name)
        return video_files

    def get_video_id(self, video_path: Path) -> str:
        return video_path.stem
