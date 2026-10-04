"""Sub-tickets: the planner's output parsed into tickets under a parent (doc §4 Planner OUTPUT;
build spec part B `subticket add`, part G dependants, part H `ready-implementers`).

A sub-ticket is a ticket record like any other (tickets/<PARENT>.<n>.yaml) with `parent`,
`depends_on`, `parallel_safe`, `branch` and `head`, and its text at specs/<ID>/subticket.md.

The planner prompt asks for "ID / Title" without fixing the id's form, so real plans use
`T-0001-A`, `ST-1` or `T-0001.1`, usually under a `##` heading, with bold field names. The store
numbers them <PARENT>.1, .2, … in plan order and keeps the planner's own id as `label`.

A later plan for the same parent (a re-plan after a failed parent-close check) continues that
numbering: its sub-tickets take the next free ids after the parent's existing ones, its
`Depends on:` lines may name an existing sub-ticket, and a head line that reuses an existing
sub-ticket's id is refused.

A field line may start with a `- ` or `* ` list bullet, before any bold marks. Every sub-ticket
needs a `Depends on:` line (`Depends on: none` when it depends on nothing); a plan with a
sub-ticket that has none is refused with that sub-ticket's label.
"""
from __future__ import annotations

import re

LABEL = r"(?:T-\d{4}[.-][A-Za-z0-9]+|ST-\d+)"
HEAD_RE = re.compile(r"^(?:#{1,4}\s+)?\**(" + LABEL + r")\**\s+/\s+(.+?)\s*$")  # a heading or a line at column 0, never a bullet
FIELD_RE = re.compile(r"^\s*(?:[-*]\s+)?\**\s*([A-Z][A-Za-z -]+?)\s*:\s*\**\s*(.*)$")
REF_RE = re.compile(r"T-\d{4}(?:[.-][A-Za-z0-9]+)?|ST-\d+")
SATISFIED = ("merged", "closed")
NONE_RE = re.compile(r"^\W*(none|n/?a|nothing|no dependenc)|^\W*$", re.I)  # "none.", "n/a", "— (none)", "-"
IN_FLIGHT_STATES = ("checks-in-flight", "ready-for-merge")
# The planner's field names (doc §4 Planner OUTPUT), lower case: a line naming one opens that field.
PLAN_FIELDS = ("scope", "acceptance", "interim tests", "tests to change", "protected paths", "out of scope",
               "depends on", "parallel-safe", "coverage map")
SIBLING_TEST_RE = re.compile(r"`([^`\s]+)`\s*\(added by\s+[^)]+\)")


def _is_heading(line: str) -> bool:
    return bool(re.match(r"^#{1,4}\s+\S", line))


def sibling_tests(text: str) -> list[str]:
    """The test files a sub-ticket's "Tests to change" field lists as added by an earlier sibling
    (`` `<file>[::<test>]` (added by <ID>) ``), in order, without repeats. The field runs from its
    own line to the next plan field or heading; the same form anywhere else is ignored."""
    paths: list[str] = []
    inside = False
    for line in text.splitlines():
        f = FIELD_RE.match(line)
        if (f and f.group(1).strip().lower() in PLAN_FIELDS) or _is_heading(line):
            inside = bool(f) and f.group(1).strip().lower() == "tests to change"
        if inside:
            for m in SIBLING_TEST_RE.finditer(line):
                path = m.group(1).split("::", 1)[0]
                if path not in paths:
                    paths.append(path)
    return paths


