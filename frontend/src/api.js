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
    const envelope = body?.detail?.error ?? body?.error;
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
  paperPackUrl: (id) => `/api/frameworks/${id}/paper-pack`,
};
