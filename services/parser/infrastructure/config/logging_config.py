"""
중앙 집중식 로깅 설정

환경별 로그 레벨 및 출력 형식 관리
구조화된 로깅 (JSON) 지원
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

from .settings import settings


class JsonFormatter(logging.Formatter):
    """
    JSON 형식 로그 포매터
    ELK Stack, CloudWatch 등 로그 수집 시스템과 연동 용이
    """

    def format(self, record: logging.LogRecord) -> str:
        import json
        from datetime import datetime

        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 예외 정보 추가
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # 추가 필드 (extra로 전달된 값)
        if hasattr(record, "extra_data"):
            log_data["extra"] = record.extra_data

        return json.dumps(log_data, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    """
    텍스트 형식 로그 포매터 (개발 환경용)
    가독성 높은 컬러 출력
    """

    # ANSI 색상 코드
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",
    }

    def format(self, record: logging.LogRecord) -> str:
        # 레벨별 색상 적용
        level_color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]

        # 포맷팅
        formatted = (
            f"{level_color}[{record.levelname:8s}]{reset} "
            f"{record.asctime} "
            f"{record.name:20s} "
            f"{record.message}"
        )

        # 예외 정보 추가
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"

        return formatted


def setup_logging(
    log_level: Optional[str] = None,
    log_format: Optional[str] = None,
    log_file_enabled: Optional[bool] = None,
):
    """
    로깅 설정 초기화

    Args:
        log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: 로그 포맷 ("json" 또는 "text")
        log_file_enabled: 파일 로깅 활성화 여부

    Example:
        >>> setup_logging(log_level="INFO", log_format="text")
    """
    # 기본값 설정
    log_level = log_level or settings.LOG_LEVEL
    log_format = log_format or settings.LOG_FORMAT
    log_file_enabled = log_file_enabled if log_file_enabled is not None else settings.LOG_FILE_ENABLED

    # 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # 기존 핸들러 제거 (중복 방지)
    root_logger.handlers.clear()

    # 포매터 선택
    if log_format == "json":
        formatter = JsonFormatter()
    else:
        formatter = TextFormatter(
            fmt="%(asctime)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    # 1. 콘솔 핸들러 (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 2. 파일 핸들러 (RotatingFileHandler)
    if log_file_enabled:
        settings.LOG_DIR.mkdir(parents=True, exist_ok=True)

        log_file_path = settings.LOG_DIR / f"{settings.APP_NAME}.log"
        file_handler = RotatingFileHandler(
            filename=log_file_path,
            maxBytes=settings.LOG_FILE_MAX_BYTES,
            backupCount=settings.LOG_FILE_BACKUP_COUNT,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # 3. Loki 핸들러 (프로덕션 환경)
    if settings.LOKI_ENABLED:
        try:
            import logging_loki

            loki_handler = logging_loki.LokiHandler(
                url=settings.LOKI_URL,
                tags=settings.LOKI_TAGS,
                version="1",
            )
            root_logger.addHandler(loki_handler)
            loki_status = "활성화"
        except ImportError:
            logging.warning("python-logging-loki가 설치되지 않았습니다. Loki 로깅을 건너뜁니다.")
            loki_status = "비활성화 (라이브러리 없음)"
        except Exception as e:
            logging.error(f"Loki 핸들러 설정 실패: {e}")
            loki_status = f"비활성화 (에러: {e})"
    else:
        loki_status = "비활성화"

    # 4. 외부 라이브러리 로그 레벨 조정
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.INFO)

    logging.info(
        f"로깅 설정 완료 | 레벨: {log_level} | 포맷: {log_format} | "
        f"파일 로깅: {'활성화' if log_file_enabled else '비활성화'} | "
        f"Loki: {loki_status}"
    )


def get_logger(name: str) -> logging.Logger:
    """
    모듈별 로거 획득

    Args:
        name: 로거 이름 (일반적으로 __name__ 사용)

    Returns:
        로거 인스턴스

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("작업 시작")
    """
    return logging.getLogger(name)


# ===================================================================
# 애플리케이션 시작 시 자동 설정
# ===================================================================

# 설정값에 따라 자동 초기화
setup_logging()


# ===================================================================
# 사용 예시
# ===================================================================

if __name__ == "__main__":
    # 로거 사용 예시
    logger = get_logger(__name__)

    logger.debug("디버그 메시지")
    logger.info("정보 메시지")
    logger.warning("경고 메시지")
    logger.error("에러 메시지")

    # 예외 로깅
    try:
        1 / 0
    except Exception as e:
        logger.exception("예외 발생")

    # 추가 필드와 함께 로깅 (JSON 포맷 사용 시)
    logger.info("크롤링 완료", extra={"extra_data": {"count": 10, "facility": "중원유스센터"}})
