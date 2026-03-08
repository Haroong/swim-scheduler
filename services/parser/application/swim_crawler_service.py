"""
통합 수영 크롤링 서비스
1. 기본 스케줄 (이용안내 페이지) 크롤링
2. 월별 공지사항 크롤링
3. 데이터 병합 및 저장

지원 기관:
- 성남시청소년청년재단 (snyouth): 3개 유스센터
- 성남도시개발공사 (snhdc): 5개 체육센터

리팩토링: 각 책임별 서비스로 분리
- CrawlingService: 크롤링 실행
- ParsingService: 파싱 실행
- StorageService: 데이터 저장
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional

from .crawling_service import CrawlingService
from .parsing_service import ParsingService
from .storage_service import StorageService
from core.models.crawler import PostDetail
from core.models.facility import Organization
from infrastructure.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DOWNLOAD_DIR = settings.DOWNLOAD_DIR


class SwimCrawlerService:
    """통합 수영 크롤링 서비스 (snyouth + snhdc)"""

    def __init__(self, storage: StorageService):
        self.storage = storage

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

        all_facilities = {}

        # 각 기관별 크롤링
        for org in Organization:
            crawling_service = CrawlingService(org)
            facilities = crawling_service.crawl_base_schedules()
            all_facilities[org.value] = facilities

            if save:
                self.storage.save_base_schedules(org, facilities)

        total = sum(len(facilities) for facilities in all_facilities.values())
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

        all_notices = {}

        # 각 기관별 크롤링
        for org in Organization:
            crawling_service = CrawlingService(org)
            details: List[PostDetail] = crawling_service.crawl_monthly_notices(keyword, max_pages)

            # PostDetail을 dict로 변환
            all_notices[org.value] = [self._post_detail_to_dict(d) for d in details]

            if save:
                self.storage.save_monthly_notices(org, all_notices[org.value])

        total = sum(len(notices) for notices in all_notices.values())
        logger.info(f"월별 공지사항 크롤링 완료: 총 {total}개")
        return all_notices

    @staticmethod
    def _post_detail_to_dict(detail: PostDetail) -> Dict:
        """PostDetail을 dict로 변환"""
        return {
            "post_id": detail.post_id,
            "title": detail.title,
            "facility_name": detail.facility_name,
            "date": detail.date,
            "content_html": detail.content_html,
            "content_text": detail.content_text,
            "source_url": detail.source_url,
            "attachments": [
                {
                    "filename": att.filename,
                    "size": att.file_size,
                    "ext": att.file_ext,
                    "url": att.download_url
                }
                for att in detail.attachments
            ],
            "has_attachment": len(detail.attachments) > 0,
            "file_hwp": next((att.filename for att in detail.attachments if att.file_ext == "hwp"), None),
            "file_pdf": next((att.filename for att in detail.attachments if att.file_ext == "pdf"), None)
        }

    def parse_attachments(self, org: Organization, monthly_notices: Optional[Dict[str, List[Dict]]] = None,
                          save: bool = True, skip_existing: bool = True) -> List[Dict]:
        """
        기관별 첨부파일 다운로드 및 파싱 (snhdc, snyouth 모두 지원)

        Args:
            org: 기관 (Organization enum)
            monthly_notices: 월별 공지사항 (없으면 파일에서 로드)
            save: 파싱 결과 저장 여부
            skip_existing: 이미 DB에 있는 공지 건너뛰기 (True: 신규만 처리, False: 모두 처리)

        Returns:
            파싱된 결과 리스트
        """
        org_name = org.name
        logger.info(f"=== {org_name} 첨부파일 파싱 시작 ===")

        # 데이터 로드
        if monthly_notices is None:
            notices = self.storage.load_monthly_notices(org)
        else:
            notices = monthly_notices.get(org.value, [])

        # 첨부파일이 있는 공지만 필터링
        notices_with_files = [n for n in notices if n.get("has_attachment")]
        logger.info(f"첨부파일이 있는 공지: {len(notices_with_files)}개")

        if not notices_with_files:
            logger.warning(f"{org_name}: 첨부파일이 있는 공지가 없습니다.")
            return []

        # 신규 공지만 필터링 (DB 중복 확인)
        if skip_existing:
            from infrastructure.container import container
            repo = container.swim_repository()
            existing_urls = repo.get_existing_notice_urls()
            repo.close()

            notices_to_process = [
                n for n in notices_with_files
                if n.get("source_url") not in existing_urls
            ]
            skipped_count = len(notices_with_files) - len(notices_to_process)

            if skipped_count > 0:
                logger.info(f"이미 처리된 공지 {skipped_count}개 건너뛰기")
            logger.info(f"신규 공지: {len(notices_to_process)}개")

            # 신규 공지가 없으면 조기 종료
            if not notices_to_process:
                logger.info(f"{org_name}: 처리할 신규 공지가 없습니다.")
                return []
        else:
            notices_to_process = notices_with_files
            logger.info(f"처리할 공지: {len(notices_to_process)}개")

        # ParsingService 사용 (기관별 다운로더 선택)
        parsing_service = ParsingService(download_dir=DOWNLOAD_DIR / org.value, org_key=org.value)

        # Dict를 PostDetail로 변환 후 파싱
        parsed_results = []
        for notice_dict in notices_to_process:
            # Dict를 PostDetail로 변환
            post_detail = self._dict_to_post_detail(notice_dict)

            # 파싱 실행
            result = parsing_service.parse_from_notice(post_detail)
            if result:
                parsed_results.append(result)

        logger.info(f"{org_name} 파싱 완료: {len(parsed_results)}/{len(notices_to_process)}개 성공")

        # 결과 저장
        if save and parsed_results:
            self.storage.save_parsed_schedules(org, parsed_results)

        return parsed_results

    def parse_snhdc_attachments(self, monthly_notices: Optional[Dict[str, List[Dict]]] = None,
                                 save: bool = True) -> List[Dict]:
        """
        SNHDC 첨부파일 다운로드 및 파싱 (하위 호환성 유지)

        Args:
            monthly_notices: 월별 공지사항 (없으면 파일에서 로드)
            save: 파싱 결과 저장 여부

        Returns:
            파싱된 결과 리스트
        """
        return self.parse_attachments(Organization.SNHDC, monthly_notices, save)

    @staticmethod
    def _dict_to_post_detail(notice_dict: Dict) -> PostDetail:
        """Dict를 PostDetail로 변환"""
        from core.models.crawler import Attachment

        attachments = [
            Attachment(
                filename=att["filename"],
                file_size=att["size"],
                file_ext=att["ext"],
                download_url=att["url"]
            )
            for att in notice_dict.get("attachments", [])
        ]

        return PostDetail(
            post_id=notice_dict.get("post_id", ""),
            title=notice_dict.get("title", ""),
            facility_name=notice_dict.get("facility_name", ""),
            date=notice_dict.get("date", ""),
            content_html=notice_dict.get("content_html", ""),
            content_text=notice_dict.get("content_text", ""),
            attachments=attachments,
            source_url=notice_dict.get("source_url", "")
        )


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
            base_schedules = {}
            for org in Organization:
                facilities = self.storage.load_base_schedules(org)
                base_schedules[org.value] = facilities

        if monthly_notices is None:
            monthly_notices = {}
            for org in Organization:
                notices = self.storage.load_monthly_notices(org)
                monthly_notices[org.value] = notices

        # 통계 및 메타 정보 구성
        org_metadata = {}
        for org in Organization:
            org_name_map = {
                Organization.SNYOUTH: "성남시청소년청년재단",
                Organization.SNHDC: "성남도시개발공사"
            }
            org_metadata[org.value] = {
                "name": org_name_map[org],
                "base_schedule_count": len(base_schedules.get(org.value, [])),
                "monthly_notice_count": len(monthly_notices.get(org.value, []))
            }

        # 시설별로 그룹화
        merged = {
            "meta": {
                "merged_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "organizations": org_metadata
            },
            "facilities": {}
        }

        # 1. 기본 스케줄을 baseline으로 설정 (양쪽 기관 모두)
        for org in Organization:
            org_name = org_metadata[org.value]["name"]
            for facility in base_schedules.get(org.value, []):
                facility_name = facility.get("facility_name")
                merged["facilities"][facility_name] = {
                    "organization": org_name,
                    "org_key": org.value,
                    "base_schedule": facility,
                    "monthly_updates": [],
                    "current_schedule": facility.copy()  # 현재 적용중인 스케줄
                }

        # 2. 월별 공지사항 추가 (양쪽 기관 모두)
        for org in Organization:
            for notice in monthly_notices.get(org.value, []):
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
        from core.models.facility import Facility

        # 정확히 일치
        if name in candidates:
            return name

        # 부분 일치
        for candidate in candidates:
            if name in candidate or candidate in name:
                return candidate

        # 별칭 매칭 (Facility Enum 사용)
        for facility_enum in Facility:
            facility_info = facility_enum.value
            for alias in facility_info.aliases:
                if alias in name and facility_info.name in candidates:
                    return facility_info.name

        return None


# 테스트용 코드
if __name__ == "__main__":
    from infrastructure.container import container
    service = container.swim_crawler_service()

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

    # 3. SNHDC 첨부파일 파싱
    print("\n" + "="*60)
    print("3. SNHDC 첨부파일 다운로드 및 파싱")
    print("="*60)
    parsed_attachments = service.parse_snhdc_attachments(monthly_notices, save=True)
    print(f"  파싱 완료: {len(parsed_attachments)}개")
    for result in parsed_attachments[:3]:  # 처음 3개만
        print(f"    - [{result['facility_name']}] {result.get('valid_month', 'N/A')}")
        print(f"      파일: {result['source_file']}")
        print(f"      스케줄: {len(result.get('schedules', []))}개")

    # 4. 데이터 병합
    print("\n" + "="*60)
    print("4. 스케줄 병합")
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
    service.storage.save_merged_schedules(merged)
    print(f"\n{'='*60}")
    print(f"병합 결과 저장 완료")
    print(f"{'='*60}")
