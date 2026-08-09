"""
Version-dispatching to_lerfeat() - see clay/adr/942: a single clay instance
answers with different LER versions for different interesseomraader, so
which version to build against is always an explicit caller choice, never
a default.
"""

from typing import Any, Mapping

from lermodel.registry import get_version


def to_lerfeat(feat: Mapping[str, Any], version: str) -> Any:
    """
    Build a LER feature object for the given LER version. version is
    required.

    Return type is Any, not e.g. v2_1_0.AbstractFeatureType: each version
    package is an independent implementation (clay/adr/943) with its own,
    unrelated class hierarchy - there is no shared base class to name here.
    """
    return get_version(version).to_lerfeat(feat)
