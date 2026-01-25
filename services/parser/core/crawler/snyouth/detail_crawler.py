"""
상세 페이지 크롤러
게시글 상세 페이지에서 제목, 본문, 첨부파일 정보를 추출
"""
from bs4 import BeautifulSoup
from typing import List, Optional
import logging
import re

from core.crawler.base.detail_crawler import BaseDetailCrawler
from core.models.crawler import PostDetail, Attachment
from infrastructure.utils.http_utils import create_session

logger = logging.getLogger(__name__)

BASE_URL = "https://www.snyouth.or.kr"


class DetailCrawler(BaseDetailCrawler):
    """
    성남시청소년청년재단 상세 페이지 크롤러

    HTML 파싱으로 게시글 상세 정보 수집
    """

    def __init__(self):
        super().__init__()
        self.session = create_session()

    def get_detail(self, post_url: str, facility_name: str = "", **kwargs) -> Optional[PostDetail]:
        """
        상세 페이지에서 정보 추출

        Args:
            post_url: 상세 페이지 URL
            facility_name: 시설명 (리스트 크롤링 시 수집)
            **kwargs: 추가 파라미터

        Returns:
            PostDetail 객체 또는 None
        """
        try:
            response = self.session.get(post_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            self.logger.error(f"상세 페이지 요청 실패: {e}")
            return None

        return self._parse_detail_page(response.text, post_url, facility_name)

    def _parse_detail_page(self, html: str, source_url: str, facility_name: str = "") -> Optional[PostDetail]:
        """상세 페이지 HTML 파싱"""
        soup = BeautifulSoup(html, "html.parser")

        # 오류 페이지 체크 (문서 정보가 없습니다)
        if "문서 정보가 없습니다" in html or "history.back" in html[:500]:
            logger.warning(f"유효하지 않은 게시글: {source_url}")
            return None

        # 제목 추출 (h4 태그)
        title = self._extract_title(soup)
        if not title:
            logger.warning("제목을 찾을 수 없음")
            return None

        # 등록일 추출
        date = self._extract_date(soup)

        # 본문 추출
        content = self._extract_content(soup)

        # 첨부파일 추출
        attachments = self._extract_attachments(soup)

        # 시설명: 파라미터로 받은 값 우선, 없으면 제목에서 추출 시도
        if not facility_name:
            if "야탑" in title:
                facility_name = "야탑유스센터"
            elif "중원" in title:
                facility_name = "중원유스센터"
            elif "판교" in title:
                facility_name = "판교유스센터"

        # PostDetail 객체 생성 (dto 구조에 맞춰)
        content_html = str(soup.find("div", class_="view")) if soup.find("div", class_="view") else ""

        return PostDetail(
            post_id="",  # snyouth는 post_id가 URL에만 있음
            title=title,
            facility_name=facility_name,
            date=date,
            content_html=content_html,
            content_text=content,
            attachments=attachments,
            source_url=source_url
        )

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """제목 추출"""
        # h4 태그에서 제목 찾기
        h4 = soup.find("h4")
        if h4:
            return h4.get_text(strip=True)

        # div.subject 시도
        subject = soup.find("div", class_="subject")
        if subject:
            return subject.get_text(strip=True)

        # 타이틀 태그 시도
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text(strip=True)

        return ""

    def _extract_date(self, soup: BeautifulSoup) -> str:
        """등록일 추출"""
        # "등록일자" 텍스트를 포함하는 요소 찾기
        text = soup.get_text()
        match = re.search(r"등록일자\s*:\s*(\d{4}년\s*\d{1,2}월\s*\d{1,2}일)", text)
        if match:
            return match.group(1)

        # YYYY-MM-DD 형식 시도
        match = re.search(r"(\d{4}-\d{2}-\d{2})", text)
        if match:
            return match.group(1)

        return ""

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """본문 내용 추출"""
        # div.cont-text 시도
        content_div = soup.find("div", class_="cont-text")
        if content_div:
            return content_div.get_text(separator="\n", strip=True)

        # div.content 시도
        content_div = soup.find("div", class_="content")
        if content_div:
            return content_div.get_text(separator="\n", strip=True)

        # article 태그 시도
        article = soup.find("article")
        if article:
            return article.get_text(separator="\n", strip=True)

        # 본문 영역으로 추정되는 부분 찾기
        # 일반적으로 본문은 table 안에 있거나 특정 div 안에 있음
        main_content = soup.find("div", class_="board-view")
        if main_content:
            return main_content.get_text(separator="\n", strip=True)

        return ""

    def _extract_attachments(self, soup: BeautifulSoup) -> List[Attachment]:
        """첨부파일 목록 추출"""
        attachments = []

        # 다운로드 링크 패턴: /File/Download/xxx
        download_links = soup.find_all("a", href=re.compile(r"/File/Download/"))

        for link in download_links:
            href = link.get("href", "")
            if not href:
                continue

            # 절대 URL로 변환
            if href.startswith("/"):
                download_url = BASE_URL + href
            else:
                download_url = href

            # 파일명 추출 (링크 텍스트 또는 부모 요소에서)
            filename = self._extract_filename(link)
            if not filename:
                continue

            # 파일 크기 추출
            file_size = self._extract_file_size(link)

            # 확장자 추출
            file_ext = filename.split(".")[-1].lower() if "." in filename else ""

            attachment = Attachment(
                filename=filename,
                download_url=download_url,
                file_size=file_size,
                file_ext=file_ext
            )
            attachments.append(attachment)

        return attachments

    def _extract_filename(self, link) -> str:
        """첨부파일명 추출"""
        # 링크 텍스트에서 파일명 찾기
        link_text = link.get_text(strip=True)
        if link_text and "다운로드" not in link_text and "미리보기" not in link_text:
            return link_text

        # 부모 li 요소에서 div.name 찾기 (새 구조)
        parent_li = link.find_parent('li')
        if parent_li:
            name_div = parent_li.find('div', class_='name')
            if name_div:
                return name_div.get_text(strip=True)

        # 부모 요소에서 파일명 찾기 (기존 방식)
        parent = link.parent
        if parent:
            # 같은 레벨에 있는 텍스트에서 파일명 찾기
            for sibling in parent.children:
                if hasattr(sibling, "get_text"):
                    text = sibling.get_text(strip=True)
                    if text and "." in text and "다운로드" not in text:
                        # 확장자가 포함된 텍스트를 파일명으로 간주
                        return text

            # 부모의 텍스트 전체에서 파일명 패턴 찾기
            parent_text = parent.get_text(strip=True)
            match = re.search(r"([^\s]+\.(hwp|pdf|doc|docx|xlsx|xls|png|jpg|jpeg))", parent_text, re.I)
            if match:
                return match.group(1)

        return ""

    def _extract_file_size(self, link) -> str:
        """파일 크기 추출"""
        parent = link.parent
        if parent:
            text = parent.get_text()
            match = re.search(r"\((\d+\.?\d*\s*(KB|MB|GB))\)", text, re.I)
            if match:
                return match.group(1)
        return ""

    def get_hwp_attachments(self, detail_url: str) -> List[Attachment]:
        """HWP 첨부파일만 추출"""
        detail = self.get_detail(detail_url)
        if not detail:
            return []

        return [att for att in detail.attachments if att.file_ext.lower() == "hwp"]


# 테스트용 코드
if __name__ == "__main__":
    crawler = DetailCrawler()

    # 테스트 URL (실제 존재하는 게시글로 교체 필요)
    test_url = "https://www.snyouth.or.kr/fmcs/289?action=read&action-value=5b21014d4ebc7c635f54f16a77ae8bba"

    detail = crawler.get_detail(test_url)
    if detail:
        print(f"제목: {detail.title}")
        print(f"등록일: {detail.date}")
        print(f"첨부파일 수: {len(detail.attachments)}")
        for att in detail.attachments:
            print(f"  - {att.filename} ({att.file_size}) [{att.file_ext}]")
            print(f"    URL: {att.download_url}")
        print(f"\n본문 일부:\n{detail.content[:500]}...")
    else:
        print("상세 정보를 가져올 수 없습니다.")
