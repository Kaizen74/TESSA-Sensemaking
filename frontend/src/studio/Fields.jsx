/*
 * Editing controls for the Studio.
 *
 * Every respondent-facing string in PRD §1.1 has an input here: triad corners,
 * dyad poles, stones axes and chips, MCQ options, and each signifier's own
 * question. Labels say what the operator controls, in their words.
 */

import { useId } from "react";

export function Field({ label, value, onChange, hint = null }) {
  const id = useId();
  return (
    <div className="nl-field">
      <label className="nl-field__label" htmlFor={id}>
        {label}
      </label>
      {hint && <p className="nl-field__hint">{hint}</p>}
      <input
        id={id}
        className="nl-field__input"
        type="text"
        value={value ?? ""}
        onChange={(event) => onChange(event.target.value)}
      />
    </div>
  );
}

export function TextArea({ label, value, onChange, hint = null }) {
  const id = useId();
  return (
    <div className="nl-field">
      <label className="nl-field__label" htmlFor={id}>
        {label}
      </label>
      {hint && <p className="nl-field__hint">{hint}</p>}
      <textarea
        id={id}
        className="nl-field__input nl-field__input--area"
        rows={3}
        value={value ?? ""}
        onChange={(event) => onChange(event.target.value)}
      />
    </div>
  );
}

function ListEditor({ title, items, onChange, onRemove, minimum, itemLabel }) {
  return (
    <div className="nl-list">
      <p className="nl-list__title">{title}</p>
      {items.map((item, index) => (
        <Field
          key={index}
          label={`${itemLabel} ${index + 1}`}
          value={item}
          onChange={(value) => {
            const next = [...items];
            next[index] = value;
            onChange(next);
          }}
        />
      ))}
      {onRemove && items.length > minimum && (
        <button type="button" className="nl-btn nl-btn--quiet" onClick={onRemove}>
          Remove last {itemLabel.toLowerCase()}
        </button>
      )}
    </div>
  );
}

