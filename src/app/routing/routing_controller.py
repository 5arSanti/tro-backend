from fastapi import HTTPException

from src.app.core.router import Controller
from src.app.routing.routing_schema import (
    DispatchPlanSchema,
    DispatchRequestSchema,
    StationSchema,
    StationsResponseSchema,
    StationStatusesResponseSchema,
    StationStatusSchema,
    TrainModelSchema,
    TrainModelsResponseSchema,
)
from src.app.routing.services.train_dispatch_service import train_dispatch_service

router = Controller("/routing", tags=["Routing"])


def _station_to_schema(station) -> StationSchema:
    supported_trains = [
        TrainModelSchema.model_validate(train)
        for train in train_dispatch_service.get_supported_train_models(station)
    ]
    payload = {
        **station.__dict__,
        "supported_trains": supported_trains,
    }
    return StationSchema.model_validate(payload)


def _dispatch_to_schema(plan) -> DispatchPlanSchema:
    payload = {
        **plan.__dict__,
        "train_model": TrainModelSchema.model_validate(plan.train_model),
    }
    return DispatchPlanSchema.model_validate(payload)


@router.get(
    "/trains",
    response_model=TrainModelsResponseSchema,
    summary="List available train models",
)
def list_train_models() -> TrainModelsResponseSchema:
    trains = [
        TrainModelSchema.model_validate(train)
        for train in train_dispatch_service.list_train_models()
    ]
    return TrainModelsResponseSchema(trains=trains)


@router.get(
    "/stations",
    response_model=StationsResponseSchema,
    summary="List configured stations",
)
def list_stations() -> StationsResponseSchema:
    stations = [_station_to_schema(station) for station in train_dispatch_service.list_stations()]
    return StationsResponseSchema(stations=stations)


@router.get(
    "/stations/status",
    response_model=StationStatusesResponseSchema,
    summary="Retrieve the latest status for all stations",
)
def list_station_statuses() -> StationStatusesResponseSchema:
    statuses = []
    for state in train_dispatch_service.list_station_states():
        station_schema = _station_to_schema(state.station)
        dispatch_schema = _dispatch_to_schema(state.last_dispatch) if state.last_dispatch else None
        statuses.append(
            StationStatusSchema(
                station=station_schema,
                last_passenger_count=state.last_passenger_count,
                last_updated=state.last_updated,
                last_dispatch=dispatch_schema,
            )
        )
    return StationStatusesResponseSchema(stations=statuses)


@router.get(
    "/stations/{station_id}",
    response_model=StationSchema,
    summary="Get a specific station by ID",
)
def get_station(station_id: str) -> StationSchema:
    station = train_dispatch_service.get_station(station_id)
    if station is None:
        raise HTTPException(status_code=404, detail=f"Station '{station_id}' not found")
    return _station_to_schema(station)


@router.get(
    "/stations/{station_id}/status",
    response_model=StationStatusSchema,
    summary="Get the status of a specific station",
)
def get_station_status(station_id: str) -> StationStatusSchema:
    state = train_dispatch_service.get_station_state(station_id)
    if state is None:
        raise HTTPException(status_code=404, detail=f"Station '{station_id}' not found")

    station_schema = _station_to_schema(state.station)
    dispatch_schema = _dispatch_to_schema(state.last_dispatch) if state.last_dispatch else None

    return StationStatusSchema(
        station=station_schema,
        last_passenger_count=state.last_passenger_count,
        last_updated=state.last_updated,
        last_dispatch=dispatch_schema,
    )


@router.post(
    "/dispatch",
    response_model=DispatchPlanSchema,
    summary="Generate an optimal train dispatch plan",
)
def compute_dispatch_plan(request: DispatchRequestSchema) -> DispatchPlanSchema:
    station = None
    if request.station_id:
        station = train_dispatch_service.get_station(request.station_id)
        if station is None:
            raise HTTPException(status_code=404, detail=f"Station '{request.station_id}' not found")
    elif request.camera_id:
        station = train_dispatch_service.get_station_by_camera(request.camera_id)
        if station is None:
            raise HTTPException(
                status_code=404, detail=f"Camera '{request.camera_id}' is not linked to any station"
            )

    if station is None:
        raise HTTPException(status_code=400, detail="Unable to determine target station")

    if request.persist:
        plan = train_dispatch_service.update_station_load(
            station.camera_id, request.passenger_count
        )
        if plan is None:
            raise HTTPException(status_code=500, detail="Unable to calculate dispatch plan")
    else:
        plan = train_dispatch_service.compute_dispatch_plan(station, request.passenger_count)

    return _dispatch_to_schema(plan)
