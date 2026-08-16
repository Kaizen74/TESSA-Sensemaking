/*
 * The Patterns tab (PRD §5.4) — Phase 7's half of it.
 *
 * PRD §6 builds this in two passes. This one adds the supporting charts, the
 * filter rail, the version chip and the exports. The Landscape — the hero of
 * the view and the one bold element on the page (constraint 13a) — arrives with
 * Phase 8, and the layout leaves the top of the page to it rather than filling
 * the space with something that would then have to be demoted.
 *
 * Two things this screen must never do, both from constraint 11: draw anything
 * a language model produced, and pool two framework versions without being
 * asked. The first is handled by there being no AI on this path at all; the
 * second is a checkbox, and the chip that appears when it is ticked.
 */

import { useCallback, useEffect, useMemo, useState } from "react";
import { api, ApiError } from "../api.js";
import { BarChart, DyadChart, StonesChart } from "./Charts.jsx";
import "./patterns.css";

/** The provenance fields the rail can filter on, in the order it shows them. */
const FILTERS = [
  { id: "respondent_group", label: "Who told it" },
  { id: "input_method", label: "How it was written" },
  { id: "entry_mode", label: "Where it came from" },
];

/** Every framework sharing a version chain with this one. */
function lineageOf(frameworks, framework) {
  if (!framework) return [];
  const byId = new Map(frameworks.map((row) => [row.id, row]));
  let root = framework;
  const guard = new Set();
  while (root.parent_framework_id && byId.has(root.parent_framework_id) && !guard.has(root.id)) {
    guard.add(root.id);
    root = byId.get(root.parent_framework_id);
  }
  const family = [];
  const frontier = [root];
  while (frontier.length) {
    const current = frontier.pop();
    family.push(current);
    frontier.push(...frameworks.filter((row) => row.parent_framework_id === current.id));
  }
  return family.sort((a, b) => a.version - b.version);
}

