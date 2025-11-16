from collections.abc import Sequence

from fastapi import APIRouter


def Controller(prefix: str, tags: Sequence[str] | None = None) -> APIRouter:
    router_tags: list[str] = list(tags) if tags else [prefix.strip("/").title()]

    return APIRouter(prefix=prefix, tags=router_tags)  # type: ignore[arg-type]
