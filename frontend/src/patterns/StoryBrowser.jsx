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
import { api } from "../api.js";
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

              <p className="nl-story__text">{story.text}</p>

              <p className="nl-story__meta">
                {story.respondent_group && <span>{story.respondent_group}</span>}
                <span>{story.input_method}</span>
                <span>{story.entry_mode}</span>
                {story.source_file && <span>{story.source_file}</span>}
                <span>
                  {story.answered} {story.answered === 1 ? "answer" : "answers"}
                </span>
                <span>v{story.framework_version}</span>
              </p>

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
