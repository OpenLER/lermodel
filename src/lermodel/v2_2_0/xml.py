"""
XML serialization backing AbstractFeatureType.to_xml() (see base.py). Only
builds the feature element itself (e.g. <ler:Elledning>) - the envelope
(schemaVersion, id, gyldigTil, ...) is the caller's job, not lermodel's.
"""

from typing import Any, TypeGuard

from lxml import etree
from lxml.builder import ElementMaker
from shapely.geometry import LineString, MultiLineString, Point
from shapely.geometry.base import BaseGeometry

from lermodel.v2_2_0.base import AbstractFeatureType

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
# fields (including optional-and-nillable ones like noejagtighedsklasse and
# noejagtighedsklasseVertikal) are simply omitted from the output when None
# - that's also schema-valid, and simpler.
REQUIRED_NILLABLE_FIELDS = {
    "driftsstatus",
    "fareklasse",
    "type",
    "tvaersnitsform",
}

# Fields typed as gml:MeasureType in the XSD: serialized as plain numeric
# text plus a required "uom" attribute. Each field here is only ever
# produced by lermodel in the single, fixed unit given below.
#
# udnyttelsesgrad (new in 2.2.0) is NOT here - it's a plain decimal in the
# XSD, not a gml:MeasureType, so it has no uom and needs no special casing.
MEASURE_FIELDS_UOM = {
    "spaendingsniveau": "kV",
    "udvendigDiameter": "mm",
    "udvendigBredde": "mm",
    "udvendigHoejde": "mm",
    "vejledendeDybde": "m",
}

# List fields holding other feature type instances, per gml:AbstractFeatureMemberType:
# each item is wrapped in its own <name> element, keeping the item's own tag
# inside (e.g. <ledningMember><Elledning>...</Elledning></ledningMember>) -
# unlike a plain list field, which repeats <name> once per item directly.
MEMBER_LIST_FIELDS = {
    "ledningMember",
    "ledningskomponentMember",
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
        if name in MEMBER_LIST_FIELDS:
            return [make_ler(name, build_feature(item)) for item in value]
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
    # dict(obj), not obj.model_dump(): model_dump() recursively dumps nested
    # feature type instances (e.g. GraveforespoergselssvarType.ledningMember
    # items) into plain dicts, but serialize_field() needs those to still be
    # model instances to recurse into build_feature() for them.
    fields = dict(obj)

    gml_id = fields.pop("gml_id", None)
    # Only GraveforespoergselssvarType has this - an XML attribute, not a
    # sequence element, so it's popped here rather than going through
    # serialize_field(). No-op for every other feature type.
    schema_version = fields.pop("schemaVersion", None)

    children: list[etree._Element] = []
    for name, value in fields.items():
        children.extend(serialize_field(name, value))

    elm = make_ler(tag, *children)
    if gml_id is not None:
        elm.set(etree.QName(NSMAP["gml"], "id"), gml_id)
    if schema_version is not None:
        elm.set("schemaVersion", schema_version)
    return elm
