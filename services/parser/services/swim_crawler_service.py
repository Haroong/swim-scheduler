"""
통합 수영 크롤링 서비스
1. 기본 스케줄 (이용안내 페이지) 크롤링
2. 월별 공지사항 크롤링
3. 데이터 병합 및 저장

지원 기관:
- 성남시청소년청년재단 (snyouth): 3개 유스센터
- 성남도시개발공사 (snhdc): 5개 체육센터
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# 성남시청소년청년재단 크롤러
from crawler.snyouth.facility_info_crawler import FacilityInfoCrawler as SnyouthFacilityInfoCrawler
from crawler.snyouth.list_crawler import ListCrawler as SnyouthListCrawler
from crawler.snyouth.detail_crawler import DetailCrawler as SnyouthDetailCrawler

# 성남도시개발공사 크롤러
from crawler.snhdc.facility_info_crawler import FacilityInfoCrawler as SnhdcFacilityInfoCrawler
from crawler.snhdc.list_crawler import ListCrawler as SnhdcListCrawler
from crawler.snhdc.detail_crawler import DetailCrawler as SnhdcDetailCrawler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STORAGE_DIR = Path(__file__).parent.parent / "storage"


class SwimCrawlerService:
    """통합 수영 크롤링 서비스 (snyouth + snhdc)"""

    def __init__(self):
        # 성남시청소년청년재단 크롤러
        self.snyouth_facility_crawler = SnyouthFacilityInfoCrawler()
        self.snyouth_list_crawler = SnyouthListCrawler()
        self.snyouth_detail_crawler = SnyouthDetailCrawler()

        # 성남도시개발공사 크롤러
        self.snhdc_facility_crawler = SnhdcFacilityInfoCrawler()
        self.snhdc_list_crawler = SnhdcListCrawler()
        self.snhdc_detail_crawler = SnhdcDetailCrawler

    def crawl_base_schedules(self, save: bool = True) -> Dict[str, List[Dict]]:
        """
        기본 스케줄 크롤링 (이용안내 페이지)
        양쪽 기관 모두 크롤링

        Args:
            save: JSON 파일로 저장 여부

        Returns:
            {"snyouth": [...], "snhdc": [...]} 형태의 시설 기본 정보
        """
        logger.info("=== 기본 스케줄 크롤링 시작 ===")

        all_facilities = {
            "snyouth": [],
            "snhdc": []
        }

        # 1. 성남시청소년청년재단 (snyouth)
        logger.info("성남시청소년청년재단 크롤링 중...")
        snyouth_facilities = self.snyouth_facility_crawler.crawl_all_facilities()
        all_facilities["snyouth"] = [
            self.snyouth_facility_crawler.to_dict(f) for f in snyouth_facilities
        ]
        logger.info(f"  ✓ {len(all_facilities['snyouth'])}개 시설 완료")

        # 2. 성남도시개발공사 (snhdc)
        logger.info("성남도시개발공사 크롤링 중...")
        snhdc_facilities = self.snhdc_facility_crawler.crawl_all_facilities()
        all_facilities["snhdc"] = [
            self.snhdc_facility_crawler.to_dict(f) for f in snhdc_facilities
        ]
        logger.info(f"  ✓ {len(all_facilities['snhdc'])}개 시설 완료")

        if save:
            self._save_base_schedules(all_facilities)

        total = len(all_facilities["snyouth"]) + len(all_facilities["snhdc"])
        logger.info(f"기본 스케줄 크롤링 완료: 총 {total}개 시설")
        return all_facilities

    def crawl_monthly_notices(self, keyword: str = "수영", max_pages: int = 5, save: bool = True) -> Dict[str, List[Dict]]:
        """
        월별 공지사항 크롤링
        양쪽 기관 모두 크롤링

        Args:
            keyword: 검색 키워드
            max_pages: 최대 페이지 수
            save: JSON 파일로 저장 여부

        Returns:
            {"snyouth": [...], "snhdc": [...]} 형태의 게시글 상세 정보
        """
        logger.info("=== 월별 공지사항 크롤링 시작 ===")

        all_notices = {
            "snyouth": [],
            "snhdc": []
        }

        # 1. 성남시청소년청년재단 (snyouth)
        logger.info("성남시청소년청년재단 공지사항 크롤링 중...")
        snyouth_posts = self.snyouth_list_crawler.get_posts(keyword=keyword, max_pages=max_pages)
        logger.info(f"  게시글 목록: {len(snyouth_posts)}개")

        snyouth_details = []
        for post in snyouth_posts:
            detail = self.snyouth_detail_crawler.get_detail(post.detail_url)
            if detail:
                snyouth_details.append(detail)

        # to_dict 메서드를 직접 호출 (snyouth DetailCrawler에는 to_dict가 없으므로)
        all_notices["snyouth"] = [
            {
                "title": d.title,
                "date": d.date,
                "content_text": d.content,
                "source_url": d.source_url,
                "attachments": [{"filename": att.filename, "size": att.file_size, "url": att.download_url} for att in d.attachments],
                "has_attachment": len(d.attachments) > 0,
                "file_hwp": next((att.filename for att in d.attachments if att.file_ext == "hwp"), None),
                "file_pdf": next((att.filename for att in d.attachments if att.file_ext == "pdf"), None)
            }
            for d in snyouth_details
        ]
        logger.info(f"  ✓ {len(all_notices['snyouth'])}개 상세 정보 수집 완료")

        # 2. 성남도시개발공사 (snhdc)
        logger.info("성남도시개발공사 공지사항 크롤링 중...")

        # SNHDC는 list API가 이미 content를 포함하므로 list만 가져오기
        snhdc_list_crawler = self.snhdc_list_crawler
        response = snhdc_list_crawler.session.post(
            "https://spo.isdc.co.kr/selectNoticeList.ajax",
            data={"searchWord": keyword, "page": 1, "perPageNum": max_pages * 10, "brd_flg": "1"},
            timeout=10
        )

        json_data = response.json()
        notice_list = json_data.get("data", [])
        logger.info(f"  게시글 목록: {len(notice_list)}개")

        # DetailCrawler로 변환
        snhdc_details = []
        for item in notice_list:
            detail = SnhdcDetailCrawler.from_list_item(item)
            if detail:
                snhdc_details.append(detail)

        all_notices["snhdc"] = [
            SnhdcDetailCrawler.to_dict(d) for d in snhdc_details
        ]
        logger.info(f"  ✓ {len(all_notices['snhdc'])}개 상세 정보 변환 완료")

        if save:
            self._save_monthly_notices(all_notices)

        total = len(all_notices["snyouth"]) + len(all_notices["snhdc"])
        logger.info(f"월별 공지사항 크롤링 완료: 총 {total}개")
        return all_notices

    def merge_schedules(self, base_schedules: Optional[Dict[str, List[Dict]]] = None,
                       monthly_notices: Optional[Dict[str, List[Dict]]] = None) -> Dict:
        """
        기본 스케줄과 월별 공지사항 병합

        전략:
        1. 기본 스케줄을 baseline으로 사용
        2. 월별 공지사항에서 임시 변경사항 추출
        3. 특정 날짜/기간에 대한 override 정보 제공

        Args:
            base_schedules: {"snyouth": [...], "snhdc": [...]} 형태 (없으면 파일에서 로드)
            monthly_notices: {"snyouth": [...], "snhdc": [...]} 형태 (없으면 파일에서 로드)

        Returns:
            병합된 스케줄 정보
        """
        logger.info("=== 스케줄 병합 시작 ===")

        # 데이터 로드
        if base_schedules is None:
            base_schedules = self._load_base_schedules()

        if monthly_notices is None:
            monthly_notices = self._load_monthly_notices()

        # 통계
        snyouth_base_count = len(base_schedules.get("snyouth", []))
        snhdc_base_count = len(base_schedules.get("snhdc", []))
        snyouth_notice_count = len(monthly_notices.get("snyouth", []))
        snhdc_notice_count = len(monthly_notices.get("snhdc", []))

        # 시설별로 그룹화
        merged = {
            "meta": {
                "merged_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "organizations": {
                    "snyouth": {
                        "name": "성남시청소년청년재단",
                        "base_schedule_count": snyouth_base_count,
                        "monthly_notice_count": snyouth_notice_count
                    },
                    "snhdc": {
                        "name": "성남도시개발공사",
                        "base_schedule_count": snhdc_base_count,
                        "monthly_notice_count": snhdc_notice_count
                    }
                }
            },
            "facilities": {}
        }

        # 1. 기본 스케줄을 baseline으로 설정 (양쪽 기관 모두)
        for org_key in ["snyouth", "snhdc"]:
            org_name = merged["meta"]["organizations"][org_key]["name"]
            for facility in base_schedules.get(org_key, []):
                facility_name = facility.get("facility_name")
                merged["facilities"][facility_name] = {
                    "organization": org_name,
                    "org_key": org_key,
                    "base_schedule": facility,
                    "monthly_updates": [],
                    "current_schedule": facility.copy()  # 현재 적용중인 스케줄
                }

        # 2. 월별 공지사항 추가 (양쪽 기관 모두)
        for org_key in ["snyouth", "snhdc"]:
            for notice in monthly_notices.get(org_key, []):
                # 시설명 추출 (다양한 필드명 지원)
                facility_name = (
                    notice.get("facility_name") or
                    notice.get("pool_name") or
                    ""
                )

                # 시설명 매칭 (유연한 매칭)
                matched_facility = self._match_facility_name(facility_name, merged["facilities"].keys())

                if matched_facility:
                    merged["facilities"][matched_facility]["monthly_updates"].append({
                        "title": notice.get("title", ""),
                        "valid_month": notice.get("valid_month", ""),
                        "date": notice.get("date", ""),
                        "source_url": notice.get("source_url", ""),
                        "content_text_preview": notice.get("content_text", "")[:200] + "..." if notice.get("content_text") else "",
                        "has_attachment": notice.get("has_attachment", False),
                        "file_hwp": notice.get("file_hwp"),
                        "file_pdf": notice.get("file_pdf")
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

    def _save_base_schedules(self, data: Dict[str, List[Dict]]):
        """기본 스케줄 저장"""
        snyouth_count = len(data.get("snyouth", []))
        snhdc_count = len(data.get("snhdc", []))

        output = {
            "meta": {
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "2.0",
                "source": "official usage guide pages",
                "organizations": {
                    "snyouth": {
                        "name": "성남시청소년청년재단",
                        "facility_count": snyouth_count
                    },
                    "snhdc": {
                        "name": "성남도시개발공사",
                        "facility_count": snhdc_count
                    }
                },
                "total_facility_count": snyouth_count + snhdc_count
            },
            "snyouth": data.get("snyouth", []),
            "snhdc": data.get("snhdc", [])
        }

        file_path = STORAGE_DIR / "facility_base_schedules.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        logger.info(f"기본 스케줄 저장 완료: {file_path}")

    def _save_monthly_notices(self, data: Dict[str, List[Dict]]):
        """월별 공지사항 저장"""
        snyouth_count = len(data.get("snyouth", []))
        snhdc_count = len(data.get("snhdc", []))

        output = {
            "meta": {
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "2.0",
                "organizations": {
                    "snyouth": {
                        "name": "성남시청소년청년재단",
                        "notice_count": snyouth_count
                    },
                    "snhdc": {
                        "name": "성남도시개발공사",
                        "notice_count": snhdc_count
                    }
                },
                "total_notice_count": snyouth_count + snhdc_count
            },
            "snyouth": data.get("snyouth", []),
            "snhdc": data.get("snhdc", [])
        }

        file_path = STORAGE_DIR / "swim_programs.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        logger.info(f"월별 공지사항 저장 완료: {file_path}")

    def _load_base_schedules(self) -> Dict[str, List[Dict]]:
        """기본 스케줄 로드"""
        file_path = STORAGE_DIR / "facility_base_schedules.json"
        if not file_path.exists():
            logger.warning(f"기본 스케줄 파일 없음: {file_path}")
            return {"snyouth": [], "snhdc": []}

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # v2.0 형식
            if "snyouth" in data and "snhdc" in data:
                return {"snyouth": data.get("snyouth", []), "snhdc": data.get("snhdc", [])}
            # v1.0 형식 (하위 호환)
            elif "facilities" in data:
                return {"snyouth": data.get("facilities", []), "snhdc": []}
            else:
                return {"snyouth": [], "snhdc": []}

    def _load_monthly_notices(self) -> Dict[str, List[Dict]]:
        """월별 공지사항 로드"""
        file_path = STORAGE_DIR / "swim_programs.json"
        if not file_path.exists():
            logger.warning(f"월별 공지사항 파일 없음: {file_path}")
            return {"snyouth": [], "snhdc": []}

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # v2.0 형식
            if "snyouth" in data and "snhdc" in data:
                return {"snyouth": data.get("snyouth", []), "snhdc": data.get("snhdc", [])}
            # v1.0 형식 (하위 호환) - 리스트 형태
            elif isinstance(data, list):
                return {"snyouth": data, "snhdc": []}
            else:
                return {"snyouth": [], "snhdc": []}


# 테스트용 코드
if __name__ == "__main__":
    service = SwimCrawlerService()

    # 1. 기본 스케줄 크롤링
    print("\n" + "="*60)
    print("1. 기본 스케줄 크롤링 (snyouth + snhdc)")
    print("="*60)
    base_schedules = service.crawl_base_schedules(save=True)
    snyouth_count = len(base_schedules.get("snyouth", []))
    snhdc_count = len(base_schedules.get("snhdc", []))
    print(f"  성남시청소년청년재단: {snyouth_count}개")
    print(f"  성남도시개발공사: {snhdc_count}개")
    print(f"  총 {snyouth_count + snhdc_count}개 시설")

    # 2. 월별 공지사항 크롤링
    print("\n" + "="*60)
    print("2. 월별 공지사항 크롤링 (snyouth + snhdc)")
    print("="*60)
    monthly_notices = service.crawl_monthly_notices(keyword="수영", max_pages=2, save=True)
    snyouth_notice_count = len(monthly_notices.get("snyouth", []))
    snhdc_notice_count = len(monthly_notices.get("snhdc", []))
    print(f"  성남시청소년청년재단: {snyouth_notice_count}개")
    print(f"  성남도시개발공사: {snhdc_notice_count}개")
    print(f"  총 {snyouth_notice_count + snhdc_notice_count}개 공지")

    # 3. 데이터 병합
    print("\n" + "="*60)
    print("3. 스케줄 병합")
    print("="*60)
    merged = service.merge_schedules(base_schedules, monthly_notices)
    print(f"병합 완료: {len(merged['facilities'])}개 시설")

    # 병합 결과 출력 (조직별로)
    for org_key in ["snyouth", "snhdc"]:
        org_facilities = {
            name: data for name, data in merged["facilities"].items()
            if data.get("org_key") == org_key
        }

        if org_facilities:
            org_name = merged["meta"]["organizations"][org_key]["name"]
            print(f"\n{'='*60}")
            print(f"{org_name} ({len(org_facilities)}개 시설)")
            print(f"{'='*60}")

            for facility_name, facility_data in list(org_facilities.items())[:3]:  # 처음 3개만
                print(f"\n  [{facility_name}]")
                weekday_schedule = facility_data['base_schedule'].get('weekday_schedule', [])
                print(f"    평일 스케줄: {len(weekday_schedule)}개")
                print(f"    월별 업데이트: {len(facility_data['monthly_updates'])}개")

                if facility_data['monthly_updates']:
                    print("    최근 공지:")
                    for update in facility_data['monthly_updates'][:2]:  # 처음 2개만
                        title = update.get('title', '')
                        date = update.get('date', '')
                        has_file = update.get('has_attachment', False)
                        file_marker = " [📎]" if has_file else ""
                        print(f"      - [{date}] {title}{file_marker}")

    # 병합 결과 저장
    merged_file = STORAGE_DIR / "merged_schedules.json"
    with open(merged_file, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"\n{'='*60}")
    print(f"병합 결과 저장: {merged_file}")
    print(f"{'='*60}")
