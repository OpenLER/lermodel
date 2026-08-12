"""
Abstract base hierarchy for LER 2.2.0 features, modeled after the type
hierarchy in 2.2_ler.xsd (ler-xml-validator's src/lerxml/xsd/2.2.0/2.2_ler.xsd,
also vendored under featurekatalog/versions/2.2.0/schemas/).

These classes are never dispatched to directly (see dispatch.py) - they only
exist to share fields/validation between concrete feature types, mirroring
the XSD's own abstract complexTypes.

Association/reference fields from the XSD (bilag, startkomponent,
slutkomponent, indeholdtLedning, tilknyttetLedning,
kontaktprofilTilTekniskeSpoergsmaal) are not modeled: they are all optional
in the schema, and cross-feature references aren't needed for the
graveforespoergsel-svar use case this package was built for.

Diff from lermodel.v2_1_0.base (2.1_ler.xsd -> 2.2_ler.xsd, confirmed by
diffing both XSDs in full - no other differences affect this package's
scope):
- LedningEllerLedningstraceType and LedningskomponentType both gained
  noejagtighedsklasseVertikal (optional, nillable, same NoejagtighedsklasseType
  enum as noejagtighedsklasse - which itself was reworded from "placering"
  to "horisontale placering" in its documentation, no behavioral change).
- RoerledningType gained udnyttelsesgrad (optional decimal in [0, 1] with at
  most 2 decimal places - a plain field, not a gml:MeasureType, so no uom).
"""

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from shapely.geometry.base import BaseGeometry

from lermodel.v2_2_0 import enums

if TYPE_CHECKING:
    from lxml import etree

_ETABLERET_FOER_2023 = "Etableret før 1. juli 2023"


def _validate_etableringstidspunkt(v: str) -> str:
    if v == _ETABLERET_FOER_2023:
        return v
    try:
        datetime.strptime(v, "%Y-%m-%d")
    except ValueError:
        raise ValueError(
            f"etableringstidspunkt must be {_ETABLERET_FOER_2023!r} or in format "
            f"YYYY-MM-DD, got {v!r}"
        ) from None
    return v


def _validate_udnyttelsesgrad(v: float) -> float:
    if not (0 <= v <= 1):
        raise ValueError(f"udnyttelsesgrad must be between 0 and 1, got {v!r}")
    if round(v, 2) != v:
        raise ValueError(f"udnyttelsesgrad must have at most 2 decimal places, got {v!r}")
    return v


