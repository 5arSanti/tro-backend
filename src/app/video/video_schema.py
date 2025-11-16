from __future__ import annotations

from typing import Literal

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

