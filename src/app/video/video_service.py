"""Main video service that coordinates other services."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from src.app.core.config import Settings
from src.app.video.services.model_service import ModelService
from src.app.video.services.video_file_service import VideoFileService
from src.app.video.services.video_stream_service import VideoStreamService
from src.app.video.video_schema import DetectionConfigSchema, VideoInfoSchema, VideoListSchema

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

logger = logging.getLogger(__name__)


class VideoService:
    def __init__(self, settings: Settings) -> None:
        self._settings: Settings = settings

        project_root = Path(__file__).parent.parent.parent.parent.parent
        model_path = project_root / "yolo-train-routes-optimization" / "my_model" / "my_model.pt"
        assets_path = project_root / "yolo-train-routes-optimization" / "assets"

        self._model_service: ModelService = ModelService()
        try:
            self._model_service.initialize(model_path)
        except Exception as e:
            logger.warning(f"Model service initialization failed: {e}")

        self._video_file_service: VideoFileService = VideoFileService(assets_path)

    def get_available_videos(self) -> VideoListSchema:
        try:
            video_files = self._video_file_service.list_video_files()

            videos: list[VideoInfoSchema] = []
            for video_file in video_files:
                video_id = self._video_file_service.get_video_id(video_file)
                videos.append(
                    VideoInfoSchema(
                        id=video_id,
                        filename=video_file.name,
                        name=f"Video {video_id.replace('video', '')}",
                    )
                )

            return VideoListSchema(videos=videos)
        except Exception:
            return VideoListSchema(videos=[])

    async def process_video_stream(
        self, video_id: str, config: DetectionConfigSchema
    ) -> AsyncGenerator[bytes, None]:
        video_path = self._video_file_service.find_video_file(video_id)

        resolution: tuple[int, int] | None = None
        if config.resolution:
            try:
                width, height = map(int, config.resolution.split("x"))
                resolution = (width, height)
            except ValueError:
                pass

        stream_service = VideoStreamService(
            model_service=self._model_service,
            video_path=video_path,
            confidence_threshold=config.confidence_threshold,
            resolution=resolution,
        )

        async for frame_bytes in stream_service.stream_frames():
            yield frame_bytes
