"""
Discord Webhook HTTP 클라이언트
"""
import logging

import requests

from infrastructure.config import settings

logger = logging.getLogger(__name__)


class DiscordClient:
    """Discord Incoming Webhook 클라이언트"""

    def __init__(self, webhook_url: str = None, timeout: int = None):
        self.webhook_url = webhook_url or settings.DISCORD_WEBHOOK_URL
        self.timeout = timeout or settings.DISCORD_TIMEOUT
        self._enabled = settings.DISCORD_ENABLED and bool(self.webhook_url)

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def send(self, payload: dict) -> bool:
        """
        Discord Webhook으로 메시지 전송

        Args:
            payload: Discord 메시지 payload (content 또는 embeds)

        Returns:
            전송 성공 여부
        """
        if not self._enabled:
            logger.debug("Discord 알림 비활성화 상태")
            return False

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=self.timeout,
            )

            if response.status_code == 204:
                logger.debug("Discord 메시지 전송 성공")
                return True

            logger.warning(
                f"Discord 메시지 전송 실패: status={response.status_code}, body={response.text}"
            )
            return False

        except requests.exceptions.Timeout:
            logger.warning(f"Discord 메시지 전송 타임아웃 ({self.timeout}초)")
            return False
        except requests.exceptions.RequestException as e:
            logger.warning(f"Discord 메시지 전송 오류: {e}")
            return False
