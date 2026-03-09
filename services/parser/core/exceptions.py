"""
Parser 서비스 커스텀 예외 계층

에러 유형을 명확히 구분하여 호출자가 프로그래밍적으로 에러를 처리할 수 있도록 한다.
"""


class ParserBaseError(Exception):
    """Parser 서비스 기본 예외"""

    def __init__(self, message: str, cause: Exception | None = None):
        self.cause = cause
        super().__init__(message)


class CrawlError(ParserBaseError):
    """크롤링 실패 (페이지 요청, HTML 파싱)"""


class DownloadError(ParserBaseError):
    """첨부파일 다운로드 실패"""


class TextExtractionError(ParserBaseError):
    """HWP/PDF 텍스트 추출 실패"""


class ParseError(ParserBaseError):
    """LLM 파싱 실패 (API 호출, JSON 추출, 검증)"""


class RepositoryError(ParserBaseError):
    """DB 저장/조회 실패"""
