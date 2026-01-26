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

from infrastructure.config import settings
from infrastructure.config.logging_config import get_logger
from application.swim_crawler_service import SwimCrawlerService
from infrastructure.database.repository import SwimRepository
from core.parser.validators.date_validator import validate_valid_month
from core.models.facility import Organization

logger = get_logger(__name__)
STORAGE_DIR = settings.STORAGE_DIR

# 모든 기관 목록
ALL_ORGANIZATIONS = list(Organization)


def _get_search_keywords(primary_keyword: str) -> list[str]:
    """
    검색 키워드 목록 생성

    Args:
        primary_keyword: 주 검색 키워드

    Returns:
        검색할 키워드 목록 (중복 제거)
    """
    if primary_keyword == "일일자유":
        return [primary_keyword]
    return [primary_keyword, "일일자유"]


def _merge_notices_without_duplicates(all_notices: dict, new_notices: dict, org_key: str) -> int:
    """
    중복 제거하면서 공지사항 병합

    Args:
        all_notices: 기존 공지사항 딕셔너리 (수정됨)
        new_notices: 새로운 공지사항 딕셔너리
        org_key: 기관 키 (snyouth, snhdc)

    Returns:
        추가된 공지사항 개수
    """
    existing_urls = {n.get("source_url") for n in all_notices[org_key]}
    new_items = [n for n in new_notices.get(org_key, []) if n.get("source_url") not in existing_urls]
    all_notices[org_key].extend(new_items)
    return len(new_items)


def _crawl_monthly_notices_with_keywords(
    service: SwimCrawlerService,
    keywords: list[str],
    max_pages: int
) -> dict:
    """
    여러 키워드로 공지사항 크롤링 및 병합

    Args:
        service: SwimCrawlerService 인스턴스
        keywords: 검색 키워드 목록
        max_pages: 키워드당 최대 페이지 수

    Returns:
        {"snyouth": [...], "snhdc": [...]} 형태의 병합된 공지사항
    """
    all_notices = {org.value: [] for org in ALL_ORGANIZATIONS}

    for keyword in keywords:
        logger.info(f"키워드 '{keyword}' 검색 중...")
        monthly_notices = service.crawl_monthly_notices(keyword=keyword, max_pages=max_pages, save=False)

        # 중복 제거하면서 병합
        for org in ALL_ORGANIZATIONS:
            new_count = _merge_notices_without_duplicates(all_notices, monthly_notices, org.value)
            logger.info(f"  {org.value}: {new_count}개 신규 공지")

    return all_notices


def _validate_parsed_results(parsed_results: list) -> tuple[list, int]:
    """
    파싱 결과의 valid_month 검증

    Args:
        parsed_results: 파싱된 결과 리스트

    Returns:
        (validated_results, invalid_count) 튜플
    """
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
    return validated_results, invalid_count


def _save_validated_results(validated_results: list) -> None:
    """
    검증된 파싱 결과를 JSON 파일로 저장

    Args:
        validated_results: 검증된 결과 리스트
    """
    if validated_results:
        validated_path = STORAGE_DIR / "validated_parsed_data.json"
        with open(validated_path, "w", encoding="utf-8") as f:
            json.dump(validated_results, f, ensure_ascii=False, indent=2)
        logger.info(f"검증된 데이터 저장: {validated_path}")


def crawl(keyword: str = "수영", max_pages: int = 3):
    """1단계: 크롤링"""
    logger.info("=== 1단계: 크롤링 시작 ===")

    service = SwimCrawlerService()

    # 기본 스케줄 크롤링
    logger.info("기본 스케줄 크롤링...")
    base_schedules = service.crawl_base_schedules(save=True)
    total_facilities = sum(len(facilities) for facilities in base_schedules.values())
    logger.info(f"기본 스케줄 완료: {total_facilities}개 시설")

    # 월별 공지사항 크롤링 (여러 키워드로 검색)
    logger.info("월별 공지사항 크롤링...")
    keywords = _get_search_keywords(keyword)
    all_notices = _crawl_monthly_notices_with_keywords(service, keywords, max_pages)

    # 병합된 결과 저장
    for org in ALL_ORGANIZATIONS:
        service.storage.save_monthly_notices(org, all_notices[org.value])

    total_notices = sum(len(notices) for notices in all_notices.values())
    logger.info(f"월별 공지사항 완료: {total_notices}개 (중복 제거 후)")

    logger.info("=== 크롤링 완료 ===")
    return all_notices


def parse(monthly_notices=None):
    """2단계: LLM 파싱 (첨부파일 기반)"""
    logger.info("=== 2단계: LLM 파싱 시작 ===")

    service = SwimCrawlerService()

    # 양쪽 기관 모두 처리
    parsed_results = []
    for org in ALL_ORGANIZATIONS:
        org_results = service.parse_attachments(
            org=org,
            monthly_notices=monthly_notices,
            save=True
        )
        parsed_results.extend(org_results)
        logger.info(f"{org.name} 파싱 완료: {len(org_results)}개")

    logger.info(f"전체 파싱 완료: {len(parsed_results)}개")

    # valid_month 검증 및 저장
    validated_results, _ = _validate_parsed_results(parsed_results)
    _save_validated_results(validated_results)

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
