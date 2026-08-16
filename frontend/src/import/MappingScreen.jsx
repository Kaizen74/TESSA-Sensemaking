/*
 * The confirmation screen — the human "yes" constraint 1 requires.
 *
 * Two shapes, because the two decisions are different. A table asks which
 * column holds the story and which sheets are not responses at all. Written
 * text asks which of the suggested passages really are whole accounts.
 *
 * Both start from what the AI proposed and both let the operator change it.
 * Confidence under 0.70 is flagged amber (constraint 2) — it changes the colour
 * and nothing else, because everything queues either way.
 */

import { useState } from "react";
import "./import-tab.css";

const LOW_CONFIDENCE = 0.7;

export function MappingScreen({ job, busy, onConfirm }) {
  return job.file_class === "tabular" ? (
    <TableMapping job={job} busy={busy} onConfirm={onConfirm} />
  ) : (
    <SegmentChecklist job={job} busy={busy} onConfirm={onConfirm} />
  );
}

function Amber({ confidence }) {
  if (confidence >= LOW_CONFIDENCE) return null;
  return (
    <span className="nl-amber" title="Less certain than usual — worth a closer look">
      Less certain
    </span>
  );
}

/* ---------------------------------------------------------------- tables -- */

function TableMapping({ job, busy, onConfirm }) {
  const [sheets, setSheets] = useState(() =>
    job.organisation.sheets.map((proposal) => ({
      sheet: proposal.sheet,
      role: proposal.role,
      story_column: proposal.story_column,
      respondent_group_column: proposal.respondent_group_column,
      title_column: proposal.title_column,
    })),
  );

  function update(name, changes) {
    setSheets((current) =>
      current.map((sheet) => (sheet.sheet === name ? { ...sheet, ...changes } : sheet)),
    );
  }

  const bySheet = Object.fromEntries(job.sheets.map((sheet) => [sheet.name, sheet]));
  const proposalFor = Object.fromEntries(
    job.organisation.sheets.map((proposal) => [proposal.sheet, proposal]),
  );
  const kept = sheets
    .filter((sheet) => sheet.role === "stories")
    .reduce((total, sheet) => total + bySheet[sheet.sheet].row_count, 0);
  const total = job.sheets.reduce((sum, sheet) => sum + sheet.row_count, 0);

  return (
    <section className="nl-import__step">
      <h3 className="nl-import__section">Which column holds the story?</h3>
      <p className="nl-import__step-text">
        Check each sheet below. Narrative Lens reads the rows itself once you
        confirm — the AI only suggested where to look.
      </p>

      {sheets.map((mapping) => {
        const sheet = bySheet[mapping.sheet];
        const proposal = proposalFor[mapping.sheet];
        return (
          <div key={mapping.sheet} className="nl-sheet">
            <div className="nl-sheet__head">
              <h4 className="nl-sheet__name">{sheet.name}</h4>
              <p className="nl-sheet__meta">
                {sheet.row_count === 1 ? "1 row" : `${sheet.row_count} rows`}
                {proposal.note && ` · ${proposal.note}`}
              </p>
              <Amber confidence={proposal.confidence} />
            </div>

            <div className="nl-sheet__controls">
              <label className="nl-sheet__field">
                <span className="nl-sheet__field-label">This sheet</span>
                <select
                  className="nl-sheet__select"
                  value={mapping.role}
                  onChange={(event) =>
                    update(
                      mapping.sheet,
                      event.target.value === "ignore"
                        ? {
                            role: "ignore",
                            story_column: null,
                            respondent_group_column: null,
                            title_column: null,
                          }
                        : { role: "stories", story_column: sheet.headers[0] },
                    )
                  }
                >
                  <option value="stories">holds people&rsquo;s stories</option>
                  <option value="ignore">is not responses — skip it</option>
                </select>
              </label>

              {mapping.role === "stories" && (
                <>
                  <ColumnPicker
                    label="The story is in"
                    headers={sheet.headers}
                    value={mapping.story_column}
                    optional={false}
                    onChange={(value) => update(mapping.sheet, { story_column: value })}
                  />
                  <ColumnPicker
                    label="Who they are (optional)"
                    headers={sheet.headers}
                    value={mapping.respondent_group_column}
                    optional
                    onChange={(value) =>
                      update(mapping.sheet, { respondent_group_column: value })
                    }
                  />
                  <ColumnPicker
                    label="A title (optional)"
                    headers={sheet.headers}
                    value={mapping.title_column}
                    optional
                    onChange={(value) => update(mapping.sheet, { title_column: value })}
                  />
                </>
              )}
            </div>

            <SamplePreview sheet={sheet} />
          </div>
        );
      })}

      <p className="nl-import__step-text">
        {kept} of {total} rows are on sheets you are keeping. Narrative Lens will
        show you the exact figures — including any rows with nothing written in
        them — as soon as you confirm.
      </p>

      <button
        type="button"
        className="nl-import__primary"
        disabled={busy}
        onClick={() => onConfirm({ sheets })}
      >
        {busy ? "Working…" : "Confirm this mapping"}
      </button>
    </section>
  );
}

