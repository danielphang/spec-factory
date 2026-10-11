"""`factory stats`: what each role catches and what it costs, counted from one or more stores.

A store is read from `runs/*/meta.yaml`, `runs/*/output.md`, `runs/*/input.md` and `log/*.jsonl`, and
Claude Code transcripts only from the `--transcripts` directories (placed on runs by
`cost.match_transcripts`). Nothing is written. `report()` returns four Markdown tables:
A. runs and verdicts by role and model; B. parks by normalised reason, with the gate and merge
decisions; C. each spec defect caught downstream, against the runs that wrote and critiqued that spec;
D. each role's wall time and tokens, from the run's cost record, else its transcript.

Runs are windowed by `started` and events by `ts`: `since` inclusive, `until` exclusive. Looking up
who wrote and who critiqued a spec ignores the window. A `park.corrected` event applies when it is
dated before `until`.
"""
from __future__ import annotations

import glob
import os
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from factory.cli import ROLES
from factory.cost import _records, _when, gate_failures, match_transcripts, transcript_usage
from factory.store import Refused, read_yaml

# Verdicts that change what happens next, from any role.
CHANGED = frozenset({"REQUEST-CHANGES", "ESCALATE", "FAILED", "SPEC-DEFECT", "REVISE", "BLOCKED"})
# A BLOCKING finding: a line starting `[BLOCKING]` after optional spaces and a `-`, `*` or `1.` marker.
BLOCKING = re.compile(r"^\s*(?:[-*]|1\.)?\s*\[BLOCKING\]")
# Park-reason normalisation, step 2: applied in order to the reason's first line. Extend this list
# when a new reason carries an id that splits one kind of park into many rows.
PARK_RULES = (
    (re.compile(r"\brun-\d+-\w+"), "<run>"),
    (re.compile(r"\bT-\d+(?:\.\d+)*\b"), "<ticket>"),
    (re.compile(r"\b(?=\d*[a-f])[0-9a-f]{7,40}\b"), "<sha>"),
)
IN_FLIGHT = (None, "running")
RUN_ID = re.compile(r"run-\d+-\w+")


def parse_when(text: str, flag: str) -> datetime:
    """An ISO date or date-time, taken as UTC when it has no zone; refused when unparsable."""
    try:
        return _when(text)
    except ValueError:
        raise Refused(f"factory stats: {flag} {text!r} is not an ISO date or date-time") from None


def normalise(reason: str) -> str:
    """First line, ids replaced (PARK_RULES), first two `: `-separated fields, trimmed, no trailing colon."""
    line = (reason or "").split("\n", 1)[0]
    for pattern, repl in PARK_RULES:
        line = pattern.sub(repl, line)
    line = ": ".join(line.split(": ")[:2]).strip()
    return line[:-1] if line.endswith(":") else line


def _parent(ticket: str) -> str:
    return re.sub(r"\.\d+$", "", ticket)


def _load(store: str) -> tuple[list[dict], list[dict]]:
    """(runs, events) of one store. Each run is its meta.yaml plus `_store`, `_id`, `_dir`, `_started`."""
    runs = []
    for mf in sorted(glob.glob(os.path.join(store, "runs", "*", "meta.yaml"))):
        m = read_yaml(Path(mf)) or {}
        d = os.path.dirname(mf)
        m.update(_store=store, _id=os.path.basename(d), _dir=d, _started=_when(m.get("started")))
        runs.append(m)
    events = []
    for lf in sorted(glob.glob(os.path.join(store, "log", "*.jsonl"))):
        for e in _records(lf):
            if isinstance(e, dict) and e.get("ts"):
                events.append({**e, "_ts": _when(e["ts"])})
    events.sort(key=lambda e: e["_ts"])
    return runs, events


def _key(row: tuple[str, str]) -> tuple:
    role, model = row
    return (ROLES.index(role), "", model) if role in ROLES else (len(ROLES), role, model)


def _blocking(run_dir: str) -> int:
    p = os.path.join(run_dir, "output.md")
    if not os.path.isfile(p):
        return 0
    with open(p, encoding="utf-8") as fh:
        return sum(1 for ln in fh if BLOCKING.match(ln) and "RESOLVED" not in ln)


