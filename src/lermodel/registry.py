"""Maps a LER version string to its lermodel.v2_x_x module. Add new versions here."""

from types import ModuleType

from lermodel import v2_1_0, v2_2_0

VERSIONS = {
    v2_1_0.SCHEMA_VERSION: v2_1_0,
    v2_2_0.SCHEMA_VERSION: v2_2_0,
}


def get_version(version: str) -> ModuleType:
    """Look up a LER version's lermodel.v2_x_x module. version is required, no default."""
    module = VERSIONS.get(version)
    if module is None:
        raise ValueError(f"Unsupported LER version: {version!r}. Supported: {sorted(VERSIONS)}.")
    return module
