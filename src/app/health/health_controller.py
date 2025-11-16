from fastapi import APIRouter

from src.app.common.common_schema import HealthCheckSchema
from src.app.core.dependencies import SettingsDep
from src.app.core.router import Controller
from src.app.health.health_service import HealthService

router: APIRouter = Controller("/health", tags=["Health"])


@router.get(
    "",
    response_model=HealthCheckSchema,
    summary="Health check endpoint",
    description="Returns the health status of the application",
)
async def health_check(settings: SettingsDep) -> HealthCheckSchema:
    return HealthService(settings).get_health_status()
