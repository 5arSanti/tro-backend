from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from src.app.common.common_schema import ErrorSchema
from src.app.core.dependencies import SettingsDep
from src.app.core.router import Controller
from src.app.video.video_schema import DetectionConfigSchema, VideoListSchema
from src.app.video.video_service import VideoService

router: APIRouter = Controller("/videos", tags=["Videos"])


@router.get(
    "",
    response_model=VideoListSchema,
    summary="List available videos",
    description="Returns a list of all available videos for detection",
    responses={200: {"model": VideoListSchema}},
)
async def list_videos(settings: SettingsDep) -> VideoListSchema:
    service = VideoService(settings)
    return service.get_available_videos()


@router.get(
    "/{video_id}/stream",
    summary="Stream video with detection",
    description="Streams video frames with YOLO object detection applied in real-time",
    responses={
        200: {
            "content": {"image/jpeg": {}},
            "description": "Video stream with detections",
        },
        404: {"model": ErrorSchema},
        500: {"model": ErrorSchema},
    },
)
async def stream_video_with_detection(
    video_id: str,
    settings: SettingsDep,
    confidence_threshold: float = Query(
        default=0.5, ge=0.0, le=1.0, description="Confidence threshold for detections"
    ),
    resolution: str | None = Query(
        default=None, description="Output resolution in format WxH (e.g., '640x480')"
    ),
) -> StreamingResponse:
    try:
        service = VideoService(settings)
        config = DetectionConfigSchema(
            confidence_threshold=confidence_threshold, resolution=resolution
        )

        def generate() -> bytes:
            for frame in service.process_video_stream(video_id, config):
                yield b"--frame\r\n"
                yield b"Content-Type: image/jpeg\r\n\r\n"
                yield frame
                yield b"\r\n"

        return StreamingResponse(
            generate(),
            media_type="multipart/x-mixed-replace; boundary=frame",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}") from e

