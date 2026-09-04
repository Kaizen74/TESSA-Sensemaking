/*
 * The one place the frontend talks to the server.
 *
 * Errors arrive in the PRD §4 shape — {error: {code, message, action}} — and are
 * rethrown with that message and action intact, so the UI can show the operator
 * what happened and what to do (constraint 7).
 */

export class ApiError extends Error {
  constructor(status, code, message, action) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.action = action;
  }
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new ApiError(
      0,
      "server_unreachable",
      "Narrative Lens cannot reach its own server.",
      "Close the app and start it again with the Narrative Lens shortcut.",
    );
  }

  if (response.status === 204) return null;

  let body = null;
  try {
    body = await response.json();
  } catch {
    body = null;
  }

  if (!response.ok) {
    // One shape from the server, per PRD §4. The nested reading stays as a belt
    // and braces: an error that arrives unrecognised is shown as "something
    // went wrong", which is the least useful thing this app can say.
    const envelope = body?.error ?? body?.detail?.error;
    if (envelope) {
      throw new ApiError(response.status, envelope.code, envelope.message, envelope.action);
    }
    throw new ApiError(
      response.status,
      "unexpected_error",
      "Something went wrong that Narrative Lens did not expect.",
      "Try again. If it keeps happening, restart the app.",
    );
  }

  return body;
}

/** Query string from a plain object, skipping anything unset. */
function queryString(params) {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== null && value !== undefined && value !== "" && value !== false) {
      search.set(key, String(value));
    }
  }
  const rendered = search.toString();
  return rendered ? `?${rendered}` : "";
}

export const api = {
  listFrameworks: () => request("/api/frameworks"),
  getFramework: (id) => request(`/api/frameworks/${id}`),
  createFramework: (name, definition) =>
    request("/api/frameworks", {
      method: "POST",
      body: JSON.stringify({ name, definition }),
    }),
  updateFramework: (id, definition, editKind = null, name = null) =>
    request(`/api/frameworks/${id}`, {
      method: "PUT",
      body: JSON.stringify({
        definition,
        ...(editKind ? { edit_kind: editKind } : {}),
        ...(name ? { name } : {}),
      }),
    }),
  // Read-time translation (delta phase F). Display-only: the reply carries the
  // original alongside so a screen cannot show the translation unlabelled.
  translateStory: (anecdoteId, target) =>
    request(`/api/stories/${anecdoteId}/translation${queryString({ target })}`),

  // The languages the Studio can offer (delta phase E). A fixed local list —
  // constraint 4 permits no network for this.
  knownLanguages: () => request("/api/frameworks/languages"),

  // The design linter (delta phase C). AI-calling, and the only model call in
  // the app that never sees a story — POST because it costs money and happens
  // when somebody clicks, never on a page load.
  lintFramework: (frameworkId) =>
    request(`/api/frameworks/${frameworkId}/lint`, { method: "POST" }),

  paperPackUrl: (id) => `/api/frameworks/${id}/paper-pack`,
  capture: (submission) =>
    request("/api/capture", { method: "POST", body: JSON.stringify(submission) }),

  // Capture links (PRD §4). Admin-side, localhost only.
  listCaptureLinks: () => request("/api/capture-links"),
  createCaptureLink: (frameworkId, label = null) =>
    request("/api/capture-links", {
      method: "POST",
      body: JSON.stringify({ framework_id: frameworkId, label }),
    }),
  revokeCaptureLink: (id) => request(`/api/capture-links/${id}/revoke`, { method: "POST" }),
  captureLinkQrUrl: (id) => `/api/capture-links/${id}/qr.png`,

  // Ingestion (PRD §4). The stage machine refuses steps taken out of turn, so
  // the screen never has to guess what is allowed — it asks and reads the 409.
  listImports: () => request("/api/import"),
  getImport: (id) => request(`/api/import/${id}`),
  uploadImport: (file) => {
    const form = new FormData();
    form.append("file", file);
    // No Content-Type of our own: the browser has to set the multipart
    // boundary, and naming the type here would leave the boundary off.
    return request("/api/import", { method: "POST", body: form, headers: {} });
  },
  organiseImport: (id) => request(`/api/import/${id}/organise`, { method: "POST" }),
  confirmMapping: (id, body) =>
    request(`/api/import/${id}/mapping`, { method: "POST", body: JSON.stringify(body) }),
  proposeImport: (id, frameworkId) =>
    request(`/api/import/${id}/propose`, {
      method: "POST",
      body: JSON.stringify({ framework_id: frameworkId }),
    }),

  // The validation queue — the only way an AI-proposed placement becomes data.
  readQueue: (jobId = null) =>
    request(jobId === null ? "/api/queue" : `/api/queue?job_id=${jobId}`),
  decideStory: (anecdoteId, body) =>
    request(`/api/queue/${anecdoteId}`, { method: "PUT", body: JSON.stringify(body) }),

  // Patterns and exports (PRD §4). Every figure here is counted locally from
  // validated stories — no AI is involved on this path at all (constraint 11).
  getPatterns: (frameworkId, params = {}) =>
    request(`/api/patterns/${frameworkId}${queryString(params)}`),
  exportCsvUrl: (frameworkId, params = {}) =>
    `/api/export/csv${queryString({ framework_id: frameworkId, ...params })}`,
  exportBriefUrl: (frameworkId, params = {}) =>
    `/api/export/brief${queryString({ framework_id: frameworkId, ...params })}`,
  // The summary that goes back to the room: no stories, no provenance, and no
  // slice fewer than five people said (PRD §1.7).
  exportHeardUrl: (frameworkId, params = {}) =>
    `/api/export/heard${queryString({ framework_id: frameworkId, ...params })}`,

  // The story browser (PRD §1.6). Reading and marking; the export of a
  // selection is the ordinary CSV with an `ids` parameter.
  browseStories: (frameworkId, params = {}) =>
    request(`/api/stories/${frameworkId}${queryString(params)}`),
  markStory: (anecdoteId, marks) =>
    request(`/api/stories/${anecdoteId}/marks`, {
      method: "PUT",
      body: JSON.stringify(marks),
    }),

  // The landscape suite. The surface and its contour twin arrive in one
  // response, because they must be the same landscape (constraint 13b).
  getLandscape: (frameworkId, triadId, params = {}) =>
    request(`/api/landscape/${frameworkId}/${triadId}${queryString(params)}`),
  getExplorer: (frameworkId, params = {}) =>
    request(`/api/explorer/${frameworkId}${queryString(params)}`),
  getClusters: (frameworkId, params = {}) =>
    request(`/api/clusters/${frameworkId}${queryString(params)}`),

  // Collective interpretations (delta phase D). What a room concluded, stored
  // beside the pattern and never merged into it — there is no endpoint here
  // that could fold one into a figure, because there is no such operation.
  listInterpretations: (frameworkId, params = {}) =>
    request(`/api/interpretations${queryString({ framework_id: frameworkId, ...params })}`),
  recordInterpretation: (body) =>
    request("/api/interpretations", { method: "POST", body: JSON.stringify(body) }),

  // The data-quality signals (delta phase B). Counted locally like everything
  // else on this tab — no AI is reachable from that endpoint at all.
  getQuality: (frameworkId, params = {}) =>
    request(`/api/quality/${frameworkId}${queryString(params)}`),

  // The respondent's path. The token carries everything — no framework id is
  // ever sent from here, so a browser cannot retarget its own story.
  publicFramework: (token) => request(`/api/public/capture/${token}`),
  publicCapture: (token, submission) =>
    request(`/api/public/capture/${token}`, {
      method: "POST",
      body: JSON.stringify(submission),
    }),
};
