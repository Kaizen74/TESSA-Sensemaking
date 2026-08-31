"""Rate limiting for the public capture endpoints (PRD §4).

The public endpoints are "token-gated, rate-limited, identifier-free". Those
three words are in tension: the usual way to rate-limit is per client IP, and
constraint 9 forbids this app from ever knowing a client IP.

So the limit is per **capture link token**, not per person. A token is something
the operator created and can revoke; it identifies a link, never a respondent.
Counters live in memory only and are keyed by token, so nothing about who
submitted anything is written down or even held between restarts.

What this protects against is a link left open on a LAN being hammered. What it
deliberately does not do is single out one respondent — it cannot, and that is
the point.
"""

from __future__ import annotations

import threading
import time
from collections import deque

#: Submissions allowed per token per window. A workshop of thirty people all
#: pressing send at once must sail through; this only bites on abuse.
SUBMIT_LIMIT = 60

#: Reads allowed per token per window. Higher than submits: a respondent loads
#: the questions once, but a reload or a flaky connection can repeat it.
FETCH_LIMIT = 240

#: Window length in seconds.
WINDOW_SECONDS = 60


class RateLimiter:
    """A sliding-window counter keyed by an opaque string.

    Deliberately simple and in-process: this is one operator's laptop serving a
    workshop over Tailscale, not a public web service.
    """

    def __init__(self, limit: int, window_seconds: int = WINDOW_SECONDS) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def check(self, key: str, now: float | None = None) -> bool:
        """Record a hit and report whether it is within the limit."""
        moment = time.monotonic() if now is None else now
        cutoff = moment - self.window_seconds

        with self._lock:
            bucket = self._hits.setdefault(key, deque())
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()

            if len(bucket) >= self.limit:
                return False

            bucket.append(moment)
            return True

    def reset(self, key: str | None = None) -> None:
        """Forget counters. Used by tests and when a link is revoked."""
        with self._lock:
            if key is None:
                self._hits.clear()
            else:
                self._hits.pop(key, None)

    def remaining(self, key: str, now: float | None = None) -> int:
        """How many hits are still allowed in the current window."""
        moment = time.monotonic() if now is None else now
        cutoff = moment - self.window_seconds
        with self._lock:
            bucket = self._hits.get(key)
            if bucket is None:
                return self.limit
            live = sum(1 for stamp in bucket if stamp > cutoff)
            return max(0, self.limit - live)


#: Module-level limiters, shared by every request.
submit_limiter = RateLimiter(SUBMIT_LIMIT)
fetch_limiter = RateLimiter(FETCH_LIMIT)


def reset_all() -> None:
    """Clear every counter. Tests call this between cases."""
    submit_limiter.reset()
    fetch_limiter.reset()
