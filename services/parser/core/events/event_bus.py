"""인프로세스 동기 이벤트 버스"""
import logging
from collections import defaultdict
from typing import Callable

logger = logging.getLogger(__name__)


class EventBus:
    """간단한 동기 Pub/Sub 이벤트 버스

    핸들러 실패 시 예외를 삼키고 로그만 남긴다 (fail-safe).
    """

    def __init__(self):
        self._handlers: dict[type, list[Callable]] = defaultdict(list)

    def subscribe(self, event_type: type, handler: Callable) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event) -> None:
        for handler in self._handlers.get(type(event), []):
            try:
                handler(event)
            except Exception as e:
                logger.warning(
                    f"이벤트 핸들러 실패 [{type(event).__name__} → {handler.__qualname__}]: {e}"
                )
