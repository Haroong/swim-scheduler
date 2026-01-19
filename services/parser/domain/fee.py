"""
Fee 도메인 엔티티

DB의 fee 테이블을 표현하는 엔티티
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Fee:
    """
    이용료 엔티티 (fee 테이블)

    비즈니스 로직:
    - 할인율 계산
    - 가격 비교
    """
    id: Optional[int]          # DB PK (생성 전에는 None)
    facility_id: int           # Facility FK
    category: str              # 대상 (성인, 청소년, 어린이 등)
    price: int                 # 금액 (원)
    note: str = ""             # 비고
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def calculate_discount(self, discount_rate: float) -> int:
        """
        할인가 계산

        Args:
            discount_rate: 할인율 (0.0 ~ 1.0)

        Returns:
            할인 적용 가격

        Example:
            >>> fee = Fee(..., price=3000)
            >>> fee.calculate_discount(0.1)  # 10% 할인
            2700
        """
        return int(self.price * (1 - discount_rate))

    def is_cheaper_than(self, other: "Fee") -> bool:
        """다른 이용료보다 저렴한지 비교"""
        return self.price < other.price

    def format_price(self) -> str:
        """가격 포맷팅 (천 단위 콤마)"""
        return f"{self.price:,}원"

    def __str__(self) -> str:
        return f"Fee({self.category}: {self.format_price()})"

    def __repr__(self) -> str:
        return self.__str__()
