/*
 * Draft persistence for the capture wizard (PRD §6 Phase 3: "draft survives
 * reload"; §7.6 "drafts survive reload").
 *
 * A respondent halfway through a story who reloads, drops signal, or locks
 * their phone must not lose what they wrote. The draft lives in the browser's
 * own storage and never reaches the server until they submit.
 *
 * Constraint 9: a draft holds only what the respondent typed and placed. There
 * is no id, no fingerprint, and nothing that could identify who wrote it — the
 * storage key names the framework version, not the person. Drafts are cleared
 * the moment a story is submitted.
 *
 * This module takes its storage as an argument rather than reaching for
 * `window.localStorage`, so the same code is exercised by the test suite.
 */

const KEY_PREFIX = "narrative-lens.draft.v1.";

/** Storage key for one framework version. Carries no respondent identifier. */
export function draftKey(frameworkId) {
  return `${KEY_PREFIX}${frameworkId}`;
}

/** The shape a fresh draft starts from. */
export function emptyDraft() {
  return { text: "", values: {}, respondentGroup: null, step: 0 };
}

function safeStorage(storage) {
  // Private browsing and locked-down browsers can throw on access rather than
  // return null. A draft is a convenience: never let it break capture.
  try {
    if (!storage) return null;
    return storage;
  } catch {
    return null;
  }
}

/** Write the draft. Returns true when it was actually stored. */
export function saveDraft(storage, frameworkId, draft) {
  const store = safeStorage(storage);
  if (!store) return false;
  try {
    store.setItem(draftKey(frameworkId), JSON.stringify(draft));
    return true;
  } catch {
    // Quota exceeded, or storage disabled mid-session.
    return false;
  }
}

/**
 * Read the draft back, or null when there is nothing usable.
 *
 * A corrupt or half-written value is treated as no draft at all: starting fresh
 * is recoverable, crashing on load is not.
 */
export function loadDraft(storage, frameworkId) {
  const store = safeStorage(storage);
  if (!store) return null;

  let raw;
  try {
    raw = store.getItem(draftKey(frameworkId));
  } catch {
    return null;
  }
  if (!raw) return null;

  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch {
    return null;
  }

  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return null;

  return {
    text: typeof parsed.text === "string" ? parsed.text : "",
    values: parsed.values && typeof parsed.values === "object" ? parsed.values : {},
    respondentGroup: typeof parsed.respondentGroup === "string" ? parsed.respondentGroup : null,
    step: Number.isInteger(parsed.step) && parsed.step >= 0 ? parsed.step : 0,
  };
}

/** Forget the draft. Called the moment a story is submitted. */
export function clearDraft(storage, frameworkId) {
  const store = safeStorage(storage);
  if (!store) return;
  try {
    store.removeItem(draftKey(frameworkId));
  } catch {
    // Nothing to do — the draft is stale at worst.
  }
}

/** Whether a draft holds anything worth offering to restore. */
export function draftHasContent(draft) {
  if (!draft) return false;
  return Boolean(draft.text?.trim()) || Object.keys(draft.values ?? {}).length > 0;
}
