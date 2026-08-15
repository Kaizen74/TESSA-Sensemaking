/*
 * The admin app shell.
 *
 * PRD §5 gives it four tabs. Phase 2 built the Studio and Phase 3 adds Capture;
 * the remaining two arrive with the phases that own them, and are shown as
 * not-yet-built rather than hidden, so the operator can see where the app is
 * going.
 */

import { useState } from "react";
import { Studio } from "./studio/Studio.jsx";
import { CaptureTab } from "./capture/CaptureTab.jsx";
import { PublicCapture, captureTokenFromPath } from "./capture/PublicCapture.jsx";
import "./app.css";

const TABS = [
  { id: "studio", label: "Studio", ready: true },
  { id: "capture", label: "Capture & Links", ready: true },
  { id: "import", label: "Import & Validate", ready: false },
  { id: "patterns", label: "Patterns", ready: false },
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
                  <span className="nl-nav__soon"> — coming soon</span>
                </span>
              </li>
            ),
          )}
        </ul>
      </nav>
      {current === "studio" ? <Studio /> : <CaptureTab />}
    </div>
  );
}
