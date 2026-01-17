"""
MariaDB 연결 관리
"""
import os
import logging
from pathlib import Path
from contextlib import contextmanager

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# .env 파일에서 환경변수 로드
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# DB 설정
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 3306)),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "swim_parser_dev"),
    "charset": "utf8mb4",
}


def get_connection():
    """MariaDB 연결 반환"""
    try:
        import pymysql
        conn = pymysql.connect(**DB_CONFIG)
        logger.debug("DB 연결 성공")
        return conn
    except ImportError:
        logger.error("pymysql 패키지가 설치되지 않았습니다. pip install pymysql")
        raise
    except Exception as e:
        logger.error(f"DB 연결 실패: {e}")
        raise


@contextmanager
def get_cursor():
    """커서 컨텍스트 매니저"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"DB 작업 실패: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
