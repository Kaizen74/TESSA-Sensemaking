/*
 * The admin app shell.
 *
 * PRD §5 gives it four tabs, and all four are built: the Studio, Capture &
 * Links, Import & Validate, and Patterns. Patterns opens on the Landscape,
 * which is the view the rest of the app exists to fill.
 */

import { useState } from "react";
import { Studio } from "./studio/Studio.jsx";
import { CaptureTab } from "./capture/CaptureTab.jsx";
import { PublicCapture, captureTokenFromPath } from "./capture/PublicCapture.jsx";
import { ImportTab } from "./import/ImportTab.jsx";
import { PatternsTab } from "./patterns/Patterns.jsx";
import "./app.css";

const TABS = [
  { id: "studio", label: "Studio" },
  { id: "capture", label: "Capture & Links" },
  { id: "import", label: "Import & Validate" },
  { id: "patterns", label: "Patterns" },
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
        <h1 className="nl-nav__brand">Narrative Lens</h1>
        <ul className="nl-nav__list">
          {TABS.map((tab) => (
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
          ))}
        </ul>
      </nav>
      {current === "studio" && <Studio />}
      {current === "capture" && <CaptureTab />}
      {current === "import" && <ImportTab />}
      {current === "patterns" && <PatternsTab />}
    </div>
  );
}
