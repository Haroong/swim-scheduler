"""
성남도시개발공사 공지사항 게시판 크롤러
AJAX API를 통해 게시글 목록을 수집
"""
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging
import time

from models.facility import Facility, Organization, SNHDC_BASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = f"{SNHDC_BASE_URL}/selectNoticeList.ajax"


@dataclass
class PostSummary:
    """게시글 요약 정보"""
    post_id: str           # idx 값
    title: str             # 게시글 제목
    facility_name: str     # 시설명 (up_nm)
    date: str              # 등록일자
    has_attachment: bool   # 첨부파일 여부
    detail_url: str        # 상세 페이지 URL


class ListCrawler:
    """공지사항 게시판 목록 크롤러"""

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

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest"
        })

    def get_posts(self, keyword: str = "수영", max_pages: int = 5,
                  facility_id: Optional[str] = None) -> List[PostSummary]:
        """
        키워드로 게시글 검색하여 목록 반환

        Args:
            keyword: 검색 키워드 (기본값: "수영")
            max_pages: 최대 검색할 페이지 수
            facility_id: 업장 ID (01~06, None이면 전체)

        Returns:
            PostSummary 객체 리스트
        """
        all_posts = []

        for page in range(1, max_pages + 1):
            logger.info(f"페이지 {page} 크롤링 중...")
            posts = self._crawl_page(keyword, page, facility_id)

            if not posts:
                logger.info(f"페이지 {page}에서 더 이상 게시글 없음. 종료.")
                break

            all_posts.extend(posts)
            time.sleep(0.5)  # 서버 부하 방지

        logger.info(f"총 {len(all_posts)}개 게시글 수집 완료")
        return all_posts

    def _crawl_page(self, keyword: str, page: int,
                    facility_id: Optional[str] = None) -> List[PostSummary]:
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
