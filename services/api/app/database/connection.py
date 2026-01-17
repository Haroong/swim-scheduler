"""
Database Connection
Parser 프로젝트의 DB 연결 로직 재사용
"""
import os
import sys
from pathlib import Path

# Parser의 database 모듈을 import할 수 있도록 경로 추가
parser_path = Path(__file__).parent.parent.parent.parent / "parser"
sys.path.insert(0, str(parser_path))

from database.connection import get_connection, close_connection

__all__ = ["get_connection", "close_connection"]
