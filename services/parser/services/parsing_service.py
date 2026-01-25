"""
파싱 실행 서비스
- 공지사항에서 첨부파일 다운로드
- 텍스트 추출 및 검증
- LLM 파싱
"""
import logging
from pathlib import Path
from typing import List, Optional, Dict
from crawler.snhdc.attachment_downloader import AttachmentDownloader as SnhdcAttachmentDownloader
from crawler.snyouth.attachment_downloader import AttachmentDownloader as SnyouthAttachmentDownloader
from extractors.hwp_text_extractor import HwpTextExtractor
from extractors.pdf_text_extractor import PdfTextExtractor
from validators.content_validator import ContentValidator
from llm.llm_parser import LLMParser
from dto.crawler_dto import PostDetail

logger = logging.getLogger(__name__)


class ParsingService:
    """파싱 실행 서비스"""

    def __init__(self, download_dir: Path, org_key: str = "snhdc"):
        """
        Args:
            download_dir: 파일 다운로드 디렉토리
            org_key: 기관 키 ("snhdc" 또는 "snyouth")
        """
        self.download_dir = download_dir
        self.org_key = org_key

        # 기관별 다운로더 선택
        if org_key == "snyouth":
            self.downloader = SnyouthAttachmentDownloader(download_dir=download_dir)
        else:
            self.downloader = SnhdcAttachmentDownloader(download_dir=download_dir)

        self.hwp_extractor = HwpTextExtractor()
        self.pdf_extractor = PdfTextExtractor()
        self.validator = ContentValidator()
        self.llm_parser = LLMParser()

    def parse_from_notice(self, notice: PostDetail) -> Optional[Dict]:
        """
        공지사항에서 스케줄 파싱

        Args:
            notice: 게시글 상세 정보

        Returns:
            파싱된 스케줄 데이터 (실패 시 None)
        """
        logger.info(f"파싱 시작: {notice.title}")

        # 1. 첨부파일 다운로드 (있는 경우)
        file_path = None
        text = None

        if notice.has_attachment:
            file_paths = self.downloader.download_from_post_detail(notice)
            if file_paths:
                # HWP 또는 PDF 파일 찾기
                for fp in file_paths:
                    if fp.suffix.lower() in [".hwp", ".pdf"]:
                        file_path = fp
                        logger.info(f"파일 다운로드 성공: {file_path.name}")
                        break

        # 2. 텍스트 추출
        if file_path:
            text = self._extract_text(file_path)
        else:
            # 본문에서 직접 파싱
            text = notice.content_text

        if not text or len(text) < 50:
            logger.warning(f"텍스트 추출 실패 또는 텍스트가 너무 짧음: {notice.title}")
            return None

        logger.info(f"텍스트 추출 성공: {len(text)}자")

        # 3. 콘텐츠 검증
        if not self.validator.contains_swim_info(text):
            logger.warning(f"수영 정보가 포함되지 않음: {notice.title}")
            return None

        logger.info("콘텐츠 검증 통과")

        # 4. LLM 파싱
        parsed_data = self.llm_parser.parse(
            raw_text=text,
            facility_name=notice.facility_name,
            notice_date=notice.date,
            source_url=notice.source_url
        )

        if parsed_data:
            # ParsedScheduleData 객체를 딕셔너리로 변환
            result = parsed_data.to_dict()

            # LLM이 시설명을 추출하지 못한 경우, 크롤링 시 수집한 시설명 사용
            if not result.get("facility_name") and notice.facility_name:
                result["facility_name"] = notice.facility_name
                logger.info(f"크롤링 시설명 사용: {notice.facility_name}")

            # 추가 메타데이터 포함
            result["source_file"] = file_path.name if file_path else None
            result["source_notice_title"] = notice.title
            result["source_notice_date"] = notice.date
            logger.info(f"파싱 성공: {notice.title}")
            return result
        else:
            logger.warning(f"LLM 파싱 실패: {notice.title}")
            return None

    def parse_batch(self, notices: List[PostDetail]) -> List[Dict]:
        """
        여러 공지사항 일괄 파싱

        Args:
            notices: 게시글 상세 정보 리스트

        Returns:
            파싱된 스케줄 데이터 리스트
        """
        logger.info(f"일괄 파싱 시작: {len(notices)}개")

        results = []
        for i, notice in enumerate(notices, 1):
            logger.info(f"[{i}/{len(notices)}] 처리 중...")
            result = self.parse_from_notice(notice)
            if result:
                results.append(result)

        logger.info(f"일괄 파싱 완료: {len(results)}/{len(notices)}개 성공")
        return results

    def _extract_text(self, file_path: Path) -> Optional[str]:
        """
        파일에서 텍스트 추출

        Args:
            file_path: 파일 경로

        Returns:
            추출된 텍스트 (실패 시 None)
        """
        try:
            ext = file_path.suffix.lower()
            if ext == ".hwp":
                return self.hwp_extractor.extract_text(file_path)
            elif ext == ".pdf":
                return self.pdf_extractor.extract_text(file_path)
            else:
                logger.warning(f"지원하지 않는 파일 형식: {ext}")
                return None
        except Exception as e:
            logger.error(f"텍스트 추출 실패: {file_path.name} - {e}")
            return None
