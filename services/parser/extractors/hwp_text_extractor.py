"""
HWP 텍스트 추출기
HWP 파일에서 텍스트를 추출
"""
import struct
import zlib
from pathlib import Path
from typing import Optional
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HwpTextExtractor:
    """HWP 파일에서 텍스트를 추출하는 클래스"""

    def __init__(self):
        self.olefile = None
        self._import_olefile()

    def _import_olefile(self):
        """olefile 모듈 동적 임포트"""
        try:
            import olefile
            self.olefile = olefile
        except ImportError:
            logger.warning("olefile 모듈이 설치되어 있지 않습니다. pip install olefile 실행 필요")
            self.olefile = None

    def extract_text(self, hwp_path: Path) -> Optional[str]:
        """
        HWP 파일에서 텍스트 추출

        Args:
            hwp_path: HWP 파일 경로

        Returns:
            추출된 텍스트 또는 None
        """
        if not self.olefile:
            logger.error("olefile 모듈이 없어 HWP 파싱 불가")
            return None

        if not hwp_path.exists():
            logger.error(f"파일이 존재하지 않음: {hwp_path}")
            return None

        try:
            ole = self.olefile.OleFileIO(str(hwp_path))
        except Exception as e:
            logger.error(f"HWP 파일 열기 실패: {e}")
            return None

        try:
            # HWP 파일 구조 확인
            if not ole.exists("FileHeader"):
                logger.error("유효한 HWP 파일이 아님 (FileHeader 없음)")
                return None

            # FileHeader에서 압축 여부 확인
            header = ole.openstream("FileHeader").read()
            is_compressed = self._is_compressed(header)

            # 본문 섹션에서 텍스트 추출
            text_parts = []

            # BodyText 섹션들 탐색
            for entry in ole.listdir():
                path = "/".join(entry)

                if path.startswith("BodyText/Section"):
                    section_text = self._extract_section_text(ole, path, is_compressed)
                    if section_text:
                        text_parts.append(section_text)

            return "\n".join(text_parts) if text_parts else None

        except Exception as e:
            logger.error(f"텍스트 추출 중 오류: {e}")
            return None
        finally:
            ole.close()

    def _is_compressed(self, header: bytes) -> bool:
        """FileHeader에서 압축 여부 확인"""
        # HWP FileHeader: offset 36에 속성 플래그
        if len(header) >= 40:
            flags = struct.unpack("<I", header[36:40])[0]
            return bool(flags & 0x01)  # bit 0: 압축 여부
        return False

    def _extract_section_text(self, ole, path: str, is_compressed: bool) -> Optional[str]:
        """섹션에서 텍스트 추출"""
        try:
            data = ole.openstream(path).read()

            # 압축 해제
            if is_compressed:
                try:
                    data = zlib.decompress(data, -15)
                except zlib.error:
                    # 압축 해제 실패 시 원본 데이터 사용
                    pass

            # 텍스트 추출
            return self._parse_section_data(data)

        except Exception as e:
            logger.debug(f"섹션 {path} 처리 실패: {e}")
            return None

    def _parse_section_data(self, data: bytes) -> str:
        """
        섹션 데이터에서 텍스트 파싱

        HWP 5.0 형식의 레코드 구조를 파싱하여 텍스트 추출
        """
        texts = []
        pos = 0

        while pos < len(data) - 4:
            # 레코드 헤더 읽기 (4바이트)
            header = struct.unpack("<I", data[pos:pos + 4])[0]

            tag_id = header & 0x3FF       # 하위 10비트: 태그 ID
            level = (header >> 10) & 0x3FF  # 중간 10비트: 레벨
            size = (header >> 20) & 0xFFF  # 상위 12비트: 크기

            # 크기가 0xFFF이면 다음 4바이트가 실제 크기
            if size == 0xFFF:
                if pos + 8 > len(data):
                    break
                size = struct.unpack("<I", data[pos + 4:pos + 8])[0]
                pos += 8
            else:
                pos += 4

            # 레코드 데이터 읽기
            if pos + size > len(data):
                break

            record_data = data[pos:pos + size]
            pos += size

            # HWPTAG_PARA_TEXT (67) 태그에서 텍스트 추출
            if tag_id == 67:
                text = self._extract_para_text(record_data)
                if text:
                    texts.append(text)

        return "\n".join(texts)

    def _extract_para_text(self, data: bytes) -> str:
        """문단 텍스트 레코드에서 텍스트 추출"""
        text_chars = []
        pos = 0

        while pos < len(data) - 1:
            # UTF-16LE로 2바이트씩 읽기
            char_code = struct.unpack("<H", data[pos:pos + 2])[0]
            pos += 2

            # 제어 문자 처리
            if char_code < 32:
                if char_code == 0:  # NULL
                    continue
                elif char_code == 10:  # 줄바꿈
                    text_chars.append("\n")
                elif char_code == 13:  # 캐리지 리턴
                    continue
                elif char_code in [1, 2, 3, 11, 12, 14, 15, 16, 17, 18, 21, 22, 23]:
                    # 확장 제어 문자 - 추가 데이터 건너뛰기
                    pos += 12  # inline 컨트롤은 12바이트 추가
                elif char_code == 4:  # 필드 시작
                    pos += 12
                elif char_code == 9:  # 탭
                    text_chars.append("\t")
                else:
                    continue
            else:
                try:
                    text_chars.append(chr(char_code))
                except ValueError:
                    continue

        return "".join(text_chars).strip()

    def extract_text_simple(self, hwp_path: Path) -> Optional[str]:
        """
        간단한 방식으로 HWP에서 텍스트 추출 (폴백용)

        바이트에서 한글 텍스트 패턴을 찾아 추출
        """
        try:
            with open(hwp_path, "rb") as f:
                data = f.read()

            # UTF-16LE로 디코딩 시도
            texts = []

            # 한글 유니코드 범위의 문자열 패턴 찾기
            # 한글 범위: 0xAC00-0xD7A3
            decoded = data.decode("utf-16le", errors="ignore")

            # 한글이 포함된 줄만 추출
            korean_pattern = re.compile(r"[\uAC00-\uD7A3]+")
            for line in decoded.split("\n"):
                line = line.strip()
                if korean_pattern.search(line) and len(line) > 5:
                    # 제어문자 제거
                    clean_line = re.sub(r"[\x00-\x1F\x7F]", " ", line)
                    clean_line = " ".join(clean_line.split())
                    if clean_line:
                        texts.append(clean_line)

            return "\n".join(texts) if texts else None

        except Exception as e:
            logger.error(f"간단 추출 실패: {e}")
            return None


# 테스트용 코드
if __name__ == "__main__":
    extractor = HwpTextExtractor()

    # 테스트 파일 경로 (실제 HWP 파일로 교체 필요)
    test_path = Path("storage/raw_data/test.hwp")

    if test_path.exists():
        text = extractor.extract_text(test_path)
        if text:
            print("추출된 텍스트:")
            print(text[:1000])
        else:
            print("텍스트 추출 실패, 간단 추출 시도...")
            text = extractor.extract_text_simple(test_path)
            if text:
                print(text[:1000])
    else:
        print(f"테스트 파일이 없습니다: {test_path}")
