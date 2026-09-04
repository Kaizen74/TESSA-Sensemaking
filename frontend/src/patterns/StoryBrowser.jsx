/*
 * The story browser (PRD §1.6, §5.4) — the fourth way of looking.
 *
 * Everything else on this tab is an aggregate. This is the stories themselves,
 * which is where a surprising hill has to end up: search them, star the ones
 * worth coming back to, tag them in your own words, and take a chosen few out
 * as a CSV with their provenance attached.
 *
 * Quiet by the same rule as the supporting charts (constraint 13a): a list of
 * text at reading weight, no colour doing any work, and the landscape still the
 * only bold thing in the tab.
 */

import { useCallback, useEffect, useState } from "react";
import { api, ApiError } from "../api.js";
import "./patterns.css";

/** Wait this long after the last keystroke before searching. */
const TYPING_PAUSE_MS = 250;

export function StoryBrowser({ framework, params }) {
  const [query, setQuery] = useState("");
  const [typed, setTyped] = useState("");
  const [tag, setTag] = useState("");
  const [starredOnly, setStarredOnly] = useState(false);
  const [offset, setOffset] = useState(0);
  const [page, setPage] = useState(null);
  const [chosen, setChosen] = useState([]);
  const [error, setError] = useState(null);

  // One search per pause in typing rather than one per keystroke.
  useEffect(() => {
    const timer = window.setTimeout(() => {
      setQuery(typed);
      setOffset(0);
    }, TYPING_PAUSE_MS);
    return () => window.clearTimeout(timer);
  }, [typed]);

  const load = useCallback(() => {
    api
      .browseStories(framework.id, { ...params, q: query, tag, starred: starredOnly, offset })
      .then((result) => {
        setPage(result);
        setError(null);
      })
      .catch(setError);
  }, [framework.id, params, query, tag, starredOnly, offset]);

  useEffect(() => {
    load();
  }, [load]);

  function mark(story, changes) {
    api
      .markStory(story.anecdote_id, changes)
      .then((updated) => {
        setPage((current) =>
          current === null
            ? current
            : {
                ...current,
                stories: current.stories.map((row) =>
                  row.anecdote_id === updated.anecdote_id ? updated : row,
                ),
              },
        );
      })
      .catch(setError);
  }

  function toggleChosen(id) {
    setChosen((current) =>
      current.includes(id) ? current.filter((entry) => entry !== id) : [...current, id],
    );
  }

  if (error) {
    return (
      <div className="nl-patterns__error" role="alert">
        <p className="nl-patterns__error-message">{error.message}</p>
        {error.action && <p className="nl-patterns__error-action">{error.action}</p>}
      </div>
    );
  }

  if (page === null) return <p className="nl-patterns__empty">Loading…</p>;

  const showing = page.stories.length;
  const more = page.offset + showing < page.matched;

  return (
    <section className="nl-browser">
      <div className="nl-browser__controls">
        <label className="nl-browser__search">
          <span className="nl-rail__label">Search the stories</span>
          <input
            type="search"
            className="nl-browser__input"
            value={typed}
            placeholder="Any word in a story"
            onChange={(event) => setTyped(event.target.value)}
          />
        </label>

        {page.known_tags.length > 0 && (
          <label className="nl-browser__field">
            <span className="nl-rail__label">Tagged</span>
            <select
              className="nl-rail__select"
              value={tag}
              onChange={(event) => {
                setTag(event.target.value);
                setOffset(0);
              }}
            >
              <option value="">Any tag</option>
              {page.known_tags.map((known) => (
                <option key={known} value={known}>
                  {known}
                </option>
              ))}
            </select>
          </label>
        )}

        <label className="nl-rail__check">
          <input
            type="checkbox"
            checked={starredOnly}
            onChange={(event) => {
              setStarredOnly(event.target.checked);
              setOffset(0);
            }}
          />
          <span>Starred only</span>
        </label>
      </div>

      <p className="nl-patterns__count">
        <strong>{page.matched}</strong> of {page.total}{" "}
        {page.total === 1 ? "story" : "stories"}
        {chosen.length > 0 && ` · ${chosen.length} ticked`}
      </p>

      {chosen.length > 0 && (
        <div className="nl-browser__selection">
          <a
            className="nl-rail__download"
            href={api.exportCsvUrl(framework.id, { ...params, ids: chosen.join(",") })}
          >
            Download the {chosen.length} ticked{" "}
            {chosen.length === 1 ? "story" : "stories"} (CSV)
          </a>
          <button type="button" className="nl-rail__clear" onClick={() => setChosen([])}>
            Untick all
          </button>
        </div>
      )}

      {page.stories.length === 0 ? (
        <p className="nl-patterns__empty">
          {page.total === 0
            ? "No validated stories here yet. Collect some under Capture & Links, or work the queue under Import & Validate."
            : "Nothing matches that. Clear the search, or pick a different tag."}
        </p>
      ) : (
        <ol className="nl-browser__list">
          {page.stories.map((story) => (
            <li key={story.anecdote_id} className="nl-story">
              <div className="nl-story__head">
                <label className="nl-story__tick">
                  <input
                    type="checkbox"
                    checked={chosen.includes(story.anecdote_id)}
                    onChange={() => toggleChosen(story.anecdote_id)}
                  />
                  <span className="nl-story__tick-label">Include in a download</span>
                </label>
                <button
                  type="button"
                  className={story.starred ? "nl-story__star nl-story__star--on" : "nl-story__star"}
                  aria-pressed={story.starred}
                  onClick={() => mark(story, { starred: !story.starred })}
                >
                  {story.starred ? "★ Starred" : "☆ Star"}
                </button>
              </div>

              {/* The name its teller gave it, when they gave it one (delta §5).
                  Attributed out loud, because a title in the storyteller's own
                  words is a different kind of thing from the machine's first
                  eighty characters — and only one of them is testimony. */}
              {story.respondent_title && (
                <p className="nl-story__title">
                  “{story.respondent_title}”
                  <span className="nl-story__title-by"> — named by the storyteller</span>
                </p>
              )}

              {/* The original is always the primary text and always comes
                  first. The translation, when asked for, appears beneath it at
                  secondary weight with a label that cannot be turned off
                  (delta §5, constraint 15). */}
              <p className="nl-story__text">{story.text}</p>

              <p className="nl-story__meta">
                {story.respondent_group && <span>{story.respondent_group}</span>}
                {/* Delta phase E: the language it was told in, wherever a story
                    is shown. Absent reads as unknown, never as English. */}
                <span>{story.language_name}</span>
                <span>{story.input_method}</span>
                <span>{story.entry_mode}</span>
                {story.source_file && <span>{story.source_file}</span>}
                <span>
                  {story.answered} {story.answered === 1 ? "answer" : "answers"}
                </span>
                <span>v{story.framework_version}</span>
              </p>

              {/* After the provenance line rather than before it: the words as
                  told and the line naming the language they were told in are
                  one record, and a reading aid does not get to split them. */}
              <StoryTranslation story={story} />

              <TagEditor story={story} onSave={(tags) => mark(story, { tags })} />
            </li>
          ))}
        </ol>
      )}

      {(page.offset > 0 || more) && (
        <div className="nl-browser__pages">
          <button
            type="button"
            className="nl-rail__clear"
            disabled={page.offset === 0}
            onClick={() => setOffset(Math.max(0, page.offset - page.page_size))}
          >
            ← Previous
          </button>
          <button
            type="button"
            className="nl-rail__clear"
            disabled={!more}
            onClick={() => setOffset(page.offset + page.page_size)}
          >
            Next →
          </button>
        </div>
      )}
    </section>
  );
}