export function PatternsTab() {
  const [frameworks, setFrameworks] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [filters, setFilters] = useState({});
  const [mixed, setMixed] = useState(false);
  const [view, setView] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .listFrameworks()
      .then((rows) => {
        setFrameworks(rows);
        setSelectedId(rows[0]?.id ?? null);
      })
      .catch((caught) => setError(caught instanceof ApiError ? caught : null));
  }, []);

  const params = useMemo(() => ({ ...filters, mixed }), [filters, mixed]);

  const load = useCallback(async () => {
    if (selectedId === null) return;
    try {
      setView(await api.getPatterns(selectedId, params));
      setError(null);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : null);
    }
  }, [selectedId, params]);

  useEffect(() => {
    load();
  }, [load]);

  if (error && view === null) {
    return (
      <div className="nl-patterns">
        <ErrorNote error={error} />
      </div>
    );
  }

  if (frameworks === null || (selectedId !== null && view === null)) {
    return (
      <div className="nl-patterns">
        <p className="nl-patterns__empty">Loading…</p>
      </div>
    );
  }

  if (frameworks.length === 0) {
    return (
      <div className="nl-patterns">
        <p className="nl-patterns__empty">
          There are no question sets yet. Go to the <strong>Studio</strong> and
          make one, then collect some stories — patterns need both.
        </p>
      </div>
    );
  }

  const selected = frameworks.find((row) => row.id === selectedId) ?? frameworks[0];
  const family = lineageOf(frameworks, selected);
  const options = optionsFrom(view);

  return (
    <div className="nl-patterns">
      <header className="nl-patterns__head">
        <h2 className="nl-patterns__title">Patterns</h2>
        <p className="nl-patterns__sub">
          Every figure below is counted from stories you validated. Nothing here
          was written or interpreted by AI.
        </p>
      </header>

      {error && <ErrorNote error={error} />}

      <div className="nl-patterns__body">
        {/* The slim rail of §5b's hero layout. It stays slim when the landscape
            arrives above it in Phase 8. */}
        <aside className="nl-rail" aria-label="Filters">
          <label className="nl-rail__field">
            <span className="nl-rail__label">Question set</span>
            <select
              className="nl-rail__select"
              value={selected.id}
              onChange={(event) => {
                setSelectedId(Number(event.target.value));
                setFilters({});
                setMixed(false);
              }}
            >
              {frameworks.map((row) => (
                <option key={row.id} value={row.id}>
                  {row.name} — v{row.version}
                </option>
              ))}
            </select>
          </label>

          {FILTERS.map((filter) => (
            <label key={filter.id} className="nl-rail__field">
              <span className="nl-rail__label">{filter.label}</span>
              <select
                className="nl-rail__select"
                value={filters[filter.id] ?? ""}
                onChange={(event) =>
                  setFilters((current) => {
                    const next = { ...current };
                    if (event.target.value) next[filter.id] = event.target.value;
                    else delete next[filter.id];
                    return next;
                  })
                }
              >
                <option value="">Everyone</option>
                {(options[filter.id] ?? []).map((value) => (
                  <option key={value} value={value}>
                    {value}
                  </option>
                ))}
              </select>
            </label>
          ))}

          {family.length > 1 && (
            <label className="nl-rail__check">
              <input
                type="checkbox"
                checked={mixed}
                onChange={(event) => setMixed(event.target.checked)}
              />
              <span>
                Include the other {family.length - 1}{" "}
                {family.length === 2 ? "version" : "versions"} of this question set
              </span>
            </label>
          )}

          {Object.keys(filters).length > 0 && (
            <button
              type="button"
              className="nl-rail__clear"
              onClick={() => setFilters({})}
            >
              Clear filters
            </button>
          )}

          <div className="nl-rail__exports">
            <a className="nl-rail__download" href={api.exportCsvUrl(selected.id, params)}>
              Download the stories (CSV)
            </a>
            <a className="nl-rail__download" href={api.exportBriefUrl(selected.id, params)}>
              Download the Pattern Brief
            </a>
          </div>
        </aside>

        <div className="nl-patterns__main">
          <p className="nl-patterns__count">
            <strong>{view.total}</strong> {view.total === 1 ? "story" : "stories"} in this
            view
          </p>

          {view.mixed && view.versions.length > 1 && <VersionChip versions={view.versions} />}

          {view.total === 0 ? (
            <p className="nl-patterns__empty">
              No validated stories match this. Collect some under{" "}
              <strong>Capture &amp; Links</strong>, or check the queue under{" "}
              <strong>Import &amp; Validate</strong>.
            </p>
          ) : (
            <>
              <section className="nl-patterns__band">
                <h3 className="nl-patterns__band-title">What people said</h3>
                <div className="nl-patterns__grid">
                  {view.dyads.map((chart) => (
                    <DyadChart key={chart.id} chart={chart} />
                  ))}
                  {view.mcqs.map((chart) => (
                    <BarChart key={chart.id} chart={chart} />
                  ))}
                  {view.stones && <StonesChart chart={view.stones} />}
                </div>
              </section>

              <section className="nl-patterns__band">
                <h3 className="nl-patterns__band-title">Who told these stories</h3>
                <div className="nl-patterns__grid">
                  {view.demographics.map((chart) => (
                    <BarChart key={chart.id} chart={chart} />
                  ))}
                </div>
              </section>
            </>
          )}

          <p className="nl-patterns__soon">
            The Narrative Landscape — the terrain that shows where stories cluster
            on each triangle — arrives with the next stage of the build, and will
            sit above these charts as the main view.
          </p>
        </div>
      </div>
    </div>
  );
}

/**
 * The values each filter can actually take, read off the unfiltered charts.
 *
 * Taken from the data rather than from a fixed list, so the rail never offers a
 * choice that would empty the screen.
 */
function optionsFrom(view) {
  const options = {};
  for (const chart of view?.demographics ?? []) {
    options[chart.id] = chart.bars.filter((bar) => bar.count > 0).map((bar) => bar.label);
  }
  return options;
}

/** The version chip (§5.4): shown whenever a view spans framework versions. */
function VersionChip({ versions }) {
  return (
    <p className="nl-version-chip" role="note">
      <strong>Mixed versions.</strong>{" "}
      {versions.map((entry) => `v${entry.version} (${entry.count})`).join(" · ")} — these
      stories answered different wording, so compare them with care.
    </p>
  );
}

function ErrorNote({ error }) {
  return (
    <div className="nl-patterns__error" role="alert">
      <p className="nl-patterns__error-message">{error?.message ?? "Something went wrong."}</p>
      {error?.action && <p className="nl-patterns__error-action">{error.action}</p>}
    </div>
  );
}
