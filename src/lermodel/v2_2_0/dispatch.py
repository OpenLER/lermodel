"""
to_lerfeat() dispatcher - see clay/adr/942 (in the sibling clay repo) for
why this lives in lermodel rather than in clay: it needs to know which
concrete feature types this LER version implements, which is exactly
lermodel's responsibility.
"""

from typing import Any, Mapping

from shapely.geometry import shape

from lermodel.errors import UnsupportedFeatureTypeError
from lermodel.v2_2_0.base import AbstractFeatureType
from lermodel.v2_2_0.coercion import coerce_properties
from lermodel.v2_2_0.featuretypes import ElkomponentType, ElledningType, FoeringsroerType

__all__ = ["FEATURE_TYPE_MAP", "UnsupportedFeatureTypeError", "to_lerfeat"]

# Keys are the LER XSD element's ASCII local name (e.g. "Foeringsroer"),
# not its Danish display name ("Føringsrør") - this is what feature_type
# must be set to on the input feature.
FEATURE_TYPE_MAP: dict[str, type[AbstractFeatureType]] = {
    "Elledning": ElledningType,
    "Foeringsroer": FoeringsroerType,
    "Elkomponent": ElkomponentType,
}


def to_lerfeat(feat: Mapping[str, Any]) -> AbstractFeatureType:
    """
    Build the appropriate concrete LER 2.2.0 feature object from a
    GeoJSON-like feature mapping (e.g. a fiona.model.Feature).

    Expected input:
        feat["properties"]["feature_type"] = "Elledning" | "Foeringsroer" | "Elkomponent"
        feat["geometry"] = a GeoJSON-like geometry mapping, or None

    Raises UnsupportedFeatureTypeError if feature_type names a real LER
    feature type not yet implemented here, and ValueError for malformed
    input (missing feature_type) or a pydantic ValidationError for
    input that fails field validation.
    """
    props = dict(feat.get("properties") or {})
    feature_type = props.pop("feature_type", None)

    if not feature_type:
        raise ValueError("Missing required property: 'feature_type'")

    cls = FEATURE_TYPE_MAP.get(feature_type)
    if cls is None:
        raise UnsupportedFeatureTypeError(
            f"Unsupported or not-yet-implemented feature_type: {feature_type!r}. "
            f"Implemented feature types in lermodel.v2_2_0: {sorted(FEATURE_TYPE_MAP)}."
        )

    props = coerce_properties(feature_type, props)

    geom = feat.get("geometry")
    shapely_geom = shape(geom) if geom else None

    allowed_field_names = set(cls.model_fields)
    kwargs = {k: v for k, v in props.items() if k in allowed_field_names}

    if "geometri" in allowed_field_names:
        kwargs["geometri"] = shapely_geom

    return cls(**kwargs)
