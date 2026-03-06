"""
Redis Pub/Sub 캐시 무효화 Publisher

Parser가 DB 저장 완료 후 API 서버에 캐시 무효화 이벤트를 발행한다.
"""
import json
import logging
from datetime import datetime

import redis

from infrastructure.config import settings

logger = logging.getLogger(__name__)

CHANNEL = "swim-scheduler:cache-invalidation"


class CacheInvalidationPublisher:
    """Redis Pub/Sub 캐시 무효화 Publisher"""

    def __init__(self):
        self._client: redis.Redis | None = None
        self._enabled = True
        self._connect()

    def _connect(self):
        try:
            self._client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                socket_connect_timeout=5,
            )
            self._client.ping()
            logger.info("Redis 캐시 무효화 Publisher 연결 성공")
        except redis.RedisError as e:
            logger.warning(f"Redis 연결 실패, 캐시 무효화 비활성화: {e}")
            self._enabled = False
            self._client = None

    def publish_schedule_saved(self, facility_name: str, valid_month: str) -> bool:
        if not self._enabled:
            return False

        try:
            message = json.dumps({
                "event": "schedule_saved",
                "facility_name": facility_name,
                "valid_month": valid_month,
                "timestamp": datetime.now().isoformat(),
            }, ensure_ascii=False)
            self._client.publish(CHANNEL, message)
            logger.info(f"캐시 무효화 이벤트 발행: {facility_name} ({valid_month})")
            return True
        except redis.RedisError as e:
            logger.warning(f"캐시 무효화 이벤트 발행 실패: {e}")
            return False

    def close(self):
        if self._client:
            self._client.close()
            self._client = None
