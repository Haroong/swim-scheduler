"""
PDF 텍스트 추출기
PDF 파일에서 텍스트를 추출
"""
from pathlib import Path
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PdfTextExtractor:
    """PDF 파일에서 텍스트를 추출하는 클래스"""

    def __init__(self):
        self.pypdf2 = None
        self._import_pypdf2()

    def _import_pypdf2(self):
        """PyPDF2 모듈 동적 임포트"""
        try:
            import PyPDF2
            self.pypdf2 = PyPDF2
        except ImportError:
            logger.warning("PyPDF2 모듈이 설치되어 있지 않습니다. pip install PyPDF2 실행 필요")
            self.pypdf2 = None

    def extract_text(self, pdf_path: Path) -> Optional[str]:
        """
        PDF 파일에서 텍스트 추출

        Args:
            pdf_path: PDF 파일 경로

        Returns:
            추출된 텍스트 또는 None
        """
        if not self.pypdf2:
            logger.error("PyPDF2 모듈이 없어 PDF 파싱 불가")
            return None

        if not pdf_path.exists():
            logger.error(f"파일이 존재하지 않음: {pdf_path}")
            return None

        try:
            with open(pdf_path, "rb") as f:
                reader = self.pypdf2.PdfReader(f)

                text_parts = []
                for page_num, page in enumerate(reader.pages):
                    try:
                        text = page.extract_text()
                        if text:
                            text_parts.append(text.strip())
                    except Exception as e:
                        logger.debug(f"페이지 {page_num} 추출 실패: {e}")
                        continue

                if text_parts:
                    result = "\n".join(text_parts)
                    logger.info(f"PDF 텍스트 추출 성공: {len(result)}자")
                    return result
                else:
                    logger.warning(f"PDF에서 텍스트를 추출할 수 없음: {pdf_path}")
                    return None

        except Exception as e:
            logger.error(f"PDF 파일 처리 중 오류: {e}")
            return None


# 테스트용 코드
if __name__ == "__main__":
    extractor = PdfTextExtractor()

    # storage/raw_data 폴더에서 PDF 파일 찾기
    raw_data_dir = Path(__file__).parent.parent / "storage" / "raw_data"

    pdf_files = list(raw_data_dir.glob("*.pdf"))
    if pdf_files:
        test_path = pdf_files[0]
        print(f"테스트 파일: {test_path.name}")

        text = extractor.extract_text(test_path)
        if text:
            print(f"추출된 텍스트 ({len(text)}자):")
            print(text[:500])
        else:
            print("텍스트 추출 실패")
    else:
        print("PDF 파일이 없습니다.")
