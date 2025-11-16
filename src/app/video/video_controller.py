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


# @router.get(
#     "/{video_id}/stream",
#     summary="Stream video with detection",
#     description="Streams video frames with YOLO object detection applied in real-time",
#     responses={
#         200: {
#             "content": {"image/jpeg": {}},
#             "description": "Video stream with detections",
#         },
#         404: {"model": ErrorSchema},
#         500: {"model": ErrorSchema},
#     },
# )
# async def stream_video_with_detection(
#     video_id: str,
#     settings: SettingsDep,
#     confidence_threshold: float = Query(
#         default=0.5, ge=0.0, le=1.0, description="Confidence threshold for detections"
#     ),
#     resolution: str | None = Query(
#         default=None, description="Output resolution in format WxH (e.g., '640x480')"
#     ),
# ) -> StreamingResponse:
#     try:
#         service = VideoService(settings)
#         config = DetectionConfigSchema(
#             confidence_threshold=confidence_threshold, resolution=resolution
#         )

#         async def generate() -> bytes:
#             async for frame in service.process_video_stream(video_id, config):
#                 yield b"--frame\r\n"
#                 yield b"Content-Type: image/jpeg\r\n\r\n"
#                 yield frame
#                 yield b"\r\n"

#         return StreamingResponse(
#             generate(),
#             media_type="multipart/x-mixed-replace; boundary=frame",
#             headers={
#                 "Cache-Control": "no-cache, no-store, must-revalidate",
#                 "Pragma": "no-cache",
#                 "Expires": "0",
#             },
#         )
#     except FileNotFoundError as e:
#         raise HTTPException(status_code=404, detail=str(e)) from e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}") from e

