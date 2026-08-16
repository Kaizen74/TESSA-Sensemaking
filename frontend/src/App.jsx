/*
 * The admin app shell.
 *
 * PRD §5 gives it four tabs, and from Phase 7 all four are built: the Studio,
 * Capture & Links, Import & Validate, and Patterns. Patterns opens on its
 * supporting charts for now; the Landscape becomes its default view in Phase 8.
 */

import { useState } from "react";
import { Studio } from "./studio/Studio.jsx";
import { CaptureTab } from "./capture/CaptureTab.jsx";
import { PublicCapture, captureTokenFromPath } from "./capture/PublicCapture.jsx";
import { ImportTab } from "./import/ImportTab.jsx";
import { PatternsTab } from "./patterns/Patterns.jsx";
import "./app.css";

const TABS = [
  { id: "studio", label: "Studio", ready: true },
  { id: "capture", label: "Capture & Links", ready: true },
  { id: "import", label: "Import & Validate", ready: true },
  { id: "patterns", label: "Patterns", ready: true },
];

export function App() {
  const [current, setCurrent] = useState("studio");

  // A scanned QR lands on /c/{token}. That is a respondent's page, so it gets
  // the wizard alone — no admin navigation, nothing about the operator's setup.
  const token = captureTokenFromPath(
    typeof window === "undefined" ? "" : window.location.pathname,
  );
  if (token) return <PublicCapture token={token} />;

  return (
    <div className="nl-app">
      <nav className="nl-nav" aria-label="Sections">
        <span className="nl-nav__brand">Narrative Lens</span>
        <ul className="nl-nav__list">
          {TABS.map((tab) =>
            tab.ready ? (
              <li key={tab.id}>
                <button
                  type="button"
                  className={
                    current === tab.id ? "nl-nav__tab nl-nav__tab--current" : "nl-nav__tab"
                  }
                  aria-current={current === tab.id ? "page" : undefined}
                  onClick={() => setCurrent(tab.id)}
                >
                  {tab.label}
                </button>
              </li>
            ) : (
              <li key={tab.id}>
                <span className="nl-nav__tab" aria-disabled="true">
                  {tab.label}
                  {/* Non-breaking: the leading space of an inline element is
                      collapsed, which ran the label into the dash. */}
                  <span className="nl-nav__soon">&nbsp;— coming soon</span>
                </span>
              </li>
            ),
          )}
        </ul>
      </nav>
      {current === "studio" && <Studio />}
      {current === "capture" && <CaptureTab />}
      {current === "import" && <ImportTab />}
      {current === "patterns" && <PatternsTab />}
    </div>
  );
}
