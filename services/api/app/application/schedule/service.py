"""
Schedule Service
자유 수영 스케줄 데이터 조회 비즈니스 로직
"""
import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload

from app.domain import Facility, SwimSchedule, SwimSession, Notice
from app.domain.closure import FacilityClosure
from app.shared.util import get_season_from_month, should_include_schedule, should_include_session, check_facility_closure

logger = logging.getLogger(__name__)


class ScheduleService:
    """스케줄 조회 서비스"""

    @staticmethod
    def get_facilities(db: Session) -> List[dict]:
        """
        시설 목록 조회

        Args:
            db: SQLAlchemy Session

        Returns:
            시설명, 최신 월, 스케줄 개수
        """
        try:
            # Facility + SwimSchedule 조인, 집계
            stmt = (
                select(
                    Facility.id,
                    Facility.name,
                    func.max(SwimSchedule.valid_month).label('latest_month'),
                    func.count(func.distinct(SwimSchedule.id)).label('schedule_count')
                )
                .outerjoin(SwimSchedule)
                .group_by(Facility.id, Facility.name)
                .order_by(Facility.name)
            )

            results = db.execute(stmt).all()

            facilities = []
            for row in results:
                facilities.append({
                    "facility_id": row.id,
                    "facility_name": row.name,
                    "latest_month": row.latest_month if row.latest_month else None,
                    "schedule_count": row.schedule_count
                })

            return facilities

        except Exception as e:
            logger.error(f"시설 목록 조회 실패: {e}")
            return []

    @staticmethod
    def get_schedules(
        db: Session,
        facility: Optional[str] = None,
        month: Optional[str] = None,
        season: Optional[str] = None
    ) -> List[dict]:
        """
        스케줄 조회

        Args:
            db: SQLAlchemy Session
            facility: 시설명 (예: "야탑유스센터")
            month: 월 (예: "2026-01" 또는 "2026-02")
            season: 계절 필터 (예: "하절기", "동절기") - 제공시 해당 계절만 반환

        Returns:
            스케줄 목록
        """
        try:
            stmt = (
                select(SwimSchedule)
                .join(SwimSchedule.facility)
                .options(
                    selectinload(SwimSchedule.facility),
                    selectinload(SwimSchedule.sessions)
                )
                .order_by(
                    SwimSchedule.valid_month.desc(),
                    Facility.name,
                    SwimSchedule.day_type
                )
            )

            # 동적 필터
            if facility:
                stmt = stmt.where(Facility.name == facility)

            if month:
                stmt = stmt.where(SwimSchedule.valid_month == month)
                # 자동 계절 계산 (season이 명시되지 않은 경우)
                if not season:
                    try:
                        # month에서 월 추출 (YYYY-MM 형식)
                        month_num = int(month.split('-')[1])
                        season = get_season_from_month(month_num)
                        logger.info(f"Auto-calculated season from month {month}: {season}")
                    except (IndexError, ValueError) as e:
                        logger.warning(f"Could not parse month '{month}': {e}")

            schedules = db.execute(stmt).scalars().all()

            # Season filtering
            if season:
                # 명시적으로 season이 제공된 경우
                logger.info(f"Season filter applied: {season}")
                schedules = [
                    schedule for schedule in schedules
                    if should_include_schedule(schedule.season, season)
                ]
            elif not month:
                # month가 없는 경우, 각 스케줄의 valid_month를 기반으로 계절 필터링
                logger.info("Auto-filtering each schedule by its month's season")
                filtered_schedules = []
                for schedule in schedules:
                    try:
                        # valid_month에서 월 추출 (YYYY-MM 형식)
                        month_num = int(schedule.valid_month.split('-')[1])
                        schedule_season = get_season_from_month(month_num)
                        if should_include_schedule(schedule.season, schedule_season):
                            filtered_schedules.append(schedule)
                    except (IndexError, ValueError, AttributeError) as e:
                        logger.warning(f"Could not parse valid_month '{schedule.valid_month}': {e}")
                        filtered_schedules.append(schedule)  # 파싱 실패시 포함
                schedules = filtered_schedules

            # 데이터 그룹핑 (facility + month 기준)
            schedules_map = {}

            for schedule in schedules:
                facility_id = schedule.facility.id
                facility_name = schedule.facility.name
                valid_month = schedule.valid_month

                # 시설+월 키
                key = f"{facility_id}_{valid_month}"

                if key not in schedules_map:
                    # 휴장 정보 조회
                    closure_stmt = (
                        select(FacilityClosure)
                        .where(
                            FacilityClosure.facility_id == facility_id,
                            FacilityClosure.valid_month == valid_month
                        )
                    )
                    closures = db.execute(closure_stmt).scalars().all()

                    # 휴장 정보 파싱
                    closure_info = None
                    if closures:
                        # 월 전체 휴장 여부 판단 (specific_date가 많거나 reason에 '휴장' 포함)
                        specific_dates = [c for c in closures if c.closure_type == 'specific_date']
                        regular_closures = [c for c in closures if c.closure_type == 'regular']

                        # 임시휴장 판단: 특정 날짜 휴무가 15일 이상이면 월 전체 휴장으로 간주
                        if len(specific_dates) >= 15:
                            reason = specific_dates[0].reason if specific_dates else "임시휴장"
                            closure_info = {
                                "is_closed": True,
                                "closure_type": "monthly",
                                "reason": reason
                            }
                        elif specific_dates or regular_closures:
                            # 부분 휴장 정보
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

                # 스케줄 키 (day_type + season)
                schedule_key = f"{schedule.day_type}_{schedule.season or ''}"

                if schedule_key not in schedules_map[key]["schedules"]:
                    schedules_map[key]["schedules"][schedule_key] = {
                        "day_type": schedule.day_type,
                        "season": schedule.season if schedule.season else "",
                        "sessions": []
                    }

                # 세션 추가
                for session in schedule.sessions:
                    schedules_map[key]["schedules"][schedule_key]["sessions"].append({
                        "session_name": session.session_name,
                        "start_time": str(session.start_time),
                        "end_time": str(session.end_time),
                        "capacity": session.capacity,
                        "lanes": session.lanes,
                        "applicable_days": session.applicable_days
                    })

            # 결과 변환
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

    @staticmethod
    def get_daily_schedules(db: Session, date_str: str) -> List[dict]:
        """
        특정 날짜의 자유수영 스케줄 조회

        Args:
            db: SQLAlchemy Session
            date_str: 날짜 (예: "2026-01-18")

        Returns:
            해당 날짜에 운영하는 모든 시설의 스케줄 목록
        """
        try:
            # 1. 날짜 파싱
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")

            # 2. 요일 계산
            weekday = date_obj.weekday()  # 0=월요일, 6=일요일
            if weekday == 5:
                day_type = "토요일"
            elif weekday == 6:
                day_type = "일요일"
            else:
                day_type = "평일"

            # 3. 계절 판단 (월 기준: 3~10월=하절기, 11~2월=동절기)
            season = get_season_from_month(date_obj.month)

            # 4. valid_month 생성 (YYYY-MM 형식)
            valid_month = f"{date_obj.year}-{date_obj.month:02d}"

            logger.info(f"날짜 조회: {date_str} → {day_type}, {season}, {valid_month}")

            # 5. ORM 쿼리
            stmt = (
                select(SwimSchedule)
                .join(SwimSchedule.facility)
                .options(
                    selectinload(SwimSchedule.facility),
                    selectinload(SwimSchedule.sessions)
                )
                .where(
                    SwimSchedule.day_type == day_type,
                    SwimSchedule.valid_month == valid_month
                )
                .order_by(Facility.name)
            )

            schedules = db.execute(stmt).scalars().all()

            # Filter by season
            schedules = [
                schedule for schedule in schedules
                if should_include_schedule(schedule.season, season)
            ]
            logger.info(f"Season filter: {season}, {len(schedules)} schedules after filtering")

            # 시설별로 데이터 구성
            facilities_map = {}

            for schedule in schedules:
                facility_id = schedule.facility.id
                facility_name = schedule.facility.name

                if facility_id not in facilities_map:
                    # Notice 정보 조회 (해당 시설 + 월)
                    notice_stmt = (
                        select(Notice)
                        .where(
                            Notice.facility_id == facility_id,
                            Notice.valid_date == valid_month
                        )
                        .limit(1)
                    )
                    notice = db.execute(notice_stmt).scalar_one_or_none()

                    # 휴무일 체크
                    is_closed, closure_reason = check_facility_closure(
                        db, facility_id, date_obj, valid_month
                    )

                    facilities_map[facility_id] = {
                        "facility_id": facility_id,
                        "facility_name": facility_name,
                        "date": date_str,
                        "day_type": schedule.day_type,
                        "season": schedule.season if schedule.season else "",
                        "valid_month": schedule.valid_month,
                        "sessions": [],
                        "source_url": notice.source_url if notice else None,
                        "notice_title": notice.title if notice else None,
                        "is_closed": is_closed,
                        "closure_reason": closure_reason
                    }

                    # 휴무일이면 세션 추가 건너뛰기
                    if is_closed:
                        continue

                # 휴무일이면 세션 추가 건너뛰기
                if facilities_map[facility_id].get("is_closed"):
                    continue

                # 세션 추가 (applicable_days 필터링 적용)
                for session in schedule.sessions:
                    # 해당 요일에 적용되는 세션만 포함
                    if not should_include_session(session.applicable_days, weekday):
                        continue

                    facilities_map[facility_id]["sessions"].append({
                        "session_name": session.session_name,
                        "start_time": str(session.start_time),
                        "end_time": str(session.end_time),
                        "capacity": session.capacity,
                        "lanes": session.lanes
                    })

            result = list(facilities_map.values())
            logger.info(f"조회 결과: {len(result)}개 시설")

            return result

        except ValueError as e:
            logger.error(f"날짜 파싱 실패: {date_str}, {e}")
            return []
        except Exception as e:
            logger.error(f"일별 스케줄 조회 실패: {e}")
            return []

    @staticmethod
    def get_calendar_data(db: Session, year: int, month: int) -> dict:
        """
        달력용 데이터 조회

        Args:
            db: SQLAlchemy Session
            year: 년도 (예: 2026)
            month: 월 (1-12)

        Returns:
            달력 데이터 (해당 월의 계절에 맞는 스케줄만 포함)
        """
        month_str = f"{year}-{month:02d}"

        # Calculate season for the requested month
        season = get_season_from_month(month)
        logger.info(f"Calendar data: {year}-{month:02d}, Season: {season}")

        # Get schedules with season filter
        schedules = ScheduleService.get_schedules(db, month=month_str, season=season)

        return {
            "year": year,
            "month": month,
            "season": season,  # 응답에 계절 정보 추가
            "schedules": schedules
        }
