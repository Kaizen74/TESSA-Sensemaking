/*
 * The admin app shell.
 *
 * PRD §5 gives it four tabs. They are still four places, but they are shown as
 * what they actually are: the four stages of one piece of work, in the order an
 * operator does them — Design a question set, Collect stories against it,
 * Validate what came in, Read what it says.
 *
 * The spine carries live counts, so the state of the study is readable from any
 * stage without going to look. Stages stay always-clickable: this is a progress
 * indicator, not a wizard, and somebody returning to a finished study has to
 * reach any stage at once.
 *
 * Counts come from three calls the app already makes — the framework list, the
 * capture links, the queue. Nothing is polled and nothing is scheduled; they are
 * fetched on load and again when the operator changes stage, which is the moment
 * they were going to look anyway.
 */

import { useCallback, useEffect, useState } from "react";
import { api } from "./api.js";
import { Studio } from "./studio/Studio.jsx";
import { CaptureTab } from "./capture/CaptureTab.jsx";
import { PublicCapture, captureTokenFromPath } from "./capture/PublicCapture.jsx";
import { ImportTab } from "./import/ImportTab.jsx";
import { PatternsTab } from "./patterns/Patterns.jsx";
import "./app.css";

/** Where a stage's own controls are rendered, from inside the stage. */
export const STAGE_ASIDE_ID = "nl-stage-aside";

const STAGES = [
  {
    id: "studio",
    label: "Design",
    tab: "Studio",
    detail: (s) =>
      s.frameworks === null
        ? "…"
        : s.latest
          ? `v${s.latest.version} · ${s.latest.signifier_count} ${
              s.latest.signifier_count === 1 ? "question" : "questions"
            }`
          : "no question set yet",
    done: (s) => Boolean(s.latest),
  },
  {
    id: "capture",
    label: "Collect",
    tab: "Capture & Links",
    detail: (s) =>
      s.frameworks === null
        ? "…"
        : `${s.stories} ${s.stories === 1 ? "story" : "stories"} · ${s.openLinks} ${
            s.openLinks === 1 ? "link" : "links"
          } open`,
    done: (s) => s.stories > 0,
  },
  {
    id: "import",
    label: "Validate",
    tab: "Import & Validate",
    detail: (s) => (s.pending === null ? "…" : `${s.pending} waiting for you`),
    // The one stage whose marker is a number rather than a tick: work waiting
    // is the thing an operator most needs to see from somewhere else.
    mark: (s) => (s.pending ? String(s.pending) : null),
    done: (s) => s.pending === 0,
    urgent: (s) => Boolean(s.pending),
  },
  {
    id: "patterns",
    label: "Read",
    tab: "Patterns",
    detail: (s) =>
      s.frameworks === null
        ? "…"
        : `${s.stories} ${s.stories === 1 ? "story" : "stories"} to read`,
    done: (s) => s.stories > 0,
  },
];

/*
 * What the bar says on each stage, and the one line of context under it.
 *
 * The note is the sentence an operator needs at that moment and nowhere else —
 * the thing that is true of this stage and easy to forget.
 */
const BAR = {
  studio: {
    label: "Editing",
    note:
      "Once stories exist, changing the words is not free — the app will ask " +
      "which kind of change you are making, because only you know.",
  },
  capture: {
    label: "Collecting into",
    note:
      "Every way in stamps how it arrived, so paper stories and phone stories " +
      "stay tellable apart later.",
  },
  import: {
    label: "Queue",
    note:
      "Nothing the AI proposes enters your data on its own — not at high " +
      "confidence, not at low.",
  },
  patterns: {
    label: "Reading",
    note:
      "Every figure is counted from stories you validated, and the rail says " +
      "whose readings they are.",
  },
};

function stageOf(id) {
  return STAGES.find((stage) => stage.id === id) ?? STAGES[0];
}

