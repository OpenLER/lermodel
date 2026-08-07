"""Maps a LER version string to its lermodel.v2_x_x module. Add new versions here."""

from lermodel import v2_1_0, v2_2_0

VERSIONS = {
    v2_1_0.SCHEMA_VERSION: v2_1_0,
    v2_2_0.SCHEMA_VERSION: v2_2_0,
}
