import logging

from src.app.common.constants import VIDEO_ASSETS_PATH
from src.app.video.services.video_file_service import VideoFileService
from src.app.video.video_schema import VideoInfoSchema, VideoListSchema

logger = logging.getLogger(__name__)


class VideoService:
    def __init__(self) -> None:
        self._assets_path = VIDEO_ASSETS_PATH

        self._video_file_service = VideoFileService(self._assets_path)

    def get_available_videos(self) -> VideoListSchema:
        try:
            print("list_video_files")
            print(self._assets_path)
            video_files = self._video_file_service.list_video_files()
        except Exception:
            logger.exception("Failed to list video files from %s", self._assets_path)
            raise

        videos: list[VideoInfoSchema] = []
        for video_file in video_files:
            video_id = self._video_file_service.get_video_id(video_file)
            videos.append(
                VideoInfoSchema(
                    id=video_id,
                    filename=video_file.name,
                    name=f"Video {video_id.replace('video', '')}",
                )
            )

        return VideoListSchema(videos=videos)
