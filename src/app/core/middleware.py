from collections.abc import Awaitable, Callable

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

MAX_REQUEST_SIZE: int = 2 * 1024 * 1024 * 1024


class MaxRequestSizeMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        content_length: str | None = request.headers.get("content-length")
        if content_length:
            try:
                size: int = int(content_length)
                if size > MAX_REQUEST_SIZE:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": "PayloadTooLarge",
                            "message": f"Request body size ({size / (1024 * 1024):.2f} MB) exceeds maximum allowed size of 2GB",
                            "status_code": 413,
                        },
                    )
            except ValueError:
                pass

        response: Response = await call_next(request)
        return response
