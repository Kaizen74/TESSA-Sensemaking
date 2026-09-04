/*
 * Paper batch entry (PRD §1.2, §5.2, §7.5).
 *
 * A transcription desk, not a wizard. Everything for one returned sheet is on
 * one screen: the story, then every widget. Enter advances; the running count
 * tells the operator how far through the pile they are. Built for entering 30
 * workshop responses in one sitting, and measured by §7.5 — five fixture
 * responses in under four minutes.
 *
 * Every record is stamped input_method=paper. The operator is transcribing
 * someone else's marks, so the interpretation is still the respondent's; the
 * input method is what records that it came off paper.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { api, ApiError } from "../api.js";
import { SignifierWidget } from "../widgets/Widgets.jsx";
import { orderedSignifiers } from "../studio/PhonePreview.jsx";
import {
  MAX_RESPONDENT_TITLE_CHARS,
  STORY_NAME_PROMPT,
  toSubmission,
} from "./Wizard.jsx";
import "./paper-batch.css";

export function PaperBatch({ framework }) {
  const definition = framework.definition;
  const groups = definition.capture_settings?.respondent_groups ?? [];
  const signifiers = orderedSignifiers(definition);

  const [text, setText] = useState("");
  // The name line on the returned card, when the person filling it in wrote one.
  const [respondentTitle, setRespondentTitle] = useState("");
  const [values, setValues] = useState({});
  const [group, setGroup] = useState(null);
  const [entered, setEntered] = useState(0);
  const [lastSaved, setLastSaved] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const storyRef = useRef(null);

  const canSave = Boolean(text.trim()) && !busy;

  const save = useCallback(async () => {
    if (!text.trim() || busy) return;
    setBusy(true);
    setError(null);
    try {
      const result = await api.capture({
        framework_id: framework.id,
        text,
        respondent_title: respondentTitle.trim() || null,
        input_method: "paper",
        respondent_group: group,
        significations: toSubmission(definition, values),
      });
      setEntered((count) => count + 1);
      setLastSaved(result.anecdote_id);
      // Clear for the next sheet, but keep the group: a pile of sheets from one
      // session is usually one group, and retyping it 30 times is wasted effort.
      setText("");
      setRespondentTitle("");
      setValues({});
      storyRef.current?.focus();
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : null);
    } finally {
      setBusy(false);
    }
  }, [text, respondentTitle, busy, framework.id, group, definition, values]);

  // Enter advances from anywhere on the screen. The story field needs real
  // newlines, so there it takes Ctrl/Cmd+Enter instead.
  useEffect(() => {
    function onKeyDown(event) {
      if (event.key !== "Enter") return;
      const inStoryField = event.target === storyRef.current;
      if (inStoryField && !(event.metaKey || event.ctrlKey)) return;
      if (event.target.tagName === "BUTTON") return;
      event.preventDefault();
      save();
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [save]);

  return (
    <div className="nl-batch">
      <header className="nl-batch__head">
        <div>
          <h2 className="nl-batch__title">Paper entry</h2>
          <p className="nl-batch__sub">
            One returned sheet per entry. Type the story, mark each scale where the
            respondent marked it, then press Enter. In the story box, press Ctrl+Enter.
          </p>
        </div>
        <div className="nl-batch__count" role="status" aria-live="polite">
          <span className="nl-numeric nl-batch__count-value">{entered}</span>
          <span className="nl-batch__count-label">
            entered this sitting
            {lastSaved !== null && (
              <span className="nl-batch__count-last"> · last saved #{lastSaved}</span>
            )}
          </span>
        </div>
      </header>

      {error && (
        <div className="nl-batch__error" role="alert">
          <p className="nl-batch__error-message">{error.message}</p>
          {error.action && <p className="nl-batch__error-action">{error.action}</p>}
        </div>
      )}

      <label className="nl-batch__label" htmlFor="nl-batch-story">
        The story, as written on the card
      </label>
      <textarea
        id="nl-batch-story"
        ref={storyRef}
        className="nl-batch__textarea"
        rows={5}
        value={text}
        onChange={(event) => setText(event.target.value)}
        placeholder="Type or paste what they wrote…"
      />

      {/* The card's own name line (delta §5). Blank on most sheets, and that is
          the normal case, not a gap to chase up. */}
      <label className="nl-batch__label" htmlFor="nl-batch-story-name">
        {STORY_NAME_PROMPT}
      </label>
      <input
        id="nl-batch-story-name"
        type="text"
        className="nl-batch__input"
        maxLength={MAX_RESPONDENT_TITLE_CHARS}
        value={respondentTitle}
        onChange={(event) => setRespondentTitle(event.target.value)}
        placeholder="Leave blank if the card has no name on it"
      />

      {groups.length > 0 && (
        <div className="nl-batch__groups">
          <span className="nl-batch__label">Group ticked on the card</span>
          <div className="nl-batch__group-row">
            {groups.map((option) => (
              <button
                key={option}
                type="button"
                className={
                  group === option
                    ? "nl-batch__group nl-batch__group--selected"
                    : "nl-batch__group"
                }
                aria-pressed={group === option}
                onClick={() => setGroup(group === option ? null : option)}
              >
                {option}
              </button>
            ))}
          </div>
          <p className="nl-batch__hint">Kept between entries — most piles are one group.</p>
        </div>
      )}

      <div className="nl-batch__widgets">
        {signifiers.map(({ kind, signifier }) => (
          <div className="nl-batch__widget" key={signifier.id}>
            <SignifierWidget
              kind={kind}
              signifier={signifier}
              value={values[signifier.id] ?? null}
              onChange={(value) => setValues((current) => ({ ...current, [signifier.id]: value }))}
            />
          </div>
        ))}
      </div>

      <div className="nl-batch__actions">
        <button type="button" className="nl-batch__save" disabled={!canSave} onClick={save}>
          {busy ? "Saving…" : "Save and next  ⏎"}
        </button>
        <button
          type="button"
          className="nl-batch__clear"
          onClick={() => {
            setText("");
            setValues({});
            storyRef.current?.focus();
          }}
        >
          Clear this sheet
        </button>
      </div>
    </div>
  );
}
