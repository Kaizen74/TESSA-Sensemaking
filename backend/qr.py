"""QR codes for capture links (PRD §4, §1.8).

A QR is how a phone gets to the capture wizard without anyone typing a URL, so
it appears on the admin home screen, in the link manager's printable poster, and
optionally on the paper story card.

Rendered locally with no network call, like everything else (constraint 4).
Black on white at the default error-correction level, which survives being
printed and photographed off a wall.
"""

from __future__ import annotations

import io

import qrcode
from qrcode.constants import ERROR_CORRECT_M

#: Pixels per QR module. 10 gives a code that scans reliably from a poster on a
#: wall without producing a needlessly large PNG.
DEFAULT_BOX_SIZE = 10

#: Quiet zone, in modules. Four is the QR specification's minimum; going below
#: it is the most common reason a printed code will not scan.
QUIET_ZONE_MODULES = 4


def qr_png_bytes(payload: str, box_size: int = DEFAULT_BOX_SIZE) -> bytes:
    """Return a PNG of ``payload`` as QR, as raw bytes.

    Error correction is set to M (about 15% recoverable), which tolerates a
    scuffed print or a poor camera angle without inflating the code.
    """
    code = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_M,
        box_size=box_size,
        border=QUIET_ZONE_MODULES,
    )
    code.add_data(payload)
    code.make(fit=True)

    image = code.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
