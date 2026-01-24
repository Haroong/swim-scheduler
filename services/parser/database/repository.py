"""
수영 데이터 Repository
파싱된 JSON 데이터를 MariaDB에 저장
"""
import json
import re
import logging
from pathlib import Path
from typing import Optional, List

from database.connection import get_connection

logger = logging.getLogger(__name__)


class SwimRepository:
    """수영 데이터 저장소"""

    def __init__(self):
        self.conn = None

    def _get_conn(self):
        """연결 획득"""
        if self.conn is None or not self.conn.open:
            self.conn = get_connection()
        return self.conn

    def _commit(self):
        """커밋"""
        if self.conn:
            self.conn.commit()

    def _rollback(self):
        """롤백"""
        if self.conn:
            self.conn.rollback()

    def close(self):
        """연결 종료"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def save_parsed_data(self, data: dict) -> bool:
        """
        파싱된 데이터 저장

        Args:
            data: LLM 파싱 결과 딕셔너리

        Returns:
            성공 여부
        """
        try:
            conn = self._get_conn()
            cursor = conn.cursor()

            # 1. facility 저장/조회
            facility_name = data.get("facility_name", "")
            facility_id = self._get_or_create_facility(cursor, facility_name)

            # 2. notice 저장 (중복 체크)
            source_url = data.get("source_url", "")
            if self._notice_exists(cursor, source_url):
                logger.info(f"이미 저장된 공지: {source_url}")
                return False

            valid_date = self._convert_valid_month(data.get("valid_month", ""))
            notes = data.get("notes", [])
            notice_id = self._save_notice(cursor, facility_id, source_url, valid_date, notes)

            # 3. schedule + session 저장
            schedules = data.get("schedules", [])
            for schedule in schedules:
                schedule_id = self._save_schedule(cursor, facility_id, schedule, valid_date)
                sessions = schedule.get("sessions", [])
                self._save_sessions(cursor, schedule_id, sessions)

            # 4. fee 저장
            fees = data.get("fees", [])
            self._save_fees(cursor, facility_id, fees)

            self._commit()
            logger.info(f"저장 완료: {facility_name}")
            return True

        except Exception as e:
            self._rollback()
            logger.error(f"저장 실패: {e}")
            return False

    def _get_or_create_facility(self, cursor, name: str) -> int:
        """시설 조회 또는 생성"""
        # 조회
        cursor.execute("SELECT id FROM facility WHERE name = %s", (name,))
        row = cursor.fetchone()
        if row:
            return row[0]

        # 생성
        cursor.execute("INSERT INTO facility (name) VALUES (%s)", (name,))
        return cursor.lastrowid

    def _notice_exists(self, cursor, source_url: str) -> bool:
        """공지 존재 여부 확인"""
        cursor.execute("SELECT id FROM notice WHERE source_url = %s", (source_url,))
        return cursor.fetchone() is not None

    def is_new_notice(self, source_url: str) -> bool:
        """
        신규 공지사항 여부 확인 (DB에 없으면 신규)

        Args:
            source_url: 공지사항 URL

        Returns:
            신규 여부 (True: 신규, False: 이미 처리됨)
        """
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            return not self._notice_exists(cursor, source_url)
        except Exception as e:
            logger.error(f"신규 공지 확인 실패: {e}")
            return True  # 에러 시 안전하게 신규로 간주

    def get_existing_notice_urls(self) -> set:
        """
        DB에 저장된 모든 공지사항 URL 조회

        Returns:
            URL set
        """
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT source_url FROM notice")
            rows = cursor.fetchall()
            return {row[0] for row in rows if row[0]}
        except Exception as e:
            logger.error(f"기존 공지 URL 조회 실패: {e}")
            return set()

    def _save_notice(self, cursor, facility_id: int, source_url: str,
                     valid_date: str, notes: List[str]) -> int:
        """공지 저장"""
        notes_json = json.dumps(notes, ensure_ascii=False) if notes else None
        cursor.execute(
            """INSERT INTO notice (facility_id, source_url, valid_date, notes)
               VALUES (%s, %s, %s, %s)""",
            (facility_id, source_url, valid_date, notes_json)
        )
        return cursor.lastrowid

    def _save_schedule(self, cursor, facility_id: int, schedule: dict, valid_month: str) -> int:
        """스케줄 저장"""
        day_type = schedule.get("day_type", "")
        season = schedule.get("season") or None  # 빈 문자열 -> None

        cursor.execute(
            """INSERT INTO swim_schedule (facility_id, day_type, season, valid_month)
               VALUES (%s, %s, %s, %s)""",
            (facility_id, day_type, season, valid_month)
        )
        return cursor.lastrowid

    def _save_sessions(self, cursor, schedule_id: int, sessions: List[dict]):
        """세션 일괄 저장"""
        for session in sessions:
            cursor.execute(
                """INSERT INTO swim_session
                   (schedule_id, session_name, start_time, end_time, capacity, lanes)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    schedule_id,
                    session.get("session_name"),
                    session.get("start_time"),
                    session.get("end_time"),
                    session.get("capacity"),
                    session.get("lanes"),
                )
            )

    def _save_fees(self, cursor, facility_id: int, fees: List[dict]):
        """이용료 일괄 저장"""
        for fee in fees:
            cursor.execute(
                """INSERT INTO fee (facility_id, category, price, note)
                   VALUES (%s, %s, %s, %s)""",
                (
                    facility_id,
                    fee.get("category"),
                    fee.get("price"),
                    fee.get("note", ""),
                )
            )

    def _convert_valid_month(self, valid_month: str) -> str:
        """
        valid_month 형식 변환
        "2026년 1월" -> "2026-01"
        "2026년 12월" -> "2026-12"
        """
        if not valid_month:
            return ""

        match = re.search(r"(\d{4})년\s*(\d{1,2})월", valid_month)
        if match:
            year = match.group(1)
            month = match.group(2).zfill(2)
            return f"{year}-{month}"

        return valid_month[:7] if len(valid_month) >= 7 else valid_month

    def migrate_from_json(self, json_path: Optional[Path] = None) -> int:
        """
        JSON 파일에서 DB로 마이그레이션

        Args:
            json_path: JSON 파일 경로 (기본: storage/parsed_swim_data.json)

        Returns:
            저장된 레코드 수
        """
        if json_path is None:
            json_path = Path(__file__).parent.parent / "storage" / "parsed_swim_data.json"

        if not json_path.exists():
            logger.error(f"JSON 파일 없음: {json_path}")
            return 0

        with open(json_path, "r", encoding="utf-8") as f:
            data_list = json.load(f)

        logger.info(f"마이그레이션 시작: {len(data_list)}개 항목")

        success_count = 0
        for i, data in enumerate(data_list, 1):
            logger.info(f"처리 중: {i}/{len(data_list)} - {data.get('facility_name', 'Unknown')}")
            if self.save_parsed_data(data):
                success_count += 1

        self.close()
        logger.info(f"마이그레이션 완료: {success_count}/{len(data_list)} 성공")
        return success_count


# CLI 실행
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    repo = SwimRepository()
    repo.migrate_from_json()
