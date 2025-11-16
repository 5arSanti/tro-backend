from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class VideoFileService:
    def __init__(self, assets_path: Path) -> None:
        self._assets_path: Path = assets_path
        self._video_extensions: set[str] = {".mp4", ".avi", ".mov", ".mkv", ".wmv"}

    def get_assets_path(self) -> Path:
        return self._assets_path

    def find_video_file(self, video_id: str) -> Path:
        video_path = self._assets_path / f"{video_id}.mp4"
        if video_path.exists():
            return video_path

        for ext in (".avi", ".mov", ".mkv", ".wmv"):
            alt_path = self._assets_path / f"{video_id}{ext}"
            if alt_path.exists():
                return alt_path

        logger.error("Video '%s' not found in %s", video_id, self._assets_path)
        raise FileNotFoundError(f"Video {video_id} not found in {self._assets_path}")

    def list_video_files(self) -> list[Path]:
        if not self._assets_path.exists():
            logger.warning("Assets path %s does not exist", self._assets_path)
            return []

        try:
            all_files = list(self._assets_path.glob("*"))
        except Exception:  # pragma: no cover - unexpected filesystem failures
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
