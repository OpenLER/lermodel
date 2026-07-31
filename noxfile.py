import nox

# Assumes the usual openler checkout layout: lermodel and ler-xml-validator
# are sibling directories. lerxml is only needed for tests (to validate
# to_xml() output against the real LER XSD/schematron rules), not as a
# runtime dependency of lermodel itself.
LERXML_PATH = "../ler-xml-validator"


@nox.session(python="3.12")
def tests(session: nox.Session) -> None:
    session.install("-e", ".[dev]")
    session.install("-e", LERXML_PATH)
    session.run("pytest", *session.posargs)


@nox.session(python="3.12")
def lint(session: nox.Session) -> None:
    session.install("-e", ".[dev]")
    session.run("ruff", "check", ".")
    session.run("ruff", "format", "--check", ".")
