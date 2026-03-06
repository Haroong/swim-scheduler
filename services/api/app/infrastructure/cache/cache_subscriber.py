"""
Redis Pub/Sub 캐시 무효화 Subscriber

Parser의 DB 저장 이벤트를 수신하여 API 캐시를 클리어한다.
2초 디바운스로 배치 저장 시 한 번만 클리어.
"""
import asyncio
import json
import logging

from redis import asyncio as aioredis
from fastapi_cache import FastAPICache

from app.shared.config import settings

logger = logging.getLogger(__name__)

CHANNEL = "swim-scheduler:cache-invalidation"
DEBOUNCE_SECONDS = 2.0


class CacheSubscriber:
    """Redis Pub/Sub 캐시 무효화 Subscriber"""

    def __init__(self):
        self._redis: aioredis.Redis | None = None
        self._pubsub: aioredis.client.PubSub | None = None
        self._task: asyncio.Task | None = None
        self._debounce_task: asyncio.Task | None = None

    async def start(self):
        try:
            self._redis = aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
            )
            self._pubsub = self._redis.pubsub()
            await self._pubsub.subscribe(CHANNEL)
            self._task = asyncio.create_task(self._listen())
            logger.info("캐시 무효화 Subscriber 시작")
        except Exception as e:
            logger.warning(f"캐시 무효화 Subscriber 시작 실패: {e}")

    async def _listen(self):
        try:
            async for message in self._pubsub.listen():
                if message["type"] != "message":
                    continue

                try:
                    data = json.loads(message["data"])
                    logger.info(
                        f"캐시 무효화 이벤트 수신: {data.get('facility_name')} "
                        f"({data.get('valid_month')})"
                    )
                except (json.JSONDecodeError, TypeError):
                    logger.warning("캐시 무효화 메시지 파싱 실패")

                # 디바운스: 기존 예약된 클리어 취소 후 재예약
                if self._debounce_task and not self._debounce_task.done():
                    self._debounce_task.cancel()
                self._debounce_task = asyncio.create_task(self._debounced_clear())
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.warning(f"캐시 무효화 리스너 오류: {e}")

    async def _debounced_clear(self):
        await asyncio.sleep(DEBOUNCE_SECONDS)
        await self._clear_all_cache()

    async def _clear_all_cache(self):
        try:
            backend = FastAPICache.get_backend()
            redis_client = backend.redis
            prefix = FastAPICache.get_prefix()

            keys = await redis_client.keys(f"{prefix}:*")
            if keys:
                await redis_client.delete(*keys)
                logger.info(f"캐시 무효화 완료: {len(keys)}개 키 삭제")
            else:
                logger.info("캐시 무효화: 삭제할 키 없음")
        except Exception as e:
            logger.warning(f"캐시 클리어 실패: {e}")

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._debounce_task and not self._debounce_task.done():
            self._debounce_task.cancel()
        if self._pubsub:
            await self._pubsub.unsubscribe(CHANNEL)
            await self._pubsub.aclose()
        if self._redis:
            await self._redis.aclose()
        logger.info("캐시 무효화 Subscriber 종료")
