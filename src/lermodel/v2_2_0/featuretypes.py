"""
Concrete LER 2.2.0 feature types.

Per clay/adr/944 (in the sibling clay repo), this package deliberately only
implements the feature types actually needed by clay's current owners:
Elledning, Foeringsroer and Elkomponent. See lermodel.support for the full
list of feature types defined by the LER 2.2.0 schema and which ones are
covered here.

ElledningType, FoeringsroerType and ElkomponentType are all unchanged
between 2.1_ler.xsd and 2.2_ler.xsd (confirmed by diffing both XSDs in
full) - only their inherited base fields changed, in base.py.
"""

from pydantic import field_validator

from lermodel.v2_2_0 import enums
from lermodel.v2_2_0.base import LedningskomponentType, LedningType, RoerledningType


class ElledningType(LedningType):
    """ler:ElledningType - ledning til elforsyning."""

    # required, nillable
    type: str | None

    # optional
    afdaekning: str | None = None
    antalKabler: int | None = None
    kabeltype: str | None = None
    spaendingsniveau: float | None = None  # kV

    @field_validator("type")
    @classmethod
    def _type(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return enums.validate_enum(v, enums.ELLEDNINGSTYPE, field_name="type", allow_other=True)


class FoeringsroerType(RoerledningType):
    """ler:FoeringsroerType - rør hvori der kan føres en eller flere ledninger."""

    forsyningsart: list[str] = []

    @field_validator("forsyningsart")
    @classmethod
    def _forsyningsart(cls, v: list[str]) -> list[str]:
        return [
            enums.validate_enum(
                item, enums.FORSYNINGSART, field_name="forsyningsart", allow_other=True
            )
            for item in v
        ]


class ElkomponentType(LedningskomponentType):
    """ler:ElkomponentType - komponent der har tilknytning til elledninger."""

    # required, not nillable
    type: str

    # optional
    relativNiveau: str | None = None
    spaendingsniveau: float | None = None  # kV

    @field_validator("type")
    @classmethod
    def _type(cls, v: str) -> str:
        return enums.validate_enum(v, enums.ELKOMPONENTTYPE, field_name="type", allow_other=True)

    @field_validator("relativNiveau")
    @classmethod
    def _relativNiveau(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return enums.validate_enum(v, enums.RELATIV_NIVEAU, field_name="relativNiveau")
