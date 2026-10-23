"""STATUS trailer parser: one implementation, used by `run finish`.

The LAST line matching ^STATUS: wins. CONFIDENCE: is the next labelled line after it and
ESCALATIONS: the next labelled line after that (models wrap and interleave commentary, so lines
between are continuation). A `none` head (`none` in any case, then end of line or punctuation) with
nothing below it is no escalation; prose after it on that line is returned as `escalations_note`
and kept with the run. A `none` head with further lines is a real list, every line from the head
on an item verbatim; so is anything else (operator decision 2026-10-01, option (b)). Claude Code's
attribution footer, a line below the ESCALATIONS line that is exactly `🤖 Generated with [Claude
Code](<link>)`, is dropped first: Claude Code appends it after the trailer, and the role never
raised it (T-0058, #88).
"""
from __future__ import annotations

import re

STATUS_RE = re.compile(r"^STATUS:\s*(\S+)\s*$")
NONE_HEAD_RE = re.compile(r"^none\s*($|[.,;:—–-])", re.I)
ATTRIBUTION_RE = re.compile(r"^🤖 Generated with \[Claude Code\]\(\S+\)$")


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
    tail = [ln for ln in tail if not ATTRIBUTION_RE.fullmatch(ln)]
    # Operator decision 2026-10-01, option (b): a `none` head is `none` in any case followed by end
    # of line or punctuation (never a space and a word). A none head with prose and nothing below
    # routes as no escalation and the prose is kept with the run (escalations_note). A none head
    # with further lines is a real list; anything else is an item. Unsure text goes to the queue.
    # Claude Code's attribution footer was dropped from the tail first: Claude Code appends it after
    # the trailer and the role never raised it, so it never turns a none head into a list (#88).
    note = None
    if not tail and (not esc_head or NONE_HEAD_RE.match(esc_head)):
        items = []
        if esc_head and not re.fullmatch(r"none\.?", esc_head, re.I):
            note = esc_head
    else:
        items = [x for x in [esc_head, *tail] if x]
    return {"status": status, "confidence": confidence, "escalations": [i for i in items if i],
            "escalations_note": note}


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
