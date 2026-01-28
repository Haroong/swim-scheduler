"""
성남시 수영장 스케줄 자동 수집 스케줄러

매일 자정(00:00)에 자동으로 크롤링 및 파싱 실행
"""
import signal
import sys
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from infrastructure.config.logging_config import get_logger
from main import crawl, parse, save_to_db

logger = get_logger(__name__)


def run_daily_task():
    """매일 실행되는 크롤링 및 파싱 작업"""
    try:
        logger.info("=" * 80)
        logger.info(f"일일 크롤링 작업 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)

        # 1. 크롤링
        monthly_notices = crawl(keyword="수영", max_pages=3)

        # 2. LLM 파싱
        validated_results = parse(monthly_notices=monthly_notices)

        # 3. DB 저장
        save_to_db(validated_results=validated_results)

        logger.info("=" * 80)
        logger.info(f"일일 크롤링 작업 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"일일 크롤링 작업 중 오류 발생: {e}", exc_info=True)


def shutdown_handler(signum, frame):
    """스케줄러 종료 핸들러"""
    logger.info("스케줄러 종료 신호 수신. 안전하게 종료합니다...")
    sys.exit(0)


def main():
    """스케줄러 메인 함수"""
    # 종료 신호 핸들러 등록 (Ctrl+C, Docker stop 등)
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    # 스케줄러 생성
    scheduler = BlockingScheduler()

    # 매일 자정(00:00)에 실행
    scheduler.add_job(
        run_daily_task,
        trigger=CronTrigger(hour=0, minute=0),
        id="daily_crawl_job",
        name="성남시 수영장 일일 크롤링",
        replace_existing=True
    )

    logger.info("=" * 80)
    logger.info("성남시 수영장 스케줄 수집 스케줄러 시작")
    logger.info("실행 시각: 매일 00:00 (KST)")
    logger.info("=" * 80)

    # 시작 시 즉시 한 번 실행 (선택사항)
    logger.info("시작 시 초기 크롤링 실행...")
    run_daily_task()

    # 스케줄러 실행 (블로킹)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("스케줄러 종료")


if __name__ == "__main__":
    main()
