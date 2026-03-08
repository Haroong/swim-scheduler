"""
Schedule Service
자유 수영 스케줄 데이터 조회 비즈니스 로직
"""
import logging
from typing import List, Optional
from datetime import datetime

from app.domain.facility.repository import FacilityRepository
from app.domain.schedule.repository import ScheduleRepository
from app.domain.closure.repository import ClosureRepository
from app.domain.notice.repository import NoticeRepository
from app.domain.fee.repository import FeeRepository
from app.shared.util import get_season_from_month, should_include_schedule, should_include_session
from app.shared.util.closure_utils import check_facility_closure

logger = logging.getLogger(__name__)


class ScheduleService:
    """스케줄 조회 서비스"""

    def __init__(
        self,
        facility_repo: FacilityRepository,
        schedule_repo: ScheduleRepository,
        closure_repo: ClosureRepository,
        notice_repo: NoticeRepository,
        fee_repo: FeeRepository,
    ):
        self._facility_repo = facility_repo
        self._schedule_repo = schedule_repo
        self._closure_repo = closure_repo
        self._notice_repo = notice_repo
        self._fee_repo = fee_repo

    def get_facilities(self) -> List[dict]:
        """시설 목록 조회"""
        try:
            return self._facility_repo.find_all_with_schedule_summary()
        except Exception as e:
            logger.error(f"시설 목록 조회 실패: {e}")
            return []

    def get_schedules(
        self,
        facility: Optional[str] = None,
        month: Optional[str] = None,
        season: Optional[str] = None
    ) -> List[dict]:
        """스케줄 조회"""
        try:
            schedules = self._schedule_repo.find_schedules(facility, month)

            # 자동 계절 계산 (season이 명시되지 않은 경우)
            if month and not season:
                try:
                    month_num = int(month.split('-')[1])
                    season = get_season_from_month(month_num)
                    logger.info(f"Auto-calculated season from month {month}: {season}")
                except (IndexError, ValueError) as e:
                    logger.warning(f"Could not parse month '{month}': {e}")

            # Season filtering
            if season:
                logger.info(f"Season filter applied: {season}")
                schedules = [
                    schedule for schedule in schedules
                    if should_include_schedule(schedule.season, season)
                ]
            elif not month:
                logger.info("Auto-filtering each schedule by its month's season")
                filtered_schedules = []
                for schedule in schedules:
                    try:
                        month_num = int(schedule.valid_month.split('-')[1])
                        schedule_season = get_season_from_month(month_num)
                        if should_include_schedule(schedule.season, schedule_season):
                            filtered_schedules.append(schedule)
                    except (IndexError, ValueError, AttributeError) as e:
                        logger.warning(f"Could not parse valid_month '{schedule.valid_month}': {e}")
                        filtered_schedules.append(schedule)
                schedules = filtered_schedules

            # 데이터 그룹핑 (facility + month 기준)
            schedules_map = {}

            for schedule in schedules:
                facility_id = schedule.facility.id
                facility_name = schedule.facility.name
                valid_month = schedule.valid_month

                key = f"{facility_id}_{valid_month}"

                if key not in schedules_map:
                    closures = self._closure_repo.find_by_facility_and_month(facility_id, valid_month)

                    closure_info = None
                    if closures:
                        specific_dates = [c for c in closures if c.closure_type == 'specific_date']
                        regular_closures = [c for c in closures if c.closure_type == 'regular']

                        full_closure = next(
                            (c for c in specific_dates if c.closure_date is None), None
                        )
                        if full_closure:
                            closure_info = {
                                "is_closed": True,
                                "closure_type": "monthly",
                                "reason": full_closure.reason or "임시휴장"
                            }
                        elif len(specific_dates) >= 15:
                            reason = specific_dates[0].reason if specific_dates else "임시휴장"
                            closure_info = {
                                "is_closed": True,
                                "closure_type": "monthly",
                                "reason": reason
                            }
                        elif specific_dates or regular_closures:
                            closure_info = {
                                "is_closed": False,
                                "closure_type": "partial",
                                "specific_dates": len(specific_dates),
                                "regular_closures": [
                                    {
                                        "day_of_week": c.day_of_week,
                                        "week_pattern": c.week_pattern,
                                        "reason": c.reason
                                    } for c in regular_closures
                                ]
                            }

                    schedules_map[key] = {
                        "facility_id": facility_id,
                        "facility_name": facility_name,
                        "valid_month": valid_month,
                        "schedules": {},
                        "closure_info": closure_info
                    }

                schedule_key = f"{schedule.day_type}_{schedule.season or ''}"

                if schedule_key not in schedules_map[key]["schedules"]:
                    schedules_map[key]["schedules"][schedule_key] = {
                        "day_type": schedule.day_type,
                        "season": schedule.season if schedule.season else "",
                        "sessions": []
                    }

                for session in schedule.sessions:
                    schedules_map[key]["schedules"][schedule_key]["sessions"].append({
                        "session_name": session.session_name,
                        "start_time": str(session.start_time),
                        "end_time": str(session.end_time),
                        "capacity": session.capacity,
                        "lanes": session.lanes,
                        "applicable_days": session.applicable_days
                    })

            result = []
            for key, data in schedules_map.items():
                item = {
                    "facility_id": data["facility_id"],
                    "facility_name": data["facility_name"],
                    "valid_month": data["valid_month"],
                    "schedules": list(data["schedules"].values())
                }
                if data.get("closure_info"):
                    item["closure_info"] = data["closure_info"]
                result.append(item)

            return result

        except Exception as e:
            logger.error(f"스케줄 조회 실패: {e}")
            return []

    def get_daily_schedules(self, date_str: str) -> List[dict]:
        """특정 날짜의 자유수영 스케줄 조회"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")

            weekday = date_obj.weekday()
            if weekday == 5:
                day_type = "토요일"
            elif weekday == 6:
                day_type = "일요일"
            else:
                day_type = "평일"

            season = get_season_from_month(date_obj.month)
            valid_month = f"{date_obj.year}-{date_obj.month:02d}"

            logger.info(f"날짜 조회: {date_str} → {day_type}, {season}, {valid_month}")

            schedules = self._schedule_repo.find_by_day_type_and_month(day_type, valid_month)

            # Filter by season
            schedules = [
                schedule for schedule in schedules
                if should_include_schedule(schedule.season, season)
            ]
            logger.info(f"Season filter: {season}, {len(schedules)} schedules after filtering")

            facilities_map = {}

            for schedule in schedules:
                facility_id = schedule.facility.id
                facility_name = schedule.facility.name

                if facility_id not in facilities_map:
                    notice = self._notice_repo.find_by_facility_and_month(facility_id, valid_month)

                    closures = self._closure_repo.find_by_facility_and_month(facility_id, valid_month)
                    is_closed, closure_reason = check_facility_closure(closures, date_obj, valid_month)

                    fees = self._fee_repo.find_by_facility_id(facility_id)

                    facilities_map[facility_id] = {
                        "facility_id": facility_id,
                        "facility_name": facility_name,
                        "address": schedule.facility.address,
                        "website_url": schedule.facility.website_url,
                        "date": date_str,
                        "day_type": schedule.day_type,
                        "season": schedule.season if schedule.season else "",
                        "valid_month": schedule.valid_month,
                        "sessions": [],
                        "source_url": notice.source_url if notice else None,
                        "notice_title": notice.title if notice else None,
                        "is_closed": is_closed,
                        "closure_reason": closure_reason,
                        "fees": [
                            {"category": f.category, "price": f.price, "note": f.note or ""}
                            for f in fees
                        ],
                        "crawled_at": notice.crawled_at.isoformat() if notice and notice.crawled_at else None
                    }

                    if is_closed:
                        continue

                if facilities_map[facility_id].get("is_closed"):
                    continue

                for session in schedule.sessions:
                    if not should_include_session(session.applicable_days, weekday):
                        continue

                    facilities_map[facility_id]["sessions"].append({
                        "session_name": session.session_name,
                        "start_time": str(session.start_time),
                        "end_time": str(session.end_time),
                        "capacity": session.capacity,
                        "lanes": session.lanes
                    })

            # 휴장 시설 추가
            closed_facilities = self._get_closed_facilities(
                valid_month, set(facilities_map.keys()), date_str, day_type
            )
            for closed_facility in closed_facilities:
                if closed_facility["facility_id"] not in facilities_map:
                    facilities_map[closed_facility["facility_id"]] = closed_facility

            result = list(facilities_map.values())
            logger.info(f"조회 결과: {len(result)}개 시설 (휴장 포함)")

            return result

        except ValueError as e:
            logger.error(f"날짜 파싱 실패: {date_str}, {e}")
            return []
        except Exception as e:
            logger.error(f"일별 스케줄 조회 실패: {e}")
            return []

    def _get_closed_facilities(
        self,
        valid_month: str,
        existing_facility_ids: set,
        date_str: str,
        day_type: str
    ) -> List[dict]:
        """전체 휴장 시설 조회 (스케줄이 없지만 Notice와 휴장 정보가 있는 시설)"""
        try:
            notices = self._notice_repo.find_by_valid_month(valid_month)

            closed_facilities = []
            for notice in notices:
                facility_id = notice.facility_id

                if facility_id in existing_facility_ids:
                    continue

                schedule_count = self._schedule_repo.count_by_facility_and_month(facility_id, valid_month)
                if schedule_count > 0:
                    continue

                closure = self._closure_repo.find_first_by_facility_and_month(facility_id, valid_month)
                if not closure:
                    continue

                facility = notice.facility
                fees = self._fee_repo.find_by_facility_id(facility_id)

                closed_facilities.append({
                    "facility_id": facility_id,
                    "facility_name": facility.name,
                    "address": facility.address,
                    "website_url": facility.website_url,
                    "date": date_str,
                    "day_type": day_type,
                    "season": "",
                    "valid_month": valid_month,
                    "sessions": [],
                    "source_url": notice.source_url,
                    "notice_title": notice.title,
                    "is_closed": True,
                    "closure_reason": closure.reason,
                    "fees": [
                        {"category": f.category, "price": f.price, "note": f.note or ""}
                        for f in fees
                    ],
                    "crawled_at": notice.crawled_at.isoformat() if notice.crawled_at else None
                })

            return closed_facilities

        except Exception as e:
            logger.error(f"휴장 시설 조회 실패: {e}")
            return []

    def get_calendar_data(self, year: int, month: int) -> dict:
        """달력용 데이터 조회"""
        month_str = f"{year}-{month:02d}"

        season = get_season_from_month(month)
        logger.info(f"Calendar data: {year}-{month:02d}, Season: {season}")

        schedules = self.get_schedules(month=month_str, season=season)

        return {
            "year": year,
            "month": month,
            "season": season,
            "schedules": schedules
        }
