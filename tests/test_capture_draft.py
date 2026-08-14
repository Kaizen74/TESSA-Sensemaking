"""Drafts survive a reload (PRD §6 Phase 3, §7.6).

The draft lives in the browser, so the behaviour is exercised in Node against
the real module rather than reimplemented in Python. A "reload" is modelled the
way a browser does one: the module's own state goes away, the storage does not.

Skipped where Node is unavailable, so the Python suite still runs anywhere.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

NODE = shutil.which("node")
CAPTURE_DIR = Path(__file__).resolve().parent.parent / "frontend" / "src" / "capture"

pytestmark = pytest.mark.skipif(
    NODE is None or not CAPTURE_DIR.exists(),
    reason="Node or the frontend capture module is not available",
)

#: A minimal stand-in for window.localStorage, including its string coercion.
FAKE_STORAGE = """
class FakeStorage {
  constructor() { this.map = new Map(); }
  getItem(k) { return this.map.has(k) ? this.map.get(k) : null; }
  setItem(k, v) { this.map.set(k, String(v)); }
  removeItem(k) { this.map.delete(k); }
  get size() { return this.map.size; }
}
"""


def _run_node(script: str):
    result = subprocess.run(
        [NODE, "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=CAPTURE_DIR,
    )
    if result.returncode != 0:
        raise AssertionError(f"node failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


def test_a_draft_written_before_a_reload_is_read_back_after_it() -> None:
    """The whole point: a half-written story survives the page going away."""
    script = f"""
import {{ saveDraft, loadDraft }} from './draft.js';
{FAKE_STORAGE}
const storage = new FakeStorage();

// Before the reload: the respondent has typed and placed something.
saveDraft(storage, 7, {{
  text: 'The inbound was early and nobody had the paperwork.',
  values: {{ pressure: [0.5, 0.3, 0.2], clarity: 0.75 }},
  respondentGroup: 'Ramp',
  step: 3,
}});

// The reload: page state is gone, storage is not.
const recovered = loadDraft(storage, 7);
console.log(JSON.stringify(recovered));
"""
    recovered = _run_node(script)

    assert recovered["text"] == "The inbound was early and nobody had the paperwork."
    assert recovered["values"]["pressure"] == [0.5, 0.3, 0.2]
    assert recovered["values"]["clarity"] == 0.75
    assert recovered["respondentGroup"] == "Ramp"
    assert recovered["step"] == 3


def test_drafts_are_kept_per_framework_version() -> None:
    """Answering a new version must not resurrect the old version's draft."""
    script = f"""
import {{ saveDraft, loadDraft }} from './draft.js';
{FAKE_STORAGE}
const storage = new FakeStorage();
saveDraft(storage, 1, {{ text: 'Story for v1', values: {{}}, respondentGroup: null, step: 1 }});
saveDraft(storage, 2, {{ text: 'Story for v2', values: {{}}, respondentGroup: null, step: 1 }});
console.log(JSON.stringify({{
  one: loadDraft(storage, 1).text,
  two: loadDraft(storage, 2).text,
  missing: loadDraft(storage, 3),
}}));
"""
    result = _run_node(script)

    assert result["one"] == "Story for v1"
    assert result["two"] == "Story for v2"
    assert result["missing"] is None


def test_submitting_clears_the_draft() -> None:
    """Nothing lingers once the story has been sent."""
    script = f"""
import {{ saveDraft, loadDraft, clearDraft }} from './draft.js';
{FAKE_STORAGE}
const storage = new FakeStorage();
saveDraft(storage, 5, {{ text: 'Sent already', values: {{}}, respondentGroup: null, step: 4 }});
clearDraft(storage, 5);
console.log(JSON.stringify({{ after: loadDraft(storage, 5), size: storage.size }}));
"""
    result = _run_node(script)

    assert result["after"] is None
    assert result["size"] == 0


def test_a_corrupt_draft_is_ignored_rather_than_thrown() -> None:
    """Starting fresh is recoverable; crashing on load is not."""
    script = f"""
import {{ loadDraft, draftKey }} from './draft.js';
{FAKE_STORAGE}
const storage = new FakeStorage();
storage.setItem(draftKey(9), '{{not valid json');
const first = loadDraft(storage, 9);
storage.setItem(draftKey(9), '"just a string"');
const second = loadDraft(storage, 9);
storage.setItem(draftKey(9), '[1,2,3]');
const third = loadDraft(storage, 9);
console.log(JSON.stringify({{ first, second, third }}));
"""
    result = _run_node(script)

    assert result["first"] is None
    assert result["second"] is None
    assert result["third"] is None


def test_a_partial_draft_is_filled_in_with_safe_defaults() -> None:
    """A draft from an older shape must not crash the wizard."""
    script = f"""
import {{ loadDraft, draftKey }} from './draft.js';
{FAKE_STORAGE}
const storage = new FakeStorage();
storage.setItem(draftKey(4), JSON.stringify({{ text: 'Only text survived' }}));
console.log(JSON.stringify(loadDraft(storage, 4)));
"""
    recovered = _run_node(script)

    assert recovered["text"] == "Only text survived"
    assert recovered["values"] == {}
    assert recovered["respondentGroup"] is None
    assert recovered["step"] == 0


def test_capture_still_works_when_storage_is_unavailable() -> None:
    """Private browsing must not stop someone telling their story."""
    script = f"""
import {{ saveDraft, loadDraft, clearDraft }} from './draft.js';
{FAKE_STORAGE}
class ThrowingStorage {{
  getItem() {{ throw new Error('denied'); }}
  setItem() {{ throw new Error('denied'); }}
  removeItem() {{ throw new Error('denied'); }}
}}
const blocked = new ThrowingStorage();
const saved = saveDraft(blocked, 1, {{ text: 'x', values: {{}}, respondentGroup: null, step: 0 }});
const loaded = loadDraft(blocked, 1);
clearDraft(blocked, 1);
const nothing = saveDraft(null, 1, {{ text: 'x', values: {{}}, respondentGroup: null, step: 0 }});
console.log(JSON.stringify({{ saved, loaded, nothing }}));
"""
    result = _run_node(script)

    assert result["saved"] is False
    assert result["loaded"] is None
    assert result["nothing"] is False


def test_the_storage_key_carries_no_respondent_identifier() -> None:
    """Constraint 9 reaches into the browser, not just the database."""
    script = f"""
import {{ draftKey }} from './draft.js';
{FAKE_STORAGE}
console.log(JSON.stringify({{ key: draftKey(12) }}));
"""
    key = _run_node(script)["key"]

    assert "12" in key
    for identifier in ("user", "session", "device", "id=", "uuid", "fingerprint"):
        assert identifier not in key.lower()


def test_draft_content_check_ignores_an_untouched_form() -> None:
    """Offering to restore an empty draft would be noise."""
    script = f"""
import {{ draftHasContent, emptyDraft }} from './draft.js';
{FAKE_STORAGE}
console.log(JSON.stringify({{
  empty: draftHasContent(emptyDraft()),
  whitespace: draftHasContent({{ text: '   ', values: {{}} }}),
  withText: draftHasContent({{ text: 'Something', values: {{}} }}),
  withPlacement: draftHasContent({{ text: '', values: {{ clarity: 0.5 }} }}),
  nothing: draftHasContent(null),
}}));
"""
    result = _run_node(script)

    assert result["empty"] is False
    assert result["whitespace"] is False
    assert result["withText"] is True
    assert result["withPlacement"] is True
    assert result["nothing"] is False
