from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import cv2
from ultralytics import YOLO

from src.app.core.config import Settings
from src.app.video.video_schema import DetectionConfigSchema, VideoInfoSchema, VideoListSchema

if TYPE_CHECKING:
    from collections.abc import Generator


class VideoService:
    def __init__(self, settings: Settings) -> None:
        self._settings: Settings = settings
        self._model: YOLO | None = None
        project_root = Path(__file__).parent.parent.parent.parent.parent
        self._model_path: Path = (
            project_root / "yolo-train-routes-optimization" / "my_model" / "my_model.pt"
        )
        self._assets_path: Path = project_root / "yolo-train-routes-optimization" / "assets"

    def _load_model(self) -> YOLO:
        """Load YOLO model if not already loaded."""
        if self._model is None:
            if not self._model_path.exists():
                raise FileNotFoundError(f"Model not found at {self._model_path}")
            self._model = YOLO(str(self._model_path), task="detect")
        return self._model

    def get_available_videos(self) -> VideoListSchema:
        if not self._assets_path.exists():
            return VideoListSchema(videos=[])

        video_extensions = {".mp4", ".avi", ".mov", ".mkv", ".wmv"}
        videos: list[VideoInfoSchema] = []

        for video_file in sorted(self._assets_path.glob("*")):
            if video_file.suffix.lower() in video_extensions and video_file.is_file():
                video_id = video_file.stem
                videos.append(
                    VideoInfoSchema(
                        id=video_id,
                        filename=video_file.name,
                        name=f"Video {video_id.replace('video', '')}",
                    )
                )

        return VideoListSchema(videos=videos)

    def process_video_stream(
        self, video_id: str, config: DetectionConfigSchema
    ) -> Generator[bytes, None, None]:
        """Process video with YOLO model and yield frames as JPEG bytes."""
        video_path = self._assets_path / f"{video_id}.mp4"

        if not video_path.exists():
            # Try other extensions
            for ext in [".avi", ".mov", ".mkv", ".wmv"]:
                alt_path = self._assets_path / f"{video_id}{ext}"
                if alt_path.exists():
                    video_path = alt_path
                    break
            else:
                raise FileNotFoundError(f"Video {video_id} not found")

        # Load model
        model = self._load_model()

        # Parse resolution if provided
        width, height = None, None
        if config.resolution:
            try:
                width, height = map(int, config.resolution.split("x"))
            except ValueError:
                pass

        # Open video
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            raise RuntimeError(f"Failed to open video: {video_path}")

        try:
            # Set resolution if specified
            if width and height:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

            # Bounding box colors (Tableau 10 color scheme)
            bbox_colors = [
                (164, 120, 87),
                (68, 148, 228),
                (93, 97, 209),
                (178, 182, 133),
                (88, 159, 106),
                (96, 202, 231),
                (159, 124, 168),
                (169, 162, 241),
                (98, 118, 150),
                (172, 176, 184),
            ]

            while True:
                ret, frame = cap.read()
                if not ret:
                    # Loop video by seeking to start
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = cap.read()
                    if not ret:
                        break

                # Resize if needed
                if width and height:
                    frame = cv2.resize(frame, (width, height))

                # Run inference
                results = model(frame, verbose=False, conf=config.confidence_threshold)

                # Draw detections
                detections = results[0].boxes
                labels = model.names

                for i in range(len(detections)):
                    # Get bounding box coordinates
                    xyxy_tensor = detections[i].xyxy.cpu()
                    xyxy = xyxy_tensor.numpy().squeeze()
                    xmin, ymin, xmax, ymax = xyxy.astype(int)

                    # Get class and confidence
                    classidx = int(detections[i].cls.item())
                    classname = labels[classidx]
                    conf = detections[i].conf.item()

                    if conf >= config.confidence_threshold:
                        color = bbox_colors[classidx % len(bbox_colors)]
                        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)

                        label = f"{classname}: {int(conf * 100)}%"
                        label_size, base_line = cv2.getTextSize(
                            label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
                        )
                        label_ymin = max(ymin, label_size[1] + 10)
                        cv2.rectangle(
                            frame,
                            (xmin, label_ymin - label_size[1] - 10),
                            (xmin + label_size[0], label_ymin + base_line - 10),
                            color,
                            cv2.FILLED,
                        )
                        cv2.putText(
                            frame,
                            label,
                            (xmin, label_ymin - 7),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0, 0, 0),
                            1,
                        )

                # Encode frame as JPEG
                _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                frame_bytes = buffer.tobytes()

                yield frame_bytes

        finally:
            cap.release()

