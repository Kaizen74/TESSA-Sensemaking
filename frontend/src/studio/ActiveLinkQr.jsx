/*
 * The QR of the active capture link, on the screen the app opens on
 * (PRD §1.8, acceptance criterion 1).
 *
 * The reason it is here rather than only in the link manager: a workshop starts
 * with somebody holding a laptop and a room full of phones. The first screen
 * should already have the thing those phones need to scan, without the operator
 * having to remember which tab it lives on.
 *
 * Quiet by design — it is a small square in the rail, not a poster. The poster
 * is in Capture & Links, where printing belongs.
 */

import { useEffect, useState } from "react";
import { api } from "../api.js";

export function ActiveLinkQr() {
  const [link, setLink] = useState(undefined);

  useEffect(() => {
    api
      .listCaptureLinks()
      .then((rows) => setLink(rows.find((row) => row.is_active) ?? null))
      .catch(() => setLink(null));
  }, []);

  if (link === undefined) return null;

  if (link === null) {
    return (
      <section className="nl-homeqr">
        <h3 className="nl-homeqr__title">Collecting from phones</h3>
        <p className="nl-homeqr__empty">
          No link is open. Open one under <strong>Capture &amp; Links</strong> and
          its code appears here.
        </p>
      </section>
    );
  }

  return (
    <section className="nl-homeqr">
      <h3 className="nl-homeqr__title">Scan to tell a story</h3>
      <img
        className="nl-homeqr__code"
        src={api.captureLinkQrUrl(link.id)}
        alt={`QR code for the capture link ${link.label || link.framework_name}`}
        width="140"
        height="140"
      />
      <p className="nl-homeqr__meta">
        {link.label || link.framework_name} — v{link.framework_version}
      </p>
      <p className="nl-homeqr__url">{link.url}</p>
    </section>
  );
}
