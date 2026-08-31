/*
 * The guardrail dialog (PRD §1.1, constraint 13g).
 *
 * Appears on any save to a framework that already has stories. The two choices
 * are described in terms of consequences, not mechanics: the operator is
 * choosing what happens to the stories already collected, and the wording says
 * so. There is no default and no pre-selected button — this is a decision, and
 * PRD §9 assumption 12 puts it squarely with the operator.
 */

import { useEffect, useRef } from "react";
import "./dialog.css";

export function EditKindDialog({ storyCount, onChoose, onCancel, busy }) {
  const firstButton = useRef(null);

  useEffect(() => {
    firstButton.current?.focus();
  }, []);

  useEffect(() => {
    function onKeyDown(event) {
      if (event.key === "Escape") onCancel();
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [onCancel]);

  const storyWord = storyCount === 1 ? "story" : "stories";

  return (
    <div className="nl-dialog__backdrop" role="presentation">
      <div
        className="nl-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="nl-dialog-title"
        aria-describedby="nl-dialog-body"
      >
        <h2 id="nl-dialog-title" className="nl-dialog__title">
          This framework already has {storyCount} {storyWord}
        </h2>
        <p id="nl-dialog-body" className="nl-dialog__body">
          People answered the words that are saved now. Tell Narrative Lens what kind of
          change you just made, so those answers stay honest.
        </p>

        <div className="nl-dialog__choices">
          <button
            type="button"
            ref={firstButton}
            className="nl-dialog__choice"
            disabled={busy}
            onClick={() => onChoose("wording_fix")}
          >
            <span className="nl-dialog__choice-title">Fix wording</span>
            <span className="nl-dialog__choice-detail">
              A typo, or the same question said more clearly. The change applies now, and
              goes in this version&apos;s edit log so you can see what changed later.
            </span>
          </button>

          <button
            type="button"
            className="nl-dialog__choice"
            disabled={busy}
            onClick={() => onChoose("meaning_change")}
          >
            <span className="nl-dialog__choice-title">Change meaning</span>
            <span className="nl-dialog__choice-detail">
              You are asking something different now. This starts version n+1. Your{" "}
              {storyCount} {storyWord} stay attached to the words people actually saw, and
              new responses use the new wording.
            </span>
          </button>
        </div>

        <button type="button" className="nl-dialog__cancel" onClick={onCancel} disabled={busy}>
          Keep editing
        </button>
      </div>
    </div>
  );
}
