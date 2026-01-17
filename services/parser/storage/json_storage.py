"""
JSON 파일 기반 데이터 저장소
"""
import json
import logging
from pathlib import Path
from typing import List, Tuple, Set

from models.swim_program import SwimProgram

logger = logging.getLogger(__name__)


class JsonStorage:
    """JSON 파일 저장소"""

    def __init__(self, storage_dir: Path = None):
        if storage_dir is None:
            storage_dir = Path(__file__).parent.parent / "storage"
        
        self.storage_dir = storage_dir
        self.output_file = storage_dir / "swim_programs.json"
        self.raw_data_dir = storage_dir / "raw_data"

    def load_existing_data(self) -> Tuple[List[dict], Set[str]]:
        """기존 저장된 데이터와 URL 집합 반환"""
        if self.output_file.exists():
            with open(self.output_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                urls = {item["source_url"] for item in data}
                return data, urls
        return [], set()

    def save_results(self, existing_data: List[dict], new_programs: List[SwimProgram]):
        """결과를 JSON 파일로 저장 (기존 데이터 + 새 데이터)"""
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        new_data = [p.to_dict() for p in new_programs]
        all_data = existing_data + new_data

        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

        logger.info(f"결과 저장 완료: {self.output_file}")
