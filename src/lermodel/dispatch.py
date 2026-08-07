"""
Version-dispatching to_lerfeat() - see clay/adr/942: a single clay instance
answers with different LER versions for different interesseomraader, so
which version to build against is always an explicit caller choice, never
a default.
"""

from typing import Any, Mapping

from lermodel.registry import VERSIONS


def to_lerfeat(feat: Mapping[str, Any], version: str) -> Any:
    """
    Build a LER feature object for the given LER version. version is
    required.

    Return type is Any, not e.g. v2_1_0.AbstractFeatureType: each version
    package is an independent implementation (clay/adr/943) with its own,
    unrelated class hierarchy - there is no shared base class to name here.
    """
    module = VERSIONS.get(version)
    if module is None:
        raise ValueError(f"Unsupported LER version: {version!r}. Supported: {sorted(VERSIONS)}.")
    return module.to_lerfeat(feat)
