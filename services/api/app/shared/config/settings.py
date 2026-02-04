"""
API 설정 관리
환경 변수 기반 설정
"""
import os
from pathlib import Path
from typing import Dict

# 프로젝트 루트 경로
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# 환경 변수 로드 (.env 파일)
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    from dotenv import load_dotenv
    load_dotenv(ENV_FILE)


class Settings:
    """애플리케이션 설정"""

    # 애플리케이션 정보
    APP_NAME: str = "swim-api"
    ENV: str = os.getenv("ENV", "dev")

    # 데이터베이스 설정 (Parser의 설정 재사용)
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "swim_app")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "swim_dev")
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_POOL_MAX_OVERFLOW: int = int(os.getenv("DB_POOL_MAX_OVERFLOW", "10"))

    @property
    def db_url(self) -> str:
        """SQLAlchemy 데이터베이스 URL"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # 로깅 설정
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")  # "json" or "text"
    LOG_FILE_ENABLED: bool = os.getenv("LOG_FILE_ENABLED", "true").lower() == "true"
    LOG_DIR: Path = BASE_DIR / "logs"
    LOG_FILE_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_FILE_BACKUP_COUNT: int = 5

    # Loki 설정
    LOKI_ENABLED: bool = os.getenv("LOKI_ENABLED", "false").lower() == "true"
    LOKI_URL: str = os.getenv("LOKI_URL", "http://localhost:3100/loki/api/v1/push")

    @property
    def LOKI_TAGS(self) -> Dict[str, str]:
        """Loki 태그"""
        return {
            "application": self.APP_NAME,
            "environment": self.ENV,
        }

    # Redis 설정
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))

    # 캐시 TTL 설정 (초 단위)
    CACHE_TTL_FACILITIES: int = 86400   # 24시간 - 시설 목록
    CACHE_TTL_SCHEDULES: int = 86400    # 24시간 - 월별 스케줄
    CACHE_TTL_DAILY: int = 43200        # 12시간 - 일별 스케줄
    CACHE_TTL_CALENDAR: int = 86400     # 24시간 - 캘린더 데이터


# 싱글톤 인스턴스
settings = Settings()
