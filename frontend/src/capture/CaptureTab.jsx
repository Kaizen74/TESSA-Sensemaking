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
import { LinkManager } from "./LinkManager.jsx";
import "./capture-tab.css";

const MODE_WIZARD = "wizard";
const MODE_PAPER = "paper";
const MODE_LINKS = "links";
const MODE_KIOSK = "kiosk";

const MODES = [
  { id: MODE_WIZARD, label: "One at a time" },
  { id: MODE_PAPER, label: "From paper" },
  { id: MODE_LINKS, label: "Links & QR" },
  { id: MODE_KIOSK, label: "Kiosk" },
];

/** How long the thank-you stays up before the kiosk resets for the next person. */
const KIOSK_RESET_DELAY_MS = 6000;

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

        <nav className="nl-capture__modes" aria-label="How to enter stories">
          {MODES.map((option) => (
            <button
              key={option.id}
              type="button"
              aria-current={mode === option.id ? "true" : undefined}
              className={
                mode === option.id
                  ? "nl-capture__mode nl-capture__mode--current"
                  : "nl-capture__mode"
              }
              onClick={() => setMode(option.id)}
            >
              {option.label}
            </button>
          ))}
        </nav>
      </div>

      {mode === MODE_WIZARD && <Wizard key={`wizard-${selected.id}`} framework={selected} />}
      {mode === MODE_PAPER && <PaperBatch key={`paper-${selected.id}`} framework={selected} />}
      {mode === MODE_LINKS && <LinkManager frameworks={frameworks} />}
      {mode === MODE_KIOSK && <Kiosk framework={selected} onExit={() => setMode(MODE_WIZARD)} />}
    </div>
  );
}

/**
 * Kiosk mode (PRD §1.2, §5.2).
 *
 * The same wizard, running full-screen on a machine left out at a workshop, and
 * looping straight back to a fresh welcome after every story. Two things differ
 * from admin capture: records are stamped ``entry_mode=kiosk``, and the admin
 * chrome is hidden so the next person does not land in the operator's app.
 *
 * Leaving is deliberately slightly awkward — a corner button rather than a
 * prominent one — because the person at the keyboard is a respondent, not the
 * operator.
 */
function Kiosk({ framework, onExit }) {
  const [round, setRound] = useState(0);

  return (
    <div className="nl-kiosk">
      <Wizard
        key={`kiosk-${framework.id}-${round}`}
        framework={framework}
        submit={(payload) =>
          api.capture({ framework_id: framework.id, entry_mode: "kiosk", ...payload })
        }
        onFinished={() => {
          // Back to a clean welcome, so nobody sees the last person's answers.
          window.setTimeout(() => setRound((n) => n + 1), KIOSK_RESET_DELAY_MS);
        }}
      />
      <button type="button" className="nl-kiosk__exit" onClick={onExit}>
        Leave kiosk mode
      </button>
    </div>
  );
}
