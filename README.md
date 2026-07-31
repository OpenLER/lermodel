# lermodel

En implementering af LER's featurekatalog / datamodel, i Python,
vha pydantic.

På sigt skal den kunne repræsentere de forskellige versioner
af LER, men lige nu er det kun 2.1.0.

Se [VERSION_SUPPORT.md](VERSION_SUPPORT.md) for hvilke feature types der er
understøttet.

## Usage

```python
from lermodel import to_lerfeat, to_xml
from lxml import etree

feat = {
    "type": "Feature",
    "properties": {
        "feature_type": "Elledning",
        "driftsstatus": "i drift",
        "etableringstidspunkt": "2014-12-01",
        "fareklasse": "farlig",
        "type": "luftledning",
        "kabeltype": "Cu 4x6",
    },
    "geometry": {
        "type": "LineString",
        "coordinates": [[565984, 6237039], [565985, 6237040]],
    },
}

lerfeat = to_lerfeat(feat)
xml_element = to_xml(lerfeat)
print(etree.tostring(xml_element, pretty_print=True).decode())
```