def parse(planner_output: str, parent: str, existing=()) -> list[dict]:
    """Split a PLANNED planner output into sub-tickets, in plan order. Each: id (<parent>.<n>),
    label (the planner's id), title, depends_on (sibling ids, existing sub-ticket ids, plus other
    parents' ids for a cross-ticket dependency), parallel_safe, text (its block, then the plan's
    shared sections). `existing` holds the ids of the parent's sub-tickets already in the store;
    new ones are numbered after the highest of them."""
    lines = planner_output.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("STATUS:"):
            lines = lines[:i]
            break
    heads = [(i, m) for i, line in enumerate(lines) if (m := HEAD_RE.match(line))]
    if not heads:
        return []
    labels = [m.group(1) for _, m in heads]
    dup = sorted({x for x in labels if labels.count(x) > 1})
    if dup:
        raise ValueError(f"sub-ticket id used more than once in the plan: {', '.join(dup)}")
    existing = set(existing)
    for label in labels:
        if label in existing:
            raise ValueError(f"{label}: {label} is already a sub-ticket of {parent}; give the new sub-ticket another id")
    first = max((int(x.rsplit(".", 1)[1]) for x in existing), default=0) + 1
    alias = {m.group(1): f"{parent}.{n}" for n, (_, m) in enumerate(heads, first)}

    def block_end(start: int) -> int:
        for j in range(start + 1, len(lines)):
            if HEAD_RE.match(lines[j]) or _is_heading(lines[j]) or re.match(r"^\s*Coverage map", lines[j]):
                return j
        return len(lines)

    # Shared sections: everything before the first sub-ticket (grounding, fixture preludes) minus
    # the plan's title line. Every sub-ticket needs them, so each sub-ticket text carries them.
    preamble = "\n".join(lines[:heads[0][0]]).strip()
    preamble = re.sub(r"\A#\s+.*\n?", "", preamble).strip()

    subs = []
    for i, m in heads:
        body = lines[i:block_end(i)]
        # Parallel-safe defaults to no: a plan that does not say "yes" runs that sub-ticket alone.
        sub = {"id": alias[m.group(1)], "label": m.group(1), "title": m.group(2).strip(" :*"),
               "depends_on": [], "parallel_safe": False}
        has_depends_on = False
        for line in body[1:]:
            f = FIELD_RE.match(line)
            if not f:
                continue
            key, val = f.group(1).strip().lower(), f.group(2).strip()
            if key == "depends on":
                has_depends_on = True
                deps: list[str] = []
                if not NONE_RE.match(val):
                    for ref in REF_RE.findall(val) + [f"{parent}{x}" for x in re.findall(r"(?<![\w-])\.\d+\b", val)]:
                        if ref in alias.values():
                            dep = ref
                        elif ref in alias:
                            dep = alias[ref]
                        elif ref in existing:
                            dep = ref  # a sub-ticket of an earlier plan, usually merged
                        elif ref[:6] != parent and re.fullmatch(r"T-\d{4}.*", ref):
                            dep = ref[:6]  # another parent ticket (or one of its sub-tickets): wait for that parent
                        elif re.fullmatch(re.escape(parent) + r"\.\d+", ref):
                            raise ValueError(f"{sub['label']}: depends on {ref}, which is not a sub-ticket of this plan")
                        else:
                            continue
                        if dep != sub["id"] and dep not in deps:
                            deps.append(dep)
                    if not deps:
                        raise ValueError(f"{sub['label']}: cannot resolve `Depends on: {val}` to a sub-ticket of this plan or another ticket")
                sub["depends_on"] = deps
            elif key == "parallel-safe":
                sub["parallel_safe"] = val.lower().startswith("yes")
        if not has_depends_on:
            raise ValueError(f'{sub["label"]}: no "Depends on:" line; write "Depends on: none" when it depends on nothing')
        text = "\n".join(body).rstrip() + "\n"
        if preamble:
            text += "\n## Shared plan context (from the plan; applies to every sub-ticket)\n\n" + preamble + "\n"
        sub["text"] = text
        subs.append(sub)
    return subs


def ready_implementers(subs: list[dict], status_of=None) -> list[str]:
    """Doc §Routing table, Planner row: sub-tickets whose dependencies are merged (a dependency on
    another parent ticket: closed), minus any with a run in flight; a parallel_safe=false one runs
    alone (listed only when no sibling is in flight, and nothing is listed with it; nothing is
    listed while it is in flight).

    `subs` are the parent's sub-ticket records. `status_of(ticket_id)` resolves a dependency that
    is not a sibling; without it such a dependency counts as unmet."""
    by_id = {s["id"]: s for s in subs}

    def met(dep: str) -> bool:
        if dep in by_id:  # a sibling must be merged; one the human closed parks the parent instead
            return by_id[dep]["status"] == "merged"
        return (status_of(dep) if status_of else None) in SATISFIED

    in_flight = [s for s in subs if s.get("in_flight") or s.get("status") in IN_FLIGHT_STATES]
    if any(not s.get("parallel_safe", True) for s in in_flight):
        return []
    ready = [s for s in subs
             if s.get("status") in ("ready-for-implementer", "waiting-dependencies") and not s.get("in_flight")
             and all(met(d) for d in s.get("depends_on", []))]
    if in_flight:
        ready = [s for s in ready if s.get("parallel_safe", True)]
    elif any(not s.get("parallel_safe", True) for s in ready):
        return [next(s for s in ready if not s.get("parallel_safe", True))["id"]]
    return [s["id"] for s in ready]
