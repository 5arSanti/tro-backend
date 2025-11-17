from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TrainModelSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Train model identifier")
    name: str = Field(..., description="Human readable name for the train model")
    wagon_count: int = Field(..., ge=1, description="Number of wagons in the train")
    capacity_per_wagon: int = Field(..., ge=1, description="Capacity per wagon")
    total_capacity: int = Field(..., ge=1, description="Total passenger capacity")


class StationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Station identifier")
    name: str = Field(..., description="Station name")
    line: str = Field(..., description="Transit line to which the station belongs")
    camera_id: str = Field(..., description="Camera identifier associated with the station")
    travel_time_seconds: int = Field(
        ..., ge=0, description="Average travel time between this station and the next one in seconds"
    )
    supported_trains: list[TrainModelSchema] = Field(
        default_factory=list, description="Train models available for this station"
    )


class DispatchPlanSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    station_id: str = Field(..., description="Target station identifier")
    station_name: str = Field(..., description="Target station name")
    camera_id: str = Field(..., description="Camera linked to the station")
    passenger_count: int = Field(..., ge=0, description="Observed passenger count")
    train_model: TrainModelSchema = Field(..., description="Selected train model")
    trains_required: int = Field(..., ge=0, description="Number of trains to dispatch")
    total_capacity: int = Field(..., ge=0, description="Total passenger capacity provided")
    surplus_capacity: int = Field(
        ..., ge=0, description="Remaining capacity after serving the passenger count"
    )
    status: str = Field(..., description="Dispatch status message")
    estimated_cycle_time_seconds: int = Field(
        ..., ge=0, description="Estimated travel time for the scheduled trains in seconds"
    )
    generated_at: datetime = Field(..., description="Timestamp when the plan was generated")


class StationStatusSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    station: StationSchema = Field(..., description="Station configuration data")
    last_passenger_count: int | None = Field(
        None, ge=0, description="Last observed passenger count"
    )
    last_updated: datetime | None = Field(
        None, description="Timestamp of the latest observation"
    )
    last_dispatch: DispatchPlanSchema | None = Field(
        None, description="Latest dispatch plan generated for the station"
    )


class DispatchRequestSchema(BaseModel):
    station_id: str | None = Field(
        default=None, description="Station identifier; required if camera_id is not provided"
    )
    camera_id: str | None = Field(
        default=None, description="Camera identifier; required if station_id is not provided"
    )
    passenger_count: int = Field(..., ge=0, description="Observed passenger count")
    persist: bool = Field(
        default=True,
        description="Whether the generated dispatch plan should update the real-time station status",
    )

    @model_validator(mode="after")
    def validate_target(self) -> DispatchRequestSchema:
        if not self.station_id and not self.camera_id:
            raise ValueError("Either station_id or camera_id must be provided")
        return self


class TrainModelsResponseSchema(BaseModel):
    trains: list[TrainModelSchema]


class StationsResponseSchema(BaseModel):
    stations: list[StationSchema]


class StationStatusesResponseSchema(BaseModel):
    stations: list[StationStatusSchema]

