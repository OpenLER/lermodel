"""
Python data model for LER (LedningsEjerRegister) features: pydantic classes
with light coercion, validation, and to_xml serialization.

See clay/adr/941-944 (in the sibling clay repo) for the design decisions
behind this package: it lives in its own repo, and rather than one
cross-version abstraction it has one complete, independent implementation
per supported LER version (lermodel.v2_1_0, ...), each implementing however
many of that version's feature types are actually needed (see
lermodel.support for what's currently covered).
"""

from lermodel.v2_1_0 import SCHEMA_VERSION as _V2_1_0
from lermodel.v2_1_0 import UnsupportedFeatureTypeError, to_lerfeat, to_xml

SUPPORTED_VERSIONS = (_V2_1_0,)

__all__ = [
    "SUPPORTED_VERSIONS",
    "UnsupportedFeatureTypeError",
    "to_lerfeat",
    "to_xml",
]
