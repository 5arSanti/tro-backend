import logging

from fastapi import APIRouter, HTTPException

from src.app.core.dependencies import SettingsDep
from src.app.core.router import Controller
from src.app.video.video_schema import VideoListSchema
from src.app.video.video_service import VideoService

logger = logging.getLogger(__name__)

router: APIRouter = Controller("/videos", tags=["Videos"])


@router.get(
    "/list",
    response_model=VideoListSchema,
    summary="List available videos",
    description="Returns a list of all available videos for detection",
    responses={200: {"model": VideoListSchema}},
)
async def list_videos(settings: SettingsDep) -> VideoListSchema:
    try:
        service = VideoService(settings)
        result = service.get_available_videos()
        return result
    except Exception as exc:
        logger.exception("Failed to list available videos")
        raise HTTPException(status_code=500, detail="Error listing videos") from exc
