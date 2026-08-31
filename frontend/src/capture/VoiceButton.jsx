/*
 * The dictation control (constraint 10, §7.12).
 *
 * It sits *beside* the text box, never instead of it. When speech is
 * unavailable the button disappears rather than sitting there dead — an offer
 * that cannot be accepted is worse than no offer, and the keyboard is already
 * the working path.
 *
 * PRD §9 assumption 4 allows browser voice "with notice": the notice is on
 * screen before the microphone opens, not buried in a policy.
 */

import { useEffect, useRef, useState } from "react";
import {
  appendDictation,
  isVoiceSupported,
  startDictation,
  voiceFailureMessage,
} from "./voice.js";

export function VoiceButton({ text, onText, onUsed }) {
  const [supported] = useState(() => isVoiceSupported());
  const [listening, setListening] = useState(false);
  const [failure, setFailure] = useState(null);
  const handleRef = useRef(null);

  // Whatever happens to the screen, the microphone closes with it.
  useEffect(() => () => handleRef.current?.stop(), []);

  if (!supported) return null;

  function stop() {
    handleRef.current?.stop();
    handleRef.current = null;
    setListening(false);
  }

  function start() {
    setFailure(null);
    onUsed?.();
    handleRef.current = startDictation({
      onText: (spoken) => onText(appendDictation(text, spoken)),
      onError: (reason) => {
        setFailure(voiceFailureMessage(reason));
        stop();
      },
      onEnd: () => setListening(false),
    });
    setListening(handleRef.current.active);
  }

  return (
    <div className="nl-voice">
      <button
        type="button"
        className={listening ? "nl-voice__button nl-voice__button--live" : "nl-voice__button"}
        aria-pressed={listening}
        onClick={listening ? stop : start}
      >
        {listening ? "Stop listening" : "Speak instead of typing"}
      </button>

      {listening ? (
        <p className="nl-voice__note" role="status">
          Listening. Your words appear in the box as you speak — you can still type,
          and you can edit anything afterwards.
        </p>
      ) : (
        <p className="nl-voice__note">
          Speech is handled by your browser, which may send audio to its own service.
          Typing works entirely offline.
        </p>
      )}

      {failure && (
        <div className="nl-voice__failure" role="alert">
          <p className="nl-voice__failure-message">{failure.message}</p>
          <p className="nl-voice__failure-action">{failure.action}</p>
        </div>
      )}
    </div>
  );
}
