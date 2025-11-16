"""Main video service that coordinates other services."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from src.app.common.constants import PROJECT_ROOT, VIDEO_ASSETS_PATH, YOLO_MODEL_PATH
from src.app.core.config import Settings

# from src.app.video.services.model_service import ModelService
from src.app.video.services.video_file_service import VideoFileService

# from src.app.video.services.video_stream_service import VideoStreamService
from src.app.video.video_schema import DetectionConfigSchema, VideoInfoSchema, VideoListSchema

logger = logging.getLogger(__name__)


class VideoService:
    def __init__(self, settings: Settings) -> None:
        self._settings: Settings = settings

        self._project_root = PROJECT_ROOT
        self._model_path = YOLO_MODEL_PATH
        self._assets_path = VIDEO_ASSETS_PATH

        self._video_file_service: VideoFileService = VideoFileService(self._assets_path)
        # self._model_service: ModelService = ModelService()

    def get_available_videos(self) -> VideoListSchema:
        try:
            video_files = self._video_file_service.list_video_files()
        except Exception:
            logger.exception("Failed to list video files from %s", self._assets_path)
            raise

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

    # async def process_video_stream(
    #     self, video_id: str, config: DetectionConfigSchema
    # ) -> AsyncGenerator[bytes, None]:
    #     video_path = self._video_file_service.find_video_file(video_id)

    #     resolution: tuple[int, int] | None = None
    #     if config.resolution:
    #         try:
    #             width, height = map(int, config.resolution.split("x"))
    #             resolution = (width, height)
    #         except ValueError:
    #             logger.warning("Invalid resolution '%s'. Using original video dimensions.", config.resolution)

    #     stream_service = VideoStreamService(
    #         model_service=self._model_service,
    #         video_path=video_path,
    #         confidence_threshold=config.confidence_threshold,
    #         resolution=resolution,
    #     )

    #     async for frame_bytes in stream_service.stream_frames():
    #         yield frame_bytes
