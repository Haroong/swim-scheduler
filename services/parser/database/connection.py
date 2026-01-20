"""
MariaDB 연결 관리
"""
import logging
from contextlib import contextmanager

from config import settings
from config.logging_config import get_logger

logger = get_logger(__name__)

# DB 설정
DB_CONFIG = {
    "host": settings.DB_HOST,
    "port": settings.DB_PORT,
    "user": settings.DB_USER,
    "password": settings.DB_PASSWORD,
    "database": settings.DB_NAME,
    "charset": settings.DB_CHARSET,
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
