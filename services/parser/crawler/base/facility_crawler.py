"""
시설 기본 정보 크롤러 추상 베이스 클래스

모든 기관의 FacilityCrawler가 상속해야 하는 공통 인터페이스
"""
from abc import ABC, abstractmethod
from typing import List, Dict
import logging

from models.enum.facility import Facility, Organization

logger = logging.getLogger(__name__)


class BaseFacilityCrawler(ABC):
    """
    시설 기본 정보 크롤러 추상 클래스

    공통 로직:
    - 모든 시설 크롤링 (crawl_all_facilities)

    기관별 구현 필요:
    - 단일 시설 크롤링 (crawl_facility)
    - 대상 시설 목록 (get_target_facilities)
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def crawl_facility(self, facility: Facility) -> dict:
        """
        단일 시설의 기본 스케줄 크롤링

        Args:
            facility: Facility Enum 객체

        Returns:
            시설 정보 딕셔너리
            {
                "facility_name": str,
                "weekday_schedule": [...],
                "saturday_schedule": [...],
                "sunday_schedule": [...],
                "fees": [...],
                ...
            }

        Example:
            >>> def crawl_facility(self, facility: Facility):
            ...     url = get_snyouth_facility_url(facility)
            ...     response = self.session.get(url)
            ...     return self._parse_facility_page(response.text)
        """
        pass

    @abstractmethod
    def get_target_facilities(self) -> List[Facility]:
        """
        크롤링 대상 시설 목록

        Returns:
            Facility Enum 리스트

        Example:
            >>> def get_target_facilities(self):
            ...     return Facility.snyouth_facilities()
        """
        pass

    def crawl_all_facilities(self) -> List[dict]:
        """
        모든 시설 크롤링 (공통 로직)

        Returns:
            시설 정보 딕셔너리 리스트
        """
        facilities = self.get_target_facilities()
        results = []

        for facility in facilities:
            self.logger.info(f"[{facility.name}] 크롤링 시작...")

            try:
                data = self.crawl_facility(facility)
                if data:
                    results.append(data)
                    self.logger.info(f"[{facility.name}] 크롤링 완료")
                else:
                    self.logger.warning(f"[{facility.name}] 데이터 없음")

            except Exception as e:
                self.logger.error(f"[{facility.name}] 크롤링 실패: {e}")
                continue

        self.logger.info(f"전체 크롤링 완료: {len(results)}/{len(facilities)}개 시설")
        return results

    def to_dict(self, facility_data: dict) -> dict:
        """
        시설 데이터를 표준 형식으로 변환 (공통 유틸리티)

        Args:
            facility_data: 크롤링한 시설 데이터

        Returns:
            표준화된 딕셔너리
        """
        # 기본 구조는 그대로 반환 (필요시 하위 클래스에서 오버라이드)
        return facility_data

    def validate_schedule(self, schedule: dict) -> bool:
        """
        스케줄 데이터 유효성 검증

        Args:
            schedule: 스케줄 딕셔너리

        Returns:
            유효성 여부
        """
        required_fields = ["facility_name"]

        for field in required_fields:
            if field not in schedule or not schedule[field]:
                self.logger.warning(f"필수 필드 누락: {field}")
                return False

        return True
