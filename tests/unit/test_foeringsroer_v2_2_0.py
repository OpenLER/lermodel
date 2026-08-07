from copy import deepcopy

import lerxml
import pytest
from lxml import etree
from pydantic import ValidationError

from lermodel.v2_2_0 import to_lerfeat

VALID = {
    "type": "Feature",
    "properties": {
        "feature_type": "Foeringsroer",
        "driftsstatus": "i drift",
        "etableringstidspunkt": "2014-12-01",
        "fareklasse": "ikke farlig",
        "tvaersnitsform": "cirkulær",
        "noejagtighedsklasse": "<= 2.00 m",
        # required whenever geometry is present, same as noejagtighedsklasse
        # itself - new in 2.2.0 (nøjagtighedsklasseVertikalBetingelse)
        "noejagtighedsklasseVertikal": "<= 2.00 m",
    },
    "geometry": {
        "type": "LineString",
        "coordinates": [[565984, 6237039], [565985, 6237040]],
    },
}


def _to_valid_xml(feat):
    lerfeat = to_lerfeat(feat)
    elm = lerfeat.to_xml()
    report = lerxml.validate(etree.ElementTree(elm), version="2.2.0")
    assert report.valid, report.violations
    return lerfeat


def test_minimal_valid_foeringsroer():
    _to_valid_xml(VALID)


def test_foeringsroer_with_forsyningsart():
    feat = deepcopy(VALID)
    feat["properties"]["forsyningsart"] = ["el", "telekommunikation"]
    lerfeat = _to_valid_xml(feat)
    assert lerfeat.forsyningsart == ["el", "telekommunikation"]


def test_foeringsroer_other_tvaersnitsform():
    feat = deepcopy(VALID)
    feat["properties"]["tvaersnitsform"] = "other: ovalformet"
    _to_valid_xml(feat)


def test_foeringsroer_nil_tvaersnitsform():
    feat = deepcopy(VALID)
    feat["properties"]["tvaersnitsform"] = None
    _to_valid_xml(feat)


def test_foeringsroer_udnyttelsesgrad():
    # new in 2.2.0 - not present at all in 2.1.0
    feat = deepcopy(VALID)
    feat["properties"]["udnyttelsesgrad"] = 0.75
    lerfeat = _to_valid_xml(feat)
    assert lerfeat.udnyttelsesgrad == 0.75


@pytest.mark.parametrize("value", [-0.1, 1.1, 0.333])
def test_foeringsroer_invalid_udnyttelsesgrad_raises(value):
    feat = deepcopy(VALID)
    feat["properties"]["udnyttelsesgrad"] = value
    with pytest.raises(ValidationError):
        to_lerfeat(feat)


def test_foeringsroer_noejagtighedsklasse_vertikal():
    feat = deepcopy(VALID)
    feat["properties"]["noejagtighedsklasseVertikal"] = "<= 0.50 m"
    lerfeat = _to_valid_xml(feat)
    assert lerfeat.noejagtighedsklasseVertikal == "<= 0.50 m"


def test_foeringsroer_missing_noejagtighedsklasse_vertikal_is_schematron_invalid():
    # required whenever geometry is present (nøjagtighedsklasseVertikalBetingelse)
    # - a cross-field schematron/xta rule, deliberately not enforced by
    # lermodel itself (see clay/adr/913 in the sibling clay repo).
    feat = deepcopy(VALID)
    del feat["properties"]["noejagtighedsklasseVertikal"]
    lerfeat = to_lerfeat(feat)
    elm = lerfeat.to_xml()
    report = lerxml.validate(etree.ElementTree(elm), version="2.2.0")
    assert not report.valid
    assert any(v.code == "nøjagtighedsklasseVertikalBetingelse" for v in report.violations)
