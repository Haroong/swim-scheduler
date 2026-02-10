"""
파싱 실행 서비스
- 공지사항에서 첨부파일 다운로드
- 텍스트 추출 및 검증
- LLM 파싱
"""
import logging
from pathlib import Path
from typing import List, Optional, Dict
from core.crawler.snhdc.attachment_downloader import AttachmentDownloader as SnhdcAttachmentDownloader
from core.crawler.snyouth.attachment_downloader import AttachmentDownloader as SnyouthAttachmentDownloader
from core.parser.extractors.hwp_text_extractor import HwpTextExtractor
from core.parser.extractors.pdf_text_extractor import PdfTextExtractor
from core.parser.validators.content_validator import ContentValidator
from core.parser.llm.llm_parser import LLMParser
from core.models.crawler import PostDetail
from core.models.facility_manager import FacilityNameMatcher

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
                # HWP 또는 PDF 파일 찾기 (우선순위 기반)
                file_path = self._select_best_file(file_paths)
                if file_path:
                    logger.info(f"파일 다운로드 성공: {file_path.name}")

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
            notice_title=notice.title,
            source_url=notice.source_url
        )

        if parsed_data:
            # ParsedScheduleData 객체를 딕셔너리로 변환
            result = parsed_data.to_dict()

            # LLM이 시설명을 추출하지 못한 경우, 크롤링 시 수집한 시설명 사용
            if not result.get("facility_name") and notice.facility_name:
                result["facility_name"] = notice.facility_name
                logger.info(f"크롤링 시설명 사용: {notice.facility_name}")

            # 시설명 정규화 (Fuzzy matching)
            if result.get("facility_name"):
                original_name = result["facility_name"]
                normalized_name, confidence, match_type = FacilityNameMatcher.normalize_facility_name(original_name)

                if normalized_name != original_name:
                    logger.info(
                        f"시설명 정규화: '{original_name}' -> '{normalized_name}' "
                        f"(confidence: {confidence:.2f}, type: {match_type})"
                    )
                    result["facility_name"] = normalized_name

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

    def _select_best_file(self, file_paths: List[Path]) -> Optional[Path]:
        """
        첨부파일 중 가장 적합한 파일 선택 (우선순위 기반)

        Args:
            file_paths: 첨부파일 경로 리스트

        Returns:
            선택된 파일 경로 (없으면 None)
        """
        # 우선순위 키워드 (높을수록 좋음)
        priority_keywords = ["프로그램", "스케줄", "진도", "자유수영", "운영", "일일"]

        # 제외 키워드 (낮을수록 좋음)
        exclude_keywords = ["이용법규", "해설", "규칙", "약관", "안내문"]

        def get_file_priority(fp: Path) -> int:
            """파일 우선순위 점수 계산"""
            if fp.suffix.lower() not in [".hwp", ".pdf"]:
                return -100  # 지원하지 않는 형식

            score = 0
            filename = fp.name

            # 우선순위 키워드 가산점
            for keyword in priority_keywords:
                if keyword in filename:
                    score += 10

            # 제외 키워드 감점
            for keyword in exclude_keywords:
                if keyword in filename:
                    score -= 20

            # 파일명에서 날짜 추출 (YYYYMMDD 형식)
            import re
            date_match = re.search(r'(\d{8})', filename)
            if date_match:
                # 날짜를 점수에 반영 (최신 파일이 높은 점수)
                # 예: 20260115 -> +20260115 (날짜를 직접 점수로 사용)
                date_score = int(date_match.group(1))
                score += date_score

            # HWP 파일 약간 선호 (텍스트 추출이 더 안정적) - 날짜보다 우선순위 낮음
            if fp.suffix.lower() == ".hwp":
                score += 1

            return score

        # HWP/PDF 파일만 필터링
        valid_files = [fp for fp in file_paths if fp.suffix.lower() in [".hwp", ".pdf"]]

        if not valid_files:
            return None

        # 우선순위 정렬하여 가장 높은 점수의 파일 선택
        sorted_files = sorted(valid_files, key=get_file_priority, reverse=True)
        selected = sorted_files[0]

        # 디버깅용 로그
        if len(sorted_files) > 1:
            logger.info(f"첨부파일 {len(sorted_files)}개 중 선택: {selected.name} (점수: {get_file_priority(selected)})")

        return selected

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
