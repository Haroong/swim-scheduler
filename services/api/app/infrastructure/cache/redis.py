"""
Redis 캐시 설정
fastapi-cache2를 사용한 캐싱 구현
"""
from typing import Optional
from fastapi import Request, Response
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from app.shared.config import settings


async def init_cache() -> None:
    """
    Redis 캐시 초기화
    애플리케이션 시작 시 호출
    """
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
    )
    FastAPICache.init(RedisBackend(redis), prefix="swim-api-cache")


async def close_cache() -> None:
    """
    Redis 연결 종료
    애플리케이션 종료 시 호출
    """
    backend = FastAPICache.get_backend()
    if backend and hasattr(backend, 'redis'):
        await backend.redis.close()


def cache_key_builder(
    func,
    namespace: Optional[str] = "",
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    *args,
    **kwargs
) -> str:
    """
    커스텀 캐시 키 빌더

    형식: swim-api-cache:{module}:{function}:{params}
    예: swim-api-cache:app.presentation.schedule.controller:get_schedules:facility=야탑유스센터:month=2026-01
    """
    prefix = FastAPICache.get_prefix()
    module = func.__module__
    func_name = func.__name__

    # 쿼리 파라미터를 키에 포함
    params_str = ""
    if request and request.query_params:
        sorted_params = sorted(request.query_params.items())
        params_str = ":".join(f"{k}={v}" for k, v in sorted_params)

    if params_str:
        return f"{prefix}:{module}:{func_name}:{params_str}"
    return f"{prefix}:{module}:{func_name}"
