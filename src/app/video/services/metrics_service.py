from __future__ import annotations
from asyncio.queues import Queue


import asyncio
from collections import defaultdict
from collections.abc import AsyncGenerator

from src.app.video.interfaces.detection_metrics import DetectionMetrics


class DetectionMetricsService:
    _instance: DetectionMetricsService | None = None

    def __new__(cls) -> DetectionMetricsService:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        self._subscribers: defaultdict[str, list[asyncio.Queue[DetectionMetrics]]] = defaultdict[
            str, list[Queue[DetectionMetrics]]
        ](list)
        self._latest_metrics: dict[str, DetectionMetrics] = {}
        self._lock = asyncio.Lock()

    async def publish(self, metrics: DetectionMetrics) -> None:
        async with self._lock:
            subscribers = list[Queue[DetectionMetrics]](self._subscribers.get(metrics.video_id, []))
            self._latest_metrics[metrics.video_id] = metrics

        if not subscribers:
            return

        for queue in subscribers:
            if queue.full():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
            await queue.put(metrics)

    async def subscribe(self, video_id: str) -> AsyncGenerator[DetectionMetrics, None]:
        queue: asyncio.Queue[DetectionMetrics] = asyncio.Queue(maxsize=5)

        async with self._lock:
            self._subscribers[video_id].append(queue)
            latest = self._latest_metrics.get(video_id)

        if latest is not None:
            await queue.put(latest)

        try:
            while True:
                metrics = await queue.get()
                yield metrics
        finally:
            async with self._lock:
                subscribers = self._subscribers.get(video_id)
                if subscribers is not None:
                    try:
                        subscribers.remove(queue)
                    except ValueError:
                        pass
                    if not subscribers:
                        self._subscribers.pop(video_id, None)
