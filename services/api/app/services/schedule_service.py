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
                    facility_name,
                    valid_month,
                    COUNT(*) as schedule_count
                FROM parsed_swim_schedules
                GROUP BY facility_name, valid_month
                ORDER BY facility_name, valid_month DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            # 시설별로 최신 데이터만 선택
            facilities = {}
            for row in rows:
                facility_name = row[0]
                if facility_name not in facilities:
                    facilities[facility_name] = {
                        "facility_name": facility_name,
                        "latest_month": row[1],
                        "schedule_count": row[2]
                    }

            return list(facilities.values())

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
            month: 월 (예: "2026-01" 또는 "2026년 1월")

        Returns:
            스케줄 목록
        """
        conn = get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()

            query = "SELECT * FROM parsed_swim_schedules WHERE 1=1"
            params = []

            if facility:
                query += " AND facility_name = %s"
                params.append(facility)

            if month:
                # "2026-01" 또는 "2026년 1월" 형식 모두 지원
                if "-" in month:
                    # "2026-01" → "2026년 1월"
                    year, month_num = month.split("-")
                    month_str = f"{year}년 {int(month_num)}월"
                else:
                    month_str = month

                query += " AND valid_month = %s"
                params.append(month_str)

            query += " ORDER BY facility_name, valid_month DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            schedules = []
            for row in rows:
                schedules.append({
                    "id": row[0],
                    "facility_name": row[1],
                    "valid_month": row[2],
                    "schedules": json.loads(row[3]) if row[3] else [],
                    "fees": json.loads(row[4]) if row[4] else [],
                    "notes": json.loads(row[5]) if row[5] else [],
                    "source_url": row[6],
                    "created_at": row[7].isoformat() if row[7] else None
                })

            return schedules

        except Exception as e:
            logger.error(f"스케줄 조회 실패: {e}")
            return []
        finally:
            close_connection(conn)

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
