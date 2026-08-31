/*
 * Turning an edit-log field path into something a person can read.
 *
 * The log stores paths the way the schema does — `triads.0.corners.1`,
 * `capture_settings.anonymity_text` — because that is what points at exactly one
 * string, and PRD §3 fixes that shape. It is also the only place in the app
 * where a non-technical operator was being shown a machine's idea of a name
 * (constraint 7), so the path is stored as it always was and translated here.
 *
 * Plain JavaScript rather than JSX so the translation can be tested directly.
 */

/** Repeated signifiers: the operator counts them from one, not from zero. */
const GROUPS = {
  triads: "Triangle",
  dyads: "Slider",
  mcqs: "Choice",
};

/** Every leaf the definition can hold, in the words the Studio uses for it. */
const LEAVES = {
  prompt_text: "the story prompt",
  prompt_text_alt: "the second story prompt",
  title: "the question",
  corners: "corner",
  left: "the left end",
  right: "the right end",
  low: "the low end",
  high: "the high end",
  x_axis: "the across axis",
  y_axis: "the up axis",
  options: "option",
  chips: "item",
  stones: "The square",
  welcome_text: "the welcome",
  anonymity_text: "the anonymity statement",
  thanks_text: "the thank-you",
  respondent_groups: "group",
};

/** Structure the operator never named and does not need to see. */
const SILENT = new Set(["capture_settings"]);

const isIndex = (part) => /^\d+$/.test(part ?? "");

/**
 * A field path as a phrase: `triads.0.corners.1` → "Triangle 1 · corner 2".
 *
 * Anything unrecognised falls back to the raw path. A log entry that cannot be
 * translated is still worth showing — losing the record would be worse than
 * showing it in the shape it was stored in.
 */
export function describePath(path) {
  if (typeof path !== "string" || path === "") return "";

  const parts = path.split(".");
  const words = [];

  for (let index = 0; index < parts.length; index += 1) {
    const part = parts[index];
    if (isIndex(part)) continue; // counted with whatever it belongs to
    if (SILENT.has(part)) continue;

    const position = isIndex(parts[index + 1]) ? Number(parts[index + 1]) + 1 : null;
    const group = GROUPS[part];
    if (group) {
      words.push(position === null ? group : `${group} ${position}`);
      continue;
    }

    const leaf = LEAVES[part];
    if (leaf === undefined) return path;
    words.push(position === null ? leaf : `${leaf} ${position}`);
  }

  if (words.length === 0) return path;

  // Sentence case: the first word starts the phrase, whatever it was in the map.
  const phrase = words.join(" · ");
  return phrase.charAt(0).toUpperCase() + phrase.slice(1);
}
