from dataclasses import dataclass
from datetime import datetime, timezone
from math import ceil
from collections.abc import Iterable

import logging


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TrainModelConfig:
    id: str
    name: str
    wagon_count: int
    capacity_per_wagon: int

    @property
    def total_capacity(self) -> int:
        return self.wagon_count * self.capacity_per_wagon


@dataclass(frozen=True)
class StationConfig:
    id: str
    name: str
    line: str
    camera_id: str
    travel_time_seconds: int
    supported_train_ids: tuple[str, ...]


@dataclass
class DispatchPlan:
    station_id: str
    station_name: str
    camera_id: str
    passenger_count: int
    train_model: TrainModelConfig
    trains_required: int
    total_capacity: int
    surplus_capacity: int
    status: str
    estimated_cycle_time_seconds: int
    generated_at: datetime


@dataclass
class StationState:
    station: StationConfig
    last_passenger_count: int | None = None
    last_updated: datetime | None = None
    last_dispatch: DispatchPlan | None = None


class TrainDispatchService:
    """Service responsible for determining optimal train dispatch plans based on passenger density."""

    def __init__(self) -> None:
        self._train_models: dict[str, TrainModelConfig] = self._build_train_models()
        self._stations: dict[str, StationConfig] = self._build_station_configs()
        self._states: dict[str, StationState] = {
            station_id: StationState(station=config)
            for station_id, config in self._stations.items()
        }

    # -------------------------------------------------------------------------
    # Initialization helpers
    # -------------------------------------------------------------------------

    def _build_train_models(self) -> dict[str, TrainModelConfig]:
        base_capacity = 5  # Passengers per wagon, configurable if needed.
        return {
            "light": TrainModelConfig(
                id="light",
                name="Tren Ligero (1 vagón)",
                wagon_count=1,
                capacity_per_wagon=base_capacity,
            ),
            "medium": TrainModelConfig(
                id="medium",
                name="Tren Medio (2 vagones)",
                wagon_count=2,
                capacity_per_wagon=base_capacity,
            ),
            "heavy": TrainModelConfig(
                id="heavy",
                name="Tren Pesado (3 vagones)",
                wagon_count=3,
                capacity_per_wagon=base_capacity,
            ),
        }

    def _build_station_configs(self) -> dict[str, StationConfig]:
        return {
            "station_sur": StationConfig(
                id="station_sur",
                name="Estación Sur",
                line="Línea 3",
                camera_id="usb1",
                travel_time_seconds=210,
                supported_train_ids=("light", "medium", "heavy"),
            ),
            "station_central": StationConfig(
                id="station_central",
                name="Estación Central",
                line="Línea 1",
                camera_id="video1",
                travel_time_seconds=180,
                supported_train_ids=("light", "medium", "heavy"),
            ),
            "station_norte": StationConfig(
                id="station_norte",
                name="Estación Norte",
                line="Línea 2",
                camera_id="video2",
                travel_time_seconds=240,
                supported_train_ids=("light", "medium", "heavy"),
            ),
            "station_east": StationConfig(
                id="station_east",
                name="Estación Este",
                line="Línea 4",
                camera_id="video3",
                travel_time_seconds=270,
                supported_train_ids=("light", "medium"),
            ),
            "station_west": StationConfig(
                id="station_west",
                name="Estación Oeste",
                line="Línea 5",
                camera_id="video4",
                travel_time_seconds=300,
                supported_train_ids=("light", "medium"),
            ),
        }

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def list_train_models(self) -> Iterable[TrainModelConfig]:
        return self._train_models.values()

    def list_stations(self) -> Iterable[StationConfig]:
        return self._stations.values()

    def get_station(self, station_id: str) -> StationConfig | None:
        return self._stations.get(station_id)

    def get_station_by_camera(self, camera_id: str) -> StationConfig | None:
        for station in self._stations.values():
            if station.camera_id == camera_id:
                return station
        return None

    def get_train_model(self, train_id: str) -> TrainModelConfig | None:
        return self._train_models.get(train_id)

    def get_supported_train_models(self, station: StationConfig) -> list[TrainModelConfig]:
        return [
            self._train_models[train_id]
            for train_id in station.supported_train_ids
            if train_id in self._train_models
        ]

    def get_station_state(self, station_id: str) -> StationState | None:
        return self._states.get(station_id)

    def list_station_states(self) -> Iterable[StationState]:
        return self._states.values()

    def compute_dispatch_plan(self, station: StationConfig, passenger_count: int) -> DispatchPlan:
        if passenger_count < 0:
            raise ValueError("Passenger count cannot be negative")

        supported_models = [
            self._train_models[train_id] for train_id in station.supported_train_ids
        ]

        model = self._select_model(supported_models, passenger_count)
        trains_required = ceil(passenger_count / model.total_capacity) if passenger_count > 0 else 0
        total_capacity = trains_required * model.total_capacity
        surplus = max(total_capacity - passenger_count, 0)

        if passenger_count == 0:
            status = "No se requieren trenes adicionales"
            estimated_cycle = 0
        else:
            status = "Despacho óptimo calculado"
            estimated_cycle = trains_required * station.travel_time_seconds

        return DispatchPlan(
            station_id=station.id,
            station_name=station.name,
            camera_id=station.camera_id,
            passenger_count=passenger_count,
            train_model=model,
            trains_required=trains_required,
            total_capacity=total_capacity,
            surplus_capacity=surplus,
            status=status,
            estimated_cycle_time_seconds=estimated_cycle,
            generated_at=datetime.now(timezone.utc),
        )

    def update_station_load(self, camera_id: str, passenger_count: int) -> DispatchPlan | None:
        station = self.get_station_by_camera(camera_id)
        if station is None:
            logger.debug("No station configuration found for camera '%s'", camera_id)
            return None

        plan = self.compute_dispatch_plan(station, passenger_count)

        state = self._states.setdefault(station.id, StationState(station=station))
        state.last_passenger_count = passenger_count
        state.last_dispatch = plan
        state.last_updated = plan.generated_at

        logger.info(
            "Station '%s' updated with %s passengers. Recommended train: %s (%s trains).",
            station.name,
            passenger_count,
            plan.train_model.name,
            plan.trains_required,
        )

        return plan

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _select_model(
        self, train_models: Iterable[TrainModelConfig], passenger_count: int
    ) -> TrainModelConfig:
        sorted_models = sorted(train_models, key=lambda model: model.total_capacity)
        for model in sorted_models:
            if passenger_count <= model.total_capacity:
                return model
        # If all capacities are smaller, select the largest available model.
        return sorted_models[-1]


train_dispatch_service = TrainDispatchService()
