"""
성남도시개발공사 첨부파일 다운로더
/downloadFile.ajax API를 통해 HWP/PDF 파일 다운로드
"""
import requests
from pathlib import Path
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DOWNLOAD_API_URL = "https://spo.isdc.co.kr/downloadFile.ajax"


class AttachmentDownloader:
    """SNHDC 첨부파일 다운로더"""

    def __init__(self, download_dir: Optional[Path] = None):
        """
        Args:
            download_dir: 다운로드 디렉토리 (기본값: ./downloads)
        """
        self.download_dir = download_dir or Path("downloads")
        self.download_dir.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def download_file(self,
                     idx: str,
                     file_no: int,
                     file_a: Optional[str] = None,
                     file_b: Optional[str] = None,
                     file_c: Optional[str] = None,
                     brd_flg: str = "1") -> Optional[Path]:
        """
        첨부파일 다운로드

        Args:
            idx: 게시글 ID
            file_no: 파일 번호 (0=file_a, 1=file_b, 2=file_c)
            file_a: HWP 파일명
            file_b: PDF 파일명
            file_c: 기타 파일명
            brd_flg: 게시판 플래그 (1=공지사항)

        Returns:
            다운로드된 파일 경로 또는 None
        """
        # 파일명 결정
        filename = None
        if file_no == 0 and file_a:
            filename = file_a
        elif file_no == 1 and file_b:
            filename = file_b
        elif file_no == 2 and file_c:
            filename = file_c

        if not filename:
            logger.warning(f"파일명을 찾을 수 없습니다: file_no={file_no}")
            return None

        logger.info(f"파일 다운로드 중: {filename}")

        # API 요청
        data = {
            "idx": idx,
            "file_a": file_a or "",
            "file_b": file_b or "",
            "file_c": file_c or "",
            "file_no": str(file_no),
            "brd_flg": brd_flg
        }

        try:
            response = self.session.post(DOWNLOAD_API_URL, data=data, timeout=30)
            response.raise_for_status()

            # 파일 저장
            file_path = self.download_dir / filename
            file_path.write_bytes(response.content)

            logger.info(f"✓ 다운로드 완료: {file_path} ({len(response.content)} bytes)")
            return file_path

        except requests.RequestException as e:
            logger.error(f"다운로드 실패: {filename} - {e}")
            return None

    def download_from_post_detail(self, post_detail) -> list[Path]:
        """
        PostDetail 객체에서 모든 첨부파일 다운로드

        Args:
            post_detail: DetailCrawler의 PostDetail 객체

        Returns:
            다운로드된 파일 경로 리스트
        """
        downloaded_files = []

        # HWP 파일 다운로드
        if post_detail.file_hwp:
            file_path = self.download_file(
                idx=post_detail.post_id,
                file_no=0,
                file_a=post_detail.file_hwp,
                file_b=post_detail.file_pdf
            )
            if file_path:
                downloaded_files.append(file_path)

        # PDF 파일 다운로드
        if post_detail.file_pdf:
            file_path = self.download_file(
                idx=post_detail.post_id,
                file_no=1,
                file_a=post_detail.file_hwp,
                file_b=post_detail.file_pdf
            )
            if file_path:
                downloaded_files.append(file_path)

        return downloaded_files


# 테스트용 코드
if __name__ == "__main__":
    downloader = AttachmentDownloader(download_dir=Path("test_downloads"))

    # 테스트: 평생스포츠센터 2월 프로그램
    print("="*60)
    print("첨부파일 다운로드 테스트")
    print("="*60)

    # HWP 다운로드
    hwp_file = downloader.download_file(
        idx="0002116",
        file_no=0,
        file_a="20260115_2월 운영프로그램 및 휴장일 안내문.hwp",
        file_b="20260115_2월 운영프로그램 및 휴장일 안내문.pdf"
    )

    if hwp_file:
        print(f"\nHWP 파일: {hwp_file}")
        print(f"크기: {hwp_file.stat().st_size} bytes")

    # PDF 다운로드
    pdf_file = downloader.download_file(
        idx="0002116",
        file_no=1,
        file_a="20260115_2월 운영프로그램 및 휴장일 안내문.hwp",
        file_b="20260115_2월 운영프로그램 및 휴장일 안내문.pdf"
    )

    if pdf_file:
        print(f"\nPDF 파일: {pdf_file}")
        print(f"크기: {pdf_file.stat().st_size} bytes")

    print("\n" + "="*60)
    print("테스트 완료")
    print("="*60)
