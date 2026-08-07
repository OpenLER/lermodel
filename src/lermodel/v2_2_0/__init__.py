from lermodel.v2_2_0.base import (
    AbstractFeatureType,
    AbstractGMLType,
    LedningEllerLedningstraceType,
    LedningskomponentType,
    LedningType,
    RoerledningType,
)
from lermodel.v2_2_0.dispatch import FEATURE_TYPE_MAP, UnsupportedFeatureTypeError, to_lerfeat
from lermodel.v2_2_0.featuretypes import ElkomponentType, ElledningType, FoeringsroerType

SCHEMA_VERSION = "2.2.0"

# All concrete (non-abstract) feature types defined by the LER 2.2.0 XSD -
# used by lermodel.support to report which ones are implemented here (see
# clay/adr/944 in the sibling clay repo). Identical to v2_1_0.ALL_FEATURE_TYPES
# (confirmed by diffing the full complexType name lists of 2.1_ler.xsd and
# 2.2_ler.xsd - no feature types were added or removed between versions).
ALL_FEATURE_TYPES = (
    "Afloebskomponent",
    "Afloebsledning",
    "AndenKomponent",
    "AndenLedning",
    "Elkomponent",
    "Elledning",
    "Foeringsroer",
    "Gaskomponent",
    "Gasledning",
    "Informationsressource",
    "Kontaktprofil",
    "LedningUkendtForsyningsart",
    "Ledningstrace",
    "Oliekomponent",
    "Olieledning",
    "Telekommunikationskomponent",
    "Telekommunikationsledning",
    "TermiskKomponent",
    "TermiskLedning",
    "Vandkomponent",
    "Vandledning",
)

__all__ = [
    "SCHEMA_VERSION",
    "ALL_FEATURE_TYPES",
    "AbstractFeatureType",
    "AbstractGMLType",
    "LedningEllerLedningstraceType",
    "LedningType",
    "LedningskomponentType",
    "RoerledningType",
    "ElledningType",
    "FoeringsroerType",
    "ElkomponentType",
    "FEATURE_TYPE_MAP",
    "UnsupportedFeatureTypeError",
    "to_lerfeat",
]
