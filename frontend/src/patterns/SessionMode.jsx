/*
 * Session mode: a room reading its own landscape (delta §5, phase D).
 *
 * The landscape at full screen with the controls gone, and a side panel where
 * somebody types what the room concludes. It is the one view in this app built
 * for a projector rather than a desk, which is why everything that helps at a
 * desk — filters, exports, sub-navigation — is deliberately absent here. The
 * picture is the thing on the wall; the panel is the person at the laptop.
 *
 * Constraint 16 is the rule this component is built around, and the way it
 * shows up in the UI is in what recording *does not do*. Nothing here changes
 * the terrain. The landscape on screen when a room writes its conclusion is the
 * same landscape afterwards, byte for byte — and the panel says so out loud,
 * because a facilitator watching a sentence be saved next to a picture will
 * reasonably wonder whether it changed the picture.
 *
 * The filter state and the signifier are captured from what is on screen rather
 * than typed. Asking a facilitator to write down which filters were in force,
 * in front of a room, is asking them to get it wrong.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { api, ApiError } from "../api.js";
import { LandscapeView } from "./Landscape.jsx";

/** How long the "saved" acknowledgement stays up before it stops being news. */
const SAVED_MS = 4000;

export function SessionMode({
  framework,
  land,
  view,
  triadId,
  filters,
  onClose,
  onRecorded,
}) {
  const [text, setText] = useState("");
  const [label, setLabel] = useState("");
  const [people, setPeople] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [saved, setSaved] = useState(null);
  const closeRef = useRef(null);

  // Escape leaves. A projector view you cannot get out of without finding the
  // right button is a view that strands whoever is driving it in front of a
  // room (constraint 10's spirit, and the delta asks for it by name).
  useEffect(() => {
    function onKeyDown(event) {
      if (event.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [onClose]);

  // Focus lands somewhere sensible on arrival, so a keyboard can drive this.
  useEffect(() => {
    closeRef.current?.focus();
  }, []);

  useEffect(() => {
    if (!saved) return undefined;
    const timer = setTimeout(() => setSaved(null), SAVED_MS);
    return () => clearTimeout(timer);
  }, [saved]);

  const record = useCallback(async () => {
    if (!text.trim() || busy) return;
    setBusy(true);
    setError(null);
    try {
      const stored = await api.recordInterpretation({
        framework_id: framework.id,
        interpretation_text: text.trim(),
        view_kind: "landscape",
        signifier_id: triadId ?? null,
        // Captured, not typed: what was on screen is a fact about the moment.
        filter_state: filters,
        session_label: label.trim() || null,
        participant_count: people.trim() === "" ? null : Number(people),
      });
      setText("");
      setSaved(stored);
      onRecorded?.();
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : null);
    } finally {
      setBusy(false);
    }
  }, [text, busy, framework.id, triadId, filters, label, people, onRecorded]);

  const panel = land?.panels?.[0] ?? null;

  return (
    <div className="nl-session" role="region" aria-label="Session mode">
      <div className="nl-session__stage">
        <div className="nl-session__head">
          <h2 className="nl-session__title">
            {panel?.title ?? framework.name}
            <span className="nl-session__count">
              {" "}
              · {view.total} {view.total === 1 ? "story" : "stories"}
            </span>
          </h2>
          <button
            type="button"
            ref={closeRef}
            className="nl-session__exit"
            onClick={onClose}
          >
            Leave session mode <span className="nl-session__key">Esc</span>
          </button>
        </div>

        {land ? (
          <LandscapeView view={land} onRegion={() => {}} />
        ) : (
          <p className="nl-session__empty">Drawing the landscape…</p>
        )}
      </div>

      <aside className="nl-session__side" aria-label="What the room concluded">
        <h3 className="nl-session__side-title">What is the room saying?</h3>
        <p className="nl-session__note">
          Type it in their words, not yours. It is stored beside this pattern —
          it does not change the landscape, and it never becomes a mark on it.
        </p>

        {error && (
          <div className="nl-session__error" role="alert">
            <p className="nl-session__error-message">{error.message}</p>
            {error.action && <p className="nl-session__note">{error.action}</p>}
          </div>
        )}

        <label className="nl-session__label" htmlFor="nl-session-text">
          What they concluded
        </label>
        <textarea
          id="nl-session-text"
          className="nl-session__textarea"
          rows={6}
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder="In the room's own words…"
        />

        <label className="nl-session__label" htmlFor="nl-session-name">
          Which session is this? (optional)
        </label>
        <input
          id="nl-session-name"
          type="text"
          className="nl-session__input"
          value={label}
          onChange={(event) => setLabel(event.target.value)}
          placeholder="Ops night shift, 12 March"
        />

        <label className="nl-session__label" htmlFor="nl-session-people">
          How many people are here? (optional)
        </label>
        <input
          id="nl-session-people"
          type="number"
          min="0"
          className="nl-session__input"
          value={people}
          onChange={(event) => setPeople(event.target.value)}
        />

        <button
          type="button"
          className="nl-session__record"
          onClick={record}
          disabled={!text.trim() || busy}
        >
          {busy ? "Recording…" : "Record what the room said"}
        </button>

        {saved && (
          <p className="nl-session__saved" role="status">
            Recorded. The landscape above is unchanged — it is the same picture
            it was before.
          </p>
        )}

        <p className="nl-session__note">
          Recorded with the question on screen
          {Object.keys(filters).length > 0
            ? ` and the filters in force (${Object.entries(filters)
                .map(([field, value]) => `${field.replace(/_/g, " ")} = ${value}`)
                .join(", ")})`
            : " and no filters"}
          , so it can be read against this exact picture later.
        </p>
      </aside>
    </div>
  );
}