export function App() {
  const [current, setCurrent] = useState("studio");
  const [frameworks, setFrameworks] = useState(null);
  const [links, setLinks] = useState([]);
  const [pending, setPending] = useState(null);
  const [asOf, setAsOf] = useState(null);
  /*
   * Stories are the one figure that moves without the operator, while a link is
   * open. It is announced rather than folded in, because a number that changes
   * under somebody mid-analysis destroys the analysis — and silently re-scoping
   * a landscape is worse than showing a stale one.
   */
  const [acknowledged, setAcknowledged] = useState(null);

  const refresh = useCallback(async () => {
    try {
      const [sets, openLinks, queue] = await Promise.all([
        api.listFrameworks(),
        api.listCaptureLinks(),
        api.readQueue(),
      ]);
      setFrameworks(sets);
      setLinks(openLinks);
      setPending(queue?.counts?.pending ?? 0);
      setAsOf(new Date());
      setAcknowledged((held) =>
        held === null ? sets.reduce((sum, s) => sum + (s.anecdote_count ?? 0), 0) : held,
      );
    } catch {
      // The spine is a convenience. If a count cannot be fetched the app still
      // works, so this stays silent rather than putting an error over the top
      // of whatever the operator came here to do.
      setFrameworks((held) => held ?? []);
      setPending((held) => (held === null ? 0 : held));
    }
  }, []);

  // On load, and whenever the operator changes stage — which is the moment they
  // were going to look at these numbers anyway. No timer, no socket, no poll.
  useEffect(() => {
    refresh();
  }, [refresh, current]);

  // A scanned QR lands on /c/{token}. That is a respondent's page, so it gets
  // the wizard alone — no admin navigation, nothing about the operator's setup.
  const token = captureTokenFromPath(
    typeof window === "undefined" ? "" : window.location.pathname,
  );
  if (token) return <PublicCapture token={token} />;

  const live = (frameworks ?? []).filter((set) => set.is_active !== false);
  const latest = live.length
    ? live.reduce((newest, set) => (set.version >= newest.version ? set : newest))
    : null;
  const stories = (frameworks ?? []).reduce((sum, set) => sum + (set.anecdote_count ?? 0), 0);
  const openLinks = links.filter((link) => link.is_active).length;
  const state = { frameworks, latest, stories, openLinks, pending };

  const arrivals = acknowledged === null ? 0 : Math.max(0, stories - acknowledged);
  const stamp = asOf
    ? `as of ${asOf.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`
    : "";

  const stage = stageOf(current);
  const bar = BAR[current];

  return (
    <div className="nl-app">
      <a className="nl-app__skip" href="#nl-main">
        Skip to the page
      </a>

      <aside className="nl-shell" aria-label="Where you are">
        <h1 className="nl-shell__brand">Narrative Lens</h1>

        <nav aria-label="Stages">
          <ol className="nl-spine">
            {STAGES.map((entry) => {
              const isCurrent = entry.id === current;
              const done = entry.done(state);
              const urgent = entry.urgent?.(state);
              const mark = entry.mark?.(state) ?? (done ? "✓" : "");
              return (
                <li key={entry.id} className="nl-spine__item">
                  <button
                    type="button"
                    className={
                      isCurrent ? "nl-spine__stage nl-spine__stage--current" : "nl-spine__stage"
                    }
                    aria-current={isCurrent ? "page" : undefined}
                    onClick={() => setCurrent(entry.id)}
                  >
                    <span
                      className={
                        "nl-spine__mark" +
                        (isCurrent ? " nl-spine__mark--current" : "") +
                        (urgent && !isCurrent ? " nl-spine__mark--urgent" : "") +
                        (done && !isCurrent && !urgent ? " nl-spine__mark--done" : "")
                      }
                      aria-hidden="true"
                    >
                      {mark}
                    </span>
                    <span className="nl-spine__text">
                      <span className="nl-spine__label">{entry.label}</span>
                      <span className="nl-spine__detail">{entry.detail(state)}</span>
                    </span>
                  </button>
                  {entry.id === "capture" && arrivals > 0 && (
                    <button
                      type="button"
                      className="nl-spine__arrivals"
                      onClick={() => setAcknowledged(stories)}
                    >
                      {arrivals} new · fold in
                    </button>
                  )}
                </li>
              );
            })}
          </ol>
        </nav>

        {/* Where the stage puts its own controls. The Patterns filter rail
            renders in here, so the page has one left column rather than two. */}
        <div id={STAGE_ASIDE_ID} className="nl-shell__aside" />
      </aside>

      <div className="nl-app__body">
        <header className="nl-topbar">
          <div className="nl-topbar__line">
            <span className="nl-topbar__label">{bar.label}</span>
            {/*
              * No question-set chip.
              *
              * Every stage has a chooser of its own — the Studio's, the capture
              * form's, the Patterns rail's — and the queue is not scoped to a
              * question set at all. A chip up here can only repeat a choice the
              * page already shows or contradict one it does not. The first
              * build of this bar did both: it read "Hangar v1" while the rail
              * below it read "Uneven — v1".
              */}
            <span className="nl-topbar__spacer" />
            {/*
              * Study-wide, and labelled as such. The Patterns page states its
              * own scope a few lines below this bar — "47 stories in this
              * view" — and two numbers on one screen, one of them 167 and the
              * other 47, both called "stories", is worse than one number.
              */}
            <span className="nl-topbar__figure">
              <strong>{stage.id === "import" ? (pending ?? 0) : stories}</strong>{" "}
              {stage.id === "import"
                ? "waiting for you"
                : `${stories === 1 ? "story" : "stories"} in the study`}
            </span>
            {stamp && <span className="nl-topbar__stamp">{stamp}</span>}
          </div>
          <p className="nl-topbar__note">{bar.note}</p>
        </header>

        <main id="nl-main" className="nl-app__main">
          {current === "studio" && <Studio />}
          {current === "capture" && <CaptureTab />}
          {current === "import" && <ImportTab />}
          {current === "patterns" && <PatternsTab />}
        </main>
      </div>
    </div>
  );
}
