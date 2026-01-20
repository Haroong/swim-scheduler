"""
성남시청소년청년재단 첨부파일 다운로더
URL이 직접 제공되므로 단순 HTTP GET 다운로드
"""
from pathlib import Path
from typing import Optional, List
import logging

from dto.crawler_dto import PostDetail
from utils.http_utils import create_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AttachmentDownloader:
    """SNYOUTH 첨부파일 다운로더"""

    def __init__(self, download_dir: Optional[Path] = None):
        """
        Args:
            download_dir: 다운로드 디렉토리 (기본값: ./downloads)
        """
        self.download_dir = download_dir or Path("downloads")
        self.download_dir.mkdir(parents=True, exist_ok=True)

        self.session = create_session()

    def download_file(self, download_url: str, filename: str) -> Optional[Path]:
        """
        첨부파일 다운로드 (직접 URL 사용)

        Args:
            download_url: 다운로드 URL
            filename: 저장할 파일명

        Returns:
            다운로드된 파일 경로 또는 None
        """
        if not download_url or not filename:
            logger.warning("다운로드 URL 또는 파일명이 없습니다.")
            return None

        logger.info(f"파일 다운로드 중: {filename}")

        try:
            response = self.session.get(download_url, timeout=30)
            response.raise_for_status()

            # 파일 저장
            file_path = self.download_dir / filename
            file_path.write_bytes(response.content)

            logger.info(f"다운로드 완료: {file_path} ({len(response.content)} bytes)")
            return file_path

        except requests.RequestException as e:
            logger.error(f"다운로드 실패: {filename} - {e}")
            return None

    def download_from_post_detail(self, post_detail: PostDetail) -> List[Path]:
        """
        PostDetail 객체에서 모든 첨부파일 다운로드

        Args:
            post_detail: PostDetail 객체 (attachments에 download_url 포함)

        Returns:
            다운로드된 파일 경로 리스트
        """
        downloaded_files = []

        for attachment in post_detail.attachments:
            # HWP 또는 PDF만 다운로드
            if attachment.file_ext.lower() not in ["hwp", "pdf"]:
                continue

            file_path = self.download_file(
                download_url=attachment.download_url,
                filename=attachment.filename
            )
            if file_path:
                downloaded_files.append(file_path)

        return downloaded_files


# 테스트용 코드
if __name__ == "__main__":
    downloader = AttachmentDownloader(download_dir=Path("test_downloads"))

    print("=" * 60)
    print("SNYOUTH 첨부파일 다운로드 테스트")
    print("=" * 60)

    # 테스트 URL (실제 존재하는 파일로 교체 필요)
    test_url = "https://www.snyouth.or.kr/File/Download/12345"
    test_filename = "test_file.pdf"

    file_path = downloader.download_file(test_url, test_filename)
    if file_path:
        print(f"다운로드 완료: {file_path}")
    else:
        print("다운로드 실패")

    print("=" * 60)
