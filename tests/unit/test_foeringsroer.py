from copy import deepcopy

import lerxml
from lxml import etree

from lermodel import to_lerfeat, to_xml

VALID = {
    "type": "Feature",
    "properties": {
        "feature_type": "Foeringsroer",
        "driftsstatus": "i drift",
        "etableringstidspunkt": "2014-12-01",
        "fareklasse": "ikke farlig",
        "tvaersnitsform": "cirkulær",
        "noejagtighedsklasse": "<= 2.00 m",
    },
    "geometry": {
        "type": "LineString",
        "coordinates": [[565984, 6237039], [565985, 6237040]],
    },
}


def _to_valid_xml(feat):
    lerfeat = to_lerfeat(feat)
    elm = to_xml(lerfeat)
    report = lerxml.validate(etree.ElementTree(elm), version="2.1.0")
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
