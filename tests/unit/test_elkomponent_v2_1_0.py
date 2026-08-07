from copy import deepcopy

import lerxml
import pytest
from lxml import etree
from pydantic import ValidationError

from lermodel.v2_1_0 import to_lerfeat

VALID = {
    "type": "Feature",
    "properties": {
        "feature_type": "Elkomponent",
        "type": "kabelskab",
        "noejagtighedsklasse": "<= 2.00 m",
    },
    "geometry": {
        "type": "Point",
        "coordinates": [565984, 6237039],
    },
}


def _to_valid_xml(feat):
    lerfeat = to_lerfeat(feat)
    elm = lerfeat.to_xml()
    report = lerxml.validate(etree.ElementTree(elm), version="2.1.0")
    assert report.valid, report.violations
    return lerfeat


def test_minimal_valid_elkomponent():
    _to_valid_xml(VALID)


def test_elkomponent_with_optional_fields():
    feat = deepcopy(VALID)
    feat["properties"].update(
        {
            "spaendingsniveau": "10kV",
            "materiale": "stål",
            "driftsstatus": "i drift",
        }
    )
    lerfeat = _to_valid_xml(feat)
    assert lerfeat.spaendingsniveau == 10.0


def test_elkomponent_relativ_niveau_only_allowed_for_roerblok():
    # relativNiveau is a real LER field, but only legal when type=rørblok -
    # this is enforced by lerxml's schematron/xta rules, not by lermodel
    # (see clay/adr/913 in the sibling clay repo: lermodel intentionally
    # only does light, generic validation, not full cross-field business
    # rules). lermodel happily builds schema-invalid-per-schematron XML
    # here; catching this class of rule is lerxml's job.
    feat = deepcopy(VALID)
    feat["properties"]["relativNiveau"] = "top"
    lerfeat = to_lerfeat(feat)
    elm = lerfeat.to_xml()
    report = lerxml.validate(etree.ElementTree(elm), version="2.1.0")
    assert not report.valid
    assert any(v.code == "relativNiveauTilladelse" for v in report.violations)


def test_elkomponent_missing_type_raises():
    feat = deepcopy(VALID)
    del feat["properties"]["type"]
    with pytest.raises(ValidationError):
        to_lerfeat(feat)


def test_elkomponent_type_is_not_nillable():
    # unlike Elledning.type, Elkomponent.type has no nilReason wrapper in
    # the XSD - None must be rejected outright, not accepted as "nil".
    feat = deepcopy(VALID)
    feat["properties"]["type"] = None
    with pytest.raises(ValidationError):
        to_lerfeat(feat)
