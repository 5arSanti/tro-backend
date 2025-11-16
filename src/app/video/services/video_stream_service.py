from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

import cv2
import numpy as np

from src.app.video.interfaces.detection_metrics import DetectionMetrics, DetectionSummary
from src.app.video.services.detection_service import DetectionService
from src.app.video.services.metrics_service import DetectionMetricsService
from src.app.video.services.model_service import ModelService

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


class VideoStreamService:
    def __init__(
        self,
        model_service: ModelService,
        video_path: Path,
        video_id: str,
        confidence_threshold: float,
        metrics_service: DetectionMetricsService | None = None,
        resolution: tuple[int, int] | None = None,
    ) -> None:
        self._model_service: ModelService = model_service
        self._video_path: Path = video_path
        self._video_id: str = video_id
        self._confidence_threshold: float = confidence_threshold
        self._resolution: tuple[int, int] | None = resolution
        self._cap: cv2.VideoCapture | None = None
        self._metrics_service: DetectionMetricsService | None = metrics_service

    async def stream_frames(self) -> AsyncGenerator[bytes, None]:
        loop = asyncio.get_event_loop()
        self._cap = await loop.run_in_executor(None, self._open_video, str(self._video_path))

        if self._cap is None or not self._cap.isOpened():
            raise RuntimeError(f"Failed to open video: {self._video_path}")

        try:
            model = self._model_service.get_model()

            detection_service = DetectionService(model, self._confidence_threshold)

            while True:
                ret, frame = await loop.run_in_executor(None, self._cap.read)

                if not ret:
                    await loop.run_in_executor(None, self._cap.set, cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = await loop.run_in_executor(None, self._cap.read)
                    if not ret:
                        break

                processed_frame = await self._process_frame(frame, detection_service)

                frame_bytes = await loop.run_in_executor(None, self._encode_frame, processed_frame)

                yield frame_bytes

        finally:
            await self._cleanup()

    def _open_video(self, video_path: str) -> cv2.VideoCapture:
        cap = cv2.VideoCapture(video_path)
        if self._resolution:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._resolution[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._resolution[1])
        return cap

    async def _process_frame(
        self, frame: np.ndarray, detection_service: DetectionService
    ) -> np.ndarray:
        loop = asyncio.get_event_loop()

        if self._resolution:
            resized_frame = await loop.run_in_executor(
                None, lambda: cv2.resize(frame, self._resolution)
            )
            frame = resized_frame

        processed_frame, summary = await loop.run_in_executor(
            None, detection_service.detect_and_draw, frame.copy()
        )

        await self._publish_metrics(summary)

        return processed_frame

    def _encode_frame(self, frame: np.ndarray) -> bytes:
        _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return buffer.tobytes()

    async def _cleanup(self) -> None:
        if self._cap is not None:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._cap.release)
            self._cap = None

    async def _publish_metrics(self, summary: DetectionSummary) -> None:
        if self._metrics_service is None:
            return

        metrics = DetectionMetrics.from_summary(
            video_id=self._video_id,
            summary=summary,
            timestamp=datetime.now(timezone.utc),
        )

        await self._metrics_service.publish(metrics)
