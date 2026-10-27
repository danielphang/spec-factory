"""One arm's operator measures for the upstream benchmark, read from timestamps. Method: docs/benchmark.md.

  python -m factory.benchmark [--store PATH] [SESSION.jsonl]...

A SESSION is the Claude Code transcript of a session the operator typed into: the baseline arm's
plain session, or the factory arm's runner sessions. --store is the factory arm's throwaway store.
Prints a Markdown table of operator messages, the store's gate and ruling events, operator time,
elapsed time and the sessions' tokens. Writes nothing.

An operator message is a `user` record, not `isMeta` or `isSidechain` and holding no `tool_result`,
whose `promptSource` is `typed`, `queued` or `suggestion_accepted`; a record with no `promptSource`
counts when its text does not start with `<`. Interactions are the operator messages and the store's
decision events (`factory.stats.DECISIONS`). Interactions no more than 15 minutes apart form one
sitting, counted from its first interaction to its last plus one minute; operator time is the sum.
It measures interactions, not attention, and undercounts reading and review time.
"""
from __future__ import annotations

import argparse
import os
import sys

from factory.cost import _log_records, _records, _user_text, _when, transcript_usage
from factory.stats import DECISIONS

PROMPT_SOURCES = ("typed", "queued", "suggestion_accepted")
SITTING_GAP = 900  # seconds: a longer gap between interactions starts a new sitting
SITTING_ADD = 60  # seconds added to each sitting


def _operator_message(o: dict) -> bool:
    text = _user_text(o)
    if text is None or o.get("isMeta") or o.get("isSidechain") or not o.get("timestamp"):
        return False
    content = o["message"]["content"]
    if isinstance(content, list) and any(isinstance(x, dict) and x.get("type") == "tool_result" for x in content):
        return False
    source = o.get("promptSource")
    return source in PROMPT_SOURCES if source is not None else not text.startswith("<")


def sittings(times: list) -> tuple[float, int]:
    """(operator minutes, sittings) of a list of interaction times."""
    seconds, count, start, prev = 0.0, 0, None, None
    for t in sorted(times):
        if prev is None or (t - prev).total_seconds() > SITTING_GAP:
            if prev is not None:
                seconds += (prev - start).total_seconds() + SITTING_ADD
            start, count = t, count + 1
        prev = t
    if prev is not None:
        seconds += (prev - start).total_seconds() + SITTING_ADD
    return seconds / 60, count


def report(store: str | None, sessions: list[str]) -> list[str]:
    """The report's table rows, from a store's event log and session transcripts."""
    messages = decisions = ctx = out = 0
    interactions, stamps = [], []
    for path in sessions:
        for o in _records(path):
            if o.get("timestamp"):
                stamps.append(_when(o["timestamp"]))
            if _operator_message(o):
                messages += 1
                interactions.append(_when(o["timestamp"]))
        _, c, u = transcript_usage(path)
        ctx, out = ctx + c, out + u
    for e in _log_records(store) if store else ():
        when = _when(e.get("ts"))
        if when is not None:
            stamps.append(when)
        if e.get("event") in DECISIONS:
            decisions += 1
            if when is not None:
                interactions.append(when)
    minutes, count = sittings(interactions)
    elapsed = f"{(max(stamps) - min(stamps)).total_seconds() / 3600:.2f}" if stamps else "-"
    return ["| measure | value |", "|---|---|",
            f"| operator messages | {messages} |",
            f"| gate and ruling events | {decisions} |",
            f"| operator time, minutes | {minutes:.1f} ({count} sittings) |",
            f"| elapsed, hours | {elapsed} |",
            f"| session tokens | {ctx} context, {out} output |"]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="factory.benchmark", description=__doc__.splitlines()[0])
    ap.add_argument("--store")
    ap.add_argument("sessions", nargs="*", metavar="SESSION.jsonl")
    args = ap.parse_args(argv)
    refusal = None
    if args.store is None and not args.sessions:
        refusal = "give --store, a session transcript, or both"
    elif missing := [s for s in args.sessions if not os.path.isfile(s)]:
        refusal = f"not a file: {missing[0]}"
    elif args.store is not None and not os.path.isdir(os.path.join(args.store, "log")):
        refusal = f"store has no log/ directory: {args.store}"
    if refusal:
        print(f"factory.benchmark: {refusal}", file=sys.stderr)
        return 2
    print("\n".join(report(args.store, args.sessions)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
