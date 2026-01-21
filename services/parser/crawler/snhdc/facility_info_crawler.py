"""
성남도시개발공사 시설 이용안내 크롤러
각 체육센터의 일일자유이용 안내 페이지에서 기본 자유수영 운영 정보 수집
"""
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import logging
import re

from enums.facility import Facility, Organization, get_snhdc_program_url
from crawler.base.facility_crawler import BaseFacilityCrawler
from dto.crawler_dto import FacilityInfoResponse, WeekdayScheduleItem, WeekendSchedule
from utils.http_utils import create_session

logger = logging.getLogger(__name__)


class FacilityInfoCrawler(BaseFacilityCrawler):
    """
    성남도시개발공사 시설 이용안내 페이지 크롤러

    각 체육센터의 일일자유이용 안내 페이지에서 기본 정보 수집
    """

    def __init__(self):
        super().__init__()
        self.session = create_session()

    def get_target_facilities(self) -> List[Facility]:
        """크롤링 대상 시설 목록 (SNHDC 시설)"""
        return Facility.snhdc_facilities()

    def crawl_facility(self, facility: Facility) -> FacilityInfoResponse:
        """
        단일 시설의 일일자유이용 안내 크롤링

        Args:
            facility: Facility Enum 객체

        Returns:
            FacilityInfoResponse DTO
        """
        url = get_snhdc_program_url(facility)

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            self.logger.error(f"페이지 요청 실패: {e}")
            return {}

        return self._parse_facility_page(facility.name, url, response.text)

    def _parse_facility_page(self, facility_name: str, url: str, html: str) -> FacilityInfoResponse:
        """일일자유이용 안내 페이지 파싱 (다양한 HTML 구조 지원)"""
        soup = BeautifulSoup(html, "html.parser")

        # 1. tabs-2 섹션 찾기 (없을 수도 있음 - 판교스포츠센터)
        search_section = soup.find('div', id='tabs-2')
        if not search_section:
            logger.info(f"{facility_name}: tabs-2 없음, 전체 페이지에서 검색")
            search_section = soup

        # 2. 수영 섹션 찾기 (다양한 패턴 지원)
        h5_swimming = None
        swimming_patterns = [
            '수영',                  # 탄천, 성남
            '수영 일일자유이용',      # 황새울
            '일일자유 수영',          # 판교, 평생
        ]

        for pattern in swimming_patterns:
            h5_swimming = search_section.find('h5', string=lambda text: text and pattern in text)
            if h5_swimming:
                logger.info(f"{facility_name}: 수영 섹션 발견 (패턴: {pattern})")
                break

        if not h5_swimming:
            logger.warning(f"{facility_name}: 수영 섹션을 찾을 수 없습니다")
            return None

        # 3. 테이블 찾기
        table = h5_swimming.find_next('table')
        if not table:
            logger.warning(f"{facility_name}: 테이블을 찾을 수 없습니다")
            return None

        # 4. 데이터 파싱
        weekday_schedule_raw, weekend_schedule_raw, fees = self._parse_schedule_table(table)
        notes = self._parse_notes(search_section)

        # DTO로 변환
        weekday_schedule = [
            WeekdayScheduleItem(
                start_time=s.get("start_time", ""),
                end_time=s.get("end_time", ""),
                days=s.get("days", ["월", "화", "수", "목", "금"]),
                capacity=s.get("capacity", 0),
                notes=s.get("notes", "")
            )
            for s in weekday_schedule_raw
        ]

        weekend_schedule = WeekendSchedule(
            saturday=weekend_schedule_raw.get("saturday", {}),
            sunday=weekend_schedule_raw.get("sunday", {})
        )

        return FacilityInfoResponse(
            facility_name=facility_name,
            facility_url=url,
            weekday_schedule=weekday_schedule,
            weekend_schedule=weekend_schedule,
            fees=fees,
            notes=notes
        )

    def _parse_schedule_table(self, table) -> tuple:
        """
        테이블에서 스케줄과 이용료 정보 파싱

        Returns:
            (weekday_schedule, weekend_schedule, fees)
        """
        weekday_schedule = []
        weekend_schedule = {"saturday": {}, "sunday": {}}
        fees = {}

        tbody = table.find('tbody')
        if not tbody:
            return weekday_schedule, weekend_schedule, fees

        rows = tbody.find_all('tr')

        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 3:  # 최소 3개 컬럼 필요 (rowspan 때문에 5개 미만일 수 있음)
                continue

            # rowspan으로 인해 컬럼 수가 다를 수 있음
            # 5개 컬럼: 대상(0), 시간(1), 요일(2), 정원(3), 이용료(4)
            # 3개 컬럼: 시간(0), 요일(1), 정원(2) - rowspan으로 대상/이용료 생략
            if len(cols) >= 5:
                time_text = cols[1].get_text(strip=True)
                day_text = cols[2].get_text(strip=True)
                capacity_text = cols[3].get_text(strip=True)
                fee_text = cols[4].get_text(strip=True)
            else:
                # rowspan으로 대상/이용료 생략된 경우
                time_text = cols[0].get_text(strip=True)
                day_text = cols[1].get_text(strip=True)
                capacity_text = cols[2].get_text(strip=True)
                fee_text = ""

            # 시간 파싱 (예: "12:00~13:50")
            time_match = re.search(r'(\d{2}:\d{2})~(\d{2}:\d{2})', time_text)
            if not time_match:
                continue

            start_time = time_match.group(1)
            end_time = time_match.group(2)

            # 정원 파싱 (예: "200명", "25M 120명")
            capacity = self._extract_capacity(capacity_text)

            # 요일 분류 (다양한 패턴 지원)
            if '월~금' in day_text or '월-금' in day_text or '월,화,목,금' in day_text:
                # 평일
                schedule_item = {
                    "start_time": start_time,
                    "end_time": end_time,
                    "days": ["월", "화", "수", "목", "금"],
                    "capacity": capacity,
                    "notes": day_text
                }
                weekday_schedule.append(schedule_item)

            elif '토' in day_text and '일' not in day_text and '공휴일' not in day_text:
                # 토요일만 (토ㆍ일, 토요일, 토 등)
                if "sessions" not in weekend_schedule["saturday"]:
                    weekend_schedule["saturday"]["sessions"] = []
                weekend_schedule["saturday"]["sessions"].append({
                    "start_time": start_time,
                    "end_time": end_time,
                    "capacity": capacity,
                    "notes": day_text
                })

            elif '일' in day_text or '공휴일' in day_text:
                # 일요일/공휴일 또는 "토ㆍ일" 패턴
                if "sessions" not in weekend_schedule["sunday"]:
                    weekend_schedule["sunday"]["sessions"] = []
                weekend_schedule["sunday"]["sessions"].append({
                    "start_time": start_time,
                    "end_time": end_time,
                    "capacity": capacity,
                    "notes": day_text
                })

            # 이용료 파싱 (첫 번째로 발견된 것만 저장)
            if fee_text and not fees:
                fees = self._parse_fee_text(fee_text)

        return weekday_schedule, weekend_schedule, fees

    def _extract_capacity(self, text: str) -> int:
        """정원 텍스트에서 숫자 추출"""
        # "200명" 또는 "25M 120명" 형식
        numbers = re.findall(r'(\d+)명', text)
        if numbers:
            return int(numbers[-1])  # 마지막 숫자 사용
        return 0

    def _parse_fee_text(self, text: str) -> Dict:
        """이용료 텍스트 파싱"""
        fees = {}

        # "일반 3,600원청소년  3,000원어린이  2,400원2시간 기준" 형식
        # 일반 추출
        general_match = re.search(r'일반[^\d]*(\d{1,},?\d{0,3})원', text)
        if general_match:
            fees["일반"] = int(general_match.group(1).replace(',', ''))

        # 청소년 추출
        youth_match = re.search(r'청소년[^\d]*(\d{1,},?\d{0,3})원', text)
        if youth_match:
            fees["청소년"] = int(youth_match.group(1).replace(',', ''))

        # 어린이 추출
        child_match = re.search(r'어린이[^\d]*(\d{1,},?\d{0,3})원', text)
        if child_match:
            fees["어린이"] = int(child_match.group(1).replace(',', ''))

        return fees

    def _parse_notes(self, tabs2_section) -> List[str]:
        """주의사항 및 공지사항 파싱"""
        notes = []

        # 테이블 하단의 안내 사항 찾기
        # ul 태그나 p 태그에서 주의사항 추출
        for ul in tabs2_section.find_all('ul'):
            for li in ul.find_all('li'):
                text = li.get_text(strip=True)
                if text and len(text) > 5:  # 너무 짧은 텍스트 제외
                    notes.append(text)

        # p 태그에서도 추출
        for p in tabs2_section.find_all('p'):
            text = p.get_text(strip=True)
            if text and len(text) > 10 and '※' in text:
                notes.append(text)

        return notes[:10]  # 최대 10개

    def to_dict(self, facility_info: FacilityInfoResponse) -> Dict:
        """시설 정보 딕셔너리 반환"""
        if facility_info is None:
            return {}
        return facility_info.to_dict()


# 테스트용 코드
if __name__ == "__main__":
    crawler = FacilityInfoCrawler()

    # 먼저 한 개 시설만 테스트
    print("=== 탄천종합운동장 HTML 구조 확인 ===")
    import requests
    response = requests.get("https://spo.isdc.co.kr/tan_programGuide.do")

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # 일일자유이용 탭 찾기
    tabs = soup.find_all("li")
    for tab in tabs:
        if "일일자유" in tab.get_text():
            print(f"탭 발견: {tab.get_text()}")
            print(f"탭 HTML: {tab}")

    print("\n" + "="*60)
    print("전체 시설 크롤링 테스트")
    print("="*60)

    facilities = crawler.crawl_all_facilities()

    import json
    for facility in facilities:
        if facility:
            print(f"\n{'='*60}")
            print(f"{facility.facility_name}")
            print(f"{'='*60}")
            print(json.dumps(facility.to_dict(), ensure_ascii=False, indent=2))
