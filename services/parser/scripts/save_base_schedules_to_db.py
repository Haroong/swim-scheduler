"""
facility_base_schedules.json을 DB에 저장하는 스크립트
"""
import json
import logging
from pathlib import Path
from infrastructure.database.repository import SwimRepository

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def convert_base_schedule_to_db_format(facility_data: dict, last_updated: str) -> dict:
    """
    facility_base_schedules 형식을 DB 저장 형식으로 변환

    Args:
        facility_data: 시설 데이터
        last_updated: 마지막 업데이트 날짜

    Returns:
        DB 저장용 딕셔너리
    """
    schedules = []

    # 평일 스케줄 변환
    for session in facility_data.get("weekday_schedule", []):
        schedules.append({
            "day_type": "평일",
            "season": "",
            "sessions": [{
                "session_name": session.get("type", "자유수영"),
                "start_time": session.get("start_time"),
                "end_time": session.get("end_time"),
                "capacity": session.get("capacity"),
                "lanes": session.get("lanes")
            }]
        })

    # 주말 스케줄 변환
    weekend_schedule = facility_data.get("weekend_schedule", {})

    # 토요일
    saturday = weekend_schedule.get("saturday", {})
    if saturday.get("parts"):
        saturday_sessions = []
        for part in saturday["parts"]:
            saturday_sessions.append({
                "session_name": f"{part.get('part')}부",
                "start_time": part.get("start"),
                "end_time": part.get("end"),
                "capacity": part.get("capacity"),
                "lanes": part.get("lanes")
            })

        if saturday.get("season"):
            for season in saturday["season"]:
                schedules.append({
                    "day_type": "토요일",
                    "season": season.get("name", ""),
                    "sessions": saturday_sessions
                })
        else:
            schedules.append({
                "day_type": "토요일",
                "season": "",
                "sessions": saturday_sessions
            })

    # 일요일
    sunday = weekend_schedule.get("sunday", {})
    if sunday.get("parts"):
        sunday_sessions = []
        for part in sunday["parts"]:
            sunday_sessions.append({
                "session_name": f"{part.get('part')}부",
                "start_time": part.get("start"),
                "end_time": part.get("end"),
                "capacity": part.get("capacity"),
                "lanes": part.get("lanes")
            })

        if sunday.get("season"):
            for season in sunday["season"]:
                schedules.append({
                    "day_type": "일요일",
                    "season": season.get("name", ""),
                    "sessions": sunday_sessions
                })
        else:
            schedules.append({
                "day_type": "일요일",
                "season": "",
                "sessions": sunday_sessions
            })

    # 이용료 변환
    fees = []
    for category, price in facility_data.get("fees", {}).items():
        fees.append({
            "category": category,
            "price": price,
            "note": ""
        })

    # valid_month 생성 (현재 날짜 기준)
    from datetime import datetime
    now = datetime.now()
    valid_month = f"{now.year}년 {now.month}월"

    return {
        "facility_name": facility_data.get("facility_name"),
        "valid_month": valid_month,
        "schedules": schedules,
        "fees": fees,
        "notes": facility_data.get("notes", []),
        "source_url": facility_data.get("facility_url", "")
    }


def main():
    """메인 실행 함수"""
    # JSON 파일 로드
    json_path = Path(__file__).parent / "storage" / "facility_base_schedules.json"

    if not json_path.exists():
        logger.error(f"JSON 파일을 찾을 수 없습니다: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    logger.info(f"JSON 파일 로드 완료: {json_path}")

    # Repository 초기화
    repo = SwimRepository()

    # 각 조직별 데이터 처리
    total_count = 0
    success_count = 0

    for org_name in ["snyouth", "snhdc"]:
        if org_name not in data:
            continue

        facilities = data[org_name]
        logger.info(f"\n=== {org_name}: {len(facilities)}개 시설 처리 중 ===")

        for facility in facilities:
            total_count += 1
            facility_name = facility.get("facility_name", "Unknown")

            try:
                # DB 형식으로 변환
                db_data = convert_base_schedule_to_db_format(
                    facility,
                    facility.get("last_updated", "")
                )

                # DB에 저장
                if repo.save_parsed_data(db_data):
                    success_count += 1
                    logger.info(f"✓ {facility_name} 저장 완료")
                else:
                    logger.warning(f"✗ {facility_name} 저장 실패 (이미 존재하거나 오류)")

            except Exception as e:
                logger.error(f"✗ {facility_name} 처리 중 오류: {e}")

    repo.close()
    logger.info(f"\n=== 완료: {success_count}/{total_count} 성공 ===")


if __name__ == "__main__":
    main()
