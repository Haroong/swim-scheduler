"""
수영장 정보 크롤링 서비스
크롤러들을 조합하여 수집 로직 실행
"""
import logging
from typing import List, Set

from crawler.list_crawler import ListCrawler, PostSummary
from crawler.detail_crawler import DetailCrawler
from crawler.attachment_downloader import AttachmentDownloader
from parser.hwp_text_extractor import HwpTextExtractor
from parser.pdf_text_extractor import PdfTextExtractor
from parser.content_validator import ContentValidator
from models.swim_program import SwimProgram
from storage.json_storage import JsonStorage

logger = logging.getLogger(__name__)


class SwimCrawlerService:
    """수영장 정보 크롤링 서비스"""

    def __init__(self):
        self.list_crawler = ListCrawler()
        self.detail_crawler = DetailCrawler()
        self.downloader = AttachmentDownloader()
        self.hwp_extractor = HwpTextExtractor()
        self.pdf_extractor = PdfTextExtractor()
        self.validator = ContentValidator()
        self.storage = JsonStorage()

    def run(self, keyword: str = "수영", max_pages: int = 3):
        """크롤링 실행"""
        logger.info("=== 성남시 수영장 자유수영 정보 수집 시작 ===")

        # 기존 데이터 로드
        existing_data, existing_urls = self.storage.load_existing_data()
        logger.info(f"기존 수집 데이터: {len(existing_data)}개")

        # 1단계: 게시글 목록 수집
        logger.info("1단계: 게시글 목록 수집")
        posts = self.list_crawler.get_posts(keyword=keyword, max_pages=max_pages)

        if not posts:
            logger.warning("수집된 게시글이 없습니다.")
            return

        logger.info(f"수집된 게시글: {len(posts)}개")

        # 2단계: 각 게시글 상세 정보 수집
        logger.info("2단계: 상세 정보 및 첨부파일 수집")
        new_programs = self._process_posts(posts, existing_urls)

        # 3단계: 결과 저장
        logger.info("3단계: 결과 저장")
        if new_programs:
            self.storage.save_results(existing_data, new_programs)
            logger.info(f"새로 수집: {len(new_programs)}개, 총 데이터: {len(existing_data) + len(new_programs)}개")
            self._print_summary(new_programs)
        else:
            logger.warning("새로 수집된 프로그램이 없습니다.")

        logger.info("=== 수집 완료 ===")

    def _process_posts(self, posts: List[PostSummary], existing_urls: Set[str]) -> List[SwimProgram]:
        """게시글 목록 처리"""
        collected_programs = []

        for post in posts:
            # 중복 체크
            if post.detail_url in existing_urls:
                logger.info(f"이미 수집된 게시글 건너뛰기: {post.title}")
                continue

            program = self._process_single_post(post)
            if program:
                collected_programs.append(program)

        return collected_programs

    def _process_single_post(self, post: PostSummary) -> SwimProgram | None:
        """단일 게시글 처리"""
        logger.info(f"처리 중: {post.title}")

        # 상세 페이지 크롤링
        detail = self.detail_crawler.get_detail(post.detail_url)
        if not detail:
            logger.warning(f"상세 정보 가져오기 실패: {post.title}")
            return None

        # 첨부파일에서 텍스트 추출
        raw_text, attachment_filename = self._extract_content(detail, post.title)
        if not raw_text:
            return None

        # SwimProgram 객체 생성
        program = SwimProgram(
            pool_name=post.facility_name,
            program_type="자유수영" if "자유수영" in post.title else "수영프로그램",
            raw_text=raw_text,
            source_url=post.detail_url,
            notice_title=post.title,
            notice_date=post.date,
            attachment_filename=attachment_filename
        )

        logger.info(f"프로그램 데이터 생성 완료: {post.title}")
        return program

    def _extract_content(self, detail, title: str) -> tuple[str, str]:
        """상세 페이지에서 콘텐츠 추출 (다중 파일 지원)"""
        import re

        # 제외 키워드 정의 (엄격/소프트 구분)
        strict_exclude = ["휴관", "긴급", "폐장", "공사"]  # 절대 처리 안 함
        soft_exclude = ["복장", "점검"]  # 우선순위만 낮춤

        # 첨부파일 필터링 및 우선순위 부여
        def calculate_priority(attachment):
            """파일명 기반 우선순위 점수 계산"""
            filename = attachment.filename
            score = 0

            # 엄격한 제외 키워드가 있으면 -1000점 (사실상 제외)
            if any(kw in filename for kw in strict_exclude):
                return -1000

            # 소프트 제외 키워드는 -50점
            if any(kw in filename for kw in soft_exclude):
                score -= 50

            # 우선순위 패턴 점수
            priority_patterns = [
                (r'자유수영', 100),           # 자유수영 직접 언급
                (r'\d+월.*수영.*프로그램', 80), # X월 수영 프로그램
                (r'진도표', 60),              # 진도표 (NEW!)
                (r'운영.*안내', 40),
                (r'프로그램', 20)
            ]

            for pattern, points in priority_patterns:
                if re.search(pattern, filename):
                    score += points

            return score

        # 모든 첨부파일 수집 및 정렬
        all_attachments = [
            a for a in detail.attachments
            if a.file_ext.lower() in ["hwp", "pdf"]
        ]

        # 우선순위로 정렬
        sorted_attachments = sorted(
            all_attachments,
            key=calculate_priority,
            reverse=True
        )

        # 우선순위 0 이상인 파일만 처리
        valid_attachments = [
            a for a in sorted_attachments
            if calculate_priority(a) >= 0
        ]

        if not valid_attachments:
            logger.warning("처리할 첨부파일이 없습니다")
            if detail.content:
                return detail.content, ""
            return "", ""

        # 다중 파일에서 자유수영 정보 추출
        extracted_contents = []

        for att in valid_attachments:
            logger.info(f"파일 다운로드 시도: {att.filename} (우선순위: {calculate_priority(att)})")
            filepath = self.downloader.download(att.download_url, att.filename)

            if not filepath:
                continue

            # 파일 형식에 따라 텍스트 추출
            text = self._extract_text_from_file(filepath, att.file_ext)

            if not text:
                continue

            # 자유수영 관련 콘텐츠인지 검증
            if self.validator.contains_swim_info(text):
                quality_score = self.validator.get_quality_score(text)
                extracted_contents.append({
                    'text': text,
                    'filename': att.filename,
                    'priority': calculate_priority(att),
                    'quality': quality_score
                })
                logger.info(f"✓ 자유수영 정보 발견: {att.filename} (품질점수: {quality_score})")
            else:
                logger.info(f"✗ 자유수영 정보 없음: {att.filename}")

        # 추출된 콘텐츠가 없으면 본문 사용
        if not extracted_contents:
            logger.warning("자유수영 정보가 포함된 파일이 없습니다")
            if detail.content:
                return detail.content, ""
            return "", ""

        # 품질 점수와 우선순위로 정렬
        extracted_contents.sort(
            key=lambda x: (x['quality'], x['priority']),
            reverse=True
        )

        # 여러 파일의 정보 병합
        merged_text, filenames = self._merge_contents(extracted_contents)

        logger.info(f"최종 선택: {', '.join(filenames)} ({len(filenames)}개 파일)")
        return merged_text, ', '.join(filenames)

    def _extract_text_from_file(self, filepath, file_ext: str) -> str:
        """파일에서 텍스트 추출"""
        text = ""

        if file_ext.lower() == "hwp":
            # HWP 추출 시도
            text = self.hwp_extractor.extract_text(filepath)
            if not text:
                text = self.hwp_extractor.extract_text_simple(filepath)
        elif file_ext.lower() == "pdf":
            text = self.pdf_extractor.extract_text(filepath)

        if text:
            logger.info(f"텍스트 추출 성공: {len(text)}자")
        else:
            logger.warning(f"텍스트 추출 실패")

        return text

    def _merge_contents(self, contents: list) -> tuple[str, list]:
        """여러 파일의 텍스트를 병합"""
        if not contents:
            return "", []

        # 가장 품질 높은 파일을 메인으로
        main_content = contents[0]
        merged_text = main_content['text']
        filenames = [main_content['filename']]

        # 추가 파일이 있고, 충분히 다른 정보가 있으면 병합
        for content in contents[1:]:
            additional_text = content['text']

            # 중복도 체크 (간단한 방식: 주요 키워드 겹치는지)
            main_keywords = set(self.validator.extract_swim_keywords(merged_text))
            additional_keywords = set(self.validator.extract_swim_keywords(additional_text))

            unique_keywords = additional_keywords - main_keywords

            # 새로운 키워드가 2개 이상 있으면 추가 정보로 간주
            if len(unique_keywords) >= 2:
                merged_text += f"\n\n{'='*60}\n[추가 정보 from {content['filename']}]\n{'='*60}\n{additional_text}"
                filenames.append(content['filename'])
                logger.info(f"추가 정보 병합: {content['filename']} (새 키워드: {unique_keywords})")

        return merged_text, filenames

    def _print_summary(self, programs: List[SwimProgram]):
        """수집 결과 요약 출력"""
        print("\n" + "=" * 60)
        print("수집 결과 요약")
        print("=" * 60)
        for i, prog in enumerate(programs, 1):
            print(f"{i}. [{prog.notice_date}] {prog.pool_name}")
            print(f"   제목: {prog.notice_title}")
            print(f"   타입: {prog.program_type}")
            print(f"   텍스트 길이: {len(prog.raw_text)}자")
            print()
