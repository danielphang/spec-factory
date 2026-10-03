"""Per-(role, model) token cost of one or more intake workflow runs, read from their transcripts.

  uv run python -m factory.cost <workflow transcript dir>...

The dirs are the "Transcript dir" the Workflow tool prints for a run. Context tokens = input +
cache_read + cache_creation per API call; output separate. Role comes from the computed-task
prompt the dispatcher gave the agent. meta.yaml records the model; this adds the cost.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
from collections import defaultdict

TASK_PREFIX = "[Workflow harness — computed task]"


def _records(path: str):
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            try:
                yield json.loads(ln)
            except ValueError:
                continue


def _role(transcript: str) -> str:
    for o in _records(transcript):
        if o.get("type") != "user":
            continue
        c = o.get("message", {}).get("content")
        text = c if isinstance(c, str) else " ".join(x.get("text", "") for x in c if isinstance(x, dict))
        if not text.startswith(TASK_PREFIX):
            continue
        if "bin/factory" in text:
            return "clerk"
        m = re.search(r"runs/run-\d+-(\w+)/", text)
        if m:
            return m.group(1)
        return "stub" if "Stub file" in text else "?"
    return "?"


def tally(dirs: list[str]) -> dict[tuple[str, str], dict[str, int]]:
    agg: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: {"agents": 0, "calls": 0, "ctx": 0, "out": 0})
    for d in dirs:
        for mf in glob.glob(os.path.join(d, "agent-*.meta.json")):
            tf = mf.replace(".meta.json", ".jsonl")
            model = None
            calls = ctx = out = 0
            for o in _records(tf):
                m = o.get("message") or {}
                u = m.get("usage") if isinstance(m, dict) else None
                if not u:
                    continue
                calls += 1
                model = m.get("model") or model
                ctx += (u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                        + u.get("cache_creation_input_tokens", 0))
                out += u.get("output_tokens", 0)
            a = agg[(_role(tf), (model or "?").replace("claude-", ""))]
            a["agents"] += 1
            a["calls"] += calls
            a["ctx"] += ctx
            a["out"] += out
    return agg


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
