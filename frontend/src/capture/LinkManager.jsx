/*
 * The link manager and QR poster (PRD §5.2, §1.8).
 *
 * A capture link is something physical in practice: a QR printed and stuck on a
 * wall where people work. So the poster is a first-class output here, printable
 * to the same black-on-white standard as the paper pack (§5b print grammar).
 *
 * Revoking is presented as what it is — permanent, and the way to close a link
 * you have taken down off a wall.
 */

import { useCallback, useEffect, useState } from "react";
import { api, ApiError } from "../api.js";
import "./link-manager.css";

export function LinkManager({ frameworks }) {
  const [links, setLinks] = useState(null);
  const [selectedFrameworkId, setSelectedFrameworkId] = useState(frameworks[0]?.id ?? null);
  const [label, setLabel] = useState("");
  const [poster, setPoster] = useState(null);
  const [confirming, setConfirming] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    try {
      setLinks(await api.listCaptureLinks());
      setError(null);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : null);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function create() {
    if (!selectedFrameworkId) return;
    setBusy(true);
    try {
      await api.createCaptureLink(selectedFrameworkId, label.trim() || null);
      setLabel("");
      await refresh();
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : null);
    } finally {
      setBusy(false);
    }
  }

  async function revoke(link) {
    setBusy(true);
    try {
      await api.revokeCaptureLink(link.id);
      setConfirming(null);
      await refresh();
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : null);
    } finally {
      setBusy(false);
    }
  }

  if (poster) {
    return <Poster link={poster} onClose={() => setPoster(null)} />;
  }

  return (
    <div className="nl-links">
      <header className="nl-links__head">
        <h2 className="nl-links__title">Links &amp; QR posters</h2>
        <p className="nl-links__sub">
          A link opens the questions on someone else&apos;s phone, over your Tailscale
          network. Print its QR and put it where the work happens.
        </p>
      </header>

      {error && (
        <div className="nl-links__error" role="alert">
          <p className="nl-links__error-message">{error.message}</p>
          {error.action && <p className="nl-links__error-action">{error.action}</p>}
        </div>
      )}

      <div className="nl-links__new">
        <label className="nl-links__field">
          <span className="nl-links__field-label">Question set</span>
          <select
            className="nl-links__select"
            value={selectedFrameworkId ?? ""}
            onChange={(event) => setSelectedFrameworkId(Number(event.target.value))}
          >
            {frameworks.map((row) => (
              <option key={row.id} value={row.id}>
                {row.name} — v{row.version}
              </option>
            ))}
          </select>
        </label>
        <label className="nl-links__field">
          <span className="nl-links__field-label">Where will it live?</span>
          <input
            className="nl-links__input"
            type="text"
            value={label}
            placeholder="Hangar noticeboard"
            onChange={(event) => setLabel(event.target.value)}
          />
        </label>
        <button
          type="button"
          className="nl-links__create"
          disabled={busy || !selectedFrameworkId}
          onClick={create}
        >
          Open a new link
        </button>
      </div>

      {links === null ? (
        <p className="nl-links__empty">Loading…</p>
      ) : links.length === 0 ? (
        <p className="nl-links__empty">
          No links yet. Open one above, print its QR, and put it where people work.
        </p>
      ) : (
        <ul className="nl-links__list">
          {links.map((link) => (
            <li
              key={link.id}
              className={link.is_active ? "nl-link" : "nl-link nl-link--closed"}
            >
              <div className="nl-link__main">
                <p className="nl-link__label">
                  {link.label || "Unlabelled link"}
                  {!link.is_active && <span className="nl-link__closed-tag"> · closed</span>}
                </p>
                <p className="nl-link__meta">
                  {link.framework_name} — v{link.framework_version} ·{" "}
                  <span className="nl-numeric">{link.story_count}</span>{" "}
                  {link.story_count === 1 ? "story" : "stories"}
                </p>
                {link.is_active && <p className="nl-link__url">{link.url}</p>}
              </div>
              <div className="nl-link__actions">
                {link.is_active && (
                  <>
                    <button
                      type="button"
                      className="nl-link__button"
                      onClick={() => setPoster(link)}
                    >
                      QR poster
                    </button>
                    {confirming === link.id ? (
                      <span className="nl-link__confirm">
                        <span className="nl-link__confirm-text">Close for good?</span>
                        <button
                          type="button"
                          className="nl-link__button nl-link__button--danger"
                          disabled={busy}
                          onClick={() => revoke(link)}
                        >
                          Yes, close it
                        </button>
                        <button
                          type="button"
                          className="nl-link__button"
                          onClick={() => setConfirming(null)}
                        >
                          Keep it open
                        </button>
                      </span>
                    ) : (
                      <button
                        type="button"
                        className="nl-link__button"
                        onClick={() => setConfirming(link.id)}
                      >
                        Close link
                      </button>
                    )}
                  </>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

/**
 * The printable poster.
 *
 * Print grammar (§5b): black on white, the QR as large as the page allows, and
 * the address written out underneath for anyone whose camera will not cooperate.
 */
function Poster({ link, onClose }) {
  return (
    <div className="nl-poster-wrap">
      <div className="nl-poster-bar">
        <button type="button" className="nl-link__button" onClick={onClose}>
          Back to links
        </button>
        <button type="button" className="nl-link__button" onClick={() => window.print()}>
          Print this poster
        </button>
      </div>

      <section className="nl-poster">
        <h2 className="nl-poster__title">Share a story</h2>
        <p className="nl-poster__lede">
          Point your phone&apos;s camera at the code. It takes about four minutes, and it
          is anonymous.
        </p>
        <img
          className="nl-poster__qr"
          src={api.captureLinkQrUrl(link.id)}
          alt={`QR code opening the capture page at ${link.url}`}
        />
        <p className="nl-poster__url">{link.url}</p>
        <p className="nl-poster__foot">
          {link.label ? `${link.label} · ` : ""}
          {link.framework_name} — version {link.framework_version}
        </p>
      </section>
    </div>
  );
}