def _parks(events: list[dict], until: datetime | None) -> list[dict]:
    """Every `ticket.parked` event, each with `_reason` after the corrections dated before `until`."""
    parks = [{**e, "_reason": e.get("reason") or ""} for e in events if e.get("event") == "ticket.parked"]
    for c in events:
        if c.get("event") != "park.corrected" or (until is not None and c["_ts"] >= until):
            continue
        hits = [p for p in parks if p.get("ticket") == c.get("ticket") and p["_ts"] < c["_ts"]
                and p["_reason"] == c.get("previous")]
        if hits:
            hits[-1]["_reason"] = c.get("reason") or ""
    return parks


def _table(header: list[str], rows: list[list]) -> list[str]:
    return ["| " + " | ".join(header) + " |", "|" + "---|" * len(header),
            *("| " + " | ".join(str(c) for c in r) + " |" for r in rows)]


def report(stores: list[str], since: datetime | None, until: datetime | None,
           transcripts: list[str]) -> str:
    def inside(t: datetime | None) -> bool:
        return t is not None and (since is None or t >= since) and (until is None or t < until)

    loaded = {s: _load(s) for s in stores}
    placed = match_transcripts(transcripts, stores) if transcripts else {}
    windowed = [r for s in stores for r in loaded[s][0] if inside(r["_started"])]
    done = [r for r in windowed if r.get("status") not in IN_FLIGHT]
    rows: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in done:
        rows[(str(r.get("role")), str(r.get("model")))].append(r)
    order = sorted(rows, key=_key)

    out = ["# factory stats", "", "Stores: " + ", ".join(stores),
           f"Window: from {since.isoformat() if since else 'the first record'} (inclusive) "
           f"to {until.isoformat() if until else 'now'} (exclusive), runs by started and events by ts; "
           f"{len(windowed) - len(done)} runs in flight left out", ""]

    # A. Runs and verdicts by role and model
    a_rows = []
    for role, model in order:
        runs = [r for r in rows[(role, model)] if r.get("status") != "KILLED"]
        killed = len(rows[(role, model)]) - len(runs)
        verdicts = Counter(str(r.get("status")) for r in runs)
        blocking = sum(_blocking(r["_dir"]) for r in runs) if role in ("reviewer", "critic") else "-"
        gate = "-"
        if role == "implementer":
            fails = read = 0
            for r in runs:
                tx, inp = placed.get((r["_store"], r["_id"])), os.path.join(r["_dir"], "input.md")
                n = gate_failures(tx, inp) if tx and os.path.isfile(inp) else None
                if n is not None:
                    fails, read = fails + n, read + 1
            gate = f"{fails} in {read} read, {len(runs) - read} not recorded"
        a_rows.append([role, model, len(runs), killed, sum(verdicts[s] for s in CHANGED),
                       ", ".join(f"{s} {n}" for s, n in sorted(verdicts.items())) or "-", blocking, gate])
    out += ["## A. Runs and verdicts by role and model", "",
            *_table(["role", "model", "runs", "killed", "changed outcome", "verdicts", "BLOCKING findings",
                     "gate fails fixed before hand-off"], a_rows), ""]

    # B. Where tickets stop
    parks = [p for s in stores for p in _parks(loaded[s][1], until) if inside(p["_ts"])]
    reasons = Counter(normalise(p["_reason"]) for p in parks)
    events = [e for s in stores for e in loaded[s][1] if inside(e["_ts"])]
    resolved = Counter(e.get("kind") for e in events if e.get("event") == "human.resolved")
    refused = Counter(e.get("reason") for e in events if e.get("event") == "merge.refused")
    decisions = [["spec approved", sum(1 for e in events if e.get("event") == "approval.recorded"
                                       and e.get("kind") == "spec")],
                 ["spec changes requested", resolved.pop("request-changes", 0)],
                 *([f"resolved: {k}", n] for k, n in sorted(resolved.items(), key=lambda kv: str(kv[0]))),
                 *([f"merge refused: {k}", n] for k, n in sorted(refused.items(), key=lambda kv: str(kv[0]))),
                 ["archive refused", sum(n for k, n in reasons.items() if k == "archive" or k.startswith("archive:"))]]
    out += ["## B. Where tickets stop", "",
            *_table(["park reason", "parks"],
                    [*([k, n] for k, n in sorted(reasons.items(), key=lambda kv: (-kv[1], kv[0]))),
                     ["all parks", len(parks)]]), "",
            *_table(["gate or merge decision", "count"], decisions), ""]

    # C. Where spec defects were caught and where they came from
    catches = sorted((r for r in done if r.get("ticket") and (r.get("role"), r.get("status")) in
                      (("verifier", "SPEC-DEFECT"), ("implementer", "BLOCKED"))), key=lambda r: r["_started"])
    critics = defaultdict(list)  # (store, ticket) -> finished critic runs, every date
    added = {}  # (store, ticket, version) -> spec.added source, every date
    for s in stores:
        for r in loaded[s][0]:
            if r.get("role") == "critic" and r.get("status") not in (*IN_FLIGHT, "KILLED") and r["_started"]:
                critics[(s, r.get("ticket"))].append(r)
        for e in loaded[s][1]:
            if e.get("event") == "spec.added":
                added[(s, e.get("ticket"), e.get("version"))] = str(e.get("source"))
    revise = {k: sum(1 for r in v if r.get("status") == "REVISE") for k, v in critics.items()}
    c_rows = []
    for r in catches:
        s, parent, ver = r["_store"], _parent(str(r["ticket"])), r.get("spec_version")
        src = added.get((s, parent, ver))
        wrote = "unknown" if src is None else src if RUN_ID.fullmatch(src) else "human"
        of_ver = sorted((c for c in critics[(s, parent)] if c.get("spec_version") == ver), key=lambda c: c["_started"])
        c_rows.append([r["_id"], r["status"], r["ticket"], ver, wrote, of_ver[-1]["_id"] if of_ver else "none",
                       revise.get((s, parent), 0)])
    approved: dict[tuple[str, str], datetime] = {}
    for s in stores:
        for e in loaded[s][1]:
            if e.get("event") == "approval.recorded" and e.get("kind") == "spec" and inside(e["_ts"]):
                approved.setdefault((s, e.get("ticket")), e["_ts"])
    split = {"yes": [0, 0], "no": [0, 0]}
    for (s, t), ts in approved.items():
        cell = split["yes" if revise.get((s, t), 0) else "no"]
        cell[0] += 1
        cell[1] += any(r["_store"] == s and _parent(str(r["ticket"])) == t and r["_started"] > ts for r in catches)
    out += ["## C. Where spec defects were caught and where they came from", "",
            *_table(["caught by", "status", "ticket", "spec version", "written by", "critiqued by",
                     "critic REVISE on the ticket"], c_rows), "",
            *_table(["critic REVISE on the ticket", "approved specs", "caught downstream"],
                    [["yes", *split["yes"]], ["no", *split["no"]]]), ""]

    # D. What each role costs
    d_rows = []
    for role, model in order:
        wall = ctx = toks = 0
        usd = 0.0
        src = Counter()
        for r in rows[(role, model)]:
            wall += r.get("wall_s") or 0
            claude = r.get("claude") if isinstance(r.get("claude"), dict) else {}
            u = claude.get("usage")
            tx = placed.get((r["_store"], r["_id"]))
            if isinstance(u, dict):
                src["record"] += 1
                ctx += (u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                        + u.get("cache_creation_input_tokens", 0))
                toks += u.get("output_tokens", 0)
                usd += claude.get("total_cost_usd") or 0
            elif tx:
                src["transcript"] += 1
                _, c, o = transcript_usage(tx)
                ctx, toks = ctx + c, toks + o
            else:
                src["none"] += 1
        d_rows.append([role, model, len(rows[(role, model)]), wall, ctx, toks, f"{usd:.2f}",
                       f"record {src['record']}, transcript {src['transcript']}, none {src['none']}"])
    out += ["## D. What each role costs", "",
            *_table(["role", "model", "runs", "wall s", "context tokens", "output tokens", "USD from records",
                     "cost from"], d_rows)]
    return "\n".join(out) + "\n"
