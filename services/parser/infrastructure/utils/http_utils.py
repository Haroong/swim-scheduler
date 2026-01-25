"""
HTTP 관련 유틸리티
"""
import requests

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def create_session(extra_headers: dict = None) -> requests.Session:
    """
    공통 HTTP 세션 생성

    Args:
        extra_headers: 추가 헤더 (Content-Type 등)

    Returns:
        requests.Session
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": DEFAULT_USER_AGENT
    })
    if extra_headers:
        session.headers.update(extra_headers)
    return session
