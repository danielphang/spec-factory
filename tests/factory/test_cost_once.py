"""Transcript reading in `factory/cost.py` (T-0043 part A).

- `tally()` and `transcript_usage()` count each message id once, from its last record: Claude Code
  writes one record per streamed block of a reply, each carrying the whole call's usage.
- `match_transcripts()` places a transcript on the run its first non-relay user message names,
  preferring the store's own path (or its path before a `store.migrated`), ruling out another given
  store's path, inside the run's started/finished window, else taking a single remaining candidate.
- `gate_failures()` counts the gate commands of a run's input that a Bash call failed and a later
  call passed, and returns None for an input with no "Gate commands" line.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

# tests/factory is itself a package named `factory`, so the harness module is loaded from its file,
# as test_subtickets.py loads factory/subtickets.py.
_spec = importlib.util.spec_from_file_location("factory_cost", Path(__file__).resolve().parents[2] / "factory" / "cost.py")
cost = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cost)

TASK = "[Workflow harness — computed task]"
RELAY = "[Workflow harness — user request]"


def _jsonl(path: Path, records: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")
    return path


def _msg(ts: str, text: str) -> dict:
    return {"type": "user", "timestamp": ts, "message": {"role": "user", "content": text}}


def _use(ts: str, mid: str | None, inp: int, read: int, create: int, out: int) -> dict:
    m = {"model": "claude-fable-5", "usage": {"input_tokens": inp, "cache_read_input_tokens": read,
                                              "cache_creation_input_tokens": create, "output_tokens": out}}
    if mid is not None:
        m["id"] = mid
    return {"type": "assistant", "timestamp": ts, "message": m}


def _run(store: Path, run_id: str, started: str, finished: str | None) -> None:
    d = store / "runs" / run_id
    d.mkdir(parents=True, exist_ok=True)
    fin = "null" if finished is None else f"'{finished}'"
    (d / "meta.yaml").write_text(f"run_id: {run_id}\nstarted: '{started}'\nfinished: {fin}\nstatus: APPROVE\n")
    (store / "log").mkdir(exist_ok=True)


# --- counting usage once per message id -------------------------------------------------------------

def test_tally_counts_each_message_id_once_from_its_last_record(tmp_path):
    d = tmp_path / "wf"
    (d).mkdir()
    (d / "agent-a1.meta.json").write_text("{}")
    _jsonl(d / "agent-a1.jsonl", [
        _msg("2026-10-01T13:00:06Z", f"{TASK} First read /s/runs/run-0004-critic/system-prompt.txt"),
        _use("2026-10-01T13:01:00Z", "m1", 5, 100, 0, 3),
        _use("2026-10-01T13:01:00Z", "m1", 5, 100, 0, 3),
        _use("2026-10-01T13:01:01Z", "m1", 5, 100, 0, 7),   # the last record of m1 is the one kept
        _use("2026-10-01T13:02:00Z", "m2", 1, 200, 4, 10),
        _use("2026-10-01T13:02:01Z", "m2", 1, 200, 4, 10),
        _use("2026-10-01T13:03:00Z", None, 1, 1, 1, 1),     # no id: counts on its own
        _use("2026-10-01T13:03:01Z", None, 1, 1, 1, 1),
    ])
    assert cost.transcript_usage(str(d / "agent-a1.jsonl")) == (4, 105 + 205 + 3 + 3, 7 + 10 + 1 + 1)
    agg = cost.tally([str(d)])
    assert dict(agg) == {("critic", "fable-5"): {"agents": 1, "calls": 4, "ctx": 316, "out": 19}}


def test_cost_table_prints_one_call_per_message_id(tmp_path, capsys):
    d = tmp_path / "wf"
    d.mkdir()
    (d / "agent-a1.meta.json").write_text("{}")
    _jsonl(d / "agent-a1.jsonl", [
        _msg("2026-10-01T13:00:06Z", f"{TASK} First read /s/runs/run-0004-critic/system-prompt.txt"),
        _use("2026-10-01T13:01:00Z", "m1", 5, 100, 0, 3),
        _use("2026-10-01T13:01:01Z", "m1", 5, 100, 0, 7),
    ])
    assert cost.main([str(d)]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == "| role | model | agents | calls | ctx tokens | out tokens |"
    assert "| critic | fable-5 | 1 | 1 | 105 | 7 |" in lines


# --- matching a transcript to a run -------------------------------------------------------------------

def _stores(tmp_path: Path) -> tuple[Path, Path]:
    s1, s2 = tmp_path / "s1", tmp_path / "s2"
    for s in (s1, s2):
        _run(s, "run-0001-triage", "2026-10-01T10:00:00+00:00", "2026-10-01T10:05:00+00:00")
    _run(s1, "run-0002-critic", "2026-10-01T11:00:00+00:00", "2026-10-01T11:10:00+00:00")
    return s1, s2


def test_own_store_path_wins_over_another_candidate(tmp_path):
    s1, s2 = _stores(tmp_path)
    tx = tmp_path / "tx"
    own = _jsonl(tx / "x" / "own.jsonl", [_msg("2026-10-01T10:00:05Z", f"{TASK} read {s1}/runs/run-0001-triage/input.md")])
    _jsonl(tx / "y" / "elsewhere.jsonl", [_msg("2026-10-01T10:00:04Z", f"{TASK} read /moved/away/runs/run-0001-triage/input.md")])
    got = cost.match_transcripts([str(tx)], [str(s1)])
    assert got == {(str(s1), "run-0001-triage"): str(own)}


def test_path_before_store_migrated_counts_as_the_stores_own(tmp_path):
    repo = tmp_path / "repo"
    s = repo / ".factory" / "store"
    _run(s, "run-0001-triage", "2026-10-01T10:00:00+00:00", "2026-10-01T10:05:00+00:00")
    (s / "log" / "2026-10.jsonl").write_text(json.dumps(
        {"ts": "2026-10-04T23:37:20+00:00", "event": "store.migrated", "from": ".factory/state", "to": ".factory/store"}) + "\n")
    tx = tmp_path / "tx"
    old = _jsonl(tx / "old.jsonl", [_msg("2026-10-01T10:00:05Z", f"{TASK} read {repo}/.factory/state/runs/run-0001-triage/input.md")])
    _jsonl(tx / "other.jsonl", [_msg("2026-10-01T10:00:04Z", f"{TASK} read /moved/away/runs/run-0001-triage/input.md")])
    assert cost.match_transcripts([str(tx)], [str(s)]) == {(str(s), "run-0001-triage"): str(old)}


def test_relay_message_is_skipped(tmp_path):
    s1, _ = _stores(tmp_path)
    tx = tmp_path / "tx"
    t = _jsonl(tx / "a.jsonl", [
        _msg("2026-10-01T11:00:05Z", f"{RELAY} see {s1}/runs/run-0001-triage/output.md"),
        _msg("2026-10-01T11:00:06Z", f"{TASK} First read {s1}/runs/run-0002-critic/system-prompt.txt"),
    ])
    assert cost.match_transcripts([str(tx)], [str(s1)]) == {(str(s1), "run-0002-critic"): str(t)}


def test_another_given_stores_path_rules_the_transcript_out(tmp_path):
    s1, s2 = _stores(tmp_path)
    tx = tmp_path / "tx"
    t = _jsonl(tx / "c.jsonl", [_msg("2026-10-01T10:00:05Z", f"{TASK} First read {s2}/runs/run-0001-triage/system-prompt.txt")])
    # Given s1 and s2, the transcript belongs to s2's run of that id, not to s1's overlapping one.
    assert cost.match_transcripts([str(tx)], [str(s1), str(s2)]) == {(str(s2), "run-0001-triage"): str(t)}
    # Given s1 alone, it is the single remaining candidate for s1's run.
    assert cost.match_transcripts([str(tx)], [str(s1)]) == {(str(s1), "run-0001-triage"): str(t)}


def test_first_timestamp_must_lie_between_started_and_finished(tmp_path):
    s1, _ = _stores(tmp_path)
    tx = tmp_path / "tx"
    _jsonl(tx / "early.jsonl", [_msg("2026-10-01T09:59:59Z", f"{TASK} read {s1}/runs/run-0001-triage/input.md")])
    _jsonl(tx / "late.jsonl", [_msg("2026-10-01T10:05:01Z", f"{TASK} read {s1}/runs/run-0001-triage/input.md")])
    assert cost.match_transcripts([str(tx)], [str(s1)]) == {}


def test_a_single_remaining_candidate_is_taken_and_two_are_not(tmp_path):
    s1, _ = _stores(tmp_path)
    tx = tmp_path / "tx"
    one = _jsonl(tx / "deep" / "er" / "one.jsonl",
                 [_msg("2026-10-01T10:00:05Z", f"{TASK} read /moved/away/runs/run-0001-triage/input.md")])
    assert cost.match_transcripts([str(tx)], [str(s1)]) == {(str(s1), "run-0001-triage"): str(one)}
    _jsonl(tx / "two.jsonl", [_msg("2026-10-01T10:00:06Z", f"{TASK} read /gone/too/runs/run-0001-triage/input.md")])
    assert cost.match_transcripts([str(tx)], [str(s1)]) == {}


# --- gate commands failed and then fixed --------------------------------------------------------------

WRAP = ('([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : \'\\n\' | paste -sd: -); '
        'unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; ')


def _input(tmp_path: Path, gate_line: bool = True) -> Path:
    p = tmp_path / "input.md"
    gates = (f"Gate commands (run each from your worktree, exactly as written; each is already wrapped): "
             f"`{WRAP}git diff --check main...HEAD)`; `{WRAP}uv run pytest -q tests)`\n") if gate_line else "\n"
    p.write_text("## Where you work\nWorktree: `/w` (branch `b`). There is no remote. " + gates)
    return p


def _bash(tx: Path, n: int, command: str, is_error: bool) -> None:
    _jsonl(tx, [
        {"type": "assistant", "timestamp": f"2026-10-03T10:0{n}:00Z", "message": {"id": f"t{n}", "content": [
            {"type": "tool_use", "id": f"u{n}", "name": "Bash", "input": {"command": command}}]}},
        {"type": "user", "timestamp": f"2026-10-03T10:0{n}:30Z", "message": {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": f"u{n}", "is_error": is_error, "content": "x"}]}},
    ])


def test_gate_failure_fixed_later_counts_once(tmp_path):
    tx = tmp_path / "t.jsonl"
    _bash(tx, 1, f"{WRAP}uv run pytest -q tests) 2>&1 | tail -3", True)
    _bash(tx, 2, "uv run pytest -q tests -x", True)
    _bash(tx, 3, f"{WRAP}uv run pytest -q tests) 2>&1 | tail -3", False)
    _bash(tx, 4, "uv run pytest -q tests", False)
    _bash(tx, 5, "git diff --check main...HEAD", False)
    assert cost.gate_failures(str(tx), str(_input(tmp_path))) == 1


def test_gate_failure_never_fixed_counts_zero(tmp_path):
    tx = tmp_path / "t.jsonl"
    _bash(tx, 1, "git diff --check main...HEAD", False)
    _bash(tx, 2, "uv run pytest -q tests", False)
    _bash(tx, 3, "uv run pytest -q tests", True)        # passed, then failed: not a fix
    _bash(tx, 4, "ls /w", True)                         # the worktree path is not a gate command
    _bash(tx, 5, "ls /w", False)
    assert cost.gate_failures(str(tx), str(_input(tmp_path))) == 0


def test_input_without_a_gate_line_is_not_recorded(tmp_path):
    tx = tmp_path / "t.jsonl"
    _bash(tx, 1, "uv run pytest -q tests", True)
    _bash(tx, 2, "uv run pytest -q tests", False)
    assert cost.gate_failures(str(tx), str(_input(tmp_path, gate_line=False))) is None
