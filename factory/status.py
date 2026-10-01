"""STATUS trailer parser: one implementation, used by `run finish`.

The LAST line matching ^STATUS: wins; the next non-blank line must be CONFIDENCE:, the next
ESCALATIONS:; everything after is the escalation list. `none` iff exactly `none`.
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
    tail = nonblank[esc_i + 1:]
    items = []
    if esc_head and not esc_head.lower().startswith("none"):
        items.append(esc_head)
    for ln in tail:
        items.append(ln.lstrip("-* ").strip())
    if esc_head.lower().startswith("none") and not tail:
        items = []
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
