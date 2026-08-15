"""Voice fallback (PRD §6 Phase 4, §7.12, constraint 10).

Constraint 10 says voice is *always paired with typing*, and §7.12 says voice
must fail plain-English with a working fallback. Both are properties of
``frontend/src/capture/voice.js``, so they are exercised there in Node rather
than reimplemented in Python.

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

#: A stand-in for the browser's SpeechRecognition, driveable from a test.
FAKE_RECOGNITION = """
class FakeRecognition {
  constructor() { FakeRecognition.last = this; this.started = false; }
  start() { this.started = true; }
  stop() { this.started = false; this.onend?.(); }
  emitFinal(text) {
    this.onresult({ resultIndex: 0, results: [{ isFinal: true, 0: { transcript: text } }] });
  }
  emitError(code) { this.onerror({ error: code }); }
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


class TestFallbackMessages:
    """§7.12: voice fails plain-English with a working fallback."""

    def test_every_failure_names_typing_as_the_way_forward(self) -> None:
        script = """
import { voiceFailureMessage, VOICE_UNSUPPORTED, VOICE_DENIED, VOICE_NO_SPEECH,
         VOICE_NETWORK, VOICE_FAILED } from './voice.js';
const reasons = [VOICE_UNSUPPORTED, VOICE_DENIED, VOICE_NO_SPEECH, VOICE_NETWORK,
                 VOICE_FAILED];
console.log(JSON.stringify(reasons.map((r) => voiceFailureMessage(r))));
"""
        for failure in _run_node(script):
            combined = f"{failure['message']} {failure['action']}".lower()
            assert "typ" in combined, f"no typing fallback offered: {failure}"

    def test_messages_are_plain_english(self) -> None:
        """Constraint 7: no jargon a respondent cannot act on."""
        script = """
import { voiceFailureMessage, VOICE_UNSUPPORTED, VOICE_DENIED, VOICE_NO_SPEECH,
         VOICE_NETWORK, VOICE_FAILED } from './voice.js';
const reasons = [VOICE_UNSUPPORTED, VOICE_DENIED, VOICE_NO_SPEECH, VOICE_NETWORK,
                 VOICE_FAILED];
console.log(JSON.stringify(reasons.map((r) => voiceFailureMessage(r))));
"""
        for failure in _run_node(script):
            assert failure["message"].endswith(".")
            assert failure["action"]
            for jargon in (
                "SpeechRecognition",
                "webkit",
                "undefined",
                "null",
                "Error",
                "API",
            ):
                assert jargon not in failure["message"]
                assert jargon not in failure["action"]

    def test_an_unknown_reason_still_gets_a_usable_message(self) -> None:
        """No failure path may leave a respondent with a blank screen."""
        script = """
import { voiceFailureMessage } from './voice.js';
console.log(JSON.stringify(voiceFailureMessage('something-nobody-anticipated')));
"""
        failure = _run_node(script)
        assert failure["message"]
        assert "typ" in failure["action"].lower()


class TestUnsupportedBrowser:
    def test_voice_is_reported_unsupported_rather_than_crashing(self) -> None:
        script = """
import { isVoiceSupported, startDictation, VOICE_UNSUPPORTED } from './voice.js';
const win = {};
let reason = null;
const handle = startDictation({ win, onError: (r) => { reason = r; } });
console.log(JSON.stringify({
  supported: isVoiceSupported(win),
  reason,
  active: handle.active,
}));
"""
        result = _run_node(script)

        assert result["supported"] is False
        assert result["reason"] == "unsupported"
        assert result["active"] is False

    def test_stopping_an_unstarted_handle_is_harmless(self) -> None:
        """The UI calls stop() on unmount whether or not voice ever started."""
        script = """
import { startDictation } from './voice.js';
const handle = startDictation({ win: {}, onError: () => {} });
handle.stop();
handle.stop();
console.log(JSON.stringify({ ok: true }));
"""
        assert _run_node(script)["ok"] is True

    def test_a_recogniser_that_throws_on_construction_is_caught(self) -> None:
        script = """
import { startDictation, VOICE_FAILED } from './voice.js';
class Exploding { constructor() { throw new Error('no'); } }
let reason = null;
const handle = startDictation({
  win: { SpeechRecognition: Exploding },
  onError: (r) => { reason = r; },
});
console.log(JSON.stringify({ reason, active: handle.active }));
"""
        result = _run_node(script)

