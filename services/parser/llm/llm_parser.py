"""
LLM 기반 자유수영 정보 파서
Anthropic Claude API를 사용하여 raw_text에서 구조화된 데이터 추출
"""
import json
import os
import logging
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from llm.prompts import EXTRACTION_PROMPT
from dto.parser_dto import ParsedScheduleData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# .env 파일에서 환경변수 로드
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# 환경변수에서 API 키 및 모델 로드
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
LLM_MODEL = os.environ.get("LLM_MODEL", "claude-3-5-haiku-20241022")


class LLMParser:
    """LLM 기반 자유수영 정보 파서"""

    def __init__(self):
        """환경변수에서 API 키와 모델 정보를 로드하여 초기화"""
        self.api_key = ANTHROPIC_API_KEY
        self.model = LLM_MODEL
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

    def parse(self, raw_text: str, facility_name: str = "", notice_date: str = "", source_url: str = "") -> Optional[ParsedScheduleData]:
        """
        raw_text에서 자유수영 정보 추출

        Args:
            raw_text: HWP/PDF에서 추출한 원문 텍스트
            facility_name: 시설명 (힌트로 제공)
            notice_date: 공지 등록일 (힌트로 제공)
            source_url: 원본 URL

        Returns:
            ParsedScheduleData DTO 또는 None
        """
        if not self.client:
            logger.error("Anthropic 클라이언트가 초기화되지 않았습니다.")
            return None

        if not raw_text or len(raw_text.strip()) < 50:
            logger.warning("파싱할 텍스트가 너무 짧습니다.")
            return None

        # 프롬프트 구성
        prompt = EXTRACTION_PROMPT + raw_text[:8000]  # 토큰 제한 고려

        if facility_name:
            prompt += f"\n\n힌트: 시설명은 '{facility_name}'입니다."

        if notice_date:
            prompt += f"\n힌트: 이 공지는 '{notice_date}'에 등록되었습니다."

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # 응답에서 JSON 추출
            response_text = response.content[0].text.strip()
            result = self._extract_json(response_text)

            if result:
                result["source_url"] = source_url
                parsed_data = ParsedScheduleData.from_dict(result)
                logger.info(f"파싱 성공: {parsed_data.facility_name}")
                return parsed_data

            return None

        except Exception as e:
            logger.error(f"LLM 파싱 실패: {e}")
            return None

    def _extract_json(self, text: str) -> Optional[dict]:
        """응답 텍스트에서 JSON 추출"""
        # 먼저 전체 텍스트가 JSON인지 시도
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # JSON 블록 찾기 (```json ... ``` 형식)
        import re
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
            items: [{"raw_text": str, "facility_name": str, "source_url": str}, ...]

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
