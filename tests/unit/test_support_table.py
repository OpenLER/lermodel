from pathlib import Path

from lermodel.support import generate_support_table

START = "<!-- SUPPORT_TABLE_START -->"
END = "<!-- SUPPORT_TABLE_END -->"


def test_readme_support_table_is_up_to_date():
    readme_path = Path(__file__).resolve().parents[2] / "README.md"
    text = readme_path.read_text()
    _, rest = text.split(START, 1)
    embedded, _ = rest.split(END, 1)

    assert embedded.strip("\n") == generate_support_table().strip("\n"), (
        "README.md's supported-feature-types table is stale; run `python scripts/update_readme.py`"
    )
