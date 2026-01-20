"""
시설 기본 정보 크롤러 추상 베이스 클래스

모든 기관의 FacilityCrawler가 상속해야 하는 공통 인터페이스
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, TYPE_CHECKING
import logging

from models.enum.facility import Facility, Organization

if TYPE_CHECKING:
    from dto.crawler_dto import FacilityInfoResponse

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
    def crawl_facility(self, facility: Facility) -> Optional["FacilityInfoResponse"]:
        """
        단일 시설의 기본 스케줄 크롤링

        Args:
            facility: Facility Enum 객체

        Returns:
            FacilityInfoResponse DTO 또는 None

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

    def crawl_all_facilities(self) -> List["FacilityInfoResponse"]:
        """
        모든 시설 크롤링 (공통 로직)

        Returns:
            FacilityInfoResponse DTO 리스트
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

    def to_dict(self, facility_data: "FacilityInfoResponse") -> dict:
        """
        시설 데이터를 표준 형식으로 변환 (공통 유틸리티)

        Args:
            facility_data: FacilityInfoResponse DTO

        Returns:
            표준화된 딕셔너리
        """
        if facility_data is None:
            return {}
        return facility_data.to_dict()

    def validate_schedule(self, schedule: "FacilityInfoResponse") -> bool:
        """
        스케줄 데이터 유효성 검증

        Args:
            schedule: FacilityInfoResponse DTO

        Returns:
            유효성 여부
        """
        if schedule is None:
            self.logger.warning("스케줄 데이터가 None입니다")
            return False

        if not schedule.facility_name:
            self.logger.warning("필수 필드 누락: facility_name")
            return False

        return True
