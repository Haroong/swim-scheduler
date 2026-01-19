"""
Facility 도메인 엔티티

DB의 facility 테이블을 표현하는 엔티티
비즈니스 로직 포함
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Facility:
    """
    시설 엔티티

    DB 레코드를 표현하며, 영속성 관련 속성(id)을 포함
    """
    id: int                    # DB PK
    name: str                  # 시설명
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __str__(self) -> str:
        return f"Facility(id={self.id}, name={self.name})"

    def __repr__(self) -> str:
        return self.__str__()
