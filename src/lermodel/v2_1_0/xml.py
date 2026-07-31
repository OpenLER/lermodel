"""
to_xml() serialization: turns a feature type instance into an lxml element
conforming to the LER 2.1.0 XSD. This only builds the feature element itself
(e.g. <ler:Elledning>) - wrapping it in a Graveforespoergselssvar (or other
envelope) along with schemaVersion, id, gyldigTil etc. is the caller's
responsibility (that's business logic belonging in clay, not lermodel - see
clay/adr/941).
"""

from typing import Any, TypeGuard

from lxml import etree
from lxml.builder import ElementMaker
from shapely.geometry import LineString, MultiLineString, Point
from shapely.geometry.base import BaseGeometry

from lermodel.v2_1_0.base import AbstractFeatureType

# Same namespace across all LER versions - only the schemaVersion attribute
# on the envelope root element changes between versions.
NSMAP = {
    "ler": "http://data.gov.dk/schemas/LER/2/gml",
    "gml": "http://www.opengis.net/gml/3.2",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}

LER = ElementMaker(namespace=NSMAP["ler"], nsmap=NSMAP)
GML = ElementMaker(namespace=NSMAP["gml"])

# Fields that are required-but-nillable in the XSD: the element must always
# be present, but xsi:nil="true" is used in place of a value. All other
# fields are simply omitted from the output when their value is None.
REQUIRED_NILLABLE_FIELDS = {
    "driftsstatus",
    "fareklasse",
    "type",
    "tvaersnitsform",
}

# Fields typed as gml:MeasureType in the XSD: serialized as plain numeric
# text plus a required "uom" attribute. Each field here is only ever
# produced by lermodel in the single, fixed unit given below.
MEASURE_FIELDS_UOM = {
    "spaendingsniveau": "kV",
    "udvendigDiameter": "mm",
    "udvendigBredde": "mm",
    "udvendigHoejde": "mm",
    "vejledendeDybde": "m",
}


def local_name_for_class(cls: type) -> str:
    name = cls.__name__
    if name.endswith("Type"):
        name = name[:-4]
    return name


def make_ler(tag: str, *children, xsi_nil: bool = False, **attrs) -> etree._Element:
    element_builder = getattr(LER, tag)
    el = element_builder(*children, **attrs)
    if xsi_nil:
        el.set(etree.QName(NSMAP["xsi"], "nil"), "true")
    return el


def simple_text(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def serialize_geometry(value: BaseGeometry | None) -> etree._Element:
    geometri = make_ler("geometri")

    if value is None or value.is_empty:
        return geometri

    # Temporary compromise: accept a single-part MultiLineString.
    if isinstance(value, MultiLineString):
        if len(value.geoms) != 1:
            raise TypeError(
                "serialize_geometry currently only supports LineString, Point, "
                "or single-part MultiLineString"
            )
        value = value.geoms[0]

    if isinstance(value, LineString):
        line = GML.LineString()
        poslist = GML.posList(" ".join(f"{x} {y}" for x, y in value.coords))
        line.append(poslist)
        geometri.append(line)
    elif isinstance(value, Point):
        point = GML.Point(GML.pos(f"{value.x} {value.y}"))
        geometri.append(point)
    else:
        raise TypeError(
            f"serialize_geometry does not support geometry type {value.geom_type!r}; "
            "only LineString, single-part MultiLineString, and Point are implemented"
        )

    return geometri


def is_abstract_feature_type(value: object) -> TypeGuard[AbstractFeatureType]:
    # No field currently holds a nested feature type instance (association
    # fields like startkomponent/indeholdtLedning aren't modeled - see
    # base.py), but serialize_field() keeps this branch for when one is
    # added.
    return isinstance(value, AbstractFeatureType)


def serialize_field(name: str, value: Any) -> list[etree._Element]:
    if value is None:
        if name in REQUIRED_NILLABLE_FIELDS:
            return [make_ler(name, xsi_nil=True)]
        return []

    if isinstance(value, list):
        out: list[etree._Element] = []
        for item in value:
            out.extend(serialize_field(name, item))
        return out

    if isinstance(value, BaseGeometry):
        return [serialize_geometry(value)]

    if is_abstract_feature_type(value):
        return [build_feature(value, tag=name)]

    if name in MEASURE_FIELDS_UOM:
        return [make_ler(name, simple_text(value), uom=MEASURE_FIELDS_UOM[name])]

    return [make_ler(name, simple_text(value))]


def build_feature(obj: AbstractFeatureType, tag: str | None = None) -> etree._Element:
    """
    Recursively build an XML element from a feature type instance, using
    field names as tags, in field-declaration order (which matches the
    XSD's <sequence> order - see base.py).
    """
    tag = tag or local_name_for_class(type(obj))
    fields = obj.model_dump()

    gml_id = fields.pop("gml_id", None)

    children: list[etree._Element] = []
    for name, value in fields.items():
        children.extend(serialize_field(name, value))

    elm = make_ler(tag, *children)
    if gml_id is not None:
        elm.set(etree.QName(NSMAP["gml"], "id"), gml_id)
    return elm


def to_xml(obj: AbstractFeatureType) -> etree._Element:
    """Serialize a single LER feature type instance to its XML element."""
    return build_feature(obj)
