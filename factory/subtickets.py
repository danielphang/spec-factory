"""Sub-tickets: the planner's output parsed into tickets under a parent (doc §4 Planner OUTPUT;
build spec part B `subticket add`, part G dependants, part H `ready-implementers`).

A sub-ticket is a ticket record like any other (tickets/<PARENT>.<n>.yaml) with `parent`,
`depends_on`, `parallel_safe`, `branch` and `head`, and its text at specs/<ID>/subticket.md.
"""
from __future__ import annotations

import re

HEAD_RE = re.compile(r"^\s*(?:[-*]\s+|#{1,4}\s+)?(T-\d{4}\.\d+)\s*(?:[/:–—-]\s*)?(.*?)\s*$")
FIELD_RE = re.compile(r"^\s*([A-Z][A-Za-z -]+?):\s*(.*)$")
DEPENDS = "depends on"
PARALLEL = "parallel-safe"


def parse(planner_output: str) -> list[dict]:
    """Split a PLANNED planner output into sub-tickets, in order. Each: id, title, depends_on
    (list of ids), parallel_safe (bool), text (the sub-ticket's own block, verbatim)."""
    subs: list[dict] = []
    cur: dict | None = None
    buf: list[str] = []
    in_coverage = False

    def flush() -> None:
        nonlocal cur, buf
        if cur is not None:
            cur["text"] = "\n".join(buf).rstrip() + "\n"
            subs.append(cur)
        cur, buf = None, []

    for line in planner_output.splitlines():
        if re.match(r"^\s*(#+\s*)?Coverage map", line):
            flush()
            in_coverage = True
            continue
        if line.startswith("STATUS:"):
            flush()
            break
        m = HEAD_RE.match(line)
        if m and not in_coverage:
            flush()
            cur = {"id": m.group(1), "title": m.group(2).strip(" :"), "depends_on": [], "parallel_safe": True}
            buf = [line]
            continue
        if cur is None:
            continue
        buf.append(line)
        f = FIELD_RE.match(line)
        if not f:
            continue
        key, val = f.group(1).strip().lower(), f.group(2).strip()
        if key == DEPENDS:
            cur["depends_on"] = [] if val.lower().startswith("none") else re.findall(r"T-\d{4}\.\d+", val)
        elif key == PARALLEL:
            cur["parallel_safe"] = val.lower().startswith("yes")
    flush()
    return subs


def ready_implementers(subs: list[dict]) -> list[str]:
    """Doc §Routing table, Planner row: sub-tickets in ready-for-implementer whose dependencies
    are merged, minus any with a run in flight; a parallel_safe=false one runs alone (listed only
    when no sibling is in flight, and nothing is listed with it; nothing is listed while it is).

    `subs` are the parent's sub-ticket records (status, depends_on, parallel_safe, in_flight)."""
    by_id = {s["id"]: s for s in subs}
    in_flight = [s for s in subs if s.get("in_flight") or s.get("status") in ("checks-in-flight", "ready-for-checks")]
    if any(not s.get("parallel_safe", True) for s in in_flight):
        return []
    ready = [s for s in subs
             if s.get("status") == "ready-for-implementer" and not s.get("in_flight")
             and all(by_id.get(d, {}).get("status") == "merged" for d in s.get("depends_on", []))]
    if in_flight:
        ready = [s for s in ready if s.get("parallel_safe", True)]
    elif any(not s.get("parallel_safe", True) for s in ready):
        solo = next(s for s in ready if not s.get("parallel_safe", True))
        return [solo["id"]]
    return [s["id"] for s in ready]
