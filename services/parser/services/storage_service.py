"""
데이터 저장 서비스
- JSON 파일 저장
- DB 저장 (TODO: UnitOfWork 구현 후 추가)
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)


class StorageService:
    """데이터 저장 서비스"""

    def __init__(self, storage_dir: Path):
        """
        Args:
            storage_dir: 저장 디렉토리
        """
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_base_schedules(self, org_key: str, facilities: List[dict]):
        """
        기본 스케줄 저장

        Args:
            org_key: 기관 키 (snhdc, snyouth)
            facilities: 시설 기본 정보 리스트
        """
        filename = f"{org_key}_base_schedules.json"
        filepath = self.storage_dir / filename

        data = {
            "meta": {
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "organization": org_key,
                "facility_count": len(facilities)
            },
            "facilities": facilities
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"기본 스케줄 저장 완료: {filepath}")

    def save_monthly_notices(self, org_key: str, notices: List[dict]):
        """
        월별 공지사항 저장

        Args:
            org_key: 기관 키 (snhdc, snyouth)
            notices: 게시글 상세 정보 리스트
        """
        filename = f"{org_key}_monthly_notices.json"
        filepath = self.storage_dir / filename

        data = {
            "meta": {
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "organization": org_key,
                "notice_count": len(notices)
            },
            "notices": notices
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"월별 공지사항 저장 완료: {filepath}")

    def save_parsed_schedules(self, org_key: str, parsed_data: List[Dict]):
        """
        파싱된 스케줄 데이터 저장

        Args:
            org_key: 기관 키 (snhdc, snyouth)
            parsed_data: 파싱된 스케줄 데이터 리스트
        """
        filename = f"{org_key}_parsed_schedules.json"
        filepath = self.storage_dir / filename

        data = {
            "meta": {
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "organization": org_key,
                "parsed_count": len(parsed_data)
            },
            "parsed_schedules": parsed_data
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"파싱 결과 저장 완료: {filepath}")

    def save_merged_schedules(self, merged_data: Dict):
        """
        병합된 스케줄 저장

        Args:
            merged_data: 병합된 스케줄 데이터
        """
        filepath = self.storage_dir / "merged_schedules.json"

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)

        logger.info(f"병합 결과 저장 완료: {filepath}")

    def load_base_schedules(self, org_key: str) -> List[dict]:
        """
        기본 스케줄 로드

        Args:
            org_key: 기관 키 (snhdc, snyouth)

        Returns:
            시설 기본 정보 리스트
        """
        filename = f"{org_key}_base_schedules.json"
        filepath = self.storage_dir / filename

        if not filepath.exists():
            logger.warning(f"기본 스케줄 파일 없음: {filepath}")
            return []

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("facilities", [])

    def load_monthly_notices(self, org_key: str) -> List[dict]:
        """
        월별 공지사항 로드

        Args:
            org_key: 기관 키 (snhdc, snyouth)

        Returns:
            게시글 상세 정보 리스트
        """
        filename = f"{org_key}_monthly_notices.json"
        filepath = self.storage_dir / filename

        if not filepath.exists():
            logger.warning(f"월별 공지사항 파일 없음: {filepath}")
            return []

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("notices", [])

    def load_parsed_schedules(self, org_key: str) -> List[Dict]:
        """
        파싱된 스케줄 데이터 로드

        Args:
            org_key: 기관 키 (snhdc, snyouth)

        Returns:
            파싱된 스케줄 데이터 리스트
        """
        filename = f"{org_key}_parsed_schedules.json"
        filepath = self.storage_dir / filename

        if not filepath.exists():
            logger.warning(f"파싱 결과 파일 없음: {filepath}")
            return []

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("parsed_schedules", [])

    # TODO: DB 저장 기능은 Repository 리팩토링 후 추가
    # def save_to_database(self, data: ScheduleStorageDTO) -> bool:
    #     """DB에 저장 (트랜잭션 관리)"""
    #     pass
