"""
성남시 수영장 자유수영 정보 수집기

파이프라인: 크롤링 → LLM 파싱 → DB 저장

실행 방법:
    python main.py              # 전체 파이프라인 실행
    python main.py --crawl      # 크롤링만 실행
    python main.py --parse      # 파싱만 실행
    python main.py --save       # DB 저장만 실행
"""
import argparse
import json

from config import settings
from config.logging_config import get_logger
from services.swim_crawler_service import SwimCrawlerService
from database.repository import SwimRepository
from validators.date_validator import validate_valid_month

logger = get_logger(__name__)
STORAGE_DIR = settings.STORAGE_DIR


def crawl(keyword: str = "수영", max_pages: int = 3):
    """1단계: 크롤링"""
    logger.info("=== 1단계: 크롤링 시작 ===")

    service = SwimCrawlerService()

    # 기본 스케줄 크롤링
    logger.info("기본 스케줄 크롤링...")
    base_schedules = service.crawl_base_schedules(save=True)
    total_facilities = len(base_schedules.get("snyouth", [])) + len(base_schedules.get("snhdc", []))
    logger.info(f"기본 스케줄 완료: {total_facilities}개 시설")

    # 월별 공지사항 크롤링
    logger.info("월별 공지사항 크롤링...")
    monthly_notices = service.crawl_monthly_notices(keyword=keyword, max_pages=max_pages, save=True)
    total_notices = len(monthly_notices.get("snyouth", [])) + len(monthly_notices.get("snhdc", []))
    logger.info(f"월별 공지사항 완료: {total_notices}개")

    logger.info("=== 크롤링 완료 ===")
    return monthly_notices


def parse(monthly_notices=None):
    """2단계: LLM 파싱 (첨부파일 기반)"""
    logger.info("=== 2단계: LLM 파싱 시작 ===")

    service = SwimCrawlerService()

    # 양쪽 기관 모두 처리
    parsed_results = []
    for org_key in ["snhdc", "snyouth"]:
        org_results = service.parse_attachments(
            org_key=org_key,
            monthly_notices=monthly_notices,
            save=True
        )
        parsed_results.extend(org_results)
        logger.info(f"{org_key.upper()} 파싱 완료: {len(org_results)}개")

    logger.info(f"전체 파싱 완료: {len(parsed_results)}개")

    # valid_month 검증
    validated_results = []
    invalid_count = 0

    for result in parsed_results:
        notice_date = result.get("source_notice_date", "")
        valid_month = result.get("valid_month", "")

        if validate_valid_month(valid_month, notice_date):
            validated_results.append(result)
        else:
            invalid_count += 1
            logger.warning(
                f"invalid valid_month 제외: {result.get('facility_name', 'Unknown')} - "
                f"{valid_month} (등록일: {notice_date})"
            )

    logger.info(f"검증 완료: {len(validated_results)}개 (검증 실패: {invalid_count}개)")

    # 검증된 결과 저장
    if validated_results:
        validated_path = STORAGE_DIR / "validated_parsed_data.json"
        with open(validated_path, "w", encoding="utf-8") as f:
            json.dump(validated_results, f, ensure_ascii=False, indent=2)
        logger.info(f"검증된 데이터 저장: {validated_path}")

    logger.info("=== 파싱 완료 ===")
    return validated_results


def save_to_db(validated_results=None):
    """3단계: DB 저장"""
    logger.info("=== 3단계: DB 저장 시작 ===")

    # 데이터 로드
    if validated_results is None:
        validated_path = STORAGE_DIR / "validated_parsed_data.json"
        if not validated_path.exists():
            logger.error(f"검증된 데이터 파일 없음: {validated_path}")
            return

        with open(validated_path, "r", encoding="utf-8") as f:
            validated_results = json.load(f)

    # DB 저장
    repo = SwimRepository()
    success_count = 0

    for data in validated_results:
        if repo.save_parsed_data(data):
            success_count += 1

    repo.close()
    logger.info(f"DB 저장 완료: {success_count}/{len(validated_results)}개")
    logger.info("=== DB 저장 완료 ===")


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description="성남시 수영장 자유수영 정보 수집기")
    parser.add_argument("--crawl", action="store_true", help="크롤링만 실행")
    parser.add_argument("--parse", action="store_true", help="파싱만 실행")
    parser.add_argument("--save", action="store_true", help="DB 저장만 실행")
    parser.add_argument("--keyword", default="수영", help="검색 키워드 (기본: 수영)")
    parser.add_argument("--max-pages", type=int, default=3, help="최대 페이지 수 (기본: 3)")

    args = parser.parse_args()

    # 특정 단계만 실행
    if args.crawl:
        crawl(keyword=args.keyword, max_pages=args.max_pages)
        return

    if args.parse:
        parse()
        return

    if args.save:
        save_to_db()
        return

    # 전체 파이프라인 실행
    logger.info("=== 전체 파이프라인 시작 ===")

    monthly_notices = crawl(keyword=args.keyword, max_pages=args.max_pages)
    validated_results = parse(monthly_notices=monthly_notices)
    save_to_db(validated_results=validated_results)

    logger.info("=== 전체 파이프라인 완료 ===")


if __name__ == "__main__":
    main()
