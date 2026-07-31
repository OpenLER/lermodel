from pathlib import Path

from lermodel.support import generate_support_table


def test_version_support_md_is_up_to_date():
    version_support_path = Path(__file__).resolve().parents[2] / "VERSION_SUPPORT.md"
    text = version_support_path.read_text()

    assert text.endswith(generate_support_table()), (
        "VERSION_SUPPORT.md is stale; run `python scripts/update_version_support.py`"
    )
