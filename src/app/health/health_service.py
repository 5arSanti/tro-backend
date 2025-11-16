from src.app.common.common_schema import HealthCheckSchema
from src.app.core.config import Settings


class HealthService:
    def __init__(self, settings: Settings) -> None:
        self._settings: Settings = settings

    def get_health_status(self) -> HealthCheckSchema:
        return HealthCheckSchema(
            status="healthy",
            version=self._settings.app_version,
            environment=self._settings.environment,
        )
