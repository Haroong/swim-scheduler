"""
성남도시개발공사 공지사항 상세 페이지 크롤러
list_crawler에서 가져온 데이터를 PostDetail로 변환
(SNHDC API는 list에서 이미 content를 제공하므로 별도 detail API 불필요)
"""
from typing import Optional, Dict
import logging

from crawler.base.detail_crawler import BaseDetailCrawler
from dto.crawler_dto import PostDetail, Attachment

logger = logging.getLogger(__name__)


class DetailCrawler(BaseDetailCrawler):
    """
    성남도시개발공사 공지사항 상세 크롤러

    특징: SNHDC API는 list에서 이미 content를 제공하므로
          별도 detail 페이지 크롤링 불필요
    """

    def get_detail(self, post_url: str, **kwargs) -> Optional[PostDetail]:
        """
        게시글 상세 정보 가져오기

        SNHDC는 list_item을 kwargs로 받아서 변환

        Args:
            post_url: 사용 안 함 (호환성 유지용)
            **kwargs: list_item (Dict) - API 응답 데이터

        Returns:
            PostDetail 객체
        """
        list_item = kwargs.get("list_item")
        if not list_item:
            self.logger.error("list_item이 필요합니다")
            return None

        return self.from_list_item(list_item)

    @staticmethod
    def from_list_item(list_item: Dict) -> Optional[PostDetail]:
        """
        list_crawler의 JSON 아이템을 PostDetail로 변환

        Args:
            list_item: selectNoticeList.ajax 응답의 data 배열 아이템

        Returns:
            PostDetail 객체 또는 None
        """
        try:
            # 필드 추출
            post_id = str(list_item.get("idx", ""))
            title = list_item.get("sbjt", "").strip()
            facility_name = list_item.get("com_nm", "").strip()
            enter_dt = list_item.get("enter_dt", "")
            content_html = list_item.get("content", "")

            # 첨부파일 정보
            file_a = list_item.get("file_a", "").strip()  # HWP
            file_b = list_item.get("file_b", "").strip()  # PDF

            # HTML에서 텍스트 추출
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content_html, "html.parser")
            for tag in soup(["script", "style"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            content_text = "\n".join(lines)

            # 첨부파일 정보 생성
            attachments = []
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

            post_detail = PostDetail(
                post_id=post_id,
                title=title,
                facility_name=facility_name,
                date=enter_dt,
                content_html=content_html,
                content_text=content_text,
                attachments=attachments,
                source_url=f"https://spo.isdc.co.kr/goNoticeView.do?idx={post_id}"
            )

            logger.debug(f"게시글 파싱 완료: {title} (첨부: {len(attachments)}개)")
            return post_detail

        except Exception as e:
            logger.error(f"PostDetail 변환 실패: {e}")
            return None

    @staticmethod
    def to_dict(post_detail: PostDetail) -> Dict:
        """PostDetail을 딕셔너리로 변환"""
        return {
            "post_id": post_detail.post_id,
            "title": post_detail.title,
            "facility_name": post_detail.facility_name,
            "date": post_detail.date,
            "content_html": post_detail.content_html,
            "content_text": post_detail.content_text,
            "attachments": [
                {
                    "filename": att.filename,
                    "file_size": att.file_size,
                    "file_ext": att.file_ext,
                    "download_url": att.download_url
                }
                for att in post_detail.attachments
            ],
            "has_attachment": post_detail.has_attachment,
            "source_url": post_detail.source_url
        }


# 테스트용 코드
if __name__ == "__main__":
    import sys
    import os
    # 상위 디렉토리를 path에 추가 (모듈 import를 위해)
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

    from crawler.snhdc.list_crawler import ListCrawler
    import requests

    print("="*60)
    print("list_crawler와 연동 테스트 (API 데이터 직접 사용)")
    print("="*60)

    # list_crawler에서 게시글 목록 가져오기
    list_crawler = ListCrawler()

    # API 직접 호출하여 원본 JSON 데이터 획득
    response = list_crawler.session.post(
        "https://spo.isdc.co.kr/selectNoticeList.ajax",
        data={"searchWord": "수영", "page": 1, "perPageNum": 10, "brd_flg": "1"},
        timeout=10
    )
    json_data = response.json()
    notice_list = json_data.get("data", [])

    print(f"\n총 {len(notice_list)}개 게시글 발견\n")

    # 첨부파일이 있는 게시글만 상세 변환
    for idx, item in enumerate(notice_list[:3], 1):  # 처음 3개만
        file_a = item.get("file_a", "")
        file_b = item.get("file_b", "")

        if file_a or file_b:
            print(f"\n{idx}. [{item.get('enter_dt', '')}] {item.get('sbjt', '')}")
            print(f"   시설: {item.get('com_nm', '')}")
            print(f"   첨부: 있음 → PostDetail로 변환 중...")

            detail = DetailCrawler.from_list_item(item)
            if detail:
                print(f"   ✓ 변환 완료")
                print(f"     HWP: {detail.file_hwp or '없음'}")
                print(f"     PDF: {detail.file_pdf or '없음'}")
                print(f"     본문 길이: {len(detail.content_text)} 자")
                print(f"     본문 미리보기:")
                preview = detail.content_text[:200].replace('\n', ' ')
                print(f"       {preview}...")
            else:
                print(f"   ✗ 변환 실패")

    print("\n" + "="*60)
    print("to_dict 메서드 테스트")
    print("="*60)

    if notice_list:
        first_item = notice_list[0]
        detail = DetailCrawler.from_list_item(first_item)
        if detail:
            import json
            detail_dict = DetailCrawler.to_dict(detail)
            print(json.dumps(detail_dict, ensure_ascii=False, indent=2))
