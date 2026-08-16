/*
 * The validation queue (PRD §5.3) — the screen constraint 1 exists for.
 *
 * One story at a time, because this is a judgement and a judgement wants the
 * whole story in front of you. What the AI suggested is drawn on the same
 * widgets the respondent would have used, so agreeing or disagreeing is a
 * matter of looking at it rather than reading a number.
 *
 * Three buttons, and no fourth. There is deliberately no "accept all": a bulk
 * approve is the operator not looking, and constraint 1 asks for explicit human
 * validation, not a fast way past it.
 *
 * Correcting is the same widgets, made interactive. Moving a marker restamps
 * that placement as the analyst's and drops its model confidence; the ones left
 * alone keep saying the AI made them.
 */

import { useCallback, useEffect, useMemo, useState } from "react";
import { api, ApiError } from "../api.js";
import { fromStored, toSubmission } from "../capture/Wizard.jsx";
import { SignifierWidget } from "../widgets/Widgets.jsx";
import "./import-tab.css";

/** Signifiers in the order the respondent would have met them. */
function signifiersInOrder(definition) {
  if (!definition) return [];
  return [
    ...(definition.triads ?? []).map((triad) => ({ kind: "triad", signifier: triad })),
    ...(definition.dyads ?? []).map((dyad) => ({ kind: "dyad", signifier: dyad })),
    ...(definition.stones ? [{ kind: "stones", signifier: definition.stones }] : []),
    ...(definition.mcqs ?? []).map((mcq) => ({ kind: "mcq", signifier: mcq })),
  ];
}

/**
 * Stored placements in the shape the widgets draw.
 *
 * A widget speaks its own dialect — a triad is three ordered numbers on screen
 * and a corner-keyed object in the database — so every value read back out of
 * storage goes through the wizard's own converter on the way in, and back
 * through the wizard's own submitter on the way out.
 */
function widgetValues(definition, item) {
  const byId = Object.fromEntries(
    (item?.significations ?? []).map((placement) => [placement.signifier_id, placement.value]),
  );
  return Object.fromEntries(
    signifiersInOrder(definition)
      .filter(({ signifier }) => byId[signifier.id] !== undefined)
      .map(({ kind, signifier }) => [
        signifier.id,
        fromStored(kind, signifier, byId[signifier.id]),
      ]),
  );
}

