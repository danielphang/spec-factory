"""Per-(role, model) token cost of one or more intake workflow runs, read from their transcripts.

  uv run python -m factory.cost <workflow transcript dir>...

The dirs are the "Transcript dir" the Workflow tool prints for a run. Context tokens = input +
cache_read + cache_creation per API call; output separate. Claude Code writes one transcript record
for each streamed block of a reply, and each repeats the whole call's usage, so a call is counted
once per message id, from its last record (a record with no id counts on its own); "calls" counts
those ids. Role comes from the computed-task prompt the dispatcher gave the agent. meta.yaml records
the model; this adds the cost.

For reading one store run's transcript: `transcript_usage()` gives its tokens, `match_transcripts()`
places transcripts on store runs, `transcript_record()` gives the cost record `run finish
--transcripts` keeps for a run, and `gate_failures()` counts the gate commands an implementer saw
fail and then fixed before hand-off.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone

import yaml

TASK_PREFIX = "[Workflow harness — computed task]"
RELAY_PREFIX = "[Workflow harness — user request]"  # relays the operator's words: names no run of its own
RUN_DIR = re.compile(r"(/[^\s`'\"]*?)/runs/(run-\d+-\w+)/")


def _records(path: str):
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            try:
                yield json.loads(ln)
            except ValueError:
                continue


def _log_records(store: str):
    """Each parseable record of a store's event log, `log/*.jsonl` in file-name order."""
    for lf in sorted(glob.glob(os.path.join(store, "log", "*.jsonl"))):
        yield from _records(lf)


def _user_text(o: dict) -> str | None:
    """The text of a user record, or None for any other record."""
    if o.get("type") != "user":
        return None
    c = (o.get("message") or {}).get("content") or ""
    return c if isinstance(c, str) else " ".join(x.get("text", "") for x in c if isinstance(x, dict))


def _role(transcript: str) -> str:
    for o in _records(transcript):
        text = _user_text(o)
        if text is None or not text.startswith(TASK_PREFIX):
            continue
        if "bin/factory" in text:
            return "clerk"
        m = re.search(r"runs/run-\d+-(\w+)/", text)
        if m:
            return m.group(1)
        return "stub" if "Stub file" in text else "?"
    return "?"


def _usages(path: str) -> list[dict]:
    """The usage of each model call of one transcript, each message id counted once."""
    last: dict = {}
    for i, o in enumerate(_records(path)):
        m = o.get("message")
        if isinstance(m, dict) and m.get("usage"):
            last[m.get("id") or ("no id", i)] = m["usage"]
    return list(last.values())


def transcript_usage(path: str) -> tuple[int, int, int]:
    """(calls, context tokens, output tokens) of one transcript, each message id counted once."""
    usages = _usages(path)
    ctx = sum(u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
              + u.get("cache_creation_input_tokens", 0) for u in usages)
    return len(usages), ctx, sum(u.get("output_tokens", 0) for u in usages)


def _model(path: str) -> str | None:
    model = None
    for o in _records(path):
        m = o.get("message")
        if isinstance(m, dict) and m.get("usage"):
            model = m.get("model") or model
    return model


def tally(dirs: list[str]) -> dict[tuple[str, str], dict[str, int]]:
    agg: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: {"agents": 0, "calls": 0, "ctx": 0, "out": 0})
    for d in dirs:
        for mf in glob.glob(os.path.join(d, "agent-*.meta.json")):
            tf = mf.replace(".meta.json", ".jsonl")
            calls, ctx, out = transcript_usage(tf)
            a = agg[(_role(tf), (_model(tf) or "?").replace("claude-", ""))]
            a["agents"] += 1
            a["calls"] += calls
            a["ctx"] += ctx
            a["out"] += out
    return agg


def _when(v) -> datetime | None:
    """A timestamp from a run record or transcript, as YAML or JSON gives it; UTC when it has no zone."""
    if v is None or v == "":
        return None
    t = v if isinstance(v, datetime) else datetime.fromisoformat(str(v))
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def _opening(path: str) -> tuple[str, str, datetime | None] | None:
    """(P, R, first timestamp) from the first non-relay user message naming `<P>/runs/<R>/`.

    Reads only up to that message."""
    first = None
    for o in _records(path):
        if first is None and o.get("timestamp"):
            first = _when(o["timestamp"])
        text = _user_text(o)
        if text is None or text.startswith(RELAY_PREFIX):
            continue
        m = RUN_DIR.search(text)
        if m:
            return os.path.realpath(m.group(1)), m.group(2), first
    return None


def _store_paths(store: str) -> set[str]:
    """A store's path and its paths before each `store.migrated` event in its log."""
    here = os.path.realpath(store)
    paths = {here}
    for e in _log_records(store):
        if e.get("event") != "store.migrated" or not e.get("from") or not e.get("to"):
            continue
        src, dst = e["from"], e["to"].rstrip("/")
        if os.path.isabs(src):
            paths.add(os.path.realpath(src))
        elif here.endswith(os.sep + os.path.normpath(dst)):
            paths.add(os.path.realpath(os.path.join(here[:-len(os.path.normpath(dst))], src)))
    return paths


