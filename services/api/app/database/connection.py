"""
Database Connection
Parser 프로젝트의 DB 연결 로직 재사용
"""
import os
import sys
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Parser의 database 모듈을 import할 수 있도록 경로 추가
parser_path = Path(__file__).parent.parent.parent.parent / "parser"
sys.path.insert(0, str(parser_path))

from database.connection import get_connection as parser_get_connection


def get_connection():
    """DB 연결 반환"""
    return parser_get_connection()


def close_connection(conn):
    """DB 연결 종료"""
    if conn:
        try:
            conn.close()
            logger.debug("DB 연결 종료")
        except Exception as e:
            logger.error(f"DB 연결 종료 실패: {e}")


__all__ = ["get_connection", "close_connection"]
