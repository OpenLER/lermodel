import pytest

from lermodel.v2_2_0 import enums
from lermodel.v2_2_0.coercion import coerce_properties, normalize_enum_value, normalize_voltage


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("400V", "0.4"),
        ("400 V", "0.4"),
        ("0.4 kV", "0.4"),
        ("0,4 kV", "0.4"),
        ("10kV", "10.0"),
        ("10", "10.0"),
        ("1000V", "1.0"),
        ("not a number", "not a number"),
    ],
)
def test_normalize_voltage(raw, expected):
    assert normalize_voltage(raw) == expected


def test_normalize_voltage_passes_through_non_strings():
    assert normalize_voltage(10) == 10


def test_normalize_enum_value_exact_match():
    assert normalize_enum_value("i drift", enums.DRIFTSSTATUS) == "i drift"


def test_normalize_enum_value_case_and_whitespace():
    assert normalize_enum_value("  I DRIFT  ", enums.DRIFTSSTATUS) == "i drift"


def test_normalize_enum_value_no_match_passthrough():
    assert normalize_enum_value("bogus", enums.DRIFTSSTATUS) == "bogus"


def test_coerce_properties_normalizes_voltage_and_enum_case():
    props = {"driftsstatus": "I DRIFT", "spaendingsniveau": "400V", "type": "luftledning"}
    coerced = coerce_properties("Elledning", props)
    assert coerced["driftsstatus"] == "i drift"
    assert coerced["spaendingsniveau"] == "0.4"


def test_coerce_properties_normalizes_noejagtighedsklasse_vertikal():
    # new in 2.2.0 - not present at all in 2.1.0's coercion map
    props = {"noejagtighedsklasseVertikal": "  <= 1.00 M  "}
    coerced = coerce_properties("Elledning", props)
    assert coerced["noejagtighedsklasseVertikal"] == "<= 1.00 m"


def test_coerce_properties_unknown_feature_type_is_noop_for_enums():
    props = {"driftsstatus": "I DRIFT"}
    coerced = coerce_properties("SomeUnknownType", props)
    assert coerced["driftsstatus"] == "I DRIFT"
