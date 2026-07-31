"""
Controlled vocabularies from LER featurekatalog 2.1.0 (2.1_ler.xsd).

Only the enumerations actually reachable from the feature types implemented
in this package (see featuretypes.py) are included - not the full LER
2.1.0 vocabulary.
"""

import re

DRIFTSSTATUS = frozenset(
    {
        "under etablering",
        "i drift",
        "permanent ude af drift",
    }
)

EJERSKABSFORHOLD = frozenset(
    {
        "ejet af anden ledningsejer",
        "ejet af udleverende ledningsejer",
        "uden ejer",
    }
)

FAREKLASSE = frozenset(
    {
        "ikke farlig",
        "farlig",
        "meget farlig",
    }
)

INDTEGNINGSMETODE = frozenset(
    {
        "forskudt",
        "nøjagtigt",
        "skematisk",
    }
)

NIVEAU = frozenset(
    {
        "delvist under terræn",
        "over terræn",
        "under terræn",
    }
)

NOEJAGTIGHEDSKLASSE = frozenset(
    {
        "<= 0.25 m",
        "<= 0.50 m",
        "<= 1.00 m",
        "<= 2.00 m",
        "> 2.00 m",
    }
)

LEDNINGSETABLERINGSMETODE = frozenset(
    {
        "nedgravning",
        "styret boring",
        "indvendig foring",
        "foring med lange sammensvejste rør",
        "stram foring",
        "strømpeforing",
        "nedpløjning",
        "jordfortrængning",
        "rørsprængning",
        "skydning med jordraket",
        "underboring",
        "mikrotunnellering",
        "pilotrørsmetoden",
    }
)

RELATIV_NIVEAU = frozenset(
    {
        "bund",
        "midt",
        "top",
    }
)

TVAERSNITSFORM = frozenset(
    {
        "brilleformet",
        "cirkulær",
        "kvadratisk",
        "rektangulær",
        "sektorformet",
        "spidsbundet",
        "trapezformet",
        "trekantet",
        "tunnelformet",
        "ægformet",
        "øjestensprofil",
    }
)

ELLEDNINGSTYPE = frozenset(
    {
        "beskyttelsesleder",
        "forsyningskabel",
        "KB-kabel",
        "luftledning",
        "signalkabel",
        "stikkabel",
        "vejbelysningskabel",
    }
)

ELKOMPONENTTYPE = frozenset(
    {
        "belysningsarmatur",
        "højspændingsmast",
        "jernplade",
        "kabelbrønd",
        "kabelskab",
        "kommunikationsmuffe",
        "kvejl",
        "lavspændingsmast",
        "målerskab",
        "mastefundament uden mast",
        "muffe",
        "muffegrube",
        "rørblok",
        "sensor",
        "signalmast med galge",
        "signalmast uden galge",
        "spole",
        "station",
        "T-muffe",
        "tændskab/gadelys",
        "teknikskab",
        "trykskab",
        "vindmølle",
    }
)

FORSYNINGSART = frozenset(
    {
        "afløb",
        "el",
        "fjernvarme/fjernkøling",
        "gas",
        "olie",
        "telekommunikation",
        "vand",
    }
)

# ler:*OtherType simple types across the schema all share this exact pattern.
OTHER_PATTERN = re.compile(r"^other: \w{2,}$", re.UNICODE)


def validate_enum(
    value: str, allowed: frozenset[str], *, field_name: str, allow_other: bool = False
) -> str:
    """
    Validate value against a LER controlled vocabulary.

    Some LER enumerations are unions of a fixed set of values plus a
    free-text escape hatch matching "other: <word>" (allow_other=True).
    """
    if value in allowed:
        return value
    if allow_other and OTHER_PATTERN.match(value):
        return value
    suffix = ', or "other: ..."' if allow_other else ""
    raise ValueError(f"{field_name} must be one of {sorted(allowed)}{suffix}, got {value!r}")
