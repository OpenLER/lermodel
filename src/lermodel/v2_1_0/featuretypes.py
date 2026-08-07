"""
Concrete LER 2.1.0 feature types.

Per clay/adr/944 (in the sibling clay repo), this package deliberately only
implements the feature types actually needed by clay's current owners:
Elledning, Foeringsroer, Elkomponent, and the Graveforespoergselssvar
envelope that wraps them. See support.py for the full list of feature
types defined by the LER 2.1.0 schema and which ones are covered here.
"""

import re
import uuid
from typing import Literal

from pydantic import Field, field_validator

from lermodel.v2_1_0 import enums
from lermodel.v2_1_0.base import (
    AbstractFeatureType,
    LedningskomponentType,
    LedningType,
    RoerledningType,
)


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


_UUID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


class GraveforespoergselssvarType(AbstractFeatureType):
    """
    ler:GraveforespoergselssvarType - the response envelope for a
    graveforespoergsel, not itself a ledning/komponent feature.

    ledningstraceMember, bilagMember, lineaerMaalsaetningMember,
    tekstannotationMember and linjeannotationMember aren't modeled (all
    optional in the XSD) - member/reference fields for feature types this
    package doesn't implement (Ledningstrace, Informationsressource, ...).
    Not dispatched via to_lerfeat(): unlike a single Ledning/Ledningskomponent
    read from a source, this is assembled by the caller from already-built
    lerfeat objects plus request metadata (anm), so it's just constructed
    directly.
    """

    gml_id: str | None = "graveforespoergselssvar"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    forventetAfleveringstidspunkt: str | None = None
    gyldigTil: str | None = None
    typeSupplerendeInfo: str | None = None
    ledningMember: list[ElledningType | FoeringsroerType] = []
    ledningskomponentMember: list[ElkomponentType] = []
    schemaVersion: Literal["2.1.0"] = "2.1.0"

    @field_validator("id")
    @classmethod
    def _id(cls, v: str) -> str:
        if not _UUID_PATTERN.match(v):
            raise ValueError(f"id must be a UUID-formatted string, got {v!r}")
        return v

    @field_validator("type")
    @classmethod
    def _type(cls, v: str) -> str:
        return enums.validate_enum(v, enums.GRAVEFORESPOERGSELSSVARTYPE, field_name="type")
