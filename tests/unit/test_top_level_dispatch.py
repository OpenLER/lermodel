import lerxml
import pytest
from lxml import etree

import lermodel
from lermodel import v2_1_0, v2_2_0
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


def test_get_version_returns_the_right_module():
    assert lermodel.get_version("2.1.0") is v2_1_0
    assert lermodel.get_version("2.2.0") is v2_2_0


def test_get_version_unknown_raises_value_error():
    with pytest.raises(ValueError, match="2.1.0"):
        lermodel.get_version("9.9.9")


def test_get_version_used_to_build_dynamic_version_gfsvar():
    # mirrors the README's "dynamic version" example
    version = "2.2.0"
    feat = {
        "properties": {
            **FEAT["properties"],
            "noejagtighedsklasse": "<= 2.00 m",
            "noejagtighedsklasseVertikal": "<= 2.00 m",
        },
        "geometry": FEAT["geometry"],
    }
    svar = lermodel.get_version(version).GraveforespoergselssvarType(
        type="ledningsoplysninger udleveret",
        gyldigTil="2026-12-31",
    )
    for f in [feat]:
        lerfeat = lermodel.to_lerfeat(f, version)
        svar.ledningMember.append(lerfeat)

    assert len(svar.ledningMember) == 1
    report = lerxml.validate(etree.ElementTree(svar.to_xml()), version=version)
    assert report.valid, report.violations
