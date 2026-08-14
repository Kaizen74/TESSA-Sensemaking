/*
 * The admin app shell.
 *
 * PRD §5 gives it four tabs. Phase 2 builds the Studio; the other three arrive
 * with the phases that own them, and are shown as not-yet-built rather than
 * hidden, so the operator can see where the app is going.
 */

import { Studio } from "./studio/Studio.jsx";
import "./app.css";

const TABS = [
  { id: "studio", label: "Studio", ready: true },
  { id: "capture", label: "Capture & Links", ready: false },
  { id: "import", label: "Import & Validate", ready: false },
  { id: "patterns", label: "Patterns", ready: false },
];

export function App() {
  return (
    <div className="nl-app">
      <nav className="nl-nav" aria-label="Sections">
        <span className="nl-nav__brand">Narrative Lens</span>
        <ul className="nl-nav__list">
          {TABS.map((tab) => (
            <li key={tab.id}>
              <span
                className={tab.ready ? "nl-nav__tab nl-nav__tab--current" : "nl-nav__tab"}
                aria-current={tab.ready ? "page" : undefined}
                aria-disabled={tab.ready ? undefined : "true"}
              >
                {tab.label}
                {!tab.ready && <span className="nl-nav__soon"> — coming soon</span>}
              </span>
            </li>
          ))}
        </ul>
      </nav>
      <Studio />
    </div>
  );
}