def _window(store: str, run_id: str, cache: dict) -> tuple | None:
    key = (store, run_id)
    if key not in cache:
        mf = os.path.join(store, "runs", run_id, "meta.yaml")
        meta = None
        if os.path.isfile(mf):
            with open(mf, encoding="utf-8") as fh:
                meta = yaml.safe_load(fh) or {}
        cache[key] = None if not meta or not meta.get("started") else (
            _when(meta["started"]), _when(meta.get("finished")))
    return cache[key]


def match_transcripts(dirs: list[str], stores: list[str],
                      modified_since: datetime | None = None) -> dict[tuple[str, str], str]:
    """{(store, run_id): transcript path} for the `*.jsonl` files at any depth under `dirs`.

    A transcript's first user message naming `<P>/runs/<R>/` (relayed user requests skipped) makes
    it a candidate for run R of a store S when its first timestamp lies between R's started and
    finished, unless P is another given store's path. A candidate whose P is S's own path (or S's
    path before a `store.migrated`) wins; otherwise a single remaining candidate is taken. With
    `modified_since`, a file modified before it is not opened."""
    own = {s: _store_paths(s) for s in stores}
    windows: dict = {}
    cands: dict[tuple[str, str], list[tuple[bool, datetime, str]]] = defaultdict(list)
    for d in dirs:
        for tf in sorted(glob.glob(os.path.join(d, "**", "*.jsonl"), recursive=True)):
            if modified_since is not None and os.path.getmtime(tf) < modified_since.timestamp():
                continue
            opened = _opening(tf)
            if opened is None or opened[2] is None:
                continue
            p, r, first = opened
            for s in stores:
                w = _window(s, r, windows)
                if w is None or first < w[0] or (w[1] is not None and first > w[1]):
                    continue
                if any(p in own[o] for o in stores if o != s):
                    continue
                cands[(s, r)].append((p in own[s], first, tf))
    out: dict[tuple[str, str], str] = {}
    for key, cs in cands.items():
        mine = sorted(c for c in cs if c[0])
        # factory: several transcripts on S's own path (a role that spawned a sub-agent naming its run
        # directory) resolve to the earliest; sum them instead if sub-agent cost should count.
        if mine:
            out[key] = mine[0][2]
        elif len(cs) == 1:
            out[key] = cs[0][2]
    return out


def transcript_record(dirs: list[str], store: str, run_id: str, started) -> dict | None:
    """The cost record of a store run that is finishing, from the transcript `match_transcripts()` places
    on it among the files under `dirs` modified since the run started; None when it places none.
    Transcripts carry no dollars."""
    tf = match_transcripts(dirs, [store], modified_since=_when(started)).get((store, run_id))
    if tf is None:
        return None
    usages = _usages(tf)
    keys = ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens", "output_tokens")
    return {"source": "transcript", "transcript": tf, "usage": {k: sum(u.get(k, 0) for u in usages) for k in keys},
            "total_cost_usd": None}


def gate_failures(transcript: str, input_md: str) -> int | None:
    """Gate commands of a run's input that a Bash call failed and a later call passed, once each.

    The gate commands are the backticked commands after "Gate commands" on that line of input.md,
    each matched by its own text: what follows the wrapper's last "; ", less the closing ")". None
    when the input has no such line."""
    with open(input_md, encoding="utf-8") as fh:
        line = next((ln for ln in fh if "Gate commands" in ln), None)
    if line is None:
        return None
    gates = []
    for g in re.findall(r"`([^`]+)`", line.split("Gate commands", 1)[1]):
        g = g.rsplit("; ", 1)[-1]
        gates.append(g[:-1] if g.endswith(")") else g)
    if not gates:
        return None
    calls: list[tuple[str, str]] = []  # (tool_use id, command), in the order the calls were made
    errors: dict[str, bool] = {}
    for o in _records(transcript):
        c = (o.get("message") or {}).get("content")
        for x in c if isinstance(c, list) else []:
            if not isinstance(x, dict):
                continue
            if x.get("type") == "tool_use" and x.get("name") == "Bash":
                calls.append((x.get("id"), str((x.get("input") or {}).get("command", ""))))
            elif x.get("type") == "tool_result":
                errors[x.get("tool_use_id")] = bool(x.get("is_error"))
    fixed = 0
    for g in gates:
        failed = False
        for uid, cmd in calls:
            if g not in cmd or uid not in errors:
                continue
            if errors[uid]:
                failed = True
            elif failed:
                fixed += 1
                break
    return fixed


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    agg = tally(argv)
    print("| role | model | agents | calls | ctx tokens | out tokens |")
    print("|---|---|---|---|---|---|")
    tc = to = 0
    for (role, model), a in sorted(agg.items()):
        tc += a["ctx"]
        to += a["out"]
        print(f"| {role} | {model} | {a['agents']} | {a['calls']} | {a['ctx']:,} | {a['out']:,} |")
    print(f"| total | | | | {tc:,} | {to:,} |")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
