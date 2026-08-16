/*
 * The Import & Validate tab (PRD §5.3) — the staged pipeline and the Mapping
 * screen. The validation queue is the other half of this tab and arrives with
 * Phase 6, so it is named here rather than hidden.
 *
 * The screen is built around the one thing constraint 1 insists on: the app
 * proposes, the operator decides. So Organise is a button the operator presses,
 * what it found is shown before anything is acted on, and the Confirm button
 * says what it will do. The stage machine on the server refuses steps taken out
 * of turn, which means this screen never has to guess what is allowed — it
 * offers the next step, and a refusal comes back as a sentence to show.
 */

import { useCallback, useEffect, useState } from "react";
import { api, ApiError } from "../api.js";
import { MappingScreen } from "./MappingScreen.jsx";
import "./import-tab.css";

const ACCEPTED = ".docx,.txt,.md,.pdf,.pptx,.xlsx,.csv,.vtt,.srt";

export function ImportTab() {
  const [jobs, setJobs] = useState(null);
  const [openId, setOpenId] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    try {
      setJobs(await api.listImports());
      setError(null);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : null);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function upload(file) {
    if (!file) return;
    setBusy(true);
    try {
      const job = await api.uploadImport(file);
      setError(null);
      await refresh();
      setOpenId(job.id);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : null);
    } finally {
      setBusy(false);
    }
  }

  if (openId !== null) {
    return (
      <ImportDetail
        jobId={openId}
        onClose={async () => {
          setOpenId(null);
          await refresh();
        }}
      />
    );
  }

  return (
    <div className="nl-import">
      <header className="nl-import__head">
        <h2 className="nl-import__title">Import & Validate</h2>
        <p className="nl-import__sub">
          Bring in stories that were collected somewhere else — a transcript, a
          survey export, a set of workshop notes. Nothing goes into the data
          until you have looked at it and said yes.
        </p>
      </header>

      {error && <ErrorNote error={error} />}

      <label className="nl-import__upload">
        <span className="nl-import__upload-label">
          {busy ? "Reading the file…" : "Choose a file to import"}
        </span>
        <input
          type="file"
          className="nl-import__file"
          accept={ACCEPTED}
          disabled={busy}
          onChange={(event) => {
            const [file] = event.target.files ?? [];
            event.target.value = "";
            upload(file);
          }}
        />
      </label>
      <p className="nl-import__formats">
        Word, plain text, Markdown, PDF, PowerPoint, Excel, CSV, and .vtt or
        .srt transcripts.
      </p>

      <h3 className="nl-import__section">Files you have brought in</h3>
      {jobs === null && <p className="nl-import__empty">Loading…</p>}
      {jobs !== null && jobs.length === 0 && (
        <p className="nl-import__empty">Nothing yet. Choose a file above to start.</p>
      )}
      {jobs !== null && jobs.length > 0 && (
        <ul className="nl-import__list">
          {jobs.map((job) => (
            <li key={job.id} className="nl-job">
              <div className="nl-job__main">
                <p className="nl-job__name">{job.filename}</p>
                <p className="nl-job__meta">
                  {job.stage_label}
                  {job.segments_found !== null && ` · ${storyCount(job.segments_found)} found`}
                </p>
                {job.error_message && <p className="nl-job__problem">{job.error_message}</p>}
              </div>
              <button
                type="button"
                className="nl-job__open"
                onClick={() => setOpenId(job.id)}
              >
                Open
              </button>
            </li>
          ))}
        </ul>
      )}

      <p className="nl-import__soon">
        Once a file is confirmed, the next step marks the stories up and puts
        them in the validation queue. That part arrives with the next stage of
        the build.
      </p>
    </div>
  );
}

function storyCount(n) {
  return n === 1 ? "1 story" : `${n} stories`;
}

function ErrorNote({ error }) {
  return (
    <div className="nl-import__error" role="alert">
      <p className="nl-import__error-message">{error?.message ?? "Something went wrong."}</p>
      {error?.action && <p className="nl-import__error-action">{error.action}</p>}
    </div>
  );
}

/**
 * One file, and whatever it is waiting on.
 *
 * Three states matter to the operator: it has been read and wants organising;
 * it has been organised and wants checking; it has been checked and is done for
 * now. Each shows the one thing to do next and nothing else.
 */
function ImportDetail({ jobId, onClose }) {
  const [job, setJob] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      setJob(await api.getImport(jobId));
      setError(null);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : null);
    }
  }, [jobId]);

  useEffect(() => {
    load();
  }, [load]);

  async function run(action) {
    setBusy(true);
    try {
      setJob(await action());
      setError(null);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : null);
      await load();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="nl-import">
      <button type="button" className="nl-import__back" onClick={onClose}>
        ← All imports
      </button>

      {error && <ErrorNote error={error} />}
      {job === null && <p className="nl-import__empty">Loading…</p>}

      {job !== null && (
        <>
          <header className="nl-import__head">
            <h2 className="nl-import__title">{job.filename}</h2>
            <p className="nl-import__sub">
              {job.file_class === "tabular"
                ? `A table — ${job.sheets.length === 1 ? "one sheet" : `${job.sheets.length} sheets`}.`
                : `Written text — ${job.block_count} passages.`}{" "}
              This file is {job.stage_label}.
            </p>
          </header>

          {job.stage === "uploaded" && (
            <section className="nl-import__step">
              <p className="nl-import__step-text">
                Narrative Lens has read the file. The next step sends its text to
                the AI, which suggests where one person&rsquo;s account ends and
                the next begins. Nothing is saved until you have checked the
                suggestions.
              </p>
              <button
                type="button"
                className="nl-import__primary"
                disabled={busy}
                onClick={() => run(() => api.organiseImport(job.id))}
              >
                {busy ? "Working…" : "Organise this file"}
              </button>
            </section>
          )}

          {job.stage === "organised" && (
            <MappingScreen
              job={job}
              busy={busy}
              onConfirm={(body) => run(() => api.confirmMapping(job.id, body))}
            />
          )}

          {job.stage === "mapping_confirmed" && job.confirmation && (
            <section className="nl-import__step">
              <h3 className="nl-import__section">What you confirmed</h3>
              <Reconciliation value={job.confirmation.reconciliation} />
              <p className="nl-import__step-text">
                {storyCount(job.confirmation.candidate_count)} ready for marking
                up. That step, and the validation queue it feeds, arrive with the
                next stage of the build.
              </p>
            </section>
          )}
        </>
      )}
    </div>
  );
}

/**
 * The reconciliation line (constraint 12).
 *
 * Every row of the file lands on exactly one line, and the lines add up to the
 * total. Shown as arithmetic rather than as a summary sentence, because the
 * point is that the operator can check it against the file themselves.
 */
export function Reconciliation({ value }) {
  return (
    <table className="nl-tally">
      <caption className="nl-tally__caption">Everything in the file, accounted for</caption>
      <tbody>
        {value.lines.map((line) => (
          <tr key={line.label}>
            <th scope="row" className="nl-tally__label">
              {line.label}
            </th>
            <td className="nl-tally__count">{line.count}</td>
          </tr>
        ))}
      </tbody>
      <tfoot>
        <tr>
          <th scope="row" className="nl-tally__label nl-tally__label--total">
            {value.total_label}
          </th>
          <td className="nl-tally__count nl-tally__count--total">{value.total}</td>
        </tr>
      </tfoot>
    </table>
  );
}
