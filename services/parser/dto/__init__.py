"""
DTO (Data Transfer Object) 패키지
계층 간 데이터 전송을 위한 객체들
"""
from dto.crawler_dto import PostSummary, PostDetail, Attachment
from dto.parser_dto import ParseRequest, ParsedScheduleData
from dto.storage_dto import ScheduleStorageDTO

__all__ = [
    "PostSummary",
    "PostDetail",
    "Attachment",
    "ParseRequest",
    "ParsedScheduleData",
    "ScheduleStorageDTO",
]
