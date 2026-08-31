/*
 * Translating one placement between the two shapes it lives in.
 *
 * A placement means the same thing on screen and in the database, but it is not
 * written the same way in both. A triad is three ordered numbers to the widget
 * that draws it and a corner-keyed object to the server that stores it; stones
 * are a bare list on screen and {placements: [...]} in the database. The wizard
 * needs the trip out, the validation queue needs the trip home, and if the two
 * trips ever disagree a stored placement means one thing where it was made and
 * another where it is read back.
 *
 * So both live here, next to each other, in plain JavaScript with no JSX — which
 * lets `tests/test_placement_shape_parity.py` load this module in Node and check
 * a value the Python side actually produced all the way there and back.
 */

/** Every signifier of a definition with its kind, in respondent order. */
export function orderedSignifiers(definition) {
  if (!definition) return [];
  const ordered = [];
  (definition.triads ?? []).forEach((signifier) => ordered.push({ kind: "triad", signifier }));
  (definition.dyads ?? []).forEach((signifier) => ordered.push({ kind: "dyad", signifier }));
  if (definition.stones) ordered.push({ kind: "stones", signifier: definition.stones });
  (definition.mcqs ?? []).forEach((signifier) => ordered.push({ kind: "mcq", signifier }));
  return ordered;
}

/**
 * One stored placement back into the shape its widget draws.
 *
 * The inverse of {@link toSubmission}. Anything reading a placement out of
 * storage and onto a widget — the validation queue — goes through here.
 */
export function fromStored(kind, signifier, stored) {
  if (stored === null || stored === undefined) return null;
  if (kind === "triad") {
    return (signifier.corners ?? []).map((corner) => Number(stored[corner] ?? 0));
  }
  if (kind === "dyad") return Number(stored.value ?? 0);
  if (kind === "stones") return stored.placements ?? [];
  if (kind === "mcq") return { selected: stored.selected ?? [] };
  return null;
}

/**
 * Placements in the shape the server expects.
 *
 * An unanswered signifier is left out rather than sent as an empty value: a
 * skipped question should store nothing, not a zero somebody might later read
 * as an answer.
 */
export function toSubmission(definition, values) {
  const submission = [];
  orderedSignifiers(definition).forEach(({ kind, signifier }) => {
    const value = values[signifier.id];
    if (value === undefined || value === null) return;

    if (kind === "triad") {
      const [a, b, c] = value;
      submission.push({
        signifier_id: signifier.id,
        value: {
          [signifier.corners[0]]: a,
          [signifier.corners[1]]: b,
          [signifier.corners[2]]: c,
        },
      });
    } else if (kind === "dyad") {
      submission.push({ signifier_id: signifier.id, value: { value } });
    } else if (kind === "stones") {
      if (value.length === 0) return;
      submission.push({ signifier_id: signifier.id, value: { placements: value } });
    } else if (kind === "mcq") {
      if ((value.selected ?? []).length === 0) return;
      submission.push({ signifier_id: signifier.id, value });
    }
  });
  return submission;
}
