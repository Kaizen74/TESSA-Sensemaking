/*
 * The capture wizard (PRD §5a, constraint 10).
 *
 * One friendly screen at a time: welcome → story → one signifier per screen →
 * group → reflection → thank you. Phase 3 runs it locally in admin mode; Phase 4
 * points the same wizard at remote links and kiosk, which is why the entry mode
 * is not baked in here.
 *
 * Constraint 10 is the bar this component is built to:
 *   ≤4 minutes typical · 375px-clean · tap targets ≥44px · visible progress ·
 *   honest time promise · reflection on by default.
 *
 * Voice is Phase 4; the typing path is built first so that voice can be added
 * as a companion to it rather than a replacement (constraint 10: voice always
 * paired with typing).
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { api, ApiError } from "../api.js";
import { SignifierWidget } from "../widgets/Widgets.jsx";
import { orderedSignifiers } from "../studio/PhonePreview.jsx";
import { clearDraft, draftHasContent, loadDraft, saveDraft } from "./draft.js";
import "./wizard.css";

const STEP_WELCOME = "welcome";
const STEP_STORY = "story";
const STEP_SIGNIFIER = "signifier";
const STEP_GROUP = "group";
const STEP_REFLECTION = "reflection";
const STEP_DONE = "done";

function browserStorage() {
  try {
    return typeof window === "undefined" ? null : window.localStorage;
  } catch {
    return null;
  }
}

/** Every screen this framework produces, in order. */
export function buildSteps(definition) {
  const steps = [{ kind: STEP_WELCOME }, { kind: STEP_STORY }];
  orderedSignifiers(definition).forEach(({ kind, signifier }) =>
    steps.push({ kind: STEP_SIGNIFIER, signifierKind: kind, signifier }),
  );
  if ((definition.capture_settings?.respondent_groups ?? []).length > 0) {
    steps.push({ kind: STEP_GROUP });
  }
  if (definition.capture_settings?.reflection_enabled) {
    steps.push({ kind: STEP_REFLECTION });
  }
  steps.push({ kind: STEP_DONE });
  return steps;
}

/** Placements in the shape the server expects. */
export function toSubmission(definition, values) {
  const submission = [];
  orderedSignifiers(definition).forEach(({ kind, signifier }) => {
    const value = values[signifier.id];
    if (value === undefined || value === null) return;

    if (kind === "triad") {
      const [a, b, c] = value;
      submission.push({
        signifier_id: signifier.id,
        value: {
          [signifier.corners[0]]: a,
          [signifier.corners[1]]: b,
          [signifier.corners[2]]: c,
        },
      });
    } else if (kind === "dyad") {
      submission.push({ signifier_id: signifier.id, value: { value } });
    } else if (kind === "stones") {
      if (value.length === 0) return;
      submission.push({ signifier_id: signifier.id, value: { placements: value } });
    } else if (kind === "mcq") {
      if ((value.selected ?? []).length === 0) return;
      submission.push({ signifier_id: signifier.id, value });
    }
  });
  return submission;
}

