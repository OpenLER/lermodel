import pytest

from lermodel.v2_2_0 import UnsupportedFeatureTypeError, to_lerfeat
from lermodel.v2_2_0.featuretypes import ElledningType

VALID_ELLEDNING = {
    "properties": {
        "feature_type": "Elledning",
        "driftsstatus": "i drift",
        "etableringstidspunkt": "2014-12-01",
        "fareklasse": "farlig",
        "type": "luftledning",
        "noejagtighedsklasse": "<= 2.00 m",
        "noejagtighedsklasseVertikal": "<= 2.00 m",
    },
    "geometry": {"type": "LineString", "coordinates": [[0, 0], [1, 1]]},
}


def test_to_lerfeat_returns_correct_class():
    result = to_lerfeat(VALID_ELLEDNING)
    assert isinstance(result, ElledningType)


def test_to_lerfeat_missing_feature_type_raises_value_error():
    with pytest.raises(ValueError):
        to_lerfeat({"properties": {}})


def test_to_lerfeat_unsupported_feature_type_raises_dedicated_error():
    # Vandledning is a real LER 2.2.0 feature type, just not implemented
    # here yet (see clay/adr/944) - this must be distinguishable from
    # "malformed input".
    with pytest.raises(UnsupportedFeatureTypeError):
        to_lerfeat({"properties": {"feature_type": "Vandledning"}})


def test_unsupported_feature_type_error_lists_implemented_types():
    with pytest.raises(UnsupportedFeatureTypeError, match="Elledning"):
        to_lerfeat({"properties": {"feature_type": "Vandledning"}})


def test_to_lerfeat_ignores_unknown_properties():
    feat = dict(VALID_ELLEDNING)
    feat["properties"] = {**VALID_ELLEDNING["properties"], "some_unrelated_column": "x"}
    result = to_lerfeat(feat)
    assert isinstance(result, ElledningType)


def test_v2_1_0_and_v2_2_0_share_the_same_error_class():
    from lermodel.errors import UnsupportedFeatureTypeError as SharedError
    from lermodel.v2_1_0 import UnsupportedFeatureTypeError as V2_1_0_Error

    assert UnsupportedFeatureTypeError is V2_1_0_Error is SharedError
