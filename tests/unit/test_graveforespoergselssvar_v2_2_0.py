import re

import lerxml
import pytest
from lxml import etree
from pydantic import ValidationError
from shapely.geometry import Point

from lermodel.v2_2_0 import UnsupportedFeatureTypeError, to_lerfeat
from lermodel.v2_2_0.featuretypes import ElkomponentType, GraveforespoergselssvarType

ELLEDNING_FEAT = {
    "properties": {
        "feature_type": "Elledning",
        "driftsstatus": "i drift",
        "etableringstidspunkt": "2014-12-01",
        "fareklasse": "farlig",
        "type": "luftledning",
        "noejagtighedsklasse": "<= 2.00 m",
        "noejagtighedsklasseVertikal": "<= 2.00 m",
    },
    "geometry": {
        "type": "LineString",
        "coordinates": [[565984, 6237039], [565985, 6237040]],
    },
}

ELKOMPONENT = ElkomponentType(
    type="kabelskab",
    noejagtighedsklasse="<= 2.00 m",
    geometri=Point(565984, 6237039),
)


def _to_valid_xml(svar):
    elm = svar.to_xml()
    report = lerxml.validate(etree.ElementTree(elm), version="2.2.0")
    assert report.valid, report.violations
    return elm


def test_empty_svar_defaults():
    svar = GraveforespoergselssvarType(type="ingen ledninger i graveområde")
    assert svar.gml_id == "graveforespoergselssvar"
    assert re.match(r"^[0-9a-f-]{36}$", svar.id, re.IGNORECASE)
    assert svar.schemaVersion == "2.2.0"
    _to_valid_xml(svar)


def test_svar_with_ledning_and_komponent_members():
    elledning = to_lerfeat(ELLEDNING_FEAT)
    svar = GraveforespoergselssvarType(
        type="ledningsoplysninger udleveret",
        ledningMember=[elledning],
        ledningskomponentMember=[ELKOMPONENT],
    )
    elm = _to_valid_xml(svar)
    assert elm.find("{http://data.gov.dk/schemas/LER/2/gml}ledningMember") is not None


def test_schema_version_is_an_unprefixed_attribute():
    svar = GraveforespoergselssvarType(type="ingen ledninger i graveområde")
    elm = svar.to_xml()
    assert elm.get("schemaVersion") == "2.2.0"


def test_schema_version_cannot_be_overridden_to_another_version():
    with pytest.raises(ValidationError):
        GraveforespoergselssvarType(type="ingen ledninger i graveområde", schemaVersion="2.1.0")


def test_explicit_id_must_be_uuid_formatted():
    with pytest.raises(ValidationError):
        GraveforespoergselssvarType(type="ingen ledninger i graveområde", id="not-a-uuid")


def test_invalid_type_raises():
    with pytest.raises(ValidationError):
        GraveforespoergselssvarType(type="not a real type")


def test_missing_type_supplerende_info_is_schematron_invalid():
    # typeSupplerendeInfo is required when type is "ledningsoplysninger
    # udleveres ikke" - a cross-field schematron/xta rule, deliberately not
    # enforced by lermodel itself (see clay/adr/913 in the sibling clay repo).
    svar = GraveforespoergselssvarType(type="ledningsoplysninger udleveres ikke")
    elm = svar.to_xml()
    report = lerxml.validate(etree.ElementTree(elm), version="2.2.0")
    assert not report.valid
    assert any(v.code == "typeSupplerendeInfoBetingelse" for v in report.violations)


def test_not_dispatched_via_to_lerfeat():
    with pytest.raises(UnsupportedFeatureTypeError):
        to_lerfeat(
            {
                "properties": {"feature_type": "Graveforespoergselssvar", "type": "x"},
                "geometry": None,
            }
        )
