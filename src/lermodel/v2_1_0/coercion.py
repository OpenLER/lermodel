"""
Light, generic coercion applied before constructing a feature type - see
clay/adr/941 (in the sibling clay repo):

    "Yderligere coercion bør ligge andet steds, i et preprocessing step."

Only two kinds of correction happen here, both generic enough to be safe for
any source: unit normalization for measurement fields, and case/whitespace
normalization of enum-valued fields against the field's own controlled
vocabulary. Anything more aggressive (synonym tables, source-specific
typo fixes, etc.) belongs in a preprocessing step in the calling
application (e.g. clay), not in lermodel.
"""

import re
from typing import Any, Mapping

from lermodel.v2_1_0 import enums

_VOLTAGE_RE = re.compile(r"^([\d.,]+)\s*(kv|v)?$", re.IGNORECASE)

# Which fields of each feature type hold enum values, and against which
# vocabulary. Kept explicit (rather than derived from the pydantic models)
# so this module has no dependency on featuretypes.py / the class hierarchy.
_ENUM_FIELDS_BY_FEATURE_TYPE: dict[str, dict[str, frozenset[str]]] = {
    "Elledning": {
        "driftsstatus": enums.DRIFTSSTATUS,
        "ejerskabsforhold": enums.EJERSKABSFORHOLD,
        "fareklasse": enums.FAREKLASSE,
        "indtegningsmetode": enums.INDTEGNINGSMETODE,
        "noejagtighedsklasse": enums.NOEJAGTIGHEDSKLASSE,
        "niveau": enums.NIVEAU,
        "ledningsetableringsmetode": enums.LEDNINGSETABLERINGSMETODE,
        "type": enums.ELLEDNINGSTYPE,
    },
    "Foeringsroer": {
        "driftsstatus": enums.DRIFTSSTATUS,
        "ejerskabsforhold": enums.EJERSKABSFORHOLD,
        "fareklasse": enums.FAREKLASSE,
        "indtegningsmetode": enums.INDTEGNINGSMETODE,
        "noejagtighedsklasse": enums.NOEJAGTIGHEDSKLASSE,
        "niveau": enums.NIVEAU,
        "ledningsetableringsmetode": enums.LEDNINGSETABLERINGSMETODE,
        "tvaersnitsform": enums.TVAERSNITSFORM,
    },
    "Elkomponent": {
        "driftsstatus": enums.DRIFTSSTATUS,
        "ejerskabsforhold": enums.EJERSKABSFORHOLD,
        "fareklasse": enums.FAREKLASSE,
        "noejagtighedsklasse": enums.NOEJAGTIGHEDSKLASSE,
        "niveau": enums.NIVEAU,
        "type": enums.ELKOMPONENTTYPE,
        "relativNiveau": enums.RELATIV_NIVEAU,
    },
}

# Fields typed as gml:MeasureType that are given in kV in LER XML, but may
# arrive from source data in V, kV, or unitless (assumed already kV).
_VOLTAGE_MEASURE_FIELDS = {"spaendingsniveau"}


def normalize_voltage(value: Any) -> Any:
    """
    Normalize a voltage value to a plain kV number, regardless of unit:
    - "400V"    -> "0.4"
    - "0.4 kV"  -> "0.4"
    - "10"      -> "10.0"  (no unit given, assumed already kV)
    """
    if not isinstance(value, str):
        return value
    match = _VOLTAGE_RE.match(value.strip())
    if not match:
        return value
    number_str, unit = match.groups()
    number = float(number_str.replace(",", "."))
    if (unit or "kv").lower() == "v":
        number = number / 1000
    return str(number)


def normalize_enum_value(value: Any, allowed: frozenset[str]) -> Any:
    """
    Match value against allowed, ignoring surrounding whitespace and case.
    Returns the canonical (correctly-cased) value from allowed on a match,
    otherwise returns value unchanged - actual validation happens later, in
    the pydantic field validators.
    """
    if not isinstance(value, str):
        return value
    stripped = value.strip()
    if stripped in allowed:
        return stripped
    lowered = stripped.lower()
    for candidate in allowed:
        if candidate.lower() == lowered:
            return candidate
    return value


def coerce_properties(feature_type: str, props: Mapping[str, Any]) -> dict[str, Any]:
    """Apply light, generic coercion to a feature's raw properties dict."""
    result = dict(props)

    for field_name in _VOLTAGE_MEASURE_FIELDS:
        if result.get(field_name) is not None:
            result[field_name] = normalize_voltage(result[field_name])

    for field_name, allowed in _ENUM_FIELDS_BY_FEATURE_TYPE.get(feature_type, {}).items():
        if result.get(field_name) is not None:
            result[field_name] = normalize_enum_value(result[field_name], allowed)

    return result
