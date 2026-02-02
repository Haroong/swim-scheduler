"""
콘텐츠 검증 모듈
자유수영 관련 정보 포함 여부 및 텍스트 품질 검증
"""
import re
from typing import Dict, List


class ContentValidator:
    """자유수영 콘텐츠 검증기"""

    # 자유수영 관련 필수 키워드
    SWIM_KEYWORDS = [
        "자유수영",
        "월 자유수영",  # 진도표에서 사용
        "일일자유",  # SNHDC에서 사용
        "일일발권",
        "일일이용",
        "평일",
        "토요일",
        "일요일",
        "발권정원",
        "제공레인",
        "이용료",
        "레인",
        "운영시간",
        "동절기",
        "하절기",
        "방문접수"  # 진도표에서 사용
    ]

    # 시간 패턴 (예: 08:00, 06:30~08:00)
    TIME_PATTERN = r'\d{1,2}:\d{2}'

    def __init__(self, min_keywords: int = 3, min_length: int = 100):
        """
        Args:
            min_keywords: 최소 키워드 개수
            min_length: 최소 텍스트 길이 (기본 100자)
        """
        self.min_keywords = min_keywords
        self.min_length = min_length

    def contains_swim_info(self, text: str) -> bool:
        """
        자유수영 관련 정보 포함 여부 확인

        Args:
            text: 검증할 텍스트

        Returns:
            자유수영 정보 포함 여부
        """
        if not text or len(text) < self.min_length:
            return False

        # 자유수영 핵심 키워드 확인
        has_core_keyword = ("자유수영" in text or "월 자유수영" in text or
                           "일일자유" in text or "일일발권" in text or "일일이용" in text)

        # 키워드 개수 확인
        keyword_count = sum(1 for kw in self.SWIM_KEYWORDS if kw in text)

        # 시간 패턴 확인
        has_time = bool(re.search(self.TIME_PATTERN, text))

        # 조건: (핵심 키워드 + 시간 정보) 또는 (키워드 3개 이상 + 시간 정보)
        return (has_core_keyword and has_time) or (keyword_count >= self.min_keywords and has_time)

    def get_quality_score(self, text: str) -> int:
        """
        텍스트 품질 점수 계산

        Args:
            text: 평가할 텍스트

        Returns:
            품질 점수 (0-100)
        """
        score = 0

        # 길이 점수 (최대 20점)
        if len(text) > 500:
            score += 20
        elif len(text) > 200:
            score += 10

        # 키워드 점수 (최대 50점)
        keyword_count = sum(1 for kw in self.SWIM_KEYWORDS if kw in text)
        score += min(keyword_count * 5, 50)

        # 시간 정보 점수 (최대 20점)
        time_matches = len(re.findall(self.TIME_PATTERN, text))
        score += min(time_matches * 2, 20)

        # 구조화 정보 점수 (최대 10점)
        if "▣" in text or "■" in text:  # 구조화된 문서
            score += 5
        if "프로그램" in text and "시간" in text:
            score += 5

        return min(score, 100)

    def extract_swim_keywords(self, text: str) -> List[str]:
        """
        텍스트에서 발견된 자유수영 키워드 추출

        Args:
            text: 검색할 텍스트

        Returns:
            발견된 키워드 리스트
        """
        return [kw for kw in self.SWIM_KEYWORDS if kw in text]

    def analyze(self, text: str) -> Dict:
        """
        텍스트 종합 분석

        Args:
            text: 분석할 텍스트

        Returns:
            분석 결과 딕셔너리
        """
        return {
            "is_swim_content": self.contains_swim_info(text),
            "quality_score": self.get_quality_score(text),
            "found_keywords": self.extract_swim_keywords(text),
            "keyword_count": sum(1 for kw in self.SWIM_KEYWORDS if kw in text),
            "text_length": len(text),
            "has_time_info": bool(re.search(self.TIME_PATTERN, text))
        }


# 테스트용 코드
if __name__ == "__main__":
    validator = ContentValidator()

    test_text = """
    ▣ 자유수영 프로그램 일일발권 안내
    프로그램 | 시간 | 발권정원 | 제공레인
    평일 아침 08:00~08:50 | 30명 | 6개 레인
    토요일 동절기 06:30~08:00 | 80명 | 6개 레인
    일일 이용료: 성인 3,000원
    """

    result = validator.analyze(test_text)
    print("분석 결과:")
    print(f"  자유수영 콘텐츠: {result['is_swim_content']}")
    print(f"  품질 점수: {result['quality_score']}/100")
    print(f"  발견된 키워드: {result['found_keywords']}")
    print(f"  키워드 개수: {result['keyword_count']}")
