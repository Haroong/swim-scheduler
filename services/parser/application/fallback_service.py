"""
공지 없는 시설에 base_schedule 폴백 데이터를 생성·저장하는 서비스
"""
import re
from collections import Counter
from pathlib import Path

from infrastructure.config.logging_config import get_logger
from application.storage_service import StorageService
from infrastructure.database.repository import SwimRepository
from core.models.facility import Organization

logger = get_logger(__name__)


class FallbackService:
    """공지 없는 시설에 base_schedule 폴백 데이터를 생성·저장하는 서비스"""

    def __init__(self, storage_dir: Path):
        self.storage = StorageService(storage_dir)

    def generate_and_save(self, validated_results=None):
        """공지 없는 시설에 base_schedules 폴백을 생성하여 DB에 저장"""
        logger.info("=== 4단계: base_schedule 폴백 저장 시작 ===")

        if validated_results is None:
            validated_results = self.storage.load_validated_parsed_data()

        # 1. 대상 월 결정
        target_month = self._get_target_month(validated_results)
        if not target_month:
            logger.warning("대상 월을 결정할 수 없음. 폴백 저장 건너뜀.")
            return

        logger.info(f"대상 월: {target_month}")

        # 2. 이미 커버된 시설 목록
        covered = self._get_covered_facilities(validated_results, target_month)
        logger.info(f"이미 커버된 시설: {covered}")

        # 3. base_schedules 로드 및 폴백 데이터 생성
        fallback_data = []

        for org in Organization:
            base_facilities = self.storage.load_base_schedules(org)
            for facility in base_facilities:
                fname = facility.get("facility_name", "")
                if fname in covered:
                    continue

                # 스케줄이 있는 시설만 폴백 생성
                has_weekday = bool(facility.get("weekday_schedule"))
                has_weekend = bool(
                    facility.get("weekend_schedule", {}).get("saturday")
                    or facility.get("weekend_schedule", {}).get("sunday")
                )
                if not has_weekday and not has_weekend:
                    continue

                parsed = self._convert_base_to_parsed(facility, target_month)
                fallback_data.append(parsed)
                logger.info(f"폴백 생성: {fname}")

        if not fallback_data:
            logger.info("폴백 대상 시설 없음")
            return

        # 4. DB 저장
        with SwimRepository() as repo:
            success_count = 0
            for data in fallback_data:
                if repo.save_parsed_data(data):
                    success_count += 1

        logger.info(f"폴백 저장 완료: {success_count}/{len(fallback_data)}개")
        logger.info("=== 4단계 완료 ===")

    @staticmethod
    def _get_target_month(validated_results: list) -> str | None:
        """validated_results에서 가장 많이 등장하는 valid_month 반환"""
        months = [r.get("valid_month", "") for r in validated_results if r.get("valid_month")]
        if not months:
            return None
        return Counter(months).most_common(1)[0][0]

    @staticmethod
    def _get_covered_facilities(validated_results: list, target_month: str) -> set:
        """validated_results에서 해당 월에 이미 스케줄이 있는 시설명 set 반환"""
        return {
            r.get("facility_name")
            for r in validated_results
            if r.get("valid_month") == target_month
        }

    @staticmethod
    def _convert_base_to_parsed(facility: dict, target_month: str) -> dict:
        """base_schedule 데이터를 parsed_data 형식으로 변환"""
        facility_name = facility.get("facility_name", "")
        facility_url = facility.get("facility_url", "")

        # valid_month "2026년 2월" → "2026-02"
        match = re.search(r"(\d{4})년\s*(\d{1,2})월", target_month)
        yyyy_mm = f"{match.group(1)}-{match.group(2).zfill(2)}" if match else ""

        source_url = f"{facility_url}#base-{yyyy_mm}"

        schedules = []

        # 1. 평일 스케줄
        weekday_schedule = facility.get("weekday_schedule", [])
        if weekday_schedule:
            weekday_sessions = []
            for entry in weekday_schedule:
                days = entry.get("days", [])
                session_name = entry.get("type", "") or entry.get("start_time", "")

                applicable_days = None
                if days and set(days) != {"월", "화", "수", "목", "금"}:
                    applicable_days = ",".join(days)

                weekday_sessions.append({
                    "session_name": session_name,
                    "start_time": entry.get("start_time", ""),
                    "end_time": entry.get("end_time", ""),
                    "capacity": entry.get("capacity", 0),
                    "lanes": None,
                    "applicable_days": applicable_days,
                })

            if weekday_sessions:
                schedules.append({
                    "day_type": "평일",
                    "season": "",
                    "sessions": weekday_sessions,
                })

        # 2. 주말 스케줄
        weekend_schedule = facility.get("weekend_schedule", {})
        for day_key, day_label in [("saturday", "토요일"), ("sunday", "일요일")]:
            day_data = weekend_schedule.get(day_key, {})
            if not day_data:
                continue

            weekend_sessions = []

            # snyouth 형식: "parts"
            if "parts" in day_data:
                for part in day_data["parts"]:
                    weekend_sessions.append({
                        "session_name": f"{part.get('part', '')}부",
                        "start_time": part.get("start", ""),
                        "end_time": part.get("end", ""),
                        "capacity": 0,
                        "lanes": None,
                        "applicable_days": None,
                    })

            # snhdc 형식: "sessions"
            elif "sessions" in day_data:
                for i, session in enumerate(day_data["sessions"], 1):
                    weekend_sessions.append({
                        "session_name": f"{i}부",
                        "start_time": session.get("start_time", ""),
                        "end_time": session.get("end_time", ""),
                        "capacity": session.get("capacity", 0),
                        "lanes": None,
                        "applicable_days": None,
                    })

            if weekend_sessions:
                schedules.append({
                    "day_type": day_label,
                    "season": "",
                    "sessions": weekend_sessions,
                })

        # 3. 이용료
        fees_dict = facility.get("fees", {})
        fees = [
            {"category": category, "price": price, "note": ""}
            for category, price in fees_dict.items()
        ]

        # 4. 비고
        notes = facility.get("notes", [])

        return {
            "facility_name": facility_name,
            "valid_month": target_month,
            "source_url": source_url,
            "source_notice_title": f"{facility_name} 시설 안내 (기본 스케줄)",
            "schedules": schedules,
            "fees": fees,
            "closures": [],
            "notes": notes,
        }
