"""
계절 필터 유틸리티
현재 월에 따라 하절기/동절기 스케줄을 필터링
"""
from datetime import datetime
from typing import List, Optional
import copy


def get_current_season(month: Optional[int] = None) -> str:
    """
    현재 월에 해당하는 계절 반환

    Args:
        month: 월 (1-12), None이면 현재 월 사용

    Returns:
        "하절기" (3~10월) 또는 "동절기" (11~2월)
    """
    if month is None:
        month = datetime.now().month

    if 3 <= month <= 10:
        return "하절기"
    else:
        return "동절기"


def filter_by_current_season(parsed_data: List[dict], month: Optional[int] = None) -> List[dict]:
    """
    현재 계절에 맞는 스케줄만 필터링

    Args:
        parsed_data: 파싱된 수영장 데이터 리스트
        month: 월 (1-12), None이면 현재 월 사용

    Returns:
        현재 계절에 맞게 필터링된 데이터
    """
    current_season = get_current_season(month)
    filtered_data = []

    for item in parsed_data:
        # 원본 데이터를 복사
        filtered_item = copy.deepcopy(item)

        # 스케줄 필터링
        filtered_schedules = []
        for schedule in filtered_item.get("schedules", []):
            season = schedule.get("season", "")

            # 계절 구분이 없거나 현재 계절과 일치하는 경우만 포함
            if not season or season == current_season:
                # 계절 구분이 있었다면 제거 (이미 필터링됨)
                if season:
                    schedule["season"] = ""
                    schedule["season_months"] = ""
                filtered_schedules.append(schedule)

        filtered_item["schedules"] = filtered_schedules
        filtered_item["applied_season"] = current_season  # 적용된 계절 표시
        filtered_data.append(filtered_item)

    return filtered_data


def get_schedule_for_date(parsed_data: List[dict], target_date: Optional[datetime] = None) -> List[dict]:
    """
    특정 날짜에 맞는 스케줄 반환

    Args:
        parsed_data: 파싱된 수영장 데이터 리스트
        target_date: 대상 날짜, None이면 오늘

    Returns:
        해당 날짜에 맞게 필터링된 데이터
    """
    if target_date is None:
        target_date = datetime.now()

    return filter_by_current_season(parsed_data, target_date.month)


# 테스트
if __name__ == "__main__":
    import json

    # 현재 계절 확인
    print(f"현재 월: {datetime.now().month}월")
    print(f"현재 계절: {get_current_season()}")
    print()

    # 데이터 로드 및 필터링 테스트
    with open("storage/parsed_swim_data.json", encoding="utf-8") as f:
        data = json.load(f)

    # 현재 계절 기준 필터링
    filtered = filter_by_current_season(data)

    # 결과 저장
    with open("storage/filtered_swim_data.json", "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)

    print(f"필터링 완료: storage/filtered_swim_data.json")
    print(f"원본 스케줄 수: {sum(len(d.get('schedules', [])) for d in data)}")
    print(f"필터링 후 스케줄 수: {sum(len(d.get('schedules', [])) for d in filtered)}")
