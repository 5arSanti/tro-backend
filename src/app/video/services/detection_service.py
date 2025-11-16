from __future__ import annotations

from typing import TYPE_CHECKING

import cv2
import numpy as np
from ultralytics import YOLO

if TYPE_CHECKING:
    pass


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
        self._labels: dict[int, str] = model.names

    def detect_and_draw(self, frame: np.ndarray) -> np.ndarray:
        results = self._model(frame, verbose=False, conf=self._confidence_threshold)

        detections = results[0].boxes

        for i in range(len(detections)):
            xyxy_tensor = detections[i].xyxy.cpu()
            xyxy = xyxy_tensor.numpy().squeeze()
            xmin, ymin, xmax, ymax = xyxy.astype(int)

            classidx = int(detections[i].cls.item())
            classname = self._labels[classidx]
            conf = detections[i].conf.item()

            if conf >= self._confidence_threshold:
                self._draw_bounding_box(frame, xmin, ymin, xmax, ymax, classname, conf, classidx)

        return frame

    def _draw_bounding_box(
        self,
        frame: np.ndarray,
        xmin: int,
        ymin: int,
        xmax: int,
        ymax: int,
        classname: str,
        confidence: float,
        classidx: int,
    ) -> None:
        color = self.BBOX_COLORS[classidx % len(self.BBOX_COLORS)]

        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)

        label = f"{classname}: {int(confidence * 100)}%"
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

