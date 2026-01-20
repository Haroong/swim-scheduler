"""
HTML 처리 유틸리티
"""
from bs4 import BeautifulSoup


def extract_clean_text(html: str) -> str:
    """
    HTML에서 정제된 텍스트 추출

    - script, style 태그 제거
    - 빈 줄 제거
    - 각 줄 trim 처리

    Args:
        html: HTML 문자열

    Returns:
        정제된 텍스트
    """
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines)
