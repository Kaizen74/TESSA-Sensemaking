/*
 * Browser speech dictation (constraint 10, PRD §9 assumption 4, §7.12).
 *
 * Three rules shape this module:
 *
 * 1. **Voice is always paired with typing** (constraint 10). Dictation appends
 *    into the same text box the keyboard writes to. It is never a separate
 *    screen, never the only way forward, and the typing path never disappears
 *    while it runs.
 * 2. **It fails plain-English, with a working fallback** (§7.12). Browsers
 *    without speech, a denied microphone, and a dropped network all produce a
 *    sentence a respondent can act on — and the keyboard is still right there.
 * 3. **It is the one permitted network exception for capture** (constraint 4).
 *    Speech recognition may reach the browser's own service; nothing else in
 *    the capture path touches the network beyond this app's own server. The
 *    respondent is told before it starts, which is the "with notice" in
 *    assumption 4.
 *
 * The recogniser is injected rather than reached for, so the fallback logic is
 * exercised by the test suite instead of only in a browser.
 */

/** Why voice is unavailable, in a form the UI can turn into a sentence. */
export const VOICE_UNSUPPORTED = "unsupported";
export const VOICE_DENIED = "denied";
export const VOICE_NO_SPEECH = "no-speech";
export const VOICE_NETWORK = "network";
export const VOICE_FAILED = "failed";

/** Plain-English message and fallback for every way voice can fail (§7.12). */
export function voiceFailureMessage(reason) {
  switch (reason) {
    case VOICE_UNSUPPORTED:
      return {
        message: "This browser cannot listen for speech.",
        action: "Type your story instead — the box below works exactly the same.",
      };
    case VOICE_DENIED:
      return {
        message: "The microphone is blocked, so nothing was heard.",
        action:
          "Allow the microphone in your browser settings, or just type your " +
          "story — the box below works exactly the same.",
      };
    case VOICE_NO_SPEECH:
      return {
        message: "Nothing was picked up.",
        action: "Try speaking again, a little closer to the microphone, or type instead.",
      };
    case VOICE_NETWORK:
      return {
        message: "Speech needs a connection, and there is not one right now.",
        action: "Type your story instead — everything else works without a connection.",
      };
    default:
      return {
        message: "The microphone stopped unexpectedly.",
        action: "Try again, or type your story — the box below works exactly the same.",
      };
  }
}

/** The browser's speech recogniser, or null where there is none. */
export function getRecognitionClass(win = typeof window === "undefined" ? null : window) {
  if (!win) return null;
  return win.SpeechRecognition ?? win.webkitSpeechRecognition ?? null;
}

export function isVoiceSupported(win) {
  return getRecognitionClass(win) !== null;
}

/**
 * Start dictation.
 *
 * Returns a handle with `stop()`. `onText` receives finalised phrases only, so
 * a respondent never watches their words being rewritten mid-sentence. `onError`
 * receives one of the reason constants above.
 *
 * Never throws: a failure to start is reported through `onError` like any other,
 * because a thrown exception here would break the screen a respondent is
 * halfway through.
 */
export function startDictation({ onText, onError, onEnd, win, lang = "en-GB" } = {}) {
  const Recognition = getRecognitionClass(win);
  if (!Recognition) {
    onError?.(VOICE_UNSUPPORTED);
    return { stop: () => {}, active: false };
  }

  let recogniser;
  try {
    recogniser = new Recognition();
  } catch {
    onError?.(VOICE_FAILED);
    return { stop: () => {}, active: false };
  }

  recogniser.lang = lang;
  recogniser.continuous = true;
  // Interim results would rewrite the box as someone speaks, which reads as the
  // app second-guessing them. Only settled phrases are appended.
  recogniser.interimResults = false;

  recogniser.onresult = (event) => {
    let text = "";
    for (let i = event.resultIndex; i < event.results.length; i += 1) {
      const result = event.results[i];
      if (result.isFinal) text += result[0].transcript;
    }
    if (text.trim()) onText?.(text.trim());
  };

  recogniser.onerror = (event) => {
    const code = event?.error;
    if (code === "not-allowed" || code === "service-not-allowed") onError?.(VOICE_DENIED);
    else if (code === "no-speech") onError?.(VOICE_NO_SPEECH);
    else if (code === "network") onError?.(VOICE_NETWORK);
    else if (code === "aborted") onEnd?.();
    else onError?.(VOICE_FAILED);
  };

  recogniser.onend = () => onEnd?.();

  try {
    recogniser.start();
  } catch {
    onError?.(VOICE_FAILED);
    return { stop: () => {}, active: false };
  }

  return {
    active: true,
    stop: () => {
      try {
        recogniser.stop();
      } catch {
        // Already stopped; nothing to do.
      }
    },
  };
}

/**
 * Append dictated words to what is already written.
 *
 * Dictation adds to the story, it never replaces it — someone who typed a
 * paragraph and then spoke a sentence must end up with both.
 */
export function appendDictation(existing, addition) {
  const before = (existing ?? "").trimEnd();
  const words = (addition ?? "").trim();
  if (!words) return existing ?? "";
  if (!before) return words;
  const separator = /[.!?]$/.test(before) ? " " : ". ";
  return `${before}${separator}${words}`;
}
