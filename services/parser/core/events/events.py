"""도메인 이벤트 정의"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ScheduleSaved:
    """스케줄이 DB에 저장된 후 발행되는 이벤트"""
    data: dict
    facility_name: str
    valid_month: str


@dataclass(frozen=True)
class PoolClosureDetected:
    """수영장 휴장이 감지되었을 때 발행되는 이벤트"""
    facility_name: str
    valid_month: str
    reason: str
    source_url: str
