"""Runtime settings.

Constraint 7 (non-technical operator) forbids config editing, so every value
here has a working default. Environment variables exist for the test suite and
for developers, never as something the operator is expected to set.
"""

from __future__ import annotations

import os
from pathlib import Path

#: Repository root — the directory holding ``pyproject.toml``.
ROOT_DIR = Path(__file__).resolve().parent.parent

#: Where the SQLite file and any future local artefacts live (constraint 4).
DATA_DIR = Path(os.environ.get("NL_DATA_DIR", ROOT_DIR / "data"))

#: Port for the local server. See PROGRESS.md "Decisions" for why 8756.
PORT = int(os.environ.get("NL_PORT", "8756"))

HOST = os.environ.get("NL_HOST", "127.0.0.1")


#: Where the built frontend lands. Served by the app when it exists, so a phone
#: on Tailscale reaches the wizard from the same address as the API.
FRONTEND_DIST = Path(os.environ.get("NL_FRONTEND_DIST", ROOT_DIR / "frontend" / "dist"))


def database_url() -> str:
    """Return the SQLAlchemy URL for the local SQLite database."""
    override = os.environ.get("NL_DATABASE_URL")
    if override:
        return override
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{DATA_DIR / 'narrative_lens.db'}"


def lan_host() -> str:
    """The address other devices on the mesh can reach this machine at.

    A QR pointing at ``127.0.0.1`` would work on the operator's laptop and fail
    on every phone that scans it, so the default is the machine's own LAN or
    Tailscale address rather than loopback. Found by asking the OS which local
    address it would use to reach the outside world — no packet is actually
    sent, and nothing is looked up over the network (constraint 4).
    """
    override = os.environ.get("NL_PUBLIC_HOST")
    if override:
        return override

    import socket

    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connecting a UDP socket only sets a route; it transmits nothing.
        probe.connect(("192.0.2.1", 9))  # TEST-NET-1, guaranteed unroutable
        return probe.getsockname()[0]
    except OSError:
        # No network at all: fall back to loopback so the app still runs, and
        # the operator sees an address that plainly will not work off-machine.
        return "127.0.0.1"
    finally:
        probe.close()


def public_base_url() -> str:
    """Base URL a capture link should carry."""
    override = os.environ.get("NL_PUBLIC_BASE_URL")
    if override:
        return override.rstrip("/")
    return f"http://{lan_host()}:{PORT}"