/** The analyst's own words on one story. Comma separated, saved on blur. */
/**
 * A story's translation, read-time and display-only (delta §5, constraint 15).
 *
 * The whole design of this component is one rule: the translation and its
 * label are the same element. There is no branch in which the text renders and
 * the label does not — they are returned together, and the label is not
 * conditional on anything. A reader can never be looking at a machine's reading
 * of somebody's words while believing they are looking at the words.
 *
 * The original stays above and stays primary. This sits underneath at secondary
 * weight, because it is an aid to reading the story, not the story.
 *
 * A failure leaves the original exactly where it was. Not being able to reach
 * the AI is an ordinary state of this app (constraint 4), and the text that
 * matters is the one already on screen.
 */
function StoryTranslation({ story }) {
  const [shown, setShown] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  // Nothing to carry across: the story is already in the reading language, or
  // nobody recorded what language it is in and guessing would be inventing.
  if (!story.language_code || story.language_code === "en") return null;

  async function fetchTranslation() {
    if (shown) {
      setShown(null);
      return;
    }
    setBusy(true);
    setError(null);
    try {
      setShown(await api.translateStory(story.anecdote_id, "en"));
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : null);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="nl-translate">
      <button
        type="button"
        className="nl-translate__toggle"
        onClick={fetchTranslation}
        disabled={busy}
      >
        {busy
          ? "Translating…"
          : shown
            ? "Hide the English translation"
            : "Read it in English"}
      </button>

      {error && (
        <p className="nl-translate__error" role="alert">
          {error.message}{" "}
          {error.action && <span className="nl-translate__note">{error.action}</span>}{" "}
          <span className="nl-translate__note">
            The story above is unchanged — it is the original, and it is the one
            that counts.
          </span>
        </p>
      )}

      {shown && (
        <div className="nl-translate__body">
          {/* Label and text together, always. Not a sibling that a later edit
              could make conditional — they are one block, and the label is
              first so it is read first. */}
          <p className="nl-translate__label">
            Translated by {shown.model_used} from{" "}
            {shown.original_language_name} — the original is above, and it is
            what was actually said.
          </p>
          <p className="nl-translate__text">{shown.translated_text}</p>
        </div>
      )}
    </div>
  );
}

function TagEditor({ story, onSave }) {
  const [text, setText] = useState(story.tags.join(", "));

  useEffect(() => {
    setText(story.tags.join(", "));
  }, [story.tags]);

  return (
    <label className="nl-story__tags">
      <span className="nl-story__tags-label">Tags</span>
      <input
        type="text"
        className="nl-browser__input"
        value={text}
        placeholder="Comma separated"
        onChange={(event) => setText(event.target.value)}
        onBlur={() => {
          const tags = text
            .split(",")
            .map((entry) => entry.trim())
            .filter(Boolean);
          if (tags.join("|") !== story.tags.join("|")) onSave(tags);
        }}
      />
    </label>
  );
}
