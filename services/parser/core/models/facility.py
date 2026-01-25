"""
시설 정보 Enum
성남시 수영장 시설 정보를 중앙에서 관리
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List


class Organization(Enum):
    """운영 기관"""
    SNYOUTH = "snyouth"  # 성남시청소년청년재단
    SNHDC = "snhdc"      # 성남도시개발공사


@dataclass(frozen=True)
class FacilityInfo:
    """시설 상세 정보"""
    name: str                    # 시설명
    organization: Organization   # 운영 기관
    url_code: str               # URL 코드 (SNYOUTH: fmcs_id, SNHDC: url_prefix)
    facility_id: Optional[str] = None  # SNHDC 시설 ID (공지사항 API용)
    aliases: tuple = ()          # 별칭 (시설명 매칭용)


class Facility(Enum):
    """시설 Enum"""

    # 성남시청소년청년재단 (SNYOUTH) - 3개 유스센터
    JUNGWON_YOUTH = FacilityInfo(
        name="중원유스센터",
        organization=Organization.SNYOUTH,
        url_code="57",
        aliases=("중원", "중원유스")
    )
    PANGYO_YOUTH = FacilityInfo(
        name="판교유스센터",
        organization=Organization.SNYOUTH,
        url_code="133",
        aliases=("판교유스",)
    )
    YATAP_YOUTH = FacilityInfo(
        name="야탑유스센터",
        organization=Organization.SNYOUTH,
        url_code="158",
        aliases=("야탑", "야탑유스")
    )

    # 성남도시개발공사 (SNHDC) - 5개 체육센터
    HWANGSAEUL = FacilityInfo(
        name="황새울국민체육센터",
        organization=Organization.SNHDC,
        url_code="ggp",
        facility_id="01",
        aliases=("황새울",)
    )
    SEONGNAM_STADIUM = FacilityInfo(
        name="성남종합운동장",
        organization=Organization.SNHDC,
        url_code="sns",
        facility_id="02",
        aliases=("성남종합",)
    )
    TANCHEON_STADIUM = FacilityInfo(
        name="탄천종합운동장",
        organization=Organization.SNHDC,
        url_code="tan",
        facility_id="03",
        aliases=("탄천", "탄천종합")
    )
    PANGYO_SPORTS = FacilityInfo(
        name="판교스포츠센터",
        organization=Organization.SNHDC,
        url_code="pgs",
        facility_id="04",
        aliases=("판교스포츠",)
    )
    LIFELONG_SPORTS = FacilityInfo(
        name="평생스포츠센터",
        organization=Organization.SNHDC,
        url_code="spo",
        facility_id="05",
        aliases=("평생스포츠", "평생학습관스포츠센터")
    )

    @property
    def name(self) -> str:
        return self.value.name

    @property
    def organization(self) -> Organization:
        return self.value.organization

    @property
    def url_code(self) -> str:
        return self.value.url_code

    @property
    def facility_id(self) -> Optional[str]:
        return self.value.facility_id

    @property
    def aliases(self) -> tuple:
        return self.value.aliases

    @classmethod
    def by_organization(cls, org: Organization) -> List["Facility"]:
        """기관별 시설 목록 반환"""
        return [f for f in cls if f.organization == org]

    @classmethod
    def snyouth_facilities(cls) -> List["Facility"]:
        """SNYOUTH 시설 목록"""
        return cls.by_organization(Organization.SNYOUTH)

    @classmethod
    def snhdc_facilities(cls) -> List["Facility"]:
        """SNHDC 시설 목록"""
        return cls.by_organization(Organization.SNHDC)

    @classmethod
    def all_names(cls) -> List[str]:
        """모든 시설명 목록"""
        return [f.name for f in cls]

    @classmethod
    def find_by_name(cls, name: str) -> Optional["Facility"]:
        """시설명으로 검색 (별칭 포함)"""
        for facility in cls:
            if facility.name == name:
                return facility
            if name in facility.aliases:
                return facility
        return None

    @classmethod
    def find_by_url_code(cls, url_code: str, org: Optional[Organization] = None) -> Optional["Facility"]:
        """URL 코드로 검색"""
        for facility in cls:
            if facility.url_code == url_code:
                if org is None or facility.organization == org:
                    return facility
        return None


# 편의를 위한 상수
SNYOUTH_BASE_URL = "https://www.snyouth.or.kr"
SNHDC_BASE_URL = "https://spo.isdc.co.kr"


def get_snyouth_facility_url(facility: Facility) -> str:
    """SNYOUTH 시설 URL 생성"""
    if facility.organization != Organization.SNYOUTH:
        raise ValueError(f"{facility.name}은 SNYOUTH 시설이 아닙니다")
    return f"{SNYOUTH_BASE_URL}/fmcs/{facility.url_code}"


def get_snhdc_program_url(facility: Facility) -> str:
    """SNHDC 프로그램 안내 URL 생성"""
    if facility.organization != Organization.SNHDC:
        raise ValueError(f"{facility.name}은 SNHDC 시설이 아닙니다")

    # 판교스포츠센터는 dailyFreeGuide 사용
    if facility == Facility.PANGYO_SPORTS:
        return f"{SNHDC_BASE_URL}/{facility.url_code}_dailyFreeGuide.do"
    return f"{SNHDC_BASE_URL}/{facility.url_code}_programGuide.do"