function ColumnPicker({ label, headers, value, optional, onChange }) {
  return (
    <label className="nl-sheet__field">
      <span className="nl-sheet__field-label">{label}</span>
      <select
        className="nl-sheet__select"
        value={value ?? ""}
        onChange={(event) => onChange(event.target.value || null)}
      >
        {optional && <option value="">— none —</option>}
        {headers.map((header) => (
          <option key={header} value={header}>
            {header}
          </option>
        ))}
      </select>
    </label>
  );
}

function SamplePreview({ sheet }) {
  if (sheet.sample_rows.length === 0) return null;
  return (
    <div className="nl-sheet__preview">
      <table className="nl-preview">
        <thead>
          <tr>
            {sheet.headers.map((header) => (
              <th key={header} scope="col" className="nl-preview__head">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sheet.sample_rows.map((row, index) => (
            // Rows have no id of their own; their position in the preview is
            // what identifies them, and the preview never reorders.
            <tr key={index}>
              {row.map((cell, cellIndex) => (
                <td key={cellIndex} className="nl-preview__cell">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* ------------------------------------------------------------- narrative -- */

function SegmentChecklist({ job, busy, onConfirm }) {
  const segments = job.organisation.segments;
  const [accepted, setAccepted] = useState(() => segments.map((_, index) => index));

  function toggle(index) {
    setAccepted((current) =>
      current.includes(index)
        ? current.filter((kept) => kept !== index)
        : [...current, index].sort((a, b) => a - b),
    );
  }

  return (
    <section className="nl-import__step">
      <h3 className="nl-import__section">Which of these are whole stories?</h3>
      <p className="nl-import__step-text">
        The AI suggested {segments.length === 1 ? "one passage" : `${segments.length} passages`}.
        Untick anything that is a heading, a note, or half of somebody
        else&rsquo;s account. Nothing is saved until you confirm.
      </p>

      <div className="nl-segments__bar">
        <button
          type="button"
          className="nl-segments__all"
          onClick={() => setAccepted(segments.map((_, index) => index))}
        >
          Tick all
        </button>
        <button
          type="button"
          className="nl-segments__all"
          onClick={() => setAccepted([])}
        >
          Untick all
        </button>
        <span className="nl-segments__count">
          {accepted.length} of {segments.length} kept
        </span>
      </div>

      <ul className="nl-segments">
        {segments.map((segment, index) => (
          <li key={segment.source_locator + index} className="nl-segment">
            <label className="nl-segment__pick">
              <input
                type="checkbox"
                checked={accepted.includes(index)}
                onChange={() => toggle(index)}
              />
              <span className="nl-segment__locator">{segment.source_locator}</span>
              <Amber confidence={segment.confidence} />
            </label>
            <p className="nl-segment__text">{segment.text}</p>
          </li>
        ))}
      </ul>

      <button
        type="button"
        className="nl-import__primary"
        disabled={busy}
        onClick={() => onConfirm({ accepted })}
      >
        {busy ? "Working…" : `Confirm ${accepted.length} of ${segments.length}`}
      </button>
    </section>
  );
}
