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
    if not nonblank or not nonblank[0].startswith("CONFIDENCE:"):
        return {"status": None, "error": "parse failure: CONFIDENCE line missing after STATUS"}
    # CONFIDENCE may wrap onto continuation lines; ESCALATIONS: is the next labelled line.
    esc_i = next((i for i, ln in enumerate(nonblank) if i > 0 and ln.startswith("ESCALATIONS:")), None)
    if esc_i is None:
        return {"status": None, "error": "parse failure: ESCALATIONS line missing after CONFIDENCE"}
    confidence = " ".join([nonblank[0].split(":", 1)[1].strip()] + nonblank[1:esc_i]).strip()
    esc_head = nonblank[esc_i].split(":", 1)[1].strip()
    tail = nonblank[esc_i + 1:]
    items = []
    if esc_head and esc_head.lower() != "none":
        items.append(esc_head)
    for ln in tail:
        items.append(ln.lstrip("-* ").strip())
    if esc_head.lower() == "none" and not tail:
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
