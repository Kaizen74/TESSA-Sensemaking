/*
 * The Patterns tab (PRD §5.4) — landscape-first.
 *
 * It opens on the Landscape. That is the whole point of §5.4 and of constraint
 * 13a: the terrain is the visual anchor, the filter rail is slim beside it, and
 * the supporting charts sit in a quiet band a click away. A first-time viewer
 * should be able to say what they are looking at and where the stories cluster
 * without touching anything (§5b's ten-second test).
 *
 * Four sub-views, in the order §5.4 lists them: Landscape (default), Supporting
 * charts, 3D Explorer, and the stories a region holds. Everything reads the
 * same scope — one framework version unless mixing is asked for, and whatever
 * filters the rail has set — so no two views on this page can disagree about
 * which stories they are about.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { api, ApiError } from "../api.js";
import { BarChart, DyadChart, StonesChart } from "./Charts.jsx";
import { ExplorerView } from "./Explorer.jsx";
import { StoryBrowser } from "./StoryBrowser.jsx";
import { LandscapeView } from "./Landscape.jsx";
import {
  chartsFilename,
  saveChartsSnapshot,
  saveContourSnapshot,
  snapshotFilename,
} from "./snapshot.js";
import "./patterns.css";

const VIEW_LANDSCAPE = "landscape";
const VIEW_CHARTS = "charts";
const VIEW_EXPLORER = "explorer";
const VIEW_STORIES = "stories";

const SUB_VIEWS = [
  { id: VIEW_LANDSCAPE, label: "Landscape" },
  { id: VIEW_CHARTS, label: "Supporting charts" },
  { id: VIEW_EXPLORER, label: "3D Explorer" },
  { id: VIEW_STORIES, label: "Story browser" },
];

const FILTERS = [
  { id: "respondent_group", label: "Who told it" },
  { id: "input_method", label: "How it was written" },
  { id: "entry_mode", label: "Where it came from" },
];

/*
 * Whose interpretation a figure is made of (constraint 14).
 *
 * A segmented control rather than a dropdown, because the choice is epistemic:
 * which of these three you are looking at changes what the picture *means*, and
 * that should be readable without opening anything.
 */
const SIGNIFIED_BY_DEFAULT = "participant";

const PROVENANCE_CHOICES = [
  {
    id: "participant",
    label: "Storyteller",
    description: "Told and interpreted by the storyteller",
  },
  {
    id: "ai_validated",
    label: "Expert-validated",
    description: "Interpreted by someone else and confirmed by you",
  },
  { id: "all", label: "Both", description: "Both kinds together" },
];

function provenanceChoice(id) {
  return PROVENANCE_CHOICES.find((choice) => choice.id === id) ?? PROVENANCE_CHOICES[0];
}

/** The three-way choice, in the rail. */
function ProvenanceControl({ value, onChange }) {
  return (
    <div className="nl-rail__field">
      <span className="nl-rail__label" id="nl-provenance-label">
        Whose interpretation
      </span>
      <div className="nl-provenance" role="radiogroup" aria-labelledby="nl-provenance-label">
        {PROVENANCE_CHOICES.map((choice) => (
          <button
            key={choice.id}
            type="button"
            role="radio"
            aria-checked={value === choice.id}
            className={
              value === choice.id
                ? "nl-provenance__option nl-provenance__option--current"
                : "nl-provenance__option"
            }
            onClick={() => onChange(choice.id)}
          >
            {choice.label}
          </button>
        ))}
      </div>
      <p className="nl-rail__aside">{provenanceChoice(value).description}.</p>
    </div>
  );
}

/**
 * What the figures above are made of, said out loud (constraint 14).
 *
 * Only when the view is not the default: the storytellers' own readings need no
 * disclaimer, and a banner on every screen would be one nobody reads. Context
 * weight, not an alert — this is a fact about the picture, not a problem with it.
 */