class AbstractGMLType(BaseModel):
    """Modeled after gml:AbstractGMLType."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    gml_id: str | None = None  # maps to gml:id attribute
    identifier: str | None = None
    names: list[str] | None = None  # maps to multiple gml:name elements
    description: str | None = None
    description_reference: str | None = None

    @field_validator("gml_id")
    @classmethod
    def _gml_id(cls, v: str | None) -> str | None:
        if v and not v[0].isalpha():
            raise ValueError(f"gml_id must start with a letter, got {v!r}")
        return v


class AbstractFeatureType(AbstractGMLType):
    """Modeled after gml:AbstractFeatureType."""

    bounded_by: None = None
    location: None = None

    def to_xml(self) -> "etree._Element":
        # deferred import: xml.py imports AbstractFeatureType for type
        # hints, so importing it back at module level here would be circular
        from lermodel.v2_2_0.xml import build_feature

        return build_feature(self)


class LedningEllerLedningstraceType(AbstractFeatureType):
    """
    Modeled after the abstract ler:LedningEllerLedningstraceType.

    Field declaration order matches the XSD's <sequence> exactly - LER XML
    is schema-validated with strict element ordering, so this order is load
    bearing for to_xml() output, not just cosmetic.
    """

    # required, nillable
    driftsstatus: str | None
    # optional, defaulted
    ejerskabsforhold: str | None = "ejet af udleverende ledningsejer"
    # required, not nillable
    etableringstidspunkt: str
    # required, nillable
    fareklasse: str | None
    # optional
    id: str | None = None
    indtegningsmetode: str | None = "nøjagtigt"
    # optional, nillable
    noejagtighedsklasse: str | None = None
    noejagtighedsklasseVertikal: str | None = None
    # optional
    registreringFra: str | None = None
    sikkerhedshensyn: str | None = None
    # optional, nillable
    vejledendeDybde: float | None = None  # metres

    @field_validator("driftsstatus")
    @classmethod
    def _driftsstatus(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return enums.validate_enum(v, enums.DRIFTSSTATUS, field_name="driftsstatus")

    @field_validator("fareklasse")
    @classmethod
    def _fareklasse(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return enums.validate_enum(v, enums.FAREKLASSE, field_name="fareklasse")

    @field_validator("ejerskabsforhold")
    @classmethod
    def _ejerskabsforhold(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return enums.validate_enum(v, enums.EJERSKABSFORHOLD, field_name="ejerskabsforhold")

    @field_validator("indtegningsmetode")
    @classmethod
    def _indtegningsmetode(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return enums.validate_enum(v, enums.INDTEGNINGSMETODE, field_name="indtegningsmetode")

    @field_validator("noejagtighedsklasse")
    @classmethod
    def _noejagtighedsklasse(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return enums.validate_enum(v, enums.NOEJAGTIGHEDSKLASSE, field_name="noejagtighedsklasse")

    @field_validator("noejagtighedsklasseVertikal")
    @classmethod
    def _noejagtighedsklasseVertikal(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return enums.validate_enum(
            v, enums.NOEJAGTIGHEDSKLASSE, field_name="noejagtighedsklasseVertikal"
        )

    @field_validator("etableringstidspunkt")
    @classmethod
    def _etableringstidspunkt(cls, v: str) -> str:
        return _validate_etableringstidspunkt(v)


class LedningType(LedningEllerLedningstraceType):
    """
    Modeled after the abstract ler:LedningType.

    Field declaration order matches the XSD's <sequence> exactly - see the
    note on LedningEllerLedningstraceType above.
    """

    # optional
    geometri: BaseGeometry | None = None  # midterlinje, LineString/MultiLineString
    niveau: str | None = None
    # optional, nillable
    indeholderLedninger: bool | None = None
    # optional
    ledningsetableringsmetode: str | None = None
    liggerILedning: bool | None = None
    # optional, nillable
    udvendigDiameter: float | None = None  # mm
    # optional
    udvendigFarve: list[str] = []
    udvendigMateriale: str | None = None

    @field_validator("niveau")
    @classmethod
    def _niveau(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return enums.validate_enum(v, enums.NIVEAU, field_name="niveau")

    @field_validator("ledningsetableringsmetode")
    @classmethod
    def _ledningsetableringsmetode(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return enums.validate_enum(
            v, enums.LEDNINGSETABLERINGSMETODE, field_name="ledningsetableringsmetode"
        )

    @model_validator(mode="after")
    def _noejagtighedsklasse_kraevet_ved_geometri(self) -> "LedningType":
        # lerxml's xta restriktioner (ler:Ledning) require noejagtighedsklasse
        # and noejagtighedsklasseVertikal iff geometri is set - not the plain
        # optional the XSD alone implies.
        if (self.geometri is None) != (self.noejagtighedsklasse is None):
            raise ValueError(
                "noejagtighedsklasse must be set if and only if geometri is set"
            )
        if (self.geometri is None) != (self.noejagtighedsklasseVertikal is None):
            raise ValueError(
                "noejagtighedsklasseVertikal must be set if and only if geometri is set"
            )
        return self


class RoerledningType(LedningType):
    """
    Modeled after the abstract ler:RoerledningType.

    Field declaration order matches the XSD's <sequence> exactly - see the
    note on LedningEllerLedningstraceType above.
    """

    # required, nillable
    tvaersnitsform: str | None
    # optional
    udnyttelsesgrad: float | None = None  # ratio in [0, 1], not a gml:MeasureType
    # optional, nillable
    udvendigBredde: float | None = None  # mm
    udvendigHoejde: float | None = None  # mm

    @field_validator("tvaersnitsform")
    @classmethod
    def _tvaersnitsform(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return enums.validate_enum(
            v, enums.TVAERSNITSFORM, field_name="tvaersnitsform", allow_other=True
        )

    @field_validator("udnyttelsesgrad")
    @classmethod
    def _udnyttelsesgrad(cls, v: float | None) -> float | None:
        if v is None:
            return v
        return _validate_udnyttelsesgrad(v)


class LedningskomponentType(AbstractFeatureType):
    """
    Modeled after the abstract ler:LedningskomponentType.

    Field declaration order matches the XSD's <sequence> exactly - see the
    note on LedningEllerLedningstraceType above.
    """

    # optional, nillable
    driftsstatus: str | None = None
    # optional, defaulted
    ejerskabsforhold: str | None = "ejet af udleverende ledningsejer"
    # optional
    etableringstidspunkt: str | None = None
    # optional, nillable
    fareklasse: str | None = None
    # optional
    id: str | None = None
    materiale: str | None = None
    # optional, nillable
    noejagtighedsklasse: str | None = None
    noejagtighedsklasseVertikal: str | None = None
    # optional
    registreringFra: str | None = None
    sikkerhedshensyn: str | None = None
    vejledendeDybde: float | None = None  # metres, not nillable at this level
    # required
    geometri: BaseGeometry  # any geometry type, e.g. Point
    # optional
    niveau: str | None = None

    @field_validator("driftsstatus")
    @classmethod
    def _driftsstatus(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return enums.validate_enum(v, enums.DRIFTSSTATUS, field_name="driftsstatus")

    @field_validator("fareklasse")
    @classmethod
    def _fareklasse(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return enums.validate_enum(v, enums.FAREKLASSE, field_name="fareklasse")

    @field_validator("ejerskabsforhold")
    @classmethod
    def _ejerskabsforhold(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return enums.validate_enum(v, enums.EJERSKABSFORHOLD, field_name="ejerskabsforhold")

    @field_validator("noejagtighedsklasse")
    @classmethod
    def _noejagtighedsklasse(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return enums.validate_enum(v, enums.NOEJAGTIGHEDSKLASSE, field_name="noejagtighedsklasse")

    @field_validator("noejagtighedsklasseVertikal")
    @classmethod
    def _noejagtighedsklasseVertikal(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return enums.validate_enum(
            v, enums.NOEJAGTIGHEDSKLASSE, field_name="noejagtighedsklasseVertikal"
        )

    @field_validator("niveau")
    @classmethod
    def _niveau(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return enums.validate_enum(v, enums.NIVEAU, field_name="niveau")

    @field_validator("etableringstidspunkt")
    @classmethod
    def _etableringstidspunkt(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return _validate_etableringstidspunkt(v)
