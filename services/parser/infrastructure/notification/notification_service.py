"""
알림 오케스트레이션 서비스
"""
import logging

from infrastructure.config import settings
from .discord_client import DiscordClient
from .message_builder import DiscordMessageBuilder

logger = logging.getLogger(__name__)


class NotificationService:
    """파이프라인 알림 서비스"""

    def __init__(self):
        self._client = DiscordClient()

    def _send_safely(self, payload: dict, description: str) -> bool:
        """안전한 전송 (예외 절대 전파하지 않음)"""
        try:
            return self._client.send(payload)
        except Exception as e:
            logger.warning(f"Discord 알림 전송 실패 [{description}]: {e}")
            return False

    def notify_daily_summary(
        self,
        total_notices: int,
        new_saved: int,
        already_exists: int,
        parse_success: int,
        parse_total: int,
        errors: list[str] = None,
        closures: list[dict] = None,
        duration_seconds: float = 0.0,
        crawled_notices: list[dict] = None,
        saved_items: list[dict] = None,
    ) -> bool:
        """일일 크롤링 요약 알림"""
        if not settings.DISCORD_NOTIFY_ON_SUCCESS and not errors:
            return False

        payload = DiscordMessageBuilder.daily_summary(
            total_notices=total_notices,
            new_saved=new_saved,
            already_exists=already_exists,
            parse_success=parse_success,
            parse_total=parse_total,
            errors=errors or [],
            closures=closures or [],
            duration_seconds=duration_seconds,
            crawled_notices=crawled_notices or [],
            saved_items=saved_items or [],
        )
        return self._send_safely(payload, "일일 요약")

    def notify_new_schedule(self, data: dict) -> bool:
        """새 스케줄 저장 알림"""
        if not settings.DISCORD_NOTIFY_ON_SUCCESS:
            return False

        payload = DiscordMessageBuilder.new_schedule_saved(data)
        return self._send_safely(payload, "새 스케줄")

    def notify_error(self, stage: str, error_message: str, context: str = "") -> bool:
        """에러 알림"""
        if not settings.DISCORD_NOTIFY_ON_ERROR:
            return False

        payload = DiscordMessageBuilder.error_alert(stage, error_message, context)
        return self._send_safely(payload, f"에러-{stage}")

    def notify_pool_closure(
        self, facility_name: str, valid_month: str, reason: str, source_url: str = ""
    ) -> bool:
        """수영장 휴장 감지 알림"""
        if not settings.DISCORD_NOTIFY_ON_CLOSURE:
            return False

        payload = DiscordMessageBuilder.pool_closure_detected(
            facility_name, valid_month, reason, source_url
        )
        return self._send_safely(payload, f"휴장-{facility_name}")
