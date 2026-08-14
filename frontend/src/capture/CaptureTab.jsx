/*
 * The Capture tab (PRD §5.2).
 *
 * Phase 3 gives it two of its four parts: admin capture through the wizard, and
 * paper batch entry. The link manager with its QR poster and the kiosk launcher
 * arrive with Phase 4, and are named here so the operator can see what is
 * coming rather than wondering whether they missed it.
 */

import { useEffect, useState } from "react";
import { api } from "../api.js";
import { Wizard } from "./Wizard.jsx";
import { PaperBatch } from "./PaperBatch.jsx";
import "./capture-tab.css";

const MODE_WIZARD = "wizard";
const MODE_PAPER = "paper";

export function CaptureTab() {
  const [frameworks, setFrameworks] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [mode, setMode] = useState(MODE_WIZARD);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .listFrameworks()
      .then((rows) => {
        setFrameworks(rows);
        setSelectedId(rows[0]?.id ?? null);
      })
      .catch(setError);
  }, []);

  if (error) {
    return (
      <div className="nl-capture">
        <div className="nl-capture__error" role="alert">
          <p>{error.message}</p>
          {error.action && <p className="nl-capture__error-action">{error.action}</p>}
        </div>
      </div>
    );
  }

  if (frameworks === null) {
    return (
      <div className="nl-capture">
        <p className="nl-capture__empty">Loading…</p>
      </div>
    );
  }

  if (frameworks.length === 0) {
    return (
      <div className="nl-capture">
        <p className="nl-capture__empty">
          There are no question sets yet. Go to the <strong>Studio</strong> and make one
          first — capture needs questions to ask.
        </p>
      </div>
    );
  }

  const selected = frameworks.find((row) => row.id === selectedId) ?? frameworks[0];

  return (
    <div className="nl-capture">
      <div className="nl-capture__bar">
        <label className="nl-capture__field">
          <span className="nl-capture__field-label">Question set</span>
          <select
            className="nl-capture__select"
            value={selected.id}
            onChange={(event) => setSelectedId(Number(event.target.value))}
          >
            {frameworks.map((row) => (
              <option key={row.id} value={row.id}>
                {row.name} — v{row.version}
              </option>
            ))}
          </select>
        </label>

        <div className="nl-capture__modes" role="tablist" aria-label="How to enter stories">
          <button
            type="button"
            role="tab"
            aria-selected={mode === MODE_WIZARD}
            className={
              mode === MODE_WIZARD
                ? "nl-capture__mode nl-capture__mode--current"
                : "nl-capture__mode"
            }
            onClick={() => setMode(MODE_WIZARD)}
          >
            One at a time
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={mode === MODE_PAPER}
            className={
              mode === MODE_PAPER
                ? "nl-capture__mode nl-capture__mode--current"
                : "nl-capture__mode"
            }
            onClick={() => setMode(MODE_PAPER)}
          >
            From paper
          </button>
          <span className="nl-capture__mode nl-capture__mode--soon" aria-disabled="true">
            Links &amp; kiosk — coming soon
          </span>
        </div>
      </div>

      {mode === MODE_WIZARD ? (
        <Wizard key={`wizard-${selected.id}`} framework={selected} />
      ) : (
        <PaperBatch key={`paper-${selected.id}`} framework={selected} />
      )}
    </div>
  );
}
