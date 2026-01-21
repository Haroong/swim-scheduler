"""
성남시청소년청년재단 첨부파일 다운로더
base AttachmentDownloader를 상속하여 사용
"""
from pathlib import Path
from typing import List
import logging

from crawler.base.attachment_downloader import BaseAttachmentDownloader
from dto.crawler_dto import PostDetail

logger = logging.getLogger(__name__)


class AttachmentDownloader(BaseAttachmentDownloader):
    """SNYOUTH 첨부파일 다운로더 (base 상속)"""

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

            file_path = self.download(
                url=attachment.download_url,
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

    file_path = downloader.download(test_url, test_filename)
    if file_path:
        print(f"다운로드 완료: {file_path}")
    else:
        print("다운로드 실패")

    print("=" * 60)
