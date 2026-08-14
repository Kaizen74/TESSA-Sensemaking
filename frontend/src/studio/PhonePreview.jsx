/*
 * The live phone-frame preview (PRD §1.1, §5.1).
 *
 * Shows exactly what the respondent will see, at exactly the width constraint 10
 * sets: 375px. It updates as the operator types, so the cost of a wording choice
 * is visible while making it rather than after publishing.
 */

import { SignifierWidget } from "../widgets/Widgets.jsx";
import "./phone-preview.css";

export function PhonePreview({ definition }) {
  const settings = definition.capture_settings ?? {};
  const signifiers = orderedSignifiers(definition);

  return (
    <div className="nl-phone" aria-label="Preview of the respondent's screen">
      <div className="nl-phone__frame">
        <div className="nl-phone__screen">
          <section className="nl-phone__card">
            <p className="nl-phone__eyebrow">Welcome</p>
            <p className="nl-phone__body">{settings.welcome_text}</p>
            <p className="nl-phone__promise">{settings.time_promise_text}</p>
          </section>

          <section className="nl-phone__card">
            <h3 className="nl-phone__prompt">{definition.prompt_text}</h3>
            {definition.prompt_text_alt && (
              <p className="nl-phone__alt">Or: {definition.prompt_text_alt}</p>
            )}
            <div className="nl-phone__textarea" aria-hidden="true">
              Their story goes here…
            </div>
            {settings.voice_enabled && (
              <p className="nl-phone__hint">Type, or use the microphone. Both always work.</p>
            )}
          </section>

          {signifiers.map(({ kind, signifier }) => (
            <section className="nl-phone__card" key={signifier.id}>
              <SignifierWidget kind={kind} signifier={signifier} />
            </section>
          ))}

          {settings.respondent_groups?.length > 0 && (
            <section className="nl-phone__card">
              <h3 className="nl-phone__prompt">Which group are you in?</h3>
              <ul className="nl-phone__groups">
                {settings.respondent_groups.map((group) => (
                  <li key={group} className="nl-phone__group">
                    {group}
                  </li>
                ))}
              </ul>
            </section>
          )}

          <section className="nl-phone__card">
            <p className="nl-phone__eyebrow">Thank you</p>
            <p className="nl-phone__body">{settings.thankyou_text}</p>
            {settings.reflection_enabled && (
              <p className="nl-phone__hint">Their story then appears on the live picture.</p>
            )}
          </section>

          <p className="nl-phone__anonymity">{settings.anonymity_text}</p>
        </div>
      </div>
    </div>
  );
}

/** Signifiers in the order the respondent meets them, matching the server. */
export function orderedSignifiers(definition) {
  const ordered = [];
  (definition.triads ?? []).forEach((triad) => ordered.push({ kind: "triad", signifier: triad }));
  (definition.dyads ?? []).forEach((dyad) => ordered.push({ kind: "dyad", signifier: dyad }));
  if (definition.stones) ordered.push({ kind: "stones", signifier: definition.stones });
  (definition.mcqs ?? []).forEach((mcq) => ordered.push({ kind: "mcq", signifier: mcq }));
  return ordered;
}