export function ValidationQueue({ jobId = null, onClose = null }) {
  const [queue, setQueue] = useState(null);
  const [definitions, setDefinitions] = useState({});
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);
  const [correcting, setCorrecting] = useState(false);
  const [draft, setDraft] = useState({});

  const refresh = useCallback(async () => {
    try {
      const next = await api.readQueue(jobId);
      setQueue(next);
      setError(null);
      return next;
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : null);
      return null;
    }
  }, [jobId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const current = queue?.items?.[0] ?? null;

  // The questions this story was marked up against — the exact version, not the
  // latest one, so a later meaning change cannot redraw an old story's widgets.
  useEffect(() => {
    if (!current || definitions[current.framework_id]) return;
    let cancelled = false;
    api
      .getFramework(current.framework_id)
      .then((framework) => {
        if (!cancelled) {
          setDefinitions((known) => ({ ...known, [framework.id]: framework.definition }));
        }
      })
      .catch((caught) => setError(caught instanceof ApiError ? caught : null));
    return () => {
      cancelled = true;
    };
  }, [current, definitions]);

  const definition = current ? definitions[current.framework_id] : null;
  const signifiers = useMemo(() => signifiersInOrder(definition), [definition]);

  // A new story means a fresh decision: leave correction mode and start the
  // draft from what the AI actually proposed for this one.
  useEffect(() => {
    setCorrecting(false);
    setDraft(widgetValues(definition, current));
  }, [current?.anecdote_id, definition]); // eslint-disable-line react-hooks/exhaustive-deps

  async function decide(body) {
    if (!current) return;
    setBusy(true);
    try {
      await api.decideStory(current.anecdote_id, body);
      setError(null);
      await refresh();
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : null);
      await refresh();
    } finally {
      setBusy(false);
    }
  }

  function saveCorrection() {
    // The wizard's own converter, so a corrected placement is stored exactly as
    // a respondent's would be.
    decide({ action: "correct", significations: toSubmission(definition, draft) });
  }

  if (error && queue === null) {
    return (
      <div className="nl-import">
        <ErrorNote error={error} />
      </div>
    );
  }

  if (queue === null) {
    return (
      <div className="nl-import">
        <p className="nl-import__empty">Loading…</p>
      </div>
    );
  }

  const { counts } = queue;
  const decided = counts.validated + counts.rejected;
  const total = decided + counts.pending;

  return (
    <div className="nl-import">
      {onClose && (
        <button type="button" className="nl-import__back" onClick={onClose}>
          ← All imports
        </button>
      )}

      <header className="nl-import__head">
        <h2 className="nl-import__title">Check what the AI suggested</h2>
        <p className="nl-import__sub">
          Nothing here is in your data yet. Every story waits for you — however
          sure or unsure the suggestion looked.
        </p>
      </header>

      {error && <ErrorNote error={error} />}

      <Progress decided={decided} total={total} counts={counts} />

      {current === null ? (
        <p className="nl-import__empty">
          {total === 0
            ? "Nothing is waiting. Import a file and mark it up to fill this queue."
            : "All done — every story here has been checked."}
        </p>
      ) : (
        <article className="nl-verify">
          <div className="nl-verify__story">
            <p className="nl-verify__text">{current.text}</p>
            <Provenance item={current} />
          </div>

          {definition === null ? (
            <p className="nl-import__empty">Loading the questions…</p>
          ) : (
            <div className="nl-verify__placements">
              {signifiers.map(({ kind, signifier }) => {
                const proposed = current.significations.find(
                  (placement) => placement.signifier_id === signifier.id,
                );
                return (
                  <section key={signifier.id} className="nl-verify__signifier">
                    {/* The widget draws its own question, so this row carries
                        only what the queue adds: how sure the AI was. */}
                    <Confidence placement={proposed} />
                    <SignifierWidget
                      kind={kind}
                      signifier={signifier}
                      value={
                        correcting
                          ? (draft[signifier.id] ?? null)
                          : fromStored(kind, signifier, proposed?.value ?? null)
                      }
                      onChange={
                        correcting
                          ? (value) =>
                              setDraft((current) => ({ ...current, [signifier.id]: value }))
                          : null
                      }
                    />
                  </section>
                );
              })}
            </div>
          )}

          <div className="nl-verify__actions">
            {correcting ? (
              <>
                <button
                  type="button"
                  className="nl-import__primary"
                  disabled={busy}
                  onClick={saveCorrection}
                >
                  {busy ? "Saving…" : "Save my answers"}
                </button>
                <button
                  type="button"
                  className="nl-verify__button"
                  disabled={busy}
                  onClick={() => setCorrecting(false)}
                >
                  Cancel
                </button>
              </>
            ) : (
              <>
                <button
                  type="button"
                  className="nl-import__primary"
                  disabled={busy}
                  onClick={() => decide({ action: "accept" })}
                >
                  {busy ? "Saving…" : "That looks right"}
                </button>
                <button
                  type="button"
                  className="nl-verify__button"
                  disabled={busy || definition === null}
                  onClick={() => setCorrecting(true)}
                >
                  Change the answers
                </button>
                <button
                  type="button"
                  className="nl-verify__button nl-verify__button--quiet"
                  disabled={busy}
                  onClick={() => decide({ action: "reject" })}
                >
                  Not a usable story
                </button>
              </>
            )}
          </div>
        </article>
      )}
    </div>
  );
}

function Progress({ decided, total, counts }) {
  if (total === 0) return null;
  return (
    <p className="nl-verify__progress">
      <strong>
        {decided} of {total}
      </strong>{" "}
      checked · {counts.validated} kept · {counts.rejected} set aside
    </p>
  );
}

/** Constraint 3, where the operator making the judgement can see it. */
function Provenance({ item }) {
  const bits = [
    item.source_file,
    item.source_locator,
    item.respondent_group,
    `${item.framework_name} v${item.framework_version}`,
  ].filter(Boolean);
  return <p className="nl-verify__provenance">{bits.join(" · ")}</p>;
}

/** Constraint 2: amber below 0.70, and the same queue either way. */
function Confidence({ placement }) {
  if (!placement) {
    return <span className="nl-verify__nothing">The AI did not answer this one</span>;
  }
  if (placement.ai_confidence === null) return null;
  const percent = Math.round(placement.ai_confidence * 100);
  return placement.low_confidence ? (
    <span className="nl-amber">Less certain · {percent}%</span>
  ) : (
    <span className="nl-verify__confidence">{percent}% sure</span>
  );
}

function ErrorNote({ error }) {
  return (
    <div className="nl-import__error" role="alert">
      <p className="nl-import__error-message">{error?.message ?? "Something went wrong."}</p>
      {error?.action && <p className="nl-import__error-action">{error.action}</p>}
    </div>
  );
}
