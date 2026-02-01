"""
애플리케이션 설정

Pydantic Settings를 사용하여 환경변수 기반 설정 관리
환경별 설정: 개발(dev), 스테이징(staging), 프로덕션(prod)
"""
from pathlib import Path
from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    애플리케이션 전역 설정

    환경변수 우선순위:
    1. 시스템 환경변수
    2. .env 파일
    3. 기본값
    """

    # ===================================================================
    # 기본 설정
    # ===================================================================

    ENV: Literal["dev", "staging", "prod"] = "dev"
    DEBUG: bool = True
    APP_NAME: str = "swim-scheduler-parser"

    # ===================================================================
    # 디렉토리 경로
    # ===================================================================

    BASE_DIR: Path = Path(__file__).parent.parent
    STORAGE_DIR: Path = BASE_DIR / "storage"
    DOWNLOAD_DIR: Path = BASE_DIR / "downloads"
    LOG_DIR: Path = BASE_DIR / "logs"

    # ===================================================================
    # LLM 설정
    # ===================================================================

    ANTHROPIC_API_KEY: str
    LLM_MODEL: str = "claude-sonnet-4-5-20250929"
    LLM_MAX_TOKENS: int = 4000
    LLM_TEMPERATURE: float = 0.0

    # ===================================================================
    # Database 설정
    # ===================================================================

    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str = "swim_scheduler"
    DB_CHARSET: str = "utf8mb4"

    # Connection Pool 설정
    DB_POOL_SIZE: int = 5
    DB_POOL_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30

    # ===================================================================
    # 크롤링 설정
    # ===================================================================

    # 기관별 베이스 URL
    SNYOUTH_BASE_URL: str = "https://www.snyouth.or.kr"
    SNHDC_BASE_URL: str = "https://spo.isdc.co.kr"

    # 크롤링 제한
    CRAWL_MAX_PAGES: int = 5
    CRAWL_MAX_FILES: int = 10
    CRAWL_DELAY_SECONDS: float = 0.5  # Rate limiting

    # HTTP 타임아웃
    HTTP_TIMEOUT: int = 30
    HTTP_MAX_RETRIES: int = 3

    # ===================================================================
    # 로깅 설정
    # ===================================================================

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # "json" 또는 "text"
    LOG_FILE_ENABLED: bool = True
    LOG_FILE_MAX_BYTES: int = 10_485_760  # 10MB
    LOG_FILE_BACKUP_COUNT: int = 5

    # Loki 설정 (로컬/프로덕션 모두 사용)
    LOKI_ENABLED: bool = True
    LOKI_URL: str = "http://localhost:3100/loki/api/v1/push"
    LOKI_TAGS: dict = {"application": "swim-scheduler-parser", "env": "local"}

    # ===================================================================
    # 파싱 설정
    # ===================================================================

    # 콘텐츠 검증
    MIN_CONTENT_LENGTH: int = 100

    # 파일 처리
    MAX_FILE_SIZE_MB: int = 10
    SUPPORTED_FILE_EXTENSIONS: list[str] = ["hwp", "pdf", "xlsx"]

    # ===================================================================
    # Pydantic Settings 설정
    # ===================================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # 추가 환경변수 무시
    )

    # ===================================================================
    # 헬퍼 메서드
    # ===================================================================

    @property
    def is_dev(self) -> bool:
        """개발 환경 여부"""
        return self.ENV == "dev"

    @property
    def is_prod(self) -> bool:
        """프로덕션 환경 여부"""
        return self.ENV == "prod"

    @property
    def db_url(self) -> str:
        """데이터베이스 연결 URL"""
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?charset={self.DB_CHARSET}"
        )

    def ensure_directories(self):
        """필요한 디렉토리 생성"""
        for directory in [self.STORAGE_DIR, self.DOWNLOAD_DIR, self.LOG_DIR]:
            directory.mkdir(parents=True, exist_ok=True)


# ===================================================================
# 전역 설정 인스턴스
# ===================================================================

settings = Settings()

# 디렉토리 생성
settings.ensure_directories()


# ===================================================================
# 사용 예시
# ===================================================================

if __name__ == "__main__":
    print(f"환경: {settings.ENV}")
    print(f"디버그 모드: {settings.DEBUG}")
    print(f"LLM 모델: {settings.LLM_MODEL}")
    print(f"DB URL: {settings.db_url}")
    print(f"스토리지 디렉토리: {settings.STORAGE_DIR}")
