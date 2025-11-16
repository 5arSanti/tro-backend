from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


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

        for ext in [".avi", ".mov", ".mkv", ".wmv"]:
            alt_path = self._assets_path / f"{video_id}{ext}"
            if alt_path.exists():
                return alt_path

        raise FileNotFoundError(f"Video {video_id} not found in {self._assets_path}")

    def list_video_files(self) -> list[Path]:
        if not self._assets_path.exists():
            return []

        video_files: list[Path] = []
        for video_file in sorted(self._assets_path.glob("*")):
            if video_file.suffix.lower() in self._video_extensions and video_file.is_file():
                video_files.append(video_file)

        return video_files

    def get_video_id(self, video_path: Path) -> str:
        return video_path.stem
