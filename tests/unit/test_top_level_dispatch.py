import pytest

import lermodel
from lermodel.v2_1_0.featuretypes import ElledningType as ElledningType_2_1_0
from lermodel.v2_2_0.featuretypes import ElledningType as ElledningType_2_2_0

FEAT = {
    "properties": {
        "feature_type": "Elledning",
        "driftsstatus": "i drift",
        "etableringstidspunkt": "2014-12-01",
        "fareklasse": "farlig",
        "type": "luftledning",
    },
    "geometry": {"type": "LineString", "coordinates": [[0, 0], [1, 1]]},
}


def test_routes_to_2_1_0():
    result = lermodel.to_lerfeat(FEAT, "2.1.0")
    assert isinstance(result, ElledningType_2_1_0)


def test_routes_to_2_2_0():
    result = lermodel.to_lerfeat(FEAT, "2.2.0")
    assert isinstance(result, ElledningType_2_2_0)


def test_version_is_required():
    with pytest.raises(TypeError):
        lermodel.to_lerfeat(FEAT)


def test_unknown_version_raises_value_error():
    with pytest.raises(ValueError, match="2.1.0"):
        lermodel.to_lerfeat(FEAT, "9.9.9")
