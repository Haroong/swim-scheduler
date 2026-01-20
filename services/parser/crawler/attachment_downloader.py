"""
첨부파일 다운로더
게시글의 첨부파일을 다운로드하여 로컬에 저장
"""
import os
from pathlib import Path
from typing import Optional
import logging
import re
from urllib.parse import unquote

from utils.http_utils import create_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 기본 저장 경로
DEFAULT_DOWNLOAD_DIR = Path(__file__).parent.parent / "storage" / "raw_data"


class AttachmentDownloader:
    """첨부파일 다운로더"""

    def __init__(self, download_dir: Optional[Path] = None):
        """
        Args:
            download_dir: 다운로드 디렉토리 경로
        """
        self.download_dir = download_dir or DEFAULT_DOWNLOAD_DIR
        self.download_dir.mkdir(parents=True, exist_ok=True)

        self.session = create_session()

    def download(self, url: str, filename: Optional[str] = None) -> Optional[Path]:
        """
        파일 다운로드

        Args:
            url: 다운로드 URL
            filename: 저장할 파일명 (없으면 자동 추출)

        Returns:
            저장된 파일 경로 또는 None
        """
        try:
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"다운로드 실패 ({url}): {e}")
            return None

        # 파일명 결정
        if not filename:
            filename = self._extract_filename_from_response(response, url)

        if not filename:
            logger.error(f"파일명을 결정할 수 없음: {url}")
            return None

        # 안전한 파일명으로 변환
        safe_filename = self._sanitize_filename(filename)
        file_path = self.download_dir / safe_filename

        # 파일 저장
        try:
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            logger.info(f"다운로드 완료: {file_path}")
            return file_path

        except IOError as e:
            logger.error(f"파일 저장 실패: {e}")
            return None

    def _extract_filename_from_response(self, response, url: str) -> Optional[str]:
        """응답 헤더 또는 URL에서 파일명 추출"""
        # Content-Disposition 헤더에서 파일명 추출
        content_disp = response.headers.get("Content-Disposition", "")
        if content_disp:
            # filename*=UTF-8'' 형식
            match = re.search(r"filename\*=(?:UTF-8''|utf-8'')(.+)", content_disp, re.I)
            if match:
                return unquote(match.group(1))

            # filename="..." 형식
            match = re.search(r'filename="(.+)"', content_disp)
            if match:
                return match.group(1)

            # filename=... 형식 (따옴표 없음)
            match = re.search(r"filename=([^\s;]+)", content_disp)
            if match:
                return match.group(1)

        # URL에서 파일명 추출 (마지막 경로 세그먼트)
        url_path = url.split("?")[0]
        if "/" in url_path:
            potential_filename = url_path.split("/")[-1]
            if "." in potential_filename:
                return unquote(potential_filename)

        return None

    def _sanitize_filename(self, filename: str) -> str:
        """파일명에서 안전하지 않은 문자 제거"""
        # Windows에서 사용할 수 없는 문자 제거
        invalid_chars = r'[<>:"/\\|?*]'
        safe_name = re.sub(invalid_chars, "_", filename)

        # 연속된 공백 및 언더스코어 정리
        safe_name = re.sub(r"_+", "_", safe_name)
        safe_name = re.sub(r"\s+", " ", safe_name)

        # 앞뒤 공백 및 점 제거
        safe_name = safe_name.strip(". ")

        # 최대 길이 제한 (255자)
        if len(safe_name) > 255:
            name, ext = os.path.splitext(safe_name)
            safe_name = name[:255-len(ext)] + ext

        return safe_name

    def download_hwp(self, url: str, filename: Optional[str] = None) -> Optional[Path]:
        """HWP 파일 다운로드 (확장자 검증 포함)"""
        filepath = self.download(url, filename)

        if filepath and not filepath.suffix.lower() == ".hwp":
            logger.warning(f"다운로드된 파일이 HWP가 아님: {filepath}")

        return filepath


# 테스트용 코드
if __name__ == "__main__":
    downloader = AttachmentDownloader()

    # 테스트 다운로드 (실제 존재하는 파일 URL로 교체 필요)
    test_url = "https://www.snyouth.or.kr/File/Download/100c1cdbf2a1306e341918e1a91869ec"

    result = downloader.download(test_url, "test_file.png")
    if result:
        print(f"저장 완료: {result}")
    else:
        print("다운로드 실패")
