from lermodel.dispatch import to_lerfeat
from lermodel.errors import UnsupportedFeatureTypeError
from lermodel.registry import get_version
from lermodel.v2_1_0 import SCHEMA_VERSION as _V2_1_0
from lermodel.v2_2_0 import SCHEMA_VERSION as _V2_2_0

SUPPORTED_VERSIONS = (_V2_1_0, _V2_2_0)

__all__ = [
    "SUPPORTED_VERSIONS",
    "UnsupportedFeatureTypeError",
    "get_version",
    "to_lerfeat",
]
