"""`python -m factory.benchmark`, one arm's operator measures for the upstream benchmark (T-0060 part B).

- An operator message is a `user` record, not `isMeta` or `isSidechain`, holding no `tool_result`,
  whose `promptSource` is `typed`, `queued` or `suggestion_accepted`; with no `promptSource`, one
  whose text does not start with `<`.
- Interactions are the operator messages and the store's `approval.recorded` and `human.resolved`
  events. Interactions more than 900 s apart start a new sitting; each sitting counts its span plus
  60 s.
- Elapsed covers every timestamped session record and every store event; tokens count each message
  id once.
- No input, a session that is not a file and a store with no `log/` are refused with exit 2.

The module runs as a subprocess from the harness checkout: tests/factory is itself a package named
`factory`, so the harness package is not importable by that name here.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _jsonl(path: Path, records: list) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join((r if isinstance(r, str) else json.dumps(r)) + "\n" for r in records))
    return path


def _user(ts: str, content, **extra) -> dict:
    return {"type": "user", "timestamp": ts, **extra, "message": {"role": "user", "content": content}}


def _reply(ts: str, mid: str, ctx: int, out: int) -> dict:
    return {"type": "assistant", "timestamp": ts, "message": {"id": mid, "model": "claude-opus-5-5", "usage": {
        "input_tokens": ctx, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0, "output_tokens": out}}}


def _event(ts: str, event: str) -> dict:
    return {"ts": ts, "event": event, "ticket": "T-0001"}


def bench(*argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "factory.benchmark", *argv], capture_output=True, text=True,
                          cwd=ROOT)


def measures(cp: subprocess.CompletedProcess) -> dict[str, str]:
    assert cp.returncode == 0, cp.stderr
    lines = cp.stdout.splitlines()
    assert lines[:2] == ["| measure | value |", "|---|---|"]
    return {k: v for k, v in (ln.strip("| ").split(" | ") for ln in lines[2:])}


# --- the operator-message rule ----------------------------------------------------------------------

def test_typed_queued_accepted_text_block_and_older_prompts_count(tmp_path):
    s = _jsonl(tmp_path / "s.jsonl", [
        _user("2026-10-01T10:00:00Z", "typed", promptSource="typed"),
        _user("2026-10-01T10:01:00Z", "queued", promptSource="queued"),
        _user("2026-10-01T10:02:00Z", "accepted", promptSource="suggestion_accepted"),
        _user("2026-10-01T10:03:00Z", [{"type": "text", "text": "a text block"}], promptSource="typed"),
        _user("2026-10-01T10:04:00Z", "an older prompt with no promptSource"),
    ])
    assert measures(bench(str(s)))["operator messages"] == "5"


def test_tool_results_meta_sidechain_system_sdk_and_bracketed_records_do_not_count(tmp_path):
    s = _jsonl(tmp_path / "s.jsonl", [
        _user("2026-10-01T10:00:00Z", "the one prompt", promptSource="typed"),
        _user("2026-10-01T10:01:00Z", [{"type": "tool_result", "tool_use_id": "t1", "content": "ok"}]),
        _user("2026-10-01T10:02:00Z", [{"type": "tool_result", "tool_use_id": "t2", "content": "ok"}],
              promptSource="typed"),
        _user("2026-10-01T10:03:00Z", "caveat", isMeta=True, promptSource="typed"),
        _user("2026-10-01T10:04:00Z", "a subagent prompt", isSidechain=True, promptSource="typed"),
        _user("2026-10-01T10:05:00Z", "<task-notification>done</task-notification>", promptSource="system"),
        _user("2026-10-01T10:06:00Z", "a headless prompt", promptSource="sdk"),
        _user("2026-10-01T10:07:00Z", "<command-name>/exit</command-name>"),
        "not json",
    ])
    m = measures(bench(str(s)))
    assert m["operator messages"] == "1"
    assert m["operator time, minutes"] == "1.0 (1 sittings)"


# --- sittings -----------------------------------------------------------------------------------------

def test_exactly_900_seconds_stays_in_the_sitting_and_each_sitting_adds_one_minute(tmp_path):
    s = _jsonl(tmp_path / "s.jsonl", [
        _user("2026-10-01T10:00:00Z", "one", promptSource="typed"),
        _user("2026-10-01T10:15:00Z", "900 s later", promptSource="typed"),
    ])
    assert measures(bench(str(s)))["operator time, minutes"] == "16.0 (1 sittings)"


def test_901_seconds_starts_a_new_sitting(tmp_path):
    s = _jsonl(tmp_path / "s.jsonl", [
        _user("2026-10-01T10:00:00Z", "one", promptSource="typed"),
        _user("2026-10-01T10:15:01Z", "901 s later", promptSource="typed"),
    ])
    assert measures(bench(str(s)))["operator time, minutes"] == "2.0 (2 sittings)"


def test_store_decisions_are_interactions_and_other_events_count_only_for_elapsed(tmp_path):
    store = tmp_path / "store"
    _jsonl(store / "log" / "2026-10.jsonl", [
        _event("2026-10-02T08:00:00+00:00", "ticket.created"),
        _event("2026-10-02T09:00:00+00:00", "approval.recorded"),
        _event("2026-10-02T09:10:00+00:00", "human.resolved"),
        _event("2026-10-02T10:00:00+00:00", "merge.done"),
    ])
    m = measures(bench("--store", str(store)))
    assert m["operator messages"] == "0"
    assert m["gate and ruling events"] == "2"
    assert m["operator time, minutes"] == "11.0 (1 sittings)"
    assert m["elapsed, hours"] == "2.00"
    assert m["session tokens"] == "0 context, 0 output"


def test_session_messages_and_store_decisions_share_sittings(tmp_path):
    store = tmp_path / "store"
    _jsonl(store / "log" / "2026-10.jsonl", [_event("2026-10-02T09:05:00+00:00", "approval.recorded")])
    s = _jsonl(tmp_path / "runner.jsonl", [_user("2026-10-02T09:00:00Z", "approve it", promptSource="typed")])
    m = measures(bench("--store", str(store), str(s)))
    assert m["operator time, minutes"] == "6.0 (1 sittings)"


# --- elapsed and tokens -------------------------------------------------------------------------------

def test_tokens_count_a_repeated_message_id_once_and_elapsed_spans_every_record(tmp_path):
    a = _jsonl(tmp_path / "a.jsonl", [
        _user("2026-10-01T10:00:00Z", "go", promptSource="typed"),
        _reply("2026-10-01T10:00:30Z", "m1", 100, 10),
        _reply("2026-10-01T10:00:31Z", "m1", 100, 20),
    ])
    b = _jsonl(tmp_path / "b.jsonl", [_reply("2026-10-01T13:00:00Z", "m2", 50, 5)])
    m = measures(bench(str(a), str(b)))
    assert m["session tokens"] == "150 context, 25 output"
    assert m["elapsed, hours"] == "3.00"


def test_elapsed_is_a_dash_when_nothing_has_a_timestamp(tmp_path):
    s = _jsonl(tmp_path / "s.jsonl", ["not json"])
    m = measures(bench(str(s)))
    assert m["elapsed, hours"] == "-"
    assert m["operator time, minutes"] == "0.0 (0 sittings)"


# --- refusals -----------------------------------------------------------------------------------------

def _refused(cp: subprocess.CompletedProcess, *named: str) -> None:
    assert cp.returncode == 2
    assert cp.stdout == ""
    assert cp.stderr.startswith("factory.benchmark: ")
    assert cp.stderr.count("\n") == 1
    for n in named:
        assert n in cp.stderr


def test_no_store_and_no_session_is_refused():
    _refused(bench())


def test_a_session_that_is_not_a_file_is_refused_by_name(tmp_path):
    good = _jsonl(tmp_path / "good.jsonl", [_user("2026-10-01T10:00:00Z", "go", promptSource="typed")])
    _refused(bench(str(good), str(tmp_path / "missing.jsonl")), str(tmp_path / "missing.jsonl"))
    _refused(bench(str(tmp_path)), str(tmp_path))


def test_a_store_with_no_log_directory_is_refused_by_name(tmp_path):
    (tmp_path / "nolog").mkdir()
    _refused(bench("--store", str(tmp_path / "nolog")), str(tmp_path / "nolog"))
