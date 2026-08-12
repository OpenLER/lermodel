from copy import deepcopy

import lerxml
import pytest
from lxml import etree
from pydantic import ValidationError

from lermodel.v2_2_0 import to_lerfeat

VALID = {
    "type": "Feature",
    "properties": {
        "feature_type": "Elledning",
        "driftsstatus": "i drift",
        "etableringstidspunkt": "2014-12-01",
        "fareklasse": "farlig",
        "type": "luftledning",
        "kabeltype": "Cu 4x6",
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


def test_minimal_valid_elledning():
    _to_valid_xml(VALID)


def test_elledning_with_optional_fields():
    feat = deepcopy(VALID)
    feat["properties"].update(
        {
            "afdaekning": "PVC",
            "antalKabler": 3,
            "spaendingsniveau": "400V",
            "udvendigDiameter": 50,
            "niveau": "under terræn",
            "udvendigFarve": ["sort", "rød"],
        }
    )
    lerfeat = _to_valid_xml(feat)
    assert lerfeat.spaendingsniveau == 0.4


def test_elledning_noejagtighedsklasse_vertikal():
    # new in 2.2.0 - not present at all in 2.1.0
    feat = deepcopy(VALID)
    feat["properties"]["noejagtighedsklasseVertikal"] = "<= 1.00 m"
    lerfeat = _to_valid_xml(feat)
    assert lerfeat.noejagtighedsklasseVertikal == "<= 1.00 m"


def test_elledning_missing_noejagtighedsklasse_vertikal_raises():
    # required whenever geometry is present (nøjagtighedsklasseVertikalBetingelse)
    # - lermodel now enforces this itself (see clay/adr/913 in the sibling
    # clay repo), rather than letting it slip through to lerxml.
    feat = deepcopy(VALID)
    del feat["properties"]["noejagtighedsklasseVertikal"]
    with pytest.raises(ValidationError):
        to_lerfeat(feat)


def test_elledning_invalid_noejagtighedsklasse_vertikal_raises():
    feat = deepcopy(VALID)
    feat["properties"]["noejagtighedsklasseVertikal"] = "not a real class"
    with pytest.raises(ValidationError):
        to_lerfeat(feat)


def test_elledning_type_other():
    feat = deepcopy(VALID)
    feat["properties"]["type"] = "other: fiberkabel"
    _to_valid_xml(feat)


def test_elledning_nil_driftsstatus():
    # driftsstatus is required-but-nillable: explicit None is valid input
    # and must round-trip as xsi:nil="true".
    feat = deepcopy(VALID)
    feat["properties"]["driftsstatus"] = None
    _to_valid_xml(feat)


def test_elledning_missing_driftsstatus_raises():
    # unlike explicit None, omitting the field entirely is not a valid
    # "nil" - it's simply missing required input.
    feat = deepcopy(VALID)
    del feat["properties"]["driftsstatus"]
    with pytest.raises(ValidationError):
        to_lerfeat(feat)


def test_elledning_invalid_type_raises():
    feat = deepcopy(VALID)
    feat["properties"]["type"] = "not a real type"
    with pytest.raises(ValidationError):
        to_lerfeat(feat)


def test_elledning_invalid_etableringstidspunkt_raises():
    feat = deepcopy(VALID)
    feat["properties"]["etableringstidspunkt"] = "2014/12/01"
    with pytest.raises(ValidationError):
        to_lerfeat(feat)
