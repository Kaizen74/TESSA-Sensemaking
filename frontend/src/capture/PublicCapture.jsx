/*
 * The page a scanned QR opens (PRD §1.2, §7.6).
 *
 * This is the only screen a respondent ever sees, and it is the whole app as far
 * as they are concerned: no admin navigation, no tabs, nothing about the
 * operator's setup. Just the wizard, at the width constraint 10 sets.
 *
 * The token in the URL decides everything. This component never sends a
 * framework id — the server resolves it, so a respondent's browser cannot point
 * its story at a different question set.
 */

import { useEffect, useState } from "react";
import { api, ApiError } from "../api.js";
import { Wizard } from "./Wizard.jsx";
import "./public-capture.css";

export function PublicCapture({ token }) {
  const [framework, setFramework] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    api
      .publicFramework(token)
      .then((body) => {
        if (cancelled) return;
        // The wizard keys its draft on a framework id; a respondent only ever
        // has one link open, so the token stands in for it.
        setFramework({
          id: `link-${token}`,
          definition: body.definition,
          version: body.framework_version,
        });
      })
      .catch((caught) => {
        if (!cancelled) setError(caught instanceof ApiError ? caught : null);
      });
    return () => {
      cancelled = true;
    };
  }, [token]);

  if (error) {
    return (
      <main className="nl-public">
        <div className="nl-public__notice" role="alert">
          <h1 className="nl-public__title">{error.message}</h1>
          {error.action && <p className="nl-public__action">{error.action}</p>}
        </div>
      </main>
    );
  }

  if (!framework) {
    return (
      <main className="nl-public">
        <p className="nl-public__loading">Loading the questions…</p>
      </main>
    );
  }

  return (
    <main className="nl-public">
      <Wizard
        framework={framework}
        submit={(payload) => api.publicCapture(token, payload)}
      />
    </main>
  );
}

/** The token in a ``/c/{token}`` address, or null when this is not that page. */
export function captureTokenFromPath(pathname) {
  const match = /^\/c\/([A-Za-z0-9_-]+)\/?$/.exec(pathname ?? "");
  return match ? match[1] : null;
}
