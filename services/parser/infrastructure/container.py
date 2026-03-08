"""
Parser 서비스 DI Container

의존성 생성을 중앙 집중화하여 서비스 간 결합도를 낮춘다.
- Singleton: 프로세스 수명 동안 하나만 유지 (lazy 초기화)
- Factory: 호출할 때마다 새 인스턴스 반환
"""
from infrastructure.config import settings
from infrastructure.notification import NotificationService
from infrastructure.cache import CacheInvalidationPublisher
from infrastructure.database.repository import SwimRepository
from application.storage_service import StorageService
from application.swim_crawler_service import SwimCrawlerService
from application.fallback_service import FallbackService
from application.event_handlers import (
    DiscordEventHandler, CacheEventHandler, ClosureDetectionHandler,
)
from core.events import EventBus, ScheduleSaved, PoolClosureDetected


class Container:
    """Parser 서비스 DI Container"""

    def __init__(self):
        self._notification_service: NotificationService | None = None
        self._cache_publisher: CacheInvalidationPublisher | None = None
        self._storage_service: StorageService | None = None
        self._event_bus: EventBus | None = None
        self._discord_event_handler: DiscordEventHandler | None = None
        self._cache_event_handler: CacheEventHandler | None = None
        self._closure_detection_handler: ClosureDetectionHandler | None = None

    # -- Infrastructure (Singleton) --

    def notification_service(self) -> NotificationService:
        if self._notification_service is None:
            self._notification_service = NotificationService()
        return self._notification_service

    def cache_publisher(self) -> CacheInvalidationPublisher:
        if self._cache_publisher is None:
            self._cache_publisher = CacheInvalidationPublisher()
        return self._cache_publisher

    # -- Storage (Singleton) --

    def storage_service(self) -> StorageService:
        if self._storage_service is None:
            self._storage_service = StorageService(storage_dir=settings.STORAGE_DIR)
        return self._storage_service

    # -- Repository (Factory) --

    def swim_repository(self) -> SwimRepository:
        return SwimRepository()

    # -- Application Services (Factory) --

    def swim_crawler_service(self) -> SwimCrawlerService:
        return SwimCrawlerService(storage=self.storage_service())

    def fallback_service(self) -> FallbackService:
        return FallbackService(storage=self.storage_service())

    # -- Event System (Singleton) --

    def event_bus(self) -> EventBus:
        if self._event_bus is None:
            self._event_bus = EventBus()
        return self._event_bus

    def discord_event_handler(self) -> DiscordEventHandler:
        if self._discord_event_handler is None:
            self._discord_event_handler = DiscordEventHandler(self.notification_service())
        return self._discord_event_handler

    def cache_event_handler(self) -> CacheEventHandler:
        if self._cache_event_handler is None:
            self._cache_event_handler = CacheEventHandler(self.cache_publisher())
        return self._cache_event_handler

    def closure_detection_handler(self) -> ClosureDetectionHandler:
        if self._closure_detection_handler is None:
            self._closure_detection_handler = ClosureDetectionHandler(self.event_bus())
        return self._closure_detection_handler

    def init_event_bus(self) -> None:
        """이벤트 핸들러를 EventBus에 구독 등록. 최초 1회 호출."""
        bus = self.event_bus()
        bus.subscribe(ScheduleSaved, self.discord_event_handler().on_schedule_saved)
        bus.subscribe(ScheduleSaved, self.cache_event_handler().on_schedule_saved)
        bus.subscribe(ScheduleSaved, self.closure_detection_handler().on_schedule_saved)
        bus.subscribe(PoolClosureDetected, self.discord_event_handler().on_pool_closure)


# 모듈 레벨 싱글톤 (main.py, scheduler.py 모두 동일 인스턴스 사용)
container = Container()
container.init_event_bus()
