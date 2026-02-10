"""
LLM 기반 자유수영 정보 파서
Anthropic Claude API를 사용하여 raw_text에서 구조화된 데이터 추출

이 모듈은 두 가지 분리된 파싱 기능을 제공합니다:
1. parse_schedule(): 자유수영 스케줄 정보만 추출
2. parse_closures(): 휴무일 정보만 추출
3. parse(): 두 기능을 결합하여 전체 정보 추출 (기존 호환성 유지)
"""
import json
import logging
import re
from typing import Optional

from infrastructure.config import settings
from infrastructure.config.logging_config import get_logger
from core.parser.llm.prompts import EXTRACTION_PROMPT, CLOSURE_EXTRACTION_PROMPT
from core.parser.llm.validator import ScheduleValidator, validate_and_fix
from core.models.parser import ParsedScheduleData, ClosureData

logger = get_logger(__name__)


class LLMParser:
    """LLM 기반 자유수영 정보 파서"""

    def __init__(self):
        """환경변수에서 API 키와 모델 정보를 로드하여 초기화"""
        self.api_key = settings.ANTHROPIC_API_KEY
        self.model = settings.LLM_MODEL
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.temperature = settings.LLM_TEMPERATURE
        self.client = None
        self._init_client()

    def _init_client(self):
        """Anthropic 클라이언트 초기화"""
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY가 설정되지 않았습니다.")
            return

        try:
            from anthropic import Anthropic
            # JetBrains 프록시 대신 Anthropic API 직접 사용
            self.client = Anthropic(
                api_key=self.api_key,
                base_url="https://api.anthropic.com"
            )
            logger.info(f"Anthropic 클라이언트 초기화 완료 (모델: {self.model})")
        except ImportError:
            logger.error("anthropic 패키지가 설치되지 않았습니다. pip install anthropic 실행 필요")
        except Exception as e:
            logger.error(f"Anthropic 클라이언트 초기화 실패: {e}")

    def parse_schedule(self, raw_text: str, facility_name: str = "", notice_date: str = "", notice_title: str = "", source_url: str = "") -> Optional[ParsedScheduleData]:
        """
        raw_text에서 자유수영 스케줄 정보만 추출 (휴무일 제외)

        Args:
            raw_text: HWP/PDF에서 추출한 원문 텍스트
            facility_name: 시설명 (힌트로 제공)
            notice_date: 공지 등록일 (힌트로 제공)
            notice_title: 공지사항 제목 (연도/월 추출에 최우선으로 사용)
            source_url: 원본 URL

        Returns:
            ParsedScheduleData DTO (closures는 빈 배열) 또는 None
        """
        if not self.client:
            logger.error("Anthropic 클라이언트가 초기화되지 않았습니다.")
            return None

        if not raw_text or len(raw_text.strip()) < 50:
            logger.warning("파싱할 텍스트가 너무 짧습니다.")
            return None

        # 자유수영 전용 프롬프트 구성
        prompt = EXTRACTION_PROMPT + raw_text[:8000]  # 토큰 제한 고려

        if notice_date:
            # 등록일에서 연도와 월 추출
            date_match = re.search(r'(\d{4})-(\d{2})', notice_date)
            if date_match:
                reg_year, reg_month = int(date_match.group(1)), int(date_match.group(2))
                prompt += f"\n\n**★★★ 연도 결정 필수 정보 ★★★**"
                prompt += f"\n- 공지 등록일: {notice_date} (등록 연도: {reg_year}년, 등록 월: {reg_month}월)"
                prompt += f"\n- 문서에 '1월', '2월', '3월' 등 1~3월이 나오고, 등록일이 10~12월이면:"
                prompt += f"\n  → valid_month는 반드시 **{reg_year + 1}년** 으로 설정!"
                prompt += f"\n  예) 등록일 {reg_year}-12-29, 프로그램 '1월' → valid_month = '{reg_year + 1}년 1월'"
                prompt += f"\n- 등록일({notice_date})보다 과거의 valid_month는 절대 불가!"
            else:
                prompt += f"\n힌트: 이 공지는 '{notice_date}'에 등록되었습니다."

        if notice_title:
            prompt += f"\n\n공지사항 제목: '{notice_title}'"

        if facility_name:
            prompt += f"\n시설명: '{facility_name}'"

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # 응답에서 JSON 추출
            response_text = response.content[0].text.strip()
            result = self._extract_json(response_text)

            if result:
                result["source_url"] = source_url
                result["closures"] = []  # 자유수영 파싱에서는 closures 제외
                parsed_data = ParsedScheduleData.from_dict(result)
                logger.info(f"자유수영 스케줄 파싱 성공: {parsed_data.facility_name}")

                # 검증 및 자동 수정
                validator = ScheduleValidator()
                is_valid, warnings, errors = validator.validate(parsed_data)

                if not is_valid:
                    logger.warning(f"파싱 결과 검증 실패: {errors}")
                    parsed_data = validate_and_fix(parsed_data)

                    is_valid, warnings, errors = validator.validate(parsed_data)
                    if is_valid:
                        logger.info("자동 수정 후 검증 성공")
                    else:
                        logger.error(f"자동 수정 후에도 검증 실패: {errors}")

                return parsed_data

            return None

        except Exception as e:
            logger.error(f"자유수영 스케줄 파싱 실패: {e}")
            return None

    def parse_closures(self, raw_text: str, facility_name: str = "", notice_date: str = "") -> list[ClosureData]:
        """
        raw_text에서 휴무일 정보만 추출

        Args:
            raw_text: HWP/PDF에서 추출한 원문 텍스트
            facility_name: 시설명 (힌트로 제공)
            notice_date: 공지 등록일 (연도 결정에 사용)

        Returns:
            ClosureData 리스트 (휴무일 정보가 없으면 빈 리스트)
        """
        if not self.client:
            logger.error("Anthropic 클라이언트가 초기화되지 않았습니다.")
            return []

        if not raw_text or len(raw_text.strip()) < 50:
            logger.warning("파싱할 텍스트가 너무 짧습니다.")
            return []

        # 휴무일 전용 프롬프트 구성
        prompt = CLOSURE_EXTRACTION_PROMPT + raw_text[:8000]

        if notice_date:
            # 등록일에서 연도와 월 추출
            date_match = re.search(r'(\d{4})-(\d{2})', notice_date)
            if date_match:
                reg_year, reg_month = int(date_match.group(1)), int(date_match.group(2))
                prompt += f"\n\n**★★★ 연도 결정 필수 정보 ★★★**"
                prompt += f"\n- 공지 등록일: {notice_date} (등록 연도: {reg_year}년, 등록 월: {reg_month}월)"
                prompt += f"\n- 문서에 '1월', '2월', '3월' 등 1~3월이 나오고, 등록일이 10~12월이면:"
                prompt += f"\n  → dates는 반드시 **{reg_year + 1}년** 으로 설정!"
                prompt += f"\n  예) 등록일 {reg_year}-12-29, 휴무일 '2월 1일' → dates = ['**{reg_year + 1}-02-01**']"
                prompt += f"\n- 등록일({notice_date})보다 과거 날짜는 절대 불가!"
            else:
                prompt += f"\n힌트: 이 공지는 '{notice_date}'에 등록되었습니다."

        if facility_name:
            prompt += f"\n힌트: 시설명은 '{facility_name}'입니다."

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = response.content[0].text.strip()
            result = self._extract_json(response_text)

            if result and "closures" in result:
                closures = [
                    ClosureData(
                        closure_type=c["closure_type"],
                        day_of_week=c.get("day_of_week"),
                        week_pattern=c.get("week_pattern"),
                        dates=c.get("dates"),
                        reason=c.get("reason", "")
                    )
                    for c in result["closures"]
                ]
                logger.info(f"휴무일 파싱 성공: {len(closures)}건")
                return closures

            return []

        except Exception as e:
            logger.error(f"휴무일 파싱 실패: {e}")
            return []

    def parse(self, raw_text: str, facility_name: str = "", notice_date: str = "", notice_title: str = "", source_url: str = "") -> Optional[ParsedScheduleData]:
        """
        raw_text에서 자유수영 정보 전체 추출 (스케줄 + 휴무일)

        내부적으로 parse_schedule()과 parse_closures()를 순차 호출하여 결과를 병합합니다.

        Args:
            raw_text: HWP/PDF에서 추출한 원문 텍스트
            facility_name: 시설명 (힌트로 제공)
            notice_date: 공지 등록일 (힌트로 제공)
            notice_title: 공지사항 제목 (연도/월 추출에 최우선으로 사용)
            source_url: 원본 URL

        Returns:
            ParsedScheduleData DTO 또는 None
        """
        # 1. 자유수영 스케줄 파싱
        parsed_data = self.parse_schedule(
            raw_text=raw_text,
            facility_name=facility_name,
            notice_date=notice_date,
            notice_title=notice_title,
            source_url=source_url
        )

        if not parsed_data:
            return None

        # 2. 휴무일 파싱
        closures = self.parse_closures(
            raw_text=raw_text,
            facility_name=facility_name or parsed_data.facility_name,
            notice_date=notice_date
        )

        # 3. 결과 병합
        parsed_data.closures = closures

        logger.info(f"전체 파싱 완료: {parsed_data.facility_name} (스케줄: {len(parsed_data.schedules)}, 휴무일: {len(parsed_data.closures)})")
        return parsed_data

    def _extract_json(self, text: str) -> Optional[dict]:
        """응답 텍스트에서 JSON 추출"""
        # 먼저 전체 텍스트가 JSON인지 시도
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # JSON 블록 찾기 (```json ... ``` 형식)
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # { } 블록 찾기
        brace_match = re.search(r'\{[\s\S]*\}', text)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass

        logger.error(f"JSON 추출 실패: {text[:200]}...")
        return None

    def parse_batch(self, items: list) -> list[ParsedScheduleData]:
        """
        여러 항목 일괄 파싱

        Args:
            items: [{"raw_text": str, "facility_name": str, "notice_title": str, "source_url": str}, ...]

        Returns:
            ParsedScheduleData 리스트
        """
        results = []
        total = len(items)

        for i, item in enumerate(items, 1):
            logger.info(f"파싱 진행 중: {i}/{total}")

            result = self.parse(
                raw_text=item.get("raw_text", ""),
                facility_name=item.get("facility_name", ""),
                notice_date=item.get("notice_date", ""),
                notice_title=item.get("notice_title", ""),
                source_url=item.get("source_url", "")
            )

            if result:
                results.append(result)

        logger.info(f"파싱 완료: {len(results)}/{total} 성공")
        return results


# 테스트용 코드
if __name__ == "__main__":
    parser = LLMParser()

    test_text = """
    ▣ 자유수영 프로그램 일일발권 안내
    프로그램 | 시간 | 발권정원 | 제공레인
    평일 아침 08:00~08:50 | 30명 | 6개 레인
    점심 12:00~12:50 | 30명 | 6개 레인
    저녁 20:00~20:50 | 30명 | 6개 레인

    일일 이용료:
    - 초2 이하: 1,900원
    - 초3~만24세: 2,500원
    - 성인: 3,000원
    """

    result = parser.parse(test_text, facility_name="야탑청소년수련관")
    if result:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
