"""
시설 이용안내 크롤러
각 유스센터의 이용안내 페이지에서 기본 자유수영 운영 정보 수집
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
import re

from models.enum.facility import Facility, Organization, get_snyouth_facility_url
from crawler.base.facility_crawler import BaseFacilityCrawler
from dto.crawler_dto import FacilityInfoResponse, WeekdayScheduleItem, WeekendSchedule

logger = logging.getLogger(__name__)


class FacilityInfoCrawler(BaseFacilityCrawler):
    """
    성남시청소년청년재단 시설 이용안내 페이지 크롤러

    각 유스센터의 이용안내 페이지에서 기본 정보 수집
    """

    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def get_target_facilities(self) -> List[Facility]:
        """크롤링 대상 시설 목록 (SNYOUTH 시설)"""
        return Facility.snyouth_facilities()

    def crawl_facility(self, facility: Facility) -> FacilityInfoResponse:
        """
        단일 시설의 이용안내 크롤링

        Args:
            facility: Facility Enum 객체

        Returns:
            FacilityInfoResponse DTO
        """
        url = get_snyouth_facility_url(facility)

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            self.logger.error(f"페이지 요청 실패: {e}")
            return {}

        return self._parse_facility_page(facility.name, url, response.text)

    def _parse_facility_page(self, facility_name: str, url: str, html: str) -> FacilityInfoResponse:
        """이용안내 페이지 파싱"""
        soup = BeautifulSoup(html, "html.parser")

        # 본문 콘텐츠 찾기
        contents = soup.find('div', class_='contents')
        if not contents:
            self.logger.error("콘텐츠 영역을 찾을 수 없습니다")
            return None

        text = contents.get_text()

        # 데이터 파싱
        weekday_schedule_raw = self._parse_weekday_schedule(text)
        weekend_schedule_raw = self._parse_weekend_schedule(text)
        fees = self._parse_fees(text)
        notes = self._parse_notes(text)

        # DTO로 변환
        weekday_schedule = [
            WeekdayScheduleItem(
                start_time=s.get("start_time", ""),
                end_time=s.get("end_time", ""),
                days=s.get("days", ["월", "화", "수", "목", "금"]),
                type=s.get("type", ""),
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

    def _parse_weekday_schedule(self, text: str) -> List[Dict]:
        """평일 스케줄 파싱"""
        schedules = []

        # 평일 시간 패턴 찾기 (여러 형식 지원)
        patterns = [
            # 1. "평일(아침)" 형식
            (r'평일\s*\(?\s*아침\s*\)?\s*(\d{2}:\d{2})\s*~\s*(\d{2}:\d{2})', "아침"),
            (r'평일\s*\(?\s*점심\s*\)?\s*(\d{2}:\d{2})\s*~\s*(\d{2}:\d{2})', "점심"),
            (r'평일\s*\(?\s*저녁\s*\)?\s*(\d{2}:\d{2})\s*~\s*(\d{2}:\d{2})', "저녁"),
            (r'평일\s*\(?\s*월\s*,?\s*수\s*,?\s*금\s*\)?\s*(\d{2}:\d{2})\s*~\s*(\d{2}:\d{2})', "월수금 오후"),
        ]

        for pattern, schedule_type in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                start_time = match.group(1)
                end_time = match.group(2)
                schedules.append({
                    "type": schedule_type,
                    "start_time": start_time,
                    "end_time": end_time,
                    "days": ["월", "화", "수", "목", "금"] if "월수금" not in schedule_type else ["월", "수", "금"]
                })

        # 2. "평일(월~금)" 뒤에 연속된 시간들 - 판교 형식
        #    예: "평일(월~금) 08:00~08:50 14:00~14:50"
        weekday_section_match = re.search(r'평일\s*\(?\s*월\s*~\s*금\s*\)?([^토일]+?)(?=토요일|일요일|이용료|이용수칙|$)', text)
        if weekday_section_match:
            weekday_section = weekday_section_match.group(1)
            # 시간대 모두 추출
            time_matches = re.findall(r'(\d{2}:\d{2})\s*~\s*(\d{2}:\d{2})', weekday_section)

            # 시간대별로 타입 추정
            for idx, (start, end) in enumerate(time_matches):
                # 이미 추가된 시간인지 확인 (중복 방지)
                if not any(s['start_time'] == start and s['end_time'] == end for s in schedules):
                    # 시간대로 타입 추정
                    hour = int(start.split(':')[0])
                    if hour < 10:
                        schedule_type = "아침"
                    elif hour < 16:
                        schedule_type = "오후"
                    else:
                        schedule_type = "저녁"

                    schedules.append({
                        "type": schedule_type,
                        "start_time": start,
                        "end_time": end,
                        "days": ["월", "화", "수", "목", "금"]
                    })

        return schedules

    def _parse_weekend_schedule(self, text: str) -> Dict:
        """주말 스케줄 파싱"""
        schedule = {
            "saturday": {},
            "sunday": {}
        }

        # 토요일 하절기/동절기 시간
        summer_match = re.search(r'하절기[^\d]*(\d{2}:\d{2})\s*~\s*(\d{2}:\d{2})', text)
        if summer_match:
            schedule["saturday"]["summer"] = {
                "start": summer_match.group(1),
                "end": summer_match.group(2),
                "months": "3~10월"
            }

        winter_match = re.search(r'동절기[^\d]*(\d{2}:\d{2})\s*~\s*(\d{2}:\d{2})', text)
        if winter_match:
            schedule["saturday"]["winter"] = {
                "start": winter_match.group(1),
                "end": winter_match.group(2),
                "months": "11~2월"
            }

        # 일요일 시간 (부별 정보 포함)
        sunday_parts = []
        part_pattern = r'\((\d+)부\)\s*(\d{2}:\d{2})\s*~\s*(\d{2}:\d{2})'
        for match in re.finditer(part_pattern, text):
            if "일요일" in text[max(0, match.start()-50):match.start()]:
                sunday_parts.append({
                    "part": match.group(1),
                    "start": match.group(2),
                    "end": match.group(3)
                })

        if sunday_parts:
            schedule["sunday"]["parts"] = sunday_parts

        return schedule

    def _parse_fees(self, text: str) -> Dict:
        """이용료 파싱"""
        fees = {}

        # 이용료 패턴
        fee_patterns = [
            (r'만\s*9세\s*미만[^\d]*(\d{1,},?\d{0,3})\s*원', "만9세미만"),
            (r'만\s*9세\s*~\s*만\s*24세[^\d]*(\d{1,},?\d{0,3})\s*원', "만9-24세"),
            (r'만\s*24세\s*이하[^\d]*(\d{1,},?\d{0,3})\s*원', "만24세이하"),
            (r'초\s*2\s*이하[^\d]*(\d{1,},?\d{0,3})\s*원', "초2이하"),
            (r'초\s*3\s*이상\s*~?\s*만\s*24세\s*이하[^\d]*(\d{1,},?\d{0,3})\s*원', "초3이상-만24세"),
            (r'성\s*인[^\d]*(\d{1,},?\d{0,3})\s*원', "성인"),
        ]

        for pattern, fee_type in fee_patterns:
            match = re.search(pattern, text)
            if match:
                fee_str = match.group(1).replace(',', '')
                fees[fee_type] = int(fee_str)

        return fees

    def _parse_notes(self, text: str) -> List[str]:
        """주의사항 및 공지사항 파싱"""
        notes = []

        # 이용수칙 섹션 찾기
        if "이용수칙" in text:
            rules_start = text.find("이용수칙")
            rules_end = text.find("공지사항", rules_start)
            if rules_end == -1:
                rules_end = text.find("만족도", rules_start)

            if rules_end != -1:
                rules_section = text[rules_start:rules_end]
                # 번호가 있는 항목 찾기 (1., 2., 3. 등)
                rule_matches = re.findall(r'\d+\.\s*([^\d\n]+?)(?=\d+\.|$)', rules_section)
                notes.extend([r.strip() for r in rule_matches if r.strip()])

        # 공지사항 섹션
        if "공지사항" in text:
            notice_start = text.find("공지사항")
            notice_end = text.find("만족도", notice_start)
            if notice_end == -1:
                notice_end = len(text)

            notice_section = text[notice_start:notice_end]
            notice_matches = re.findall(r'\d+\.\s*([^\d\n]+?)(?=\d+\.|$)', notice_section)
            notes.extend([n.strip() for n in notice_matches if n.strip()])

        return notes[:10]  # 최대 10개


# 테스트용 코드
if __name__ == "__main__":
    crawler = FacilityInfoCrawler()
    facilities = crawler.crawl_all_facilities()

    import json
    for facility in facilities:
        print(f"\n{'='*60}")
        print(f"{facility.facility_name}")
        print(f"{'='*60}")
        print(json.dumps(facility.to_dict(), ensure_ascii=False, indent=2))
