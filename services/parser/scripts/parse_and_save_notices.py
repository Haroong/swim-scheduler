"""
swim_programs.json의 공지사항을 LLM으로 파싱하여 DB에 저장
"""
import json
import logging
import re
from pathlib import Path
from core.parser.llm.llm_parser import LLMParser
from core.parser.validators.content_validator import ContentValidator
from infrastructure.database.repository import SwimRepository
from core.models.facility import Facility

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_notice_date(date_str: str) -> str:
    """
    날짜 문자열을 YYYY-MM 형식으로 변환

    예: "2026년 1월 16일" -> "2026-01"
        "2026-01-15 17:17:11" -> "2026-01"
    """
    # "YYYY년 M월" 패턴
    match = re.search(r'(\d{4})년\s*(\d{1,2})월', date_str)
    if match:
        year = match.group(1)
        month = match.group(2).zfill(2)
        return f"{year}-{month}"

    # "YYYY-MM-DD" 패턴
    match = re.search(r'(\d{4})-(\d{2})', date_str)
    if match:
        return f"{match.group(1)}-{match.group(2)}"

    return ""


def extract_facility_name(notice: dict) -> str:
    """공지사항에서 시설명 추출"""
    title = notice.get('title', '')
    content = notice.get('content_text', '')
    source_url = notice.get('source_url', '')

    # 1. 제목에서 시설명 추출 시도
    for facility in Facility:
        if facility.name in title:
            return facility.name

    # 2. source_url에서 SNYOUTH fmcs 코드로 추출
    for facility in Facility.snyouth_facilities():
        if f'fmcs/{facility.url_code}' in source_url:
            return facility.name

    # 3. content_text에서 SNYOUTH 시설명 추출
    for facility in Facility.snyouth_facilities():
        if facility.name in content:
            return facility.name

    # 4. snyouth 공지사항 기본값 처리
    if 'snyouth.or.kr' in source_url:
        # 전화번호로 시설 추론 (729-93xx, 729-96xx는 중원유스센터)
        phones = re.findall(r'729-\d{4}', content)
        if phones:
            return Facility.JUNGWON_YOUTH.name

        # 기본값: 중원유스센터 (가장 큰 시설이고 대부분의 공지사항이 중원유스센터 관련)
        return Facility.JUNGWON_YOUTH.name

    return ''


def main():
    """메인 실행 함수"""
    # JSON 파일 로드
    json_path = Path(__file__).parent / "storage" / "swim_programs.json"

    if not json_path.exists():
        logger.error(f"JSON 파일을 찾을 수 없습니다: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    logger.info(f"JSON 파일 로드 완료: {json_path}")

    # LLM Parser 및 Validator 초기화
    llm_parser = LLMParser()
    validator = ContentValidator()
    repo = SwimRepository()

    # 처리 통계
    total_count = 0
    parsed_count = 0
    saved_count = 0
    skipped_count = 0

    # 각 조직별 처리
    for org_name in ["snyouth", "snhdc"]:
        if org_name not in data:
            continue

        notices = data[org_name]
        logger.info(f"\n=== {org_name}: {len(notices)}개 공지사항 처리 중 ===")

        for idx, notice in enumerate(notices, 1):
            total_count += 1
            title = notice.get('title', 'Unknown')
            content = notice.get('content_text', '')

            logger.info(f"\n[{idx}/{len(notices)}] {title[:50]}...")

            # 1. content_text가 없으면 스킵
            if not content or len(content) < 100:
                logger.warning(f"  → 스킵: content_text 없음 또는 너무 짧음 ({len(content)}자)")
                skipped_count += 1
                continue

            # 2. 자유수영 관련 내용인지 검증
            if not validator.contains_swim_info(content):
                logger.warning(f"  → 스킵: 자유수영 정보 없음")
                skipped_count += 1
                continue

            # 3. 시설명 추출
            facility_name = extract_facility_name(notice)
            if not facility_name:
                logger.warning(f"  → 스킵: 시설명 추출 실패")
                skipped_count += 1
                continue

            # 4. LLM 파싱
            try:
                logger.info(f"  → LLM 파싱 중... (시설: {facility_name})")

                notice_date = notice.get('date', '')
                valid_month_guess = parse_notice_date(notice_date)

                parsed_result = llm_parser.parse(
                    raw_text=content,
                    facility_name=facility_name,
                    notice_date=notice_date
                )

                if not parsed_result:
                    logger.warning(f"  → 스킵: LLM 파싱 실패")
                    skipped_count += 1
                    continue

                parsed_count += 1
                logger.info(f"  ✓ LLM 파싱 완료")

                # 5. DB 저장
                db_data = {
                    "facility_name": facility_name,
                    "valid_month": parsed_result.get("valid_month", valid_month_guess),
                    "schedules": parsed_result.get("schedules", []),
                    "notes": parsed_result.get("notes", []),
                    "source_url": notice.get('source_url', '') or f"공지사항: {title}"
                }

                if repo.save_parsed_data(db_data):
                    saved_count += 1
                    logger.info(f"  ✓ DB 저장 완료")
                else:
                    logger.warning(f"  → DB 저장 실패 (중복 또는 오류)")

            except Exception as e:
                logger.error(f"  ✗ 처리 중 오류: {e}")
                skipped_count += 1

    repo.close()

    # 최종 통계
    logger.info(f"""
=== 처리 완료 ===
총 공지사항: {total_count}개
LLM 파싱 성공: {parsed_count}개
DB 저장 성공: {saved_count}개
스킵: {skipped_count}개
""")


if __name__ == "__main__":
    main()