function ProvenanceLabel({ applied, counts }) {
  if (!applied || applied === SIGNIFIED_BY_DEFAULT) return null;
  const held = counts ?? { participant: 0, ai_validated: 0 };
  const other = applied === "all" ? null : held.participant;
  return (
    <p className="nl-provenance-note" role="status">
      {provenanceChoice(applied).description}.{" "}
      {applied === "all"
        ? `${held.participant} of these marks were placed by the storyteller and ` +
          `${held.ai_validated} by somebody reading their story.`
        : `${other} marks placed by storytellers themselves are not in this view.`}
    </p>
  );
}

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
  // Constraint 14: the default is the storytellers' own readings, and nothing
  // else. Every request on this screen carries it, so no view can drift into
  // showing a mixture without the reader having asked for one.
  const [signifiedBy, setSignifiedBy] = useState(SIGNIFIED_BY_DEFAULT);
  const [mixed, setMixed] = useState(false);
  const [splitBy, setSplitBy] = useState("");
  const [subView, setSubView] = useState(VIEW_LANDSCAPE);
  const [triadId, setTriadId] = useState(null);
  const [view, setView] = useState(null);
  const [land, setLand] = useState(null);
  const [explorer, setExplorer] = useState(null);
  const [clusters, setClusters] = useState(null);
  const [k, setK] = useState(3);
  const [showClusters, setShowClusters] = useState(false);
  const [region, setRegion] = useState(null);
  const [error, setError] = useState(null);
  const chartsRef = useRef(null);

  useEffect(() => {
    api
      .listFrameworks()
      .then((rows) => {
        setFrameworks(rows);
        setSelectedId(rows[0]?.id ?? null);
      })
      .catch((caught) => setError(caught instanceof ApiError ? caught : null));
  }, []);

  const params = useMemo(
    () => ({ ...filters, mixed, signified_by: signifiedBy }),
    [filters, mixed, signifiedBy],
  );

  const loadPatterns = useCallback(async () => {
    if (selectedId === null) return;
    try {
      setView(await api.getPatterns(selectedId, params));
      setError(null);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : null);
    }
  }, [selectedId, params]);

  useEffect(() => {
    loadPatterns();
  }, [loadPatterns]);

  // The triad the landscape is about. Defaults to the first, which is what
  // §5b's "zero clicks to a meaningful default" asks for.
  const triads = view?.triads ?? [];
  const currentTriad = triadId ?? triads[0]?.id ?? null;

  useEffect(() => {
    setTriadId(null);
    setRegion(null);
  }, [selectedId]);

  const loadLandscape = useCallback(async () => {
    if (selectedId === null || !currentTriad) {
      setLand(null);
      return;
    }
    try {
      setLand(
        await api.getLandscape(selectedId, currentTriad, {
          ...params,
          ...(splitBy ? { split_by: splitBy } : {}),
        }),
      );
      setError(null);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : null);
    }
  }, [selectedId, currentTriad, params, splitBy]);

  useEffect(() => {
    if (subView === VIEW_LANDSCAPE) loadLandscape();
  }, [subView, loadLandscape]);

  useEffect(() => {
    if (subView !== VIEW_EXPLORER || selectedId === null) return;
    api
      .getExplorer(selectedId, params)
      .then(setExplorer)
      .catch((caught) => setError(caught instanceof ApiError ? caught : null));
  }, [subView, selectedId, params]);

  useEffect(() => {
    if (subView !== VIEW_EXPLORER || !showClusters || selectedId === null) return;
    api
      .getClusters(selectedId, { ...params, k })
      .then(setClusters)
      .catch((caught) => setError(caught instanceof ApiError ? caught : null));
  }, [subView, showClusters, selectedId, params, k]);

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
                setSplitBy("");
              }}
            >
              {frameworks.map((row) => (
                <option key={row.id} value={row.id}>
                  {row.name} — v{row.version}
                </option>
              ))}
            </select>
          </label>

          <ProvenanceControl value={signifiedBy} onChange={setSignifiedBy} />

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

          {subView === VIEW_LANDSCAPE && (
            <label className="nl-rail__field">
              <span className="nl-rail__label">Side by side</span>
              <select
                className="nl-rail__select"
                value={splitBy}
                onChange={(event) => setSplitBy(event.target.value)}
              >
                <option value="">One landscape</option>
                {FILTERS.map((filter) => (
                  <option key={filter.id} value={filter.id}>
                    Split by {filter.label.toLowerCase()}
                  </option>
                ))}
              </select>
            </label>
          )}

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
            <button type="button" className="nl-rail__clear" onClick={() => setFilters({})}>
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
            <a className="nl-rail__download" href={api.exportHeardUrl(selected.id, params)}>
              Download “What we heard”
            </a>
            <p className="nl-rail__aside">
              “What we heard” is the one to give back: no stories, no history,
              nothing fewer than five people said.
            </p>
            {subView === VIEW_LANDSCAPE && land?.panels?.[0]?.has_surface && (
              <button
                type="button"
                className="nl-rail__clear"
                onClick={() =>
                  saveContourSnapshot(land.panels[0], snapshotFilename(land, selected))
                }
              >
                Save the contour as a picture
              </button>
            )}
            {subView === VIEW_CHARTS && (
              <button
                type="button"
                className="nl-rail__clear"
                onClick={() =>
                  saveChartsSnapshot(chartsRef.current, chartsFilename(view, selected))
                }
              >
                Save these charts as a picture
              </button>
            )}
          </div>
        </aside>

        <div className="nl-patterns__main">
          <nav className="nl-patterns__views" aria-label="Ways of looking">
            {SUB_VIEWS.map((entry) => (
              <button
                key={entry.id}
                type="button"
                className={
                  subView === entry.id
                    ? "nl-import__view nl-import__view--current"
                    : "nl-import__view"
                }
                aria-current={subView === entry.id ? "true" : undefined}
                onClick={() => setSubView(entry.id)}
              >
                {entry.label}
              </button>
            ))}
          </nav>

          {/* The story browser prints "3 of 20" itself, which says more than
              this line does. Two counts of the same thing, in two shapes, is
              one more than a reader needs. */}
          {subView !== VIEW_STORIES && (
            <p className="nl-patterns__count">
              <strong>{view.total}</strong> {view.total === 1 ? "story" : "stories"} in
              this view
            </p>
          )}

          {view.mixed && view.versions.length > 1 && <VersionChip versions={view.versions} />}

          <ProvenanceLabel
            applied={view.signified_by_applied}
            counts={view.counts_by_signified_by}
          />

          {view.total === 0 ? (
            <p className="nl-patterns__empty">
              No validated stories match this. Collect some under{" "}
              <strong>Capture &amp; Links</strong>, or check the queue under{" "}
              <strong>Import &amp; Validate</strong>.
            </p>
          ) : (
            <>
              {subView === VIEW_LANDSCAPE && (
                <>
                  {triads.length === 0 ? (
                    <p className="nl-patterns__empty">
                      A landscape is drawn from a triangle, and this question set
                      has none. Add one in the <strong>Studio</strong>.
                    </p>
                  ) : (
                    <>
                      {/* A row of buttons only when there is a choice to make.
                          One triangle in the set makes it one button that
                          cannot change anything, standing between the reader
                          and the picture — so it becomes what it always was,
                          the name of the question being looked at. */}
                      {triads.length === 1 && (
                        <p className="nl-patterns__triad-name">{triads[0].title}</p>
                      )}
                      {triads.length > 1 && (
                        <div className="nl-patterns__triads">
                          {triads.map((triad) => (
                            <button
                              key={triad.id}
                              type="button"
                              className={
                                triad.id === currentTriad
                                  ? "nl-import__view nl-import__view--current"
                                  : "nl-import__view"
                              }
                              onClick={() => {
                                setTriadId(triad.id);
                                setRegion(null);
                              }}
                            >
                              {triad.title}
                            </button>
                          ))}
                        </div>
                      )}
                      {land ? (
                        <LandscapeView view={land} onRegion={setRegion} />
                      ) : (
                        <p className="nl-patterns__empty">Drawing the landscape…</p>
                      )}
                      {region && (
                        <RegionDrawer
                          region={region}
                          view={view}
                          frameworkId={selected.id}
                          params={params}
                          onClose={() => setRegion(null)}
                        />
                      )}
                      <AnalystNotes count={view.total} />
                    </>
                  )}
                </>
              )}

              {subView === VIEW_CHARTS && (
                <div ref={chartsRef}>
                  <section className="nl-patterns__band">
                    <h3 className="nl-patterns__band-title">What people said</h3>
                    {/* A question set can be a prompt and nothing else, and then
                        this band has no charts to draw. A heading over empty
                        space reads as a fault; say what is missing instead. */}
                    {view.dyads.length === 0 &&
                    view.mcqs.length === 0 &&
                    !view.stones ? (
                      <p className="nl-patterns__empty">
                        This question set asks for the story and nothing else, so
                        there is nothing to chart here. Add a slider, a choice or
                        a square in the <strong>Studio</strong> — or read the
                        landscape, which needs only a triangle.
                      </p>
                    ) : (
                      <div className="nl-patterns__grid">
                        {view.dyads.map((chart) => (
                          <DyadChart key={chart.id} chart={chart} />
                        ))}
                        {view.mcqs.map((chart) => (
                          <BarChart key={chart.id} chart={chart} />
                        ))}
                        {view.stones && <StonesChart chart={view.stones} />}
                      </div>
                    )}
                  </section>

                  <section className="nl-patterns__band">
                    <h3 className="nl-patterns__band-title">Who told these stories</h3>
                    <div className="nl-patterns__grid">
                      {/* A bar chart is a comparison. One answer at 100% has
                          nothing to compare it to — it is a fact about the set,
                          and the CSV carries it. Drawing it is chart junk
                          (constraint 13d), so it waits until there are two. */}
                      {view.demographics
                        .filter(
                          (chart) => chart.bars.filter((bar) => bar.count > 0).length > 1,
                        )
                        .map((chart) => (
                          <BarChart key={chart.id} chart={chart} />
                        ))}
                    </div>
                  </section>
                </div>
              )}

              {subView === VIEW_EXPLORER &&
                (explorer ? (
                  <ExplorerView
                    explorer={explorer}
                    clusters={clusters}
                    k={k}
                    onK={setK}
                    showClusters={showClusters}
                    onShowClusters={setShowClusters}
                  />
                ) : (
                  <p className="nl-patterns__empty">Loading…</p>
                ))}

              {subView === VIEW_STORIES && (
                <StoryBrowser framework={selected} params={params} />
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * The stories under a peak or a region (§1.5: region → stories).
 *
 * The ids come from the landscape's own grid cells, so this list is exactly
 * what is under that hill — not a re-query that might round differently.
 */
function RegionDrawer({ region, view, frameworkId, params, onClose }) {
  const ids = useMemo(() => [...new Set(region.anecdote_ids ?? [])], [region]);
  const [named, setNamed] = useState(null);

  // The names, fetched for exactly these ids. The landscape's cells decide
  // *which* stories are here; this only asks what they are called, so a slow or
  // failed lookup leaves the list of ids standing rather than emptying it.
  useEffect(() => {
    let live = true;
    if (frameworkId === null || ids.length === 0) {
      setNamed(null);
      return undefined;
    }
    api
      .browseStories(frameworkId, { ...params, ids: ids.join(",") })
      .then((page) => {
        if (!live) return;
        setNamed(new Map(page.stories.map((story) => [story.anecdote_id, story])));
      })
      .catch(() => {
        if (live) setNamed(null);
      });
    return () => {
      live = false;
    };
  }, [frameworkId, ids, params]);

  return (
    <aside className="nl-region" aria-label="Stories in this region">
      <div className="nl-region__head">
        <h3 className="nl-region__title">
          {region.count} {region.count === 1 ? "story" : "stories"} near{" "}
          {region.nearest_corner}
        </h3>
        <button type="button" className="nl-region__close" onClick={onClose}>
          Close
        </button>
      </div>
      <ul className="nl-region__list">
        {ids.map((id) => {
          const story = named?.get(id) ?? null;
          return (
            <li key={id} className="nl-region__story">
              <span className="nl-region__id">#{id}</span>
              {story?.title && <span className="nl-region__name">{story.title}</span>}
              {story?.respondent_title && (
                <span className="nl-region__by">named by the storyteller</span>
              )}
            </li>
          );
        })}
      </ul>
      <p className="nl-region__note">
        These are the {ids.length} stories whose marks sit under that peak, out of{" "}
        {view.total} in this view. Open the CSV to read them in full.
      </p>
    </aside>
  );
}

/** The analyst notes panel (§1.5, constraint 12). */
function AnalystNotes({ count }) {
  return (
    <details className="nl-notes">
      <summary className="nl-notes__summary">How to read a landscape</summary>
      <div className="nl-notes__body">
        <p>
          The height is how thickly stories lie, not how important they are. A
          tall hill means many people put their mark in the same place; it says
          nothing about whether they were right.
        </p>
        <p>
          <strong>Triangles are closure-constrained.</strong> The three weights
          must add to one, so a rise on one corner is a fall on another. That is
          arithmetic, not a finding — read the shape of the whole, and be careful
          about reading any single corner on its own.
        </p>
        <p>
          <strong>This is exploratory.</strong> A cluster shows you where to look
          next and which stories to read. It is not evidence that anything caused
          anything, and {count} {count === 1 ? "story" : "stories"} is a set of
          accounts rather than a sample of a population.
        </p>
        <p>
          The contour twin is the same landscape seen from directly above. Use it
          when you want to measure rather than to look — and it is what a saved
          picture gives you, because a contour can be read off a printed page.
        </p>
      </div>
    </details>
  );
}

function optionsFrom(view) {
  const options = {};
  for (const chart of view?.demographics ?? []) {
    options[chart.id] = chart.bars.filter((bar) => bar.count > 0).map((bar) => bar.label);
  }
  return options;
}

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
