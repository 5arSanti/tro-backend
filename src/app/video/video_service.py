import logging
import os
from collections.abc import AsyncGenerator

from src.app.common.constants import VIDEO_ASSETS_PATH, YOLO_MODEL_PATH
from src.app.video.services.metrics_service import DetectionMetricsService
from src.app.video.services.model_service import ModelService
from src.app.video.services.video_file_service import VideoFileService
from src.app.video.services.video_stream_service import VideoSource, VideoStreamService
from src.app.video.video_schema import (
    DetectionConfigSchema,
    DetectionMetricsSchema,
    VideoInfoSchema,
    VideoListSchema,
)

logger = logging.getLogger(__name__)


class VideoService:
    USB_CAMERA_ID_ENV = "USB_CAMERA_ID"
    USB_CAMERA_SOURCE_ENV = "USB_CAMERA_SOURCE"
    USB_CAMERA_NAME_ENV = "USB_CAMERA_NAME"

    DEFAULT_USB_CAMERA_ID = "usb1"
    DEFAULT_USB_CAMERA_SOURCE = "usb1"
    DEFAULT_USB_CAMERA_NAME = "Cámara USB en Vivo"

    def __init__(self) -> None:
        self._model_path = YOLO_MODEL_PATH
        self._assets_path = VIDEO_ASSETS_PATH

        self._video_file_service = VideoFileService(self._assets_path)
        self._model_service: ModelService | None = None
        self._metrics_service: DetectionMetricsService = DetectionMetricsService()

        self._usb_camera_id: str = os.environ.get(
            self.USB_CAMERA_ID_ENV, self.DEFAULT_USB_CAMERA_ID
        )
        raw_usb_source = os.environ.get(self.USB_CAMERA_SOURCE_ENV, self.DEFAULT_USB_CAMERA_SOURCE)
        self._usb_camera_name: str = os.environ.get(
            self.USB_CAMERA_NAME_ENV, self.DEFAULT_USB_CAMERA_NAME
        )
        self._usb_camera_source_label: str = raw_usb_source
        self._usb_camera_source: VideoSource = self._parse_usb_source(raw_usb_source)

    def _get_model_service(self) -> ModelService:
        if self._model_service is None:
            service = ModelService()
            service.set_model_path(self._model_path)
            self._model_service = service
        return self._model_service

    def get_available_videos(self) -> VideoListSchema:
        try:
            video_files = self._video_file_service.list_video_files()
        except Exception:
            logger.exception("Failed to list video files from %s", self._assets_path)
            raise

        videos: list[VideoInfoSchema] = [
            VideoInfoSchema(
                id=self._usb_camera_id,
                filename=self._usb_camera_source_label,
                name=self._usb_camera_name,
            )
        ]
        for video_file in video_files:
            video_id = self._video_file_service.get_video_id(video_file)
            if video_id == self._usb_camera_id:
                # Avoid duplicating the virtual USB stream if a file shares the same identifier.
                continue
            videos.append(
                VideoInfoSchema(
                    id=video_id,
                    filename=video_file.name,
                    name=f"Video {video_id.replace('video', '')}",
                )
            )

        return VideoListSchema(videos=videos)

    async def process_video_stream(
        self, video_id: str, config: DetectionConfigSchema
    ) -> AsyncGenerator[bytes, None]:
        is_live_source = False
        if self._is_usb_camera(video_id):
            video_source = self._usb_camera_source
            is_live_source = True
        else:
            video_source = self._video_file_service.find_video_file(video_id)

        resolution: tuple[int, int] | None = None
        if config.resolution:
            try:
                width, height = map(int, config.resolution.split("x"))
                resolution = (width, height)
            except ValueError:
                logger.warning(
                    "Invalid resolution '%s'. Using original video dimensions.", config.resolution
                )

        stream_service = VideoStreamService(
            model_service=self._get_model_service(),
            video_source=video_source,
            video_id=video_id,
            confidence_threshold=config.confidence_threshold,
            metrics_service=self._metrics_service,
            resolution=resolution,
            is_live_source=is_live_source,
        )

        async for frame_bytes in stream_service.stream_frames():
            yield frame_bytes

    async def subscribe_detection_metrics(
        self, video_id: str
    ) -> AsyncGenerator[DetectionMetricsSchema, None]:
        async for metrics in self._metrics_service.subscribe(video_id):
            yield DetectionMetricsSchema(
                video_id=metrics.video_id,
                timestamp=metrics.timestamp,
                total_objects=metrics.total_objects,
                person_count=metrics.person_count,
                label_counts=dict[str, int](metrics.label_counts),
            )

    def _is_usb_camera(self, video_id: str) -> bool:
        return video_id == self._usb_camera_id

    def _parse_usb_source(self, raw_source: str) -> VideoSource:
        source = raw_source.strip()
        lower_source = source.lower()

        if lower_source.startswith("usb"):
            index_part = source[3:]
            if index_part.isdigit():
                return int(index_part)
            logger.warning("Invalid USB index '%s'. Falling back to index 0.", source)
            return 0

        if source.isdigit():
            return int(source)

        # Allow passing custom strings (e.g., RTSP urls or device paths)
        return source
