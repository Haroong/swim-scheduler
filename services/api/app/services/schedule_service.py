"""
Schedule Service
DB에서 스케줄 데이터를 조회하는 비즈니스 로직
"""
import json
import logging
from typing import List, Optional
from datetime import datetime

from app.database import get_connection, close_connection

logger = logging.getLogger(__name__)


class ScheduleService:
    """스케줄 조회 서비스"""

    @staticmethod
    def get_facilities() -> List[dict]:
        """
        시설 목록 조회

        Returns:
            시설명, 최신 월, 스케줄 개수
        """
        conn = get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            query = """
                SELECT
                    f.id,
                    f.name,
                    MAX(s.valid_month) as latest_month,
                    COUNT(DISTINCT s.id) as schedule_count
                FROM facility f
                LEFT JOIN swim_schedule s ON f.id = s.facility_id
                GROUP BY f.id, f.name
                ORDER BY f.name
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            facilities = []
            for row in rows:
                facilities.append({
                    "facility_id": row[0],
                    "facility_name": row[1],
                    "latest_month": row[2] if row[2] else None,
                    "schedule_count": row[3]
                })

            return facilities

        except Exception as e:
            logger.error(f"시설 목록 조회 실패: {e}")
            return []
        finally:
            close_connection(conn)

    @staticmethod
    def get_schedules(
        facility: Optional[str] = None,
        month: Optional[str] = None
    ) -> List[dict]:
        """
        스케줄 조회

        Args:
            facility: 시설명 (예: "야탑유스센터")
            month: 월 (예: "2026-01" 또는 "2026-02")

        Returns:
            스케줄 목록
        """
        conn = get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()

            # 기본 쿼리: facility, swim_schedule, swim_session JOIN
            query = """
                SELECT
                    f.id as facility_id,
                    f.name as facility_name,
                    s.id as schedule_id,
                    s.day_type,
                    s.season,
                    s.valid_month,
                    ss.id as session_id,
                    ss.session_name,
                    ss.start_time,
                    ss.end_time,
                    ss.capacity,
                    ss.lanes
                FROM facility f
                JOIN swim_schedule s ON f.id = s.facility_id
                JOIN swim_session ss ON s.id = ss.schedule_id
                WHERE 1=1
            """
            params = []

            if facility:
                query += " AND f.name = %s"
                params.append(facility)

            if month:
                query += " AND s.valid_month = %s"
                params.append(month)

            query += " ORDER BY f.name, s.valid_month, s.day_type, ss.start_time"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            # 데이터 그룹핑 (facility + month 기준)
            schedules_map = {}
            for row in rows:
                facility_id = row[0]
                facility_name = row[1]
                schedule_id = row[2]
                day_type = row[3]
                season = row[4]
                valid_month = row[5]
                session_name = row[7]
                start_time = str(row[8])
                end_time = str(row[9])
                capacity = row[10]
                lanes = row[11]

                # 시설+월 키
                key = f"{facility_id}_{valid_month}"

                if key not in schedules_map:
                    schedules_map[key] = {
                        "facility_id": facility_id,
                        "facility_name": facility_name,
                        "valid_month": valid_month,
                        "schedules": {}
                    }

                # 스케줄 키 (day_type + season)
                schedule_key = f"{day_type}_{season}"
                if schedule_key not in schedules_map[key]["schedules"]:
                    schedules_map[key]["schedules"][schedule_key] = {
                        "day_type": day_type,
                        "season": season if season else "",
                        "sessions": []
                    }

                # 세션 추가
                schedules_map[key]["schedules"][schedule_key]["sessions"].append({
                    "session_name": session_name,
                    "start_time": start_time,
                    "end_time": end_time,
                    "capacity": capacity,
                    "lanes": lanes
                })

            # 결과 변환
            result = []
            for key, data in schedules_map.items():
                result.append({
                    "facility_id": data["facility_id"],
                    "facility_name": data["facility_name"],
                    "valid_month": data["valid_month"],
                    "schedules": list(data["schedules"].values())
                })

            return result

        except Exception as e:
            logger.error(f"스케줄 조회 실패: {e}")
            return []
        finally:
            close_connection(conn)

    @staticmethod
    def get_daily_schedules(date_str: str) -> List[dict]:
        """
        특정 날짜의 자유수영 스케줄 조회

        Args:
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
            month = date_obj.month
            if 3 <= month <= 10:
                season = "하절기"
            else:
                season = "동절기"

            # 4. valid_month 생성 (YYYY-MM 형식)
            valid_month = f"{date_obj.year}-{date_obj.month:02d}"

            logger.info(f"날짜 조회: {date_str} → {day_type}, {season}, {valid_month}")

            # 5. DB 조회
            conn = get_connection()
            if not conn:
                return []

            try:
                cursor = conn.cursor()

                # 해당 날짜에 맞는 스케줄 조회
                # 현재 대부분의 시설이 season을 사용하지 않으므로 season 필터는 제외
                # TODO: season이 있는 시설의 경우 계절별로 다른 스케줄을 보여주도록 개선 필요
                query = """
                    SELECT
                        f.id as facility_id,
                        f.name as facility_name,
                        s.id as schedule_id,
                        s.day_type,
                        s.season,
                        s.valid_month,
                        ss.id as session_id,
                        ss.session_name,
                        ss.start_time,
                        ss.end_time,
                        ss.capacity,
                        ss.lanes,
                        n.source_url,
                        n.notes
                    FROM facility f
                    JOIN swim_schedule s ON f.id = s.facility_id
                    JOIN swim_session ss ON s.id = ss.schedule_id
                    LEFT JOIN notice n ON s.facility_id = n.facility_id AND s.valid_month = n.valid_date
                    WHERE s.day_type = %s
                        AND s.valid_month = %s
                    ORDER BY f.name, ss.start_time
                """

                cursor.execute(query, [day_type, valid_month])
                rows = cursor.fetchall()

                # 시설별로 그룹핑
                facilities_map = {}
                for row in rows:
                    facility_id = row[0]
                    facility_name = row[1]
                    day_type_db = row[3]
                    season_db = row[4]
                    valid_month_db = row[5]
                    session_name = row[7]
                    start_time = str(row[8])
                    end_time = str(row[9])
                    capacity = row[10]
                    lanes = row[11]
                    source_url = row[12]
                    notes = row[13]

                    if facility_id not in facilities_map:
                        facilities_map[facility_id] = {
                            "facility_id": facility_id,
                            "facility_name": facility_name,
                            "date": date_str,
                            "day_type": day_type_db,
                            "season": season_db if season_db else "",
                            "valid_month": valid_month_db,
                            "sessions": [],
                            "source_url": source_url,
                            "notes": notes
                        }

                    # 세션 추가
                    facilities_map[facility_id]["sessions"].append({
                        "session_name": session_name,
                        "start_time": start_time,
                        "end_time": end_time,
                        "capacity": capacity,
                        "lanes": lanes
                    })

                result = list(facilities_map.values())
                logger.info(f"조회 결과: {len(result)}개 시설")

                return result

            except Exception as e:
                logger.error(f"일별 스케줄 조회 실패: {e}")
                return []
            finally:
                close_connection(conn)

        except ValueError as e:
            logger.error(f"날짜 파싱 실패: {date_str}, {e}")
            return []

    @staticmethod
    def get_calendar_data(year: int, month: int) -> dict:
        """
        달력용 데이터 조회

        Args:
            year: 년도 (예: 2026)
            month: 월 (예: 1)

        Returns:
            달력 데이터 (일별 시설 목록)
        """
        month_str = f"{year}년 {month}월"
        schedules = ScheduleService.get_schedules(month=month_str)

        # TODO: 일별로 변환하는 로직 추가
        # 현재는 기본 스케줄 데이터만 반환
        return {
            "year": year,
            "month": month,
            "schedules": schedules
        }
