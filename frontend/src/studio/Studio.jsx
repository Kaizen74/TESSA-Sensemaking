/*
 * The Studio (PRD §1.1, §5.1).
 *
 * One panel where every question, label, and respondent-facing string is
 * editable, with the phone preview updating as the operator types. Layout is
 * three columns: version history · editing surface · live preview.
 *
 * The guardrail lives here: saving a framework that already has stories opens
 * EditKindDialog rather than writing straight through. A 409 from the server is
 * the backstop if the dialog is ever bypassed.
 */

import { useCallback, useEffect, useMemo, useState } from "react";
import { api, ApiError } from "../api.js";
import { EditKindDialog } from "./EditKindDialog.jsx";
import { PhonePreview, orderedSignifiers } from "./PhonePreview.jsx";
import { Field, TextArea, SignifierEditor } from "./Fields.jsx";
import { ActiveLinkQr } from "./ActiveLinkQr.jsx";
import { describePath } from "./editLog.js";
import "./studio.css";

const MINUTES_BAR = 4;

function newId(prefix, taken) {
  let index = taken.length + 1;
  let candidate = `${prefix}${index}`;
  while (taken.includes(candidate)) {
    index += 1;
    candidate = `${prefix}${index}`;
  }
  return candidate;
}

export function Studio() {
  const [frameworks, setFrameworks] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [draft, setDraft] = useState(null);
  const [name, setName] = useState("");
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  // The design critique, when one has been asked for. Kept apart from `error`
  // so that a linter that could not be reached never takes the Studio down with
  // it — the panel says what happened and everything else still works.
  const [lint, setLint] = useState(null);
  const [linting, setLinting] = useState(false);
  const [lintError, setLintError] = useState(null);

  const selected = frameworks.find((f) => f.id === selectedId) ?? null;

  const refresh = useCallback(async (keepId = null) => {
    try {
      const rows = await api.listFrameworks();
      setFrameworks(rows);
      const next = keepId ?? rows[0]?.id ?? null;
      setSelectedId(next);
      const chosen = rows.find((row) => row.id === next);
      if (chosen) {
        setDraft(structuredClone(chosen.definition));
        setName(chosen.name);
      }
      setError(null);
    } catch (caught) {
      setError(caught);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function checkDesign() {
    setLinting(true);
    setLintError(null);
    try {
      setLint(await api.lintFramework(selectedId));
    } catch (caught) {
      // Constraint 4: not being able to reach the service is an ordinary state
      // of the app. Nothing was written, so there is nothing to undo.
      setLintError(caught instanceof ApiError ? caught : null);
      setLint(null);
    } finally {
      setLinting(false);
    }
  }

  function selectFramework(id) {
    const chosen = frameworks.find((row) => row.id === id);
    if (!chosen) return;
    setSelectedId(id);
    setDraft(structuredClone(chosen.definition));
    setName(chosen.name);
    setStatus(null);
    // Findings belong to the version they were asked about. Carrying them over
    // to a different question set would attach advice to wording it was never
    // about.
    setLint(null);
    setLintError(null);
    setError(null);
  }

  const dirty = useMemo(() => {
    if (!selected || !draft) return false;
    return (
      JSON.stringify(draft) !== JSON.stringify(selected.definition) || name !== selected.name
    );
  }, [draft, selected, name]);

  const signifierCount = draft ? orderedSignifiers(draft).length : 0;
  const estimatedMinutes = useMemo(() => estimateMinutes(draft), [draft]);

  function patch(changes) {
    setDraft((current) => ({ ...current, ...changes }));
    setStatus(null);
  }

  function patchSettings(changes) {
    setDraft((current) => ({
      ...current,
      capture_settings: { ...current.capture_settings, ...changes },
    }));
    setStatus(null);
  }

  async function save(editKind = null) {
    setBusy(true);
    setError(null);
    try {
      const saved = await api.updateFramework(selectedId, draft, editKind, name);
      setDialogOpen(false);
      await refresh(saved.id);
      setStatus(
        saved.id === selectedId
          ? "Saved."
          : `Saved as version ${saved.version}. Earlier stories stay with the old wording.`,
      );
    } catch (caught) {
      if (caught instanceof ApiError && caught.code === "edit_kind_required") {
        setDialogOpen(true);
      } else {
        setError(caught);
        setDialogOpen(false);
      }
    } finally {
      setBusy(false);
    }
  }

  function onSaveClicked() {
    if (selected?.is_live) {
      setDialogOpen(true);
      return;
    }
    save(null);
  }

  async function createFramework() {
    setBusy(true);
    try {
      const created = await api.createFramework("New question set", {});
      await refresh(created.id);
      setStatus("Created. Give it a name and add your questions.");
    } catch (caught) {
      setError(caught);
    } finally {
      setBusy(false);
    }
  }

  if (error && !draft) {
    return <ErrorPanel error={error} />;
  }

  return (
    <div className="nl-studio">
      <aside className="nl-studio__rail" aria-label="Question sets and versions">
        <div className="nl-studio__rail-head">
          <h2 className="nl-studio__rail-title">Question sets</h2>
          <button type="button" className="nl-btn nl-btn--quiet" onClick={createFramework}>
            New
          </button>
        </div>
        {frameworks.length === 0 ? (
          <p className="nl-empty">
            No question sets yet. Choose <strong>New</strong> to write your first question.
          </p>
        ) : (
          <ul className="nl-versions">
            {frameworks.map((row) => (
              <li key={row.id}>
                <button
                  type="button"
                  onClick={() => selectFramework(row.id)}
                  className={
                    row.id === selectedId
                      ? "nl-version nl-version--current"
                      : "nl-version"
                  }
                  aria-current={row.id === selectedId ? "true" : undefined}
                >
                  <span className="nl-version__name">{row.name}</span>
                  <span className="nl-version__meta">
                    <span className="nl-numeric">v{row.version}</span>
                    <span className="nl-numeric">
                      {row.anecdote_count} {row.anecdote_count === 1 ? "story" : "stories"}
                    </span>
                  </span>
                  {row.edit_log.length > 0 && (
                    <span className="nl-version__log">
                      {row.edit_log.length} wording{" "}
                      {row.edit_log.length === 1 ? "fix" : "fixes"}
                    </span>
                  )}
                </button>
              </li>
            ))}
          </ul>
        )}

        {selected?.edit_log?.length > 0 && (
          <section className="nl-editlog">
            <h3 className="nl-editlog__title">Edit log — version {selected.version}</h3>
            <ol className="nl-editlog__list">
              {selected.edit_log.map((entry, index) => (
                <li key={`${entry.field_path}-${index}`} className="nl-editlog__entry">
                  <span className="nl-editlog__path">{describePath(entry.field_path)}</span>
                  <span className="nl-editlog__old">{entry.old_text}</span>
                  <span className="nl-editlog__new">{entry.new_text}</span>
                </li>
              ))}
            </ol>
          </section>
        )}

        <ActiveLinkQr />
      </aside>

      {draft ? (
        <>
          <main className="nl-studio__editor">
            <header className="nl-studio__header">
              <h2 className="nl-studio__title">Studio</h2>
              <p className="nl-studio__sub">
                Everything a respondent reads is on this page. The phone on the right
                updates as you type.
              </p>
            </header>

            {error && <ErrorPanel error={error} />}

            <div className="nl-meter" role="status">
              <span className="nl-numeric nl-meter__value">{estimatedMinutes} min</span>
              <span className="nl-meter__label">
                {signifierCount} question{signifierCount === 1 ? "" : "s"} after the story
              </span>
              {estimatedMinutes > MINUTES_BAR && (
                <span className="nl-meter__warn">
                  Over the {MINUTES_BAR}-minute promise — consider removing a question.
                </span>
              )}
              {signifierCount > 6 && (
                <span className="nl-meter__warn">
                  More than six question screens. People tend to drop out past this.
                </span>
              )}
            </div>

            <Field label="Name of this question set" value={name} onChange={setName} />

            <fieldset className="nl-fieldset">
              <legend className="nl-legend">The story prompt</legend>
              <TextArea
                label="Prompting question"
                value={draft.prompt_text}
                onChange={(value) => patch({ prompt_text: value })}
              />
              <TextArea
                label="Alternative prompt (optional)"
                value={draft.prompt_text_alt ?? ""}
                onChange={(value) => patch({ prompt_text_alt: value || null })}
              />
            </fieldset>

            <fieldset className="nl-fieldset">
              <legend className="nl-legend">What respondents read</legend>
              <TextArea
                label="Welcome"
                value={draft.capture_settings.welcome_text}
                onChange={(value) => patchSettings({ welcome_text: value })}
              />
              <TextArea
                label="Anonymity statement"
                hint="Printed word for word on the paper story card. Only claim what is true."
                value={draft.capture_settings.anonymity_text}
                onChange={(value) => patchSettings({ anonymity_text: value })}
              />
              <TextArea
                label="Thank you"
                value={draft.capture_settings.thankyou_text}
                onChange={(value) => patchSettings({ thankyou_text: value })}
              />
              <Field
                label="Time promise"
                hint="Be honest — the estimate above is what it actually takes."
                value={draft.capture_settings.time_promise_text}
                onChange={(value) => patchSettings({ time_promise_text: value })}
              />
              <Field
                label="Respondent groups"
                hint="Comma separated. Leave empty to not ask."
                value={(draft.capture_settings.respondent_groups ?? []).join(", ")}
                onChange={(value) =>
                  patchSettings({
                    respondent_groups: value
                      .split(",")
                      .map((part) => part.trim())
                      .filter(Boolean),
                  })
                }
              />
            </fieldset>

            <SignifierEditor draft={draft} patch={patch} newId={newId} />

            <div className="nl-actions">
              <button
                type="button"
                className="nl-btn nl-btn--primary"
                onClick={onSaveClicked}
                disabled={!dirty || busy}
              >
                {busy ? "Saving…" : "Save changes"}
              </button>
              {/* Beside the save control, and never in front of it: findings
                  are advice, and the delta is explicit that the linter can
                  never block publishing. */}
              <button
                type="button"
                className="nl-btn nl-btn--quiet"
                onClick={checkDesign}
                disabled={linting}
              >
                {linting ? "Checking…" : "Check this design"}
              </button>
              <a
                className="nl-btn nl-btn--quiet"
                href={api.paperPackUrl(selectedId)}
                target="_blank"
                rel="noreferrer"
              >
                Paper pack for version {selected?.version}
              </a>
              {status && (
                <span className="nl-status" role="status">
                  {status}
                </span>
              )}
              {!dirty && !status && <span className="nl-status">No unsaved changes.</span>}
            </div>

            <LintPanel
              report={lint}
              error={lintError}
              onDismiss={() => {
                setLint(null);
                setLintError(null);
              }}
            />
          </main>

          <aside className="nl-studio__preview" aria-label="Live preview">
            <PhonePreview definition={draft} />
          </aside>
        </>
      ) : (
        <main className="nl-studio__editor">
          <p className="nl-empty">Choose a question set on the left, or make a new one.</p>
        </main>
      )}

      {dialogOpen && selected && (
        <EditKindDialog
          storyCount={selected.anecdote_count}
          busy={busy}
          onChoose={(kind) => save(kind)}
          onCancel={() => setDialogOpen(false)}
        />
      )}
    </div>
  );
}

/**
 * The design critique (delta §5, phase C).
 *
 * Three things this panel is careful about.
 *
 * It says plainly what it is about. Every other AI surface in this app is about
 * the data; this one is about the *questions*, and a reader who mixed those up
 * would think the model had been reading their stories. It has not, and the
 * panel says so.
 *
 * A suggestion is text, never a button. The delta is explicit: "offering the
 * suggestion as text you can copy — never as a one-click apply". The operator
 * knows the workforce; the model is guessing at them. One click to accept a
 * guess is how a question set drifts away from the people answering it.
 *
 * It cannot block anything. The panel has no bearing on saving, and a failed
 * check leaves it usable — a sentence about what went wrong, and the Studio
 * carries on (constraint 4).
 */
function LintPanel({ report, error, onDismiss }) {
  if (!report && !error) return null;

  if (error) {
    return (
      <section className="nl-lint" aria-label="Design check">
        <div className="nl-lint__head">
          <h3 className="nl-lint__title">The design check could not run</h3>
          <button type="button" className="nl-lint__close" onClick={onDismiss}>
            Close
          </button>
        </div>
        <p className="nl-lint__message">{error.message}</p>
        {error.action && <p className="nl-lint__note">{error.action}</p>}
        <p className="nl-lint__note">
          Nothing was changed, and nothing else depends on this. Your question
          set is exactly as you left it, and you can save and publish as normal.
        </p>
      </section>
    );
  }

  const warnings = report.findings.filter((f) => f.severity === "warning");
  const notes = report.findings.filter((f) => f.severity === "info");

  return (
    <section className="nl-lint" aria-label="Design check">
      <div className="nl-lint__head">
        <h3 className="nl-lint__title">
          {report.findings.length === 0
            ? "Nothing stood out in this design"
            : `${report.findings.length} thing${
                report.findings.length === 1 ? "" : "s"
              } worth a look`}
        </h3>
        <button type="button" className="nl-lint__close" onClick={onDismiss}>
          Close
        </button>
      </div>

      <p className="nl-lint__note">
        These are suggestions about how the <strong>questions</strong> are
        worded — not about your data. No stories were read to produce them; none
        may even have been collected yet. Nothing here has changed your question
        set, and none of it stops you publishing.
      </p>

      {report.findings.length === 0 ? (
        <p className="nl-lint__message">
          Worth remembering that this is one reading, not a verdict. You know the
          people answering these questions and it does not.
        </p>
      ) : (
        <>
          {[
            ["Worth changing", warnings],
            ["Worth a second look", notes],
          ].map(([heading, group]) =>
            group.length === 0 ? null : (
              <div key={heading} className="nl-lint__group">
                <h4 className="nl-lint__group-title">{heading}</h4>
                <ul className="nl-lint__list">
                  {group.map((finding, index) => (
                    <li key={`${finding.location}-${index}`} className="nl-lint__finding">
                      <code className="nl-lint__where">{finding.location}</code>
                      <p className="nl-lint__what">{finding.finding}</p>
                      {/* Text, selectable, and not a button. */}
                      <p className="nl-lint__try">
                        <span className="nl-lint__try-label">Try instead:</span>{" "}
                        {finding.suggestion}
                      </p>
                    </li>
                  ))}
                </ul>
              </div>
            ),
          )}
        </>
      )}
    </section>
  );
}

function ErrorPanel({ error }) {
  return (
    <div className="nl-error" role="alert">
      <p className="nl-error__message">{error.message}</p>
      {error.action && <p className="nl-error__action">{error.action}</p>}
    </div>
  );
}

/*
 * Mirrors the server's estimate in backend/framework_schema.py. Kept in step by
 * showing the server's own figure after every save; this local copy only covers
 * the keystrokes between saves.
 */
export function estimateMinutes(definition) {
  if (!definition) return 0;
  const seconds =
    20 +
    90 +
    (definition.triads?.length ?? 0) * 25 +
    (definition.dyads?.length ?? 0) * 15 +
    (definition.mcqs?.length ?? 0) * 12 +
    (definition.stones ? 40 : 0);
  return Math.round((seconds / 60) * 10) / 10;
}