        assert result["reason"] == "failed"
        assert result["active"] is False

    def test_a_recogniser_that_throws_on_start_is_caught(self) -> None:
        script = """
import { startDictation } from './voice.js';
class WontStart { start() { throw new Error('nope'); } stop() {} }
let reason = null;
const handle = startDictation({
  win: { SpeechRecognition: WontStart },
  onError: (r) => { reason = r; },
});
console.log(JSON.stringify({ reason, active: handle.active }));
"""
        result = _run_node(script)

        assert result["reason"] == "failed"
        assert result["active"] is False


class TestErrorMapping:
    @pytest.mark.parametrize(
        ("browser_code", "expected"),
        [
            ("not-allowed", "denied"),
            ("service-not-allowed", "denied"),
            ("no-speech", "no-speech"),
            ("network", "network"),
            ("audio-capture", "failed"),
        ],
    )
    def test_browser_errors_map_to_actionable_reasons(
        self, browser_code: str, expected: str
    ) -> None:
        script = f"""
import {{ startDictation }} from './voice.js';
{FAKE_RECOGNITION}
let reason = null;
startDictation({{
  win: {{ SpeechRecognition: FakeRecognition }},
  onError: (r) => {{ reason = r; }},
}});
FakeRecognition.last.emitError('{browser_code}');
console.log(JSON.stringify({{ reason }}));
"""
        assert _run_node(script)["reason"] == expected

    def test_an_aborted_session_ends_quietly_rather_than_erroring(self) -> None:
        """Stopping on purpose is not a failure and must not show a warning."""
        script = f"""
import {{ startDictation }} from './voice.js';
{FAKE_RECOGNITION}
let reason = null;
let ended = false;
startDictation({{
  win: {{ SpeechRecognition: FakeRecognition }},
  onError: (r) => {{ reason = r; }},
  onEnd: () => {{ ended = true; }},
}});
FakeRecognition.last.emitError('aborted');
console.log(JSON.stringify({{ reason, ended }}));
"""
        result = _run_node(script)

        assert result["reason"] is None
        assert result["ended"] is True


class TestVoicePairedWithTyping:
    """Constraint 10: voice always paired with typing."""

    def test_dictation_appends_rather_than_replacing(self) -> None:
        script = """
import { appendDictation } from './voice.js';
console.log(JSON.stringify({
  ontoTyped: appendDictation('I typed this first', 'and then I said this'),
  ontoEmpty: appendDictation('', 'just spoken'),
  ontoSentence: appendDictation('Ends with a full stop.', 'Next sentence'),
  emptyAddition: appendDictation('Unchanged', '   '),
  nothingAtAll: appendDictation(null, null),
}));
"""
        result = _run_node(script)

        assert result["ontoTyped"] == "I typed this first. and then I said this"
        assert result["ontoEmpty"] == "just spoken"
        assert result["ontoSentence"] == "Ends with a full stop. Next sentence"
        assert result["emptyAddition"] == "Unchanged", "typed words must never be lost"
        assert result["nothingAtAll"] == ""

    def test_only_settled_phrases_are_delivered(self) -> None:
        """Interim results would rewrite a respondent's words as they speak."""
        script = f"""
import {{ startDictation }} from './voice.js';
{FAKE_RECOGNITION}
const heard = [];
startDictation({{
  win: {{ SpeechRecognition: FakeRecognition }},
  onText: (t) => heard.push(t),
}});
const r = FakeRecognition.last;
console.log(JSON.stringify({{ interimResults: r.interimResults, continuous: r.continuous }}));
"""
        result = _run_node(script)

        assert result["interimResults"] is False
        assert result["continuous"] is True

    def test_spoken_text_arrives_as_finalised_phrases(self) -> None:
        script = f"""
import {{ startDictation }} from './voice.js';
{FAKE_RECOGNITION}
const heard = [];
startDictation({{
  win: {{ SpeechRecognition: FakeRecognition }},
  onText: (t) => heard.push(t),
}});
FakeRecognition.last.emitFinal('the inbound was early');
FakeRecognition.last.emitFinal('nobody had the paperwork');
console.log(JSON.stringify({{ heard }}));
"""
        assert _run_node(script)["heard"] == [
            "the inbound was early",
            "nobody had the paperwork",
        ]
