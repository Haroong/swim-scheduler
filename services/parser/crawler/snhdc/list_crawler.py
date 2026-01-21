"""
성남도시개발공사 공지사항 게시판 크롤러
AJAX API를 통해 게시글 목록을 수집
"""
from typing import List, Dict, Optional
import logging

from enums.facility import Facility, Organization, SNHDC_BASE_URL
from crawler.base.list_crawler import BaseListCrawler
from dto.crawler_dto import PostSummary, PostDetail, Attachment
from utils.html_utils import extract_clean_text
from utils.http_utils import create_session

logger = logging.getLogger(__name__)

API_URL = f"{SNHDC_BASE_URL}/selectNoticeList.ajax"
BASE_URL = SNHDC_BASE_URL


class ListCrawler(BaseListCrawler):
    """
    성남도시개발공사 공지사항 게시판 목록 크롤러

    AJAX API를 사용하여 게시글 목록 수집
    """

    @staticmethod
    def get_facility_id(facility_name: str) -> Optional[str]:
        """시설명으로 facility_id 조회"""
        facility = Facility.find_by_name(facility_name)
        if facility and facility.facility_id:
            return facility.facility_id
        # 금곡공원국민체육센터는 공지사항에만 존재 (Facility Enum에 없음)
        if facility_name == "금곡공원국민체육센터":
            return "06"
        return None

    @staticmethod
    def get_all_facility_ids() -> Dict[str, str]:
        """모든 SNHDC 시설의 ID 매핑 반환"""
        result = {}
        for facility in Facility.snhdc_facilities():
            if facility.facility_id:
                result[facility.name] = facility.facility_id
        # 금곡공원국민체육센터 추가 (공지사항에만 존재)
        result["금곡공원국민체육센터"] = "06"
        return result

    def _init_session(self):
        """HTTP 세션 초기화 (SNHDC AJAX API용)"""
        return create_session({
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest"
        })

    def _crawl_page(self, keyword: str, page: int, facility_id: Optional[str] = None) -> List[PostSummary]:
        """단일 페이지 크롤링"""
        data = {
            "searchWord": keyword,
            "page": page,
            "perPageNum": 10,
            "brd_flg": "1"
        }

        if facility_id:
            data["up_id"] = facility_id

        try:
            response = self.session.post(API_URL, data=data, timeout=10)
            response.raise_for_status()

            json_data = response.json()
            return self._parse_response(json_data)

        except requests.RequestException as e:
            logger.error(f"페이지 요청 실패: {e}")
            return []
        except ValueError as e:
            logger.error(f"JSON 파싱 실패: {e}")
            return []

    def _parse_response(self, json_data: Dict) -> List[PostSummary]:
        """API 응답 파싱"""
        posts = []

        # JSON 구조: {"data": [...], "pageMaker": {...}}
        notice_list = json_data.get("data", [])

        for item in notice_list:
            # 필드 추출
            idx = str(item.get("idx", ""))
            title = item.get("sbjt", "").strip()  # 제목
            facility_name = item.get("com_nm", "").strip()  # 시설명
            enter_dt = item.get("enter_dt", "")  # 등록일

            # 첨부파일 여부 (HWP 또는 PDF)
            file_a = item.get("file_a", "")  # HWP
            file_b = item.get("file_b", "")  # PDF
            has_attachment = bool(file_a or file_b)

            # 상세 페이지 URL
            detail_url = f"{BASE_URL}/goNoticeView.do"

            post = PostSummary(
                post_id=idx,
                title=title,
                facility_name=facility_name,
                date=enter_dt,
                has_attachment=has_attachment,
                detail_url=detail_url
            )
            posts.append(post)
            logger.debug(f"게시글 발견: {title}")

        return posts

    def get_posts_with_details(self, keyword: str = "", max_pages: int = 5, **kwargs) -> List[PostDetail]:
        """
        게시글 목록과 상세 정보를 함께 수집 (SNHDC 전용)

        SNHDC API는 목록에서 이미 content를 제공하므로 별도 상세 크롤링 불필요

        Args:
            keyword: 검색 키워드
            max_pages: 최대 페이지 수

        Returns:
            PostDetail 리스트
        """
        details = []
        facility_id = kwargs.get("facility_id")

        for page in range(1, max_pages + 1):
            logger.info(f"페이지 {page} 크롤링 중...")

            data = {
                "searchWord": keyword,
                "page": page,
                "perPageNum": 10,
                "brd_flg": "1"
            }
            if facility_id:
                data["up_id"] = facility_id

            try:
                response = self.session.post(API_URL, data=data, timeout=10)
                response.raise_for_status()
                json_data = response.json()

                notice_list = json_data.get("data", [])
                if not notice_list:
                    break

                for item in notice_list:
                    detail = self._item_to_post_detail(item)
                    if detail:
                        details.append(detail)

            except Exception as e:
                logger.error(f"페이지 {page} 크롤링 실패: {e}")
                break

        logger.info(f"총 {len(details)}개 게시글 상세 수집 완료")
        return details

    def _item_to_post_detail(self, item: Dict) -> Optional[PostDetail]:
        """API 응답 아이템을 PostDetail로 변환"""
        try:
            post_id = str(item.get("idx", ""))
            title = item.get("sbjt", "").strip()
            facility_name = item.get("com_nm", "").strip()
            enter_dt = item.get("enter_dt", "")
            content_html = item.get("content", "")

            # HTML에서 텍스트 추출
            content_text = extract_clean_text(content_html)

            # 첨부파일 정보
            attachments = []
            file_a = item.get("file_a", "").strip()
            file_b = item.get("file_b", "").strip()

            if file_a:
                attachments.append(Attachment(
                    filename=file_a,
                    file_size="",
                    file_ext="hwp",
                    download_url=""
                ))
            if file_b:
                attachments.append(Attachment(
                    filename=file_b,
                    file_size="",
                    file_ext="pdf",
                    download_url=""
                ))

            return PostDetail(
                post_id=post_id,
                title=title,
                facility_name=facility_name,
                date=enter_dt,
                content_html=content_html,
                content_text=content_text,
                attachments=attachments,
                source_url=f"{BASE_URL}/goNoticeView.do?idx={post_id}"
            )

        except Exception as e:
            logger.error(f"PostDetail 변환 실패: {e}")
            return None


# 테스트용 코드
if __name__ == "__main__":
    crawler = ListCrawler()

    print("="*60)
    print("전체 게시판 검색 (수영)")
    print("="*60)
    posts = crawler.get_posts(keyword="수영", max_pages=2)

    for post in posts[:10]:  # 처음 10개만 출력
        print(f"[{post.date}] {post.facility_name} - {post.title}")
        print(f"  ID: {post.post_id}")
        print(f"  첨부: {'있음' if post.has_attachment else '없음'}")
        print()

    print("\n" + "="*60)
    print("특정 시설 검색 (탄천종합운동장)")
    print("="*60)
    posts = crawler.get_posts(
        keyword="수영",
        max_pages=1,
        facility_id="03"  # 탄천
    )

    for post in posts[:5]:
        print(f"[{post.date}] {post.title}")
        print(f"  첨부: {'있음' if post.has_attachment else '없음'}")
        print()
