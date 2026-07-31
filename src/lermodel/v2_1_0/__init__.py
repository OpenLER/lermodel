from lermodel.v2_1_0.base import (
    AbstractFeatureType,
    AbstractGMLType,
    LedningEllerLedningstraceType,
    LedningskomponentType,
    LedningType,
    RoerledningType,
)
from lermodel.v2_1_0.dispatch import FEATURE_TYPE_MAP, UnsupportedFeatureTypeError, to_lerfeat
from lermodel.v2_1_0.featuretypes import ElkomponentType, ElledningType, FoeringsroerType
from lermodel.v2_1_0.xml import to_xml

SCHEMA_VERSION = "2.1.0"

# All concrete (non-abstract) feature types defined by the LER 2.1.0 XSD -
# used by lermodel.support to report which ones are implemented here (see
# clay/adr/944 in the sibling clay repo). Sourced from the complexType
# names in 2.1_ler.xsd, excluding *PropertyType and abstract types, and
# excluding GraveforespoergselssvarType (the response envelope, not a
# ledning/komponent feature).
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
    "to_xml",
]
