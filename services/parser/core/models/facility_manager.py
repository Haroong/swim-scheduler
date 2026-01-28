"""
시설명 정규화 및 매칭 관리자
LLM이 추출한 시설명을 Facility Enum과 매칭하여 정규화
"""
from typing import Optional, Tuple
from difflib import SequenceMatcher
import logging
from core.models.facility import Facility

logger = logging.getLogger(__name__)


class FacilityNameMatcher:
    """시설명 퍼지 매칭 및 정규화"""

    # 수동 매핑 (우선순위 1)
    MANUAL_MAPPING = {
        "성남종합스포츠센터": "성남종합운동장",
        "성남종합운동장수영장": "성남종합운동장",
        # 추가 매핑이 필요한 경우 여기에 추가
    }

    # 매칭 신뢰도 임계값
    THRESHOLD_HIGH = 0.85      # 자동 교정
    THRESHOLD_MEDIUM = 0.60    # 경고 + 원본 유지

    @classmethod
    def normalize_facility_name(cls, llm_extracted_name: str) -> Tuple[str, float, str]:
        """
        LLM이 추출한 시설명을 정규화

        Args:
            llm_extracted_name: LLM이 추출한 원본 시설명

        Returns:
            (normalized_name, confidence, match_type)
            - normalized_name: 정규화된 이름 (매칭 실패 시 원본)
            - confidence: 매칭 신뢰도 (0.0 ~ 1.0)
            - match_type: 매칭 유형 ("manual"|"exact"|"fuzzy"|"none")
        """
        if not llm_extracted_name:
            return llm_extracted_name, 0.0, "none"

        # Stage 1: 수동 매핑 확인 (우선순위 최상)
        if llm_extracted_name in cls.MANUAL_MAPPING:
            normalized = cls.MANUAL_MAPPING[llm_extracted_name]
            logger.info(f"Manual mapping: '{llm_extracted_name}' → '{normalized}'")
            return normalized, 1.0, "manual"

        # Stage 2: Exact match (대소문자 구분 없음)
        for facility in Facility:
            if facility.value.name.lower() == llm_extracted_name.lower():
                logger.info(f"Exact match: '{llm_extracted_name}' → '{facility.value.name}'")
                return facility.value.name, 1.0, "exact"

            # Aliases 확인
            for alias in facility.value.aliases:
                if alias.lower() == llm_extracted_name.lower():
                    logger.info(f"Alias match: '{llm_extracted_name}' → '{facility.value.name}' (via alias '{alias}')")
                    return facility.value.name, 1.0, "exact"

        # Stage 3: Fuzzy matching
        best_match = None
        best_score = 0.0

        for facility in Facility:
            # 시설명과 비교
            score = cls._similarity(llm_extracted_name, facility.value.name)
            if score > best_score:
                best_score = score
                best_match = facility.value.name

            # Aliases와 비교
            for alias in facility.value.aliases:
                score = cls._similarity(llm_extracted_name, alias)
                if score > best_score:
                    best_score = score
                    best_match = facility.value.name

        # 매칭 결과에 따른 처리
        if best_score >= cls.THRESHOLD_HIGH:
            # High confidence: 자동 교정
            logger.info(f"Fuzzy match (HIGH): '{llm_extracted_name}' → '{best_match}' (score: {best_score:.2f})")
            return best_match, best_score, "fuzzy"

        elif best_score >= cls.THRESHOLD_MEDIUM:
            # Medium confidence: 경고 + 원본 유지
            logger.warning(
                f"Fuzzy match (MEDIUM): '{llm_extracted_name}' 유사도 {best_score:.2f} "
                f"(가장 유사: '{best_match}'). 원본 이름으로 저장됩니다."
            )
            return llm_extracted_name, best_score, "fuzzy"

        else:
            # Low confidence: 경고 + 원본 유지
            logger.warning(
                f"Fuzzy match (LOW): '{llm_extracted_name}' 유사도 {best_score:.2f} "
                f"(가장 유사: '{best_match}'). Facility Enum에 없는 시설일 수 있습니다. 원본 이름으로 저장됩니다."
            )
            return llm_extracted_name, best_score, "none"

    @staticmethod
    def _similarity(s1: str, s2: str) -> float:
        """두 문자열의 유사도 계산 (0.0 ~ 1.0)"""
        return SequenceMatcher(None, s1, s2).ratio()


# 편의 함수
def normalize_facility_name(name: str) -> str:
    """시설명 정규화 (normalized name만 반환)"""
    normalized, confidence, match_type = FacilityNameMatcher.normalize_facility_name(name)
    return normalized
