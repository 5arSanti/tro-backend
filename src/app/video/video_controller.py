import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from src.app.common.common_schema import ErrorSchema
from src.app.core.router import Controller
from src.app.video.video_schema import DetectionConfigSchema, VideoListSchema
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
async def list_videos() -> VideoListSchema:
    try:
        service = VideoService()
        return service.get_available_videos()
    except Exception as exc:
        logger.exception("Failed to list available videos")
        raise HTTPException(status_code=500, detail="Error listing videos") from exc


@router.get(
    "/{video_id}/stream",
    summary="Stream video with detection",
    description="Streams video frames with YOLO model detections in real-time",
    responses={
        200: {
            "content": {"multipart/x-mixed-replace": {}},
            "description": "Video stream with detections",
        },
        404: {"model": ErrorSchema},
        500: {"model": ErrorSchema},
    },
)
async def stream_video(
    video_id: str,
    confidence_threshold: float = Query(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for detections to be displayed",
    ),
    resolution: str | None = Query(
        default=None,
        pattern=r"^\d+x\d+$",
        description="Optional output resolution in the format WIDTHxHEIGHT (e.g. '640x480')",
    ),
) -> StreamingResponse:
    service = VideoService()
    config = DetectionConfigSchema(
        confidence_threshold=confidence_threshold,
        resolution=resolution,
    )

    try:
        async def frame_generator() -> AsyncGenerator[bytes, None]:
            async for frame in service.process_video_stream(video_id, config):
                yield b"--frame\r\n"
                yield b"Content-Type: image/jpeg\r\n\r\n"
                yield frame
                yield b"\r\n"

        return StreamingResponse(
            frame_generator(),
            media_type="multipart/x-mixed-replace; boundary=frame",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )
    except FileNotFoundError as exc:
        logger.error("Video '%s' not found", video_id)
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Failed to stream video '%s'", video_id)
        raise HTTPException(status_code=500, detail="Error streaming video") from exc
