from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping

import cv2
import numpy as np
from ultralytics import YOLO

from src.app.video.interfaces.detection_metrics import DetectionSummary


class DetectionService:
    BBOX_COLORS: list[tuple[int, int, int]] = [
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

    def __init__(self, model: YOLO, confidence_threshold: float) -> None:
        self._model: YOLO = model
        self._confidence_threshold: float = confidence_threshold
        self._labels: Mapping[int, str] = model.names

    def detect_and_draw(self, frame: np.ndarray) -> tuple[np.ndarray, DetectionSummary]:
        results = self._model(frame, verbose=False, conf=self._confidence_threshold)

        detections = results[0].boxes
        label_counts: dict[str, int] = defaultdict(int)

        for i in range(len(detections)):
            xyxy_tensor = detections[i].xyxy.cpu()
            xyxy = xyxy_tensor.numpy().squeeze()
            xmin, ymin, xmax, ymax = xyxy.astype(int)

            class_index = int(detections[i].cls.item())
            classname = self._labels[class_index]
            conf = detections[i].conf.item()

            if conf >= self._confidence_threshold:
                label_counts[classname] += 1
                self._draw_bounding_box(frame, xmin, ymin, xmax, ymax, classname, conf, class_index)

        summary = DetectionSummary(
            total_objects=sum(label_counts.values()),
            person_count=label_counts.get("person", 0),
            label_counts=dict(label_counts),
        )

        return frame, summary

    def _draw_bounding_box(
        self,
        frame: np.ndarray,
        xmin: int,
        ymin: int,
        xmax: int,
        ymax: int,
        classname: str,
        confidence: float,
        class_index: int,
    ) -> None:
        color = self.BBOX_COLORS[class_index % len(self.BBOX_COLORS)]

        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)

        label = f"{classname}: {int(confidence * 100)}%"
        label_size, base_line = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

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
