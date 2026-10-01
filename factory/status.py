"""STATUS trailer parser: one implementation, used by `run finish`.

The LAST line matching ^STATUS: wins. CONFIDENCE: is the next labelled line after it and
ESCALATIONS: the next labelled line after that (models wrap and interleave commentary, so lines
between are continuation). The escalation list is empty iff the ESCALATIONS head is exactly
`none` (trailing period tolerated) with nothing after it; otherwise every non-blank line from
the head on is an item, verbatim.
"""
from __future__ import annotations

import re

STATUS_RE = re.compile(r"^STATUS:\s*(\S+)\s*$")


def parse(text: str) -> dict:
    lines = text.splitlines()
    idx = None
    for i, line in enumerate(lines):
        if STATUS_RE.match(line.strip()):
            idx = i
    if idx is None:
        return {"status": None, "error": "parse failure: no STATUS line"}
    status = STATUS_RE.match(lines[idx].strip()).group(1)
    nonblank = [ln.strip() for ln in lines[idx + 1:] if ln.strip()]
    # Models interleave commentary and wrap lines: CONFIDENCE is the next *labelled* line after
    # STATUS, ESCALATIONS the next labelled line after that; everything between is continuation.
    conf_i = next((i for i, ln in enumerate(nonblank) if ln.startswith("CONFIDENCE:")), None)
    if conf_i is None:
        return {"status": None, "error": "parse failure: no CONFIDENCE line after STATUS"}
    esc_i = next((i for i, ln in enumerate(nonblank) if i > conf_i and ln.startswith("ESCALATIONS:")), None)
    if esc_i is None:
        return {"status": None, "error": "parse failure: no ESCALATIONS line after CONFIDENCE"}
    confidence = " ".join([nonblank[conf_i].split(":", 1)[1].strip()] + nonblank[conf_i + 1:esc_i]).strip()
    esc_head = nonblank[esc_i].split(":", 1)[1].strip()
    tail = [ln.lstrip("-* ").strip() for ln in nonblank[esc_i + 1:]]
    # Design rule: the list is empty iff the head is exactly `none` (a trailing period tolerated)
    # and nothing follows. Anything else on or after the line is an escalation, verbatim, so no
    # text is ever dropped; the human queue sorts "none, but…" prose from real items.
    if re.fullmatch(r"none\.?", esc_head, re.I) and not tail:
        items = []
    else:
        items = [x for x in [esc_head, *tail] if x]
    return {"status": status, "confidence": confidence, "escalations": [i for i in items if i]}


def strip_trailer(text: str) -> str:
    """Return the text above the final STATUS/CONFIDENCE/ESCALATIONS block (the spec body)."""
    lines = text.splitlines()
    idx = None
    for i, line in enumerate(lines):
        if STATUS_RE.match(line.strip()):
            idx = i
    if idx is None:
        return text.rstrip() + "\n"
    return "\n".join(lines[:idx]).rstrip() + "\n"