export function Wizard({ framework, onFinished = null }) {
  const definition = framework.definition;
  const settings = definition.capture_settings ?? {};
  const storage = browserStorage();

  const steps = useMemo(() => buildSteps(definition), [definition]);

  const [index, setIndex] = useState(0);
  const [text, setText] = useState("");
  const [values, setValues] = useState({});
  const [group, setGroup] = useState(null);
  const [restorable, setRestorable] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  //: True from the instant a submission succeeds, so no later navigation can
  //  write the draft back. State would lag by a render; this cannot.
  const submittedRef = useRef(false);

  // On arrival, offer to pick up an unfinished story rather than silently
  // reinstating it — the respondent should know what happened.
  useEffect(() => {
    const found = loadDraft(storage, framework.id);
    if (draftHasContent(found)) setRestorable(found);
    // Only on mount, and only for this framework version.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [framework.id]);

  const persist = useCallback(
    (next) => {
      // Once the story is sent there is nothing left to recover, and rewriting
      // the draft here would leave the next visitor being offered a story that
      // has already been submitted — and could submit it twice. A ref, not
      // state: this is read in the same handler that does the submitting, and
      // a state update would not have landed yet.
      if (submittedRef.current) return;
      saveDraft(storage, framework.id, {
        text: next.text ?? text,
        values: next.values ?? values,
        respondentGroup: next.respondentGroup ?? group,
        step: next.step ?? index,
      });
    },
    [storage, framework.id, text, values, group, index],
  );

  const step = steps[Math.min(index, steps.length - 1)];
  // Welcome and thank-you are not work; progress counts the screens that are.
  const workingSteps = steps.filter(
    (s) => s.kind !== STEP_WELCOME && s.kind !== STEP_DONE,
  ).length;
  const workingIndex = Math.max(0, Math.min(index, workingSteps));

  function go(nextIndex) {
    const clamped = Math.max(0, Math.min(nextIndex, steps.length - 1));
    setIndex(clamped);
    persist({ step: clamped });
  }

  function setValue(signifierId, value) {
    const next = { ...values, [signifierId]: value };
    setValues(next);
    persist({ values: next });
  }

  function restore() {
    setText(restorable.text);
    setValues(restorable.values);
    setGroup(restorable.respondentGroup);
    setIndex(Math.min(restorable.step, steps.length - 1));
    setRestorable(null);
  }

  function discard() {
    clearDraft(storage, framework.id);
    setRestorable(null);
  }

  async function submit() {
    setBusy(true);
    setError(null);
    try {
      const submitted = await api.capture({
        framework_id: framework.id,
        text,
        input_method: "typed",
        respondent_group: group,
        significations: toSubmission(definition, values),
      });
      submittedRef.current = true;
      clearDraft(storage, framework.id);
      setResult(submitted);
      go(steps.length - (settings.reflection_enabled ? 2 : 1));
      onFinished?.(submitted);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : null);
    } finally {
      setBusy(false);
    }
  }

  function startAgain() {
    submittedRef.current = false;
    setText("");
    setValues({});
    setGroup(null);
    setResult(null);
    setError(null);
    clearDraft(storage, framework.id);
    setIndex(0);
  }

  if (restorable) {
    return (
      <div className="nl-wizard">
        <section className="nl-wizard__screen">
          <h2 className="nl-wizard__heading">You have a story in progress</h2>
          <p className="nl-wizard__body">
            You started writing on this device and did not finish. Pick up where you left
            off, or start again.
          </p>
          <div className="nl-wizard__actions">
            <button type="button" className="nl-wizard__next" onClick={restore}>
              Pick up where I left off
            </button>
            <button type="button" className="nl-wizard__back" onClick={discard}>
              Start again
            </button>
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="nl-wizard">
      {step.kind !== STEP_WELCOME && step.kind !== STEP_DONE && (
        <div className="nl-wizard__progress">
          <div
            className="nl-wizard__progress-bar"
            role="progressbar"
            aria-valuemin={1}
            aria-valuemax={workingSteps}
            aria-valuenow={workingIndex}
            aria-label={`Screen ${workingIndex} of ${workingSteps}`}
          >
            <span
              className="nl-wizard__progress-fill"
              style={{ width: `${(workingIndex / workingSteps) * 100}%` }}
            />
          </div>
          <p className="nl-wizard__progress-text nl-numeric">
            {workingIndex} of {workingSteps}
          </p>
        </div>
      )}

      {error && (
        <div className="nl-wizard__error" role="alert">
          <p className="nl-wizard__error-message">{error.message}</p>
          {error.action && <p className="nl-wizard__error-action">{error.action}</p>}
        </div>
      )}

      {step.kind === STEP_WELCOME && (
        <section className="nl-wizard__screen">
          <h2 className="nl-wizard__heading">{settings.welcome_text}</h2>
          <p className="nl-wizard__promise">{settings.time_promise_text}</p>
          <p className="nl-wizard__anonymity">{settings.anonymity_text}</p>
          <button type="button" className="nl-wizard__next" onClick={() => go(1)}>
            Start
          </button>
        </section>
      )}

      {step.kind === STEP_STORY && (
        <section className="nl-wizard__screen">
          <h2 className="nl-wizard__heading">{definition.prompt_text}</h2>
          {definition.prompt_text_alt && (
            <p className="nl-wizard__alt">Or: {definition.prompt_text_alt}</p>
          )}
          <label className="nl-visually-hidden" htmlFor="nl-story">
            Your story
          </label>
          <textarea
            id="nl-story"
            className="nl-wizard__textarea"
            rows={8}
            value={text}
            onChange={(event) => {
              setText(event.target.value);
              persist({ text: event.target.value });
            }}
            placeholder="In your own words…"
          />
          <div className="nl-wizard__actions">
            <button type="button" className="nl-wizard__back" onClick={() => go(index - 1)}>
              Back
            </button>
            <button
              type="button"
              className="nl-wizard__next"
              disabled={!text.trim()}
              onClick={() => go(index + 1)}
            >
              Next
            </button>
          </div>
        </section>
      )}

      {step.kind === STEP_SIGNIFIER && (
        <section className="nl-wizard__screen">
          <SignifierWidget
            kind={step.signifierKind}
            signifier={step.signifier}
            value={values[step.signifier.id] ?? null}
            onChange={(value) => setValue(step.signifier.id, value)}
          />
          <div className="nl-wizard__actions">
            <button type="button" className="nl-wizard__back" onClick={() => go(index - 1)}>
              Back
            </button>
            <button type="button" className="nl-wizard__next" onClick={() => go(index + 1)}>
              {values[step.signifier.id] === undefined ? "Skip" : "Next"}
            </button>
          </div>
        </section>
      )}

      {step.kind === STEP_GROUP && (
        <section className="nl-wizard__screen">
          <h2 className="nl-wizard__heading">Which group are you in?</h2>
          <ul className="nl-wizard__groups">
            {(settings.respondent_groups ?? []).map((option) => (
              <li key={option}>
                <button
                  type="button"
                  className={
                    group === option
                      ? "nl-wizard__group nl-wizard__group--selected"
                      : "nl-wizard__group"
                  }
                  aria-pressed={group === option}
                  onClick={() => {
                    const next = group === option ? null : option;
                    setGroup(next);
                    persist({ respondentGroup: next });
                  }}
                >
                  {option}
                </button>
              </li>
            ))}
          </ul>
          <div className="nl-wizard__actions">
            <button type="button" className="nl-wizard__back" onClick={() => go(index - 1)}>
              Back
            </button>
            <button
              type="button"
              className="nl-wizard__next"
              disabled={busy}
              onClick={submit}
            >
              {busy ? "Sending…" : "Send my story"}
            </button>
          </div>
        </section>
      )}

      {step.kind === STEP_REFLECTION && (
        <section className="nl-wizard__screen">
          <h2 className="nl-wizard__heading">Here is where your story sits</h2>
          <ReflectionPanel definition={definition} values={values} result={result} />
          <button
            type="button"
            className="nl-wizard__next"
            onClick={() => go(steps.length - 1)}
          >
            Done
          </button>
        </section>
      )}

      {step.kind === STEP_DONE && (
        <section className="nl-wizard__screen">
          <h2 className="nl-wizard__heading">
            {result?.thankyou_text ?? settings.thankyou_text}
          </h2>
          <p className="nl-wizard__anonymity">{settings.anonymity_text}</p>
          <button type="button" className="nl-wizard__next" onClick={startAgain}>
            Add another story
          </button>
        </section>
      )}

      {/* The story screen is the only one that must be reached before sending,
          so signifier screens carry the send button too. */}
      {step.kind === STEP_SIGNIFIER && index === steps.length - 2 && !settings.reflection_enabled && (
        <button type="button" className="nl-wizard__next" disabled={busy} onClick={submit}>
          {busy ? "Sending…" : "Send my story"}
        </button>
      )}
    </div>
  );
}

/**
 * Reflection (PRD §9 assumption 7: shows one signifier).
 *
 * Shows the respondent their own placement on the first signifier they answered.
 * It does not show anyone else's: the aggregate views arrive in Phases 7–8, and
 * showing a half-built picture would be worse than showing their own mark.
 */
function ReflectionPanel({ definition, values, result }) {
  const answered = orderedSignifiers(definition).find(
    ({ signifier }) => values[signifier.id] !== undefined && values[signifier.id] !== null,
  );

  if (!answered) {
    return (
      <p className="nl-wizard__body">
        Your story is saved. You skipped the scales, so there is no mark to show.
      </p>
    );
  }

  return (
    <>
      <SignifierWidget
        kind={answered.kind}
        signifier={answered.signifier}
        value={values[answered.signifier.id]}
      />
      <p className="nl-wizard__body">
        That is your mark on “{answered.signifier.title}”.
        {result ? " Your story has joined the others." : ""}
      </p>
    </>
  );
}
