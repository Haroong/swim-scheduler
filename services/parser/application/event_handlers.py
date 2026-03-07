"""도메인 이벤트 핸들러

각 핸들러는 특정 이벤트에 반응하여 사이드 이펙트를 수행한다.
EventBus의 fail-safe에 의해 핸들러 실패가 파이프라인을 중단시키지 않는다.
"""
from core.events import EventBus, ScheduleSaved, PoolClosureDetected
from infrastructure.notification import NotificationService
from infrastructure.cache import CacheInvalidationPublisher


class DiscordEventHandler:
    """Discord 알림 이벤트 처리"""

    def __init__(self, notifier: NotificationService):
        self._notifier = notifier

    def on_schedule_saved(self, event: ScheduleSaved) -> None:
        self._notifier.notify_new_schedule(event.data)

    def on_pool_closure(self, event: PoolClosureDetected) -> None:
        self._notifier.notify_pool_closure(
            facility_name=event.facility_name,
            valid_month=event.valid_month,
            reason=event.reason,
            source_url=event.source_url,
        )


class CacheEventHandler:
    """캐시 무효화 이벤트 처리"""

    def __init__(self, publisher: CacheInvalidationPublisher):
        self._publisher = publisher

    def on_schedule_saved(self, event: ScheduleSaved) -> None:
        self._publisher.publish_schedule_saved(
            facility_name=event.facility_name,
            valid_month=event.valid_month,
        )


class ClosureDetectionHandler:
    """휴장 감지 → PoolClosureDetected 이벤트 발행

    스케줄 저장 데이터를 분석하여 수영장 휴장 여부를 판단하고,
    감지 시 PoolClosureDetected 이벤트를 발행한다.
    detected_closures 속성으로 감지된 휴장 목록을 외부에서 조회 가능.
    """

    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
        self.detected_closures: list[dict] = []

    def on_schedule_saved(self, event: ScheduleSaved) -> None:
        data = event.data
        closures = data.get("closures", [])
        schedules = data.get("schedules", [])
        notes = data.get("notes", [])

        has_monthly_closure = any(
            c.get("closure_type") == "monthly" for c in closures
        )
        is_closed = has_monthly_closure or (
            len(schedules) == 0
            and any(kw in note for note in notes for kw in ("미운영", "휴장", "휴관"))
        )

        if is_closed:
            reason = next(
                (n for n in notes if any(kw in n for kw in ("미운영", "휴장", "휴관"))),
                "수영장 임시휴장",
            )
            closure_info = {
                "facility_name": data.get("facility_name", ""),
                "valid_month": data.get("valid_month", ""),
                "reason": reason,
                "source_url": data.get("source_url", ""),
            }
            self.detected_closures.append(closure_info)
            self._event_bus.publish(PoolClosureDetected(**closure_info))