export function SignifierEditor({ draft, patch, newId }) {
  const triads = draft.triads ?? [];
  const dyads = draft.dyads ?? [];
  const mcqs = draft.mcqs ?? [];

  function updateAt(list, index, changes, key) {
    const next = [...list];
    next[index] = { ...next[index], ...changes };
    patch({ [key]: next });
  }

  const usedIds = [
    ...triads.map((t) => t.id),
    ...dyads.map((d) => d.id),
    ...mcqs.map((m) => m.id),
    ...(draft.stones ? [draft.stones.id] : []),
  ];

  return (
    <>
      <fieldset className="nl-fieldset">
        <legend className="nl-legend">Triangles</legend>
        <p className="nl-field__hint">
          Three pulls that compete. People place one mark between them.
        </p>
        {triads.map((triad, index) => (
          <div className="nl-signifier" key={triad.id}>
            <TextArea
              label={`Triangle ${index + 1} question`}
              value={triad.title}
              onChange={(value) => updateAt(triads, index, { title: value }, "triads")}
            />
            <ListEditor
              title="Corners"
              itemLabel="Corner"
              minimum={3}
              items={triad.corners}
              onChange={(corners) => updateAt(triads, index, { corners }, "triads")}
            />
          </div>
        ))}
        <button
          type="button"
          className="nl-btn nl-btn--quiet"
          onClick={() =>
            patch({
              triads: [
                ...triads,
                {
                  id: newId("triad", usedIds),
                  title: "What pulled hardest here?",
                  corners: ["First pull", "Second pull", "Third pull"],
                },
              ],
            })
          }
        >
          Add a triangle
        </button>
        {triads.length > 0 && (
          <button
            type="button"
            className="nl-btn nl-btn--quiet"
            onClick={() => patch({ triads: triads.slice(0, -1) })}
          >
            Remove last triangle
          </button>
        )}
      </fieldset>

      <fieldset className="nl-fieldset">
        <legend className="nl-legend">Sliders</legend>
        <p className="nl-field__hint">Two opposites. People place one mark on the line.</p>
        {dyads.map((dyad, index) => (
          <div className="nl-signifier" key={dyad.id}>
            <TextArea
              label={`Slider ${index + 1} question`}
              value={dyad.title}
              onChange={(value) => updateAt(dyads, index, { title: value }, "dyads")}
            />
            <Field
              label="Left end"
              value={dyad.left}
              onChange={(value) => updateAt(dyads, index, { left: value }, "dyads")}
            />
            <Field
              label="Right end"
              value={dyad.right}
              onChange={(value) => updateAt(dyads, index, { right: value }, "dyads")}
            />
          </div>
        ))}
        <button
          type="button"
          className="nl-btn nl-btn--quiet"
          onClick={() =>
            patch({
              dyads: [
                ...dyads,
                {
                  id: newId("dyad", usedIds),
                  title: "Where did this sit?",
                  left: "One end",
                  right: "The other end",
                },
              ],
            })
          }
        >
          Add a slider
        </button>
        {dyads.length > 0 && (
          <button
            type="button"
            className="nl-btn nl-btn--quiet"
            onClick={() => patch({ dyads: dyads.slice(0, -1) })}
          >
            Remove last slider
          </button>
        )}
      </fieldset>

      <fieldset className="nl-fieldset">
        <legend className="nl-legend">Canvas</legend>
        <p className="nl-field__hint">
          A square with a named axis each way. People place one mark per item.
        </p>
        {draft.stones ? (
          <div className="nl-signifier">
            <TextArea
              label="Canvas question"
              value={draft.stones.title}
              onChange={(value) => patch({ stones: { ...draft.stones, title: value } })}
            />
            <Field
              label="Across — left end"
              value={draft.stones.x_axis.low}
              onChange={(value) =>
                patch({
                  stones: {
                    ...draft.stones,
                    x_axis: { ...draft.stones.x_axis, low: value },
                  },
                })
              }
            />
            <Field
              label="Across — right end"
              value={draft.stones.x_axis.high}
              onChange={(value) =>
                patch({
                  stones: {
                    ...draft.stones,
                    x_axis: { ...draft.stones.x_axis, high: value },
                  },
                })
              }
            />
            <Field
              label="Up — bottom end"
              value={draft.stones.y_axis.low}
              onChange={(value) =>
                patch({
                  stones: {
                    ...draft.stones,
                    y_axis: { ...draft.stones.y_axis, low: value },
                  },
                })
              }
            />
            <Field
              label="Up — top end"
              value={draft.stones.y_axis.high}
              onChange={(value) =>
                patch({
                  stones: {
                    ...draft.stones,
                    y_axis: { ...draft.stones.y_axis, high: value },
                  },
                })
              }
            />
            <Field
              label="Items to place"
              hint="Comma separated."
              value={draft.stones.chips.join(", ")}
              onChange={(value) =>
                patch({
                  stones: {
                    ...draft.stones,
                    chips: value
                      .split(",")
                      .map((part) => part.trim())
                      .filter(Boolean),
                  },
                })
              }
            />
            <button
              type="button"
              className="nl-btn nl-btn--quiet"
              onClick={() => patch({ stones: null })}
            >
              Remove the canvas
            </button>
          </div>
        ) : (
          <button
            type="button"
            className="nl-btn nl-btn--quiet"
            onClick={() =>
              patch({
                stones: {
                  id: newId("stones", usedIds),
                  title: "Place each one where it belongs",
                  x_axis: { low: "Rare", high: "Constant" },
                  y_axis: { low: "Minor", high: "Major" },
                  chips: ["First item", "Second item"],
                },
              })
            }
          >
            Add a canvas
          </button>
        )}
      </fieldset>

      <fieldset className="nl-fieldset">
        <legend className="nl-legend">Choices</legend>
        {mcqs.map((mcq, index) => (
          <div className="nl-signifier" key={mcq.id}>
            <TextArea
              label={`Choice ${index + 1} question`}
              value={mcq.title}
              onChange={(value) => updateAt(mcqs, index, { title: value }, "mcqs")}
            />
            <Field
              label="Options"
              hint="Comma separated. At least two."
              value={mcq.options.join(", ")}
              onChange={(value) =>
                updateAt(
                  mcqs,
                  index,
                  {
                    options: value
                      .split(",")
                      .map((part) => part.trim())
                      .filter(Boolean),
                  },
                  "mcqs",
                )
              }
            />
            <label className="nl-check">
              <input
                type="checkbox"
                checked={mcq.multi}
                onChange={(event) =>
                  updateAt(mcqs, index, { multi: event.target.checked }, "mcqs")
                }
              />
              Allow more than one answer
            </label>
          </div>
        ))}
        <button
          type="button"
          className="nl-btn nl-btn--quiet"
          onClick={() =>
            patch({
              mcqs: [
                ...mcqs,
                {
                  id: newId("mcq", usedIds),
                  title: "Which one applies?",
                  options: ["First option", "Second option"],
                  multi: false,
                },
              ],
            })
          }
        >
          Add a choice
        </button>
        {mcqs.length > 0 && (
          <button
            type="button"
            className="nl-btn nl-btn--quiet"
            onClick={() => patch({ mcqs: mcqs.slice(0, -1) })}
          >
            Remove last choice
          </button>
        )}
      </fieldset>
    </>
  );
}
