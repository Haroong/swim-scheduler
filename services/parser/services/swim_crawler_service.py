"""
통합 수영 크롤링 서비스
1. 기본 스케줄 (이용안내 페이지) 크롤링
2. 월별 공지사항 크롤링
3. 데이터 병합 및 저장
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from crawler.facility_info_crawler import FacilityInfoCrawler, FacilityInfo
from crawler.list_crawler import ListCrawler
from crawler.detail_crawler import DetailCrawler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STORAGE_DIR = Path(__file__).parent.parent / "storage"


class SwimCrawlerService:
    """통합 수영 크롤링 서비스"""

    def __init__(self):
        self.facility_crawler = FacilityInfoCrawler()
        self.list_crawler = ListCrawler()
        self.detail_crawler = DetailCrawler()

    def crawl_base_schedules(self, save: bool = True) -> List[Dict]:
        """
        기본 스케줄 크롤링 (이용안내 페이지)

        Args:
            save: JSON 파일로 저장 여부

        Returns:
            시설 기본 정보 리스트
        """
        logger.info("=== 기본 스케줄 크롤링 시작 ===")

        facilities = self.facility_crawler.crawl_all_facilities()

        # Dict로 변환
        facilities_data = [
            self.facility_crawler.to_dict(f) for f in facilities
        ]

        if save:
            self._save_base_schedules(facilities_data)

        logger.info(f"기본 스케줄 크롤링 완료: {len(facilities_data)}개 시설")
        return facilities_data

    def crawl_monthly_notices(self, keyword: str = "수영", max_pages: int = 5, save: bool = True) -> List[Dict]:
        """
        월별 공지사항 크롤링

        Args:
            keyword: 검색 키워드
            max_pages: 최대 페이지 수
            save: JSON 파일로 저장 여부

        Returns:
            게시글 상세 정보 리스트
        """
        logger.info("=== 월별 공지사항 크롤링 시작 ===")

        # 1. 게시글 목록 수집
        posts = self.list_crawler.get_posts(keyword=keyword, max_pages=max_pages)
        logger.info(f"게시글 목록 수집: {len(posts)}개")

        # 2. 각 게시글 상세 정보 크롤링
        details = []
        for post in posts:
            detail = self.detail_crawler.crawl_post(
                post_id=post.post_id,
                pool_name=post.facility_name,
                title=post.title
            )
            if detail:
                details.append(detail)

        # 3. Dict로 변환
        programs_data = [
            self.detail_crawler.to_dict(d) for d in details
        ]

        if save:
            self._save_monthly_notices(programs_data)

        logger.info(f"월별 공지사항 크롤링 완료: {len(programs_data)}개")
        return programs_data

    def merge_schedules(self, base_schedules: Optional[List[Dict]] = None,
                       monthly_notices: Optional[List[Dict]] = None) -> Dict:
        """
        기본 스케줄과 월별 공지사항 병합

        전략:
        1. 기본 스케줄을 baseline으로 사용
        2. 월별 공지사항에서 임시 변경사항 추출
        3. 특정 날짜/기간에 대한 override 정보 제공

        Args:
            base_schedules: 기본 스케줄 (없으면 파일에서 로드)
            monthly_notices: 월별 공지사항 (없으면 파일에서 로드)

        Returns:
            병합된 스케줄 정보
        """
        logger.info("=== 스케줄 병합 시작 ===")

        # 데이터 로드
        if base_schedules is None:
            base_schedules = self._load_base_schedules()

        if monthly_notices is None:
            monthly_notices = self._load_monthly_notices()

        # 시설별로 그룹화
        merged = {
            "meta": {
                "merged_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "base_schedule_count": len(base_schedules),
                "monthly_notice_count": len(monthly_notices)
            },
            "facilities": {}
        }

        # 1. 기본 스케줄을 baseline으로 설정
        for facility in base_schedules:
            facility_name = facility.get("facility_name")
            merged["facilities"][facility_name] = {
                "base_schedule": facility,
                "monthly_updates": [],
                "current_schedule": facility.copy()  # 현재 적용중인 스케줄
            }

        # 2. 월별 공지사항 추가
        for notice in monthly_notices:
            # parsed_swim_data.json 형식의 경우 facility_name 사용
            # swim_programs.json 형식의 경우 pool_name 사용
            facility_name = notice.get("facility_name") or notice.get("pool_name", "")

            # 시설명 매칭 (유연한 매칭)
            matched_facility = self._match_facility_name(facility_name, merged["facilities"].keys())

            if matched_facility:
                merged["facilities"][matched_facility]["monthly_updates"].append({
                    "title": notice.get("title", ""),  # swim_programs.json용
                    "valid_month": notice.get("valid_month", ""),  # parsed_swim_data.json용
                    "date": notice.get("date", ""),  # swim_programs.json용
                    "source_url": notice.get("source_url", ""),
                    "schedules_count": len(notice.get("schedules", [])),  # parsed_swim_data.json용
                    "raw_text_preview": notice.get("raw_text", "")[:200] + "..." if "raw_text" in notice else ""
                })

        logger.info("스케줄 병합 완료")
        return merged

    def _match_facility_name(self, name: str, candidates: List[str]) -> Optional[str]:
        """시설명 매칭 (유연한 매칭)"""
        # 정확히 일치
        if name in candidates:
            return name

        # 부분 일치
        for candidate in candidates:
            if name in candidate or candidate in name:
                return candidate

        # 키워드 매칭
        keywords_map = {
            "중원": "중원유스센터",
            "판교": "판교유스센터",
            "야탑": "야탑유스센터"
        }

        for keyword, full_name in keywords_map.items():
            if keyword in name and full_name in candidates:
                return full_name

        return None

    def _save_base_schedules(self, data: List[Dict]):
        """기본 스케줄 저장"""
        output = {
            "meta": {
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0",
                "source": "official usage guide pages",
                "facility_count": len(data)
            },
            "facilities": data
        }

        file_path = STORAGE_DIR / "facility_base_schedules.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        logger.info(f"기본 스케줄 저장 완료: {file_path}")

    def _save_monthly_notices(self, data: List[Dict]):
        """월별 공지사항 저장"""
        file_path = STORAGE_DIR / "swim_programs.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"월별 공지사항 저장 완료: {file_path}")

    def _load_base_schedules(self) -> List[Dict]:
        """기본 스케줄 로드"""
        file_path = STORAGE_DIR / "facility_base_schedules.json"
        if not file_path.exists():
            logger.warning(f"기본 스케줄 파일 없음: {file_path}")
            return []

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("facilities", [])

    def _load_monthly_notices(self) -> List[Dict]:
        """월별 공지사항 로드"""
        file_path = STORAGE_DIR / "swim_programs.json"
        if not file_path.exists():
            logger.warning(f"월별 공지사항 파일 없음: {file_path}")
            return []

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)


# 테스트용 코드
if __name__ == "__main__":
    service = SwimCrawlerService()

    # 1. 기본 스케줄 크롤링
    print("\n" + "="*60)
    print("1. 기본 스케줄 크롤링")
    print("="*60)
    base_schedules = service.crawl_base_schedules(save=True)
    print(f"수집된 시설: {len(base_schedules)}개")

    # 2. 월별 공지사항 크롤링
    print("\n" + "="*60)
    print("2. 월별 공지사항 크롤링")
    print("="*60)
    monthly_notices = service.crawl_monthly_notices(keyword="수영", max_pages=2, save=True)
    print(f"수집된 공지: {len(monthly_notices)}개")

    # 3. 데이터 병합
    print("\n" + "="*60)
    print("3. 스케줄 병합")
    print("="*60)
    merged = service.merge_schedules(base_schedules, monthly_notices)
    print(f"병합 완료: {len(merged['facilities'])}개 시설")

    # 병합 결과 출력
    for facility_name, facility_data in merged["facilities"].items():
        print(f"\n{'='*60}")
        print(f"{facility_name}")
        print(f"{'='*60}")
        print(f"평일 스케줄: {len(facility_data['base_schedule']['weekday_schedule'])}개")
        print(f"월별 업데이트: {len(facility_data['monthly_updates'])}개")
        if facility_data['monthly_updates']:
            print("\n최근 공지:")
            for update in facility_data['monthly_updates'][:3]:
                print(f"  - [{update['date']}] {update['title']}")

    # 병합 결과 저장
    merged_file = STORAGE_DIR / "merged_schedules.json"
    with open(merged_file, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"\n병합 결과 저장: {merged_file}")
