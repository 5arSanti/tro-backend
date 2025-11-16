from datetime import datetime
from collections.abc import Mapping

from src.app.video.video_schema import DetectionMetricsSchema
from typing import Any
from dataclasses import dataclass, field


@dataclass(slots=True)
class DetectionSummary:
    total_objects: int
    person_count: int
    label_counts: Mapping[str, int]


@dataclass(slots=True)
class DetectionMetrics:
    video_id: str
    timestamp: datetime
    total_objects: int
    person_count: int
    label_counts: Mapping[str, int] = field(default_factory=dict)

    @classmethod
    def from_summary(
        cls,
        video_id: str,
        summary: DetectionSummary,
        *,
        timestamp: datetime | None = None,
    ) -> DetectionMetricsSchema:
        metrics_timestamp = timestamp or datetime.now(datetime.UTC)
        return cls(
            video_id=video_id,
            timestamp=metrics_timestamp,
            total_objects=summary.total_objects,
            person_count=summary.person_count,
            label_counts=dict[str, int](summary.label_counts),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "video_id": self.video_id,
            "timestamp": self.timestamp,
            "total_objects": self.total_objects,
            "person_count": self.person_count,
            "label_counts": dict[str, int](self.label_counts),
        }
