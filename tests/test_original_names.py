"""Original names and materials only (constraint 8, acceptance criterion 15).

The method this app follows — people telling short accounts and then signifying
their own accounts, read as a distribution — is a general research pattern. The
best-known product built on it is somebody else's, and its name is a registered
trademark. So the rule is not "avoid mentioning it": the rule is that the app is
called Narrative Lens everywhere, and the other name appears exactly once, in
the README, as an attribution that says plainly what this project is not.

The PRD and CLAUDE.md are outside the scan. They are the specification and the
standing instructions for building it — they *state* this constraint, and a
rule that forbade quoting itself would be a strange rule.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

#: The names that may not appear in the app, its code, or its shipped writing.
RESERVED = ("SenseMaker", "Cynefin", "Cognitive Edge")

#: Everything that ships or is read by somebody working on it, minus the two
#: documents that quote the constraint.
SCANNED = [
    ROOT / "backend",
    ROOT / "frontend" / "src",
    ROOT / "tests",
    ROOT / "Start Narrative Lens.bat",
    ROOT / "run_checks.sh",
    ROOT / "PROGRESS.md",
    ROOT / "LATEST.md",
]

TEXT_SUFFIXES = {".py", ".js", ".jsx", ".css", ".html", ".md", ".bat", ".sh", ".json", ".toml"}


def _files() -> list[Path]:
    found: list[Path] = []
    for target in SCANNED:
        if target.is_file():
            found.append(target)
        else:
            found.extend(
                path
                for path in target.rglob("*")
                if path.is_file()
                and path.suffix in TEXT_SUFFIXES
                and "__pycache__" not in path.parts
                and path.name != Path(__file__).name
            )
    return found


@pytest.mark.parametrize("path", _files(), ids=lambda p: str(p.relative_to(ROOT)))
def test_no_reserved_name_appears_in_the_app(path: Path) -> None:
    body = path.read_text(encoding="utf-8", errors="ignore")

    for name in RESERVED:
        assert name not in body, f"{path.relative_to(ROOT)} contains '{name}'"


def test_the_readme_carries_exactly_one_attribution() -> None:
    """Criterion 15 allows one attribution. One, not none — it is owed.

    Counted in paragraphs rather than in newlines: the attribution is a wrapped
    sentence, and where a line happens to break is a fact about the text editor
    rather than about how many times the app names somebody else's product.
    """
    body = (ROOT / "README.md").read_text(encoding="utf-8")
    paragraphs = [block for block in body.split("\n\n") if any(n in block for n in RESERVED)]

    assert len(paragraphs) == 1, paragraphs
    assert "trademark" in paragraphs[0]
    assert "not affiliated" in paragraphs[0]
    # And it is the last word in the file, not a claim made up front.
    assert body.rstrip().endswith(paragraphs[0].rstrip())


def test_the_app_calls_itself_narrative_lens() -> None:
    from backend.main import app

    body = (ROOT / "README.md").read_text(encoding="utf-8")

    assert app.title == "Narrative Lens"
    assert body.startswith("# Narrative Lens")
