# lermodel

En implementering af LER's featurekatalog / datamodel, i Python,
vha pydantic.

Understøtter i øjeblikket LER 2.1.0 og 2.2.0, hver som sin egen
selvstændige `lermodel.v2_1_0` / `lermodel.v2_2_0` implementation (ikke
delt via arv på tværs af versioner - se clay/adr/943 i søster-repoet clay).

Se [VERSION_SUPPORT.md](VERSION_SUPPORT.md) for hvilke feature types der er
understøttet.

## Usage

```python
import lermodel
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

lerfeat = lermodel.to_lerfeat(feat, "2.1.0")  # version is required, no default
xml_element = lerfeat.to_xml()
print(etree.tostring(xml_element, pretty_print=True).decode())
```

Version-specific `to_lerfeat` is also available directly, e.g.
`lermodel.v2_1_0.to_lerfeat(feat)`, for code that's already pinned to one
version.

`GraveforespoergselssvarType` wraps a set of already-built lerfeat objects
into the full response envelope. It's constructed directly, not via
`to_lerfeat` (it isn't read from a single source feature):

```python
from lermodel.v2_1_0 import GraveforespoergselssvarType

svar = GraveforespoergselssvarType(
    type="ledningsoplysninger udleveret",
    gyldigTil="2026-12-31",
    ledningMember=[lerfeat],
)
print(etree.tostring(svar.to_xml(), pretty_print=True).decode())
```

eller

```python
svar = GraveforespoergselssvarType(
    type="ledningsoplysninger udleveret",
    gyldigTil="2026-12-31",
)
svar.ledningMember.append(feat1)
svar.ledningMember.append(feat2)
```
