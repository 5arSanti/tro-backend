from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthCheckSchema(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"status": "healthy", "version": "0.1.0", "environment": "development"}
        }
    )

    status: Literal["healthy", "unhealthy"] = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Current environment")


class ErrorSchema(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"error": "ValidationError", "message": "Invalid input", "status_code": 400}
        }
    )

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")


NormalizationLevelType = Literal["normalizacion_alta", "normalizacion_baja"]