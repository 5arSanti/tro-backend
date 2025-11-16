from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class VideoInfoSchema(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "video1",
                "filename": "video1.mp4",
                "name": "Video 1",
            }
        }
    )

    id: str = Field(..., description="Unique video identifier")
    filename: str = Field(..., description="Video filename")
    name: str = Field(..., description="Display name for the video")


class VideoListSchema(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "videos": [
                    {"id": "video1", "filename": "video1.mp4", "name": "Video 1"},
                    {"id": "video2", "filename": "video2.mp4", "name": "Video 2"},
                ]
            }
        }
    )

    videos: list[VideoInfoSchema] = Field(..., description="List of available videos")


class DetectionConfigSchema(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "confidence_threshold": 0.5,
                "resolution": "640x480",
            }
        }
    )

    confidence_threshold: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Minimum confidence threshold for detections"
    )
    resolution: str | None = Field(
        default=None, description="Output resolution in format WxH (e.g., '640x480')"
    )


class DetectionMetricsSchema(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "video_id": "video1",
                "timestamp": "2025-11-16T22:15:30.123Z",
                "total_objects": 7,
                "person_count": 5,
                "label_counts": {"person": 5, "backpack": 1, "cell phone": 1},
            }
        }
    )

    video_id: str = Field(..., description="Unique identifier of the video stream")
    timestamp: datetime = Field(..., description="Timestamp of the detection event")
    total_objects: int = Field(..., ge=0, description="Total number of objects detected")
    person_count: int = Field(..., ge=0, description="Number of persons detected")
    label_counts: dict[str, int] = Field(
        default_factory=dict,
        description="Breakdown of detected objects by label",
    )
