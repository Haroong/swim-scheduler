"""
성남시 수영장 자유수영 정보 수집기

파이프라인: 크롤링 → LLM 파싱 → DB 저장
"""
import json
import logging
from pathlib import Path

from service.swim_crawler_service import SwimCrawlerService
from llm.llm_parser import LLMParser
from database.repository import SwimRepository
from utils.date_validator import validate_valid_month

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

STORAGE_DIR = Path(__file__).parent / "storage"


def main():
    """메인 실행 함수: 크롤링 → 파싱 → DB 저장"""

    # 1단계: 크롤링
    logger.info("=== 1단계: 크롤링 시작 ===")
    crawler_service = SwimCrawlerService()
    crawler_service.run(keyword="수영", max_pages=3)

    # 2단계: LLM 파싱
    logger.info("=== 2단계: LLM 파싱 시작 ===")
    raw_data_path = STORAGE_DIR / "swim_programs.json"
    parsed_data_path = STORAGE_DIR / "parsed_swim_data.json"

    if not raw_data_path.exists():
        logger.error("크롤링 데이터 없음")
        return

    with open(raw_data_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    parser = LLMParser()
    items = [
        {
            "raw_text": item.get("raw_text", ""),
            "facility_name": item.get("pool_name", ""),
            "notice_date": item.get("notice_date", ""),
            "source_url": item.get("source_url", "")
        }
        for item in raw_data
    ]

    parsed_results = parser.parse_batch(items)

    # valid_month 검증 및 필터링
    validated_results = []
    invalid_count = 0
    for i, result in enumerate(parsed_results):
        notice_date = items[i].get("notice_date", "")
        valid_month = result.get("valid_month", "")

        if validate_valid_month(valid_month, notice_date):
            validated_results.append(result)
        else:
            invalid_count += 1
            logger.warning(
                f"invalid valid_month 제외: {result.get('facility_name', 'Unknown')} - "
                f"{valid_month} (등록일: {notice_date})"
            )

    logger.info(f"파싱 완료: {len(validated_results)}개 (검증 실패: {invalid_count}개)")

    with open(parsed_data_path, "w", encoding="utf-8") as f:
        json.dump(validated_results, f, ensure_ascii=False, indent=2)

    logger.info(f"검증된 데이터 저장: {parsed_data_path}")

    # 3단계: DB 저장
    logger.info("=== 3단계: DB 저장 시작 ===")
    repo = SwimRepository()
    success_count = 0

    for data in validated_results:
        if repo.save_parsed_data(data):
            success_count += 1

    repo.close()
    logger.info(f"DB 저장 완료: {success_count}/{len(validated_results)}개")

    logger.info("=== 전체 파이프라인 완료 ===")


if __name__ == "__main__":
    main()
