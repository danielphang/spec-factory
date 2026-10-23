"""`factory stats` (T-0043 parts B and C), black-box through `bin/factory`.

- Sections A to D on a fixture built like the acceptance fixture: two stores and a directory of
  transcripts, with run records whose timestamps YAML reads both as strings and as datetimes.
- The window: `--since` inclusive and `--until` exclusive, runs by `started`, events by `ts`.
- Park reasons: each normalisation step, and the correction rule (a matching correction, one dated
  after `--until`, one whose `previous` matches no park).
- Refusals, each exit 2: no store found, a path with neither `runs/` nor `log/`, an unparsable WHEN.
- A run on an instance's own store with a run in flight, from inside the store's `runs/`, under a
  harness lock that names another revision: exit 0 and nothing written.

`stats` runs on the real `bin/factory`: it skips the harness lock, so the uncommitted-edit stub of
`clean_harness_cli.py` is not needed, and a refusal from the lock would fail these tests.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from ._cli import BIN, STRIP, js, tree
from ._cli import cli as factory_cli
from ._fixtures import snapshot, start_triage, state, target  # noqa: F401  (target is a fixture)

# store, run id, ticket, model, spec_version, started, finished, wall_s, status
RUNS = [
    ("s1", "run-0001-triage", "T-0001", "opus", 0, "2026-10-01T10:00:00+00:00", "2026-10-01T10:05:00+00:00", 100, "NEEDS-HUMAN"),
    ("s1", "run-0002-triage", "T-0001", "opus", 0, "2026-10-01T11:00:00+00:00", "2026-10-01T11:05:00+00:00", 50, "ACCEPT"),
    ("s1", "run-0003-spec_writer", "T-0001", "opus", 0, "2026-10-01T12:00:00+00:00", "2026-10-01T12:30:00+00:00", 300, "READY-FOR-CRITIC"),
    ("s1", "run-0004-critic", "T-0001", "fable", 1, "2026-10-01T13:00:00+00:00", "2026-10-01T13:10:00+00:00", 60, "REVISE"),
    ("s1", "run-0005-spec_writer", "T-0001", "opus", 1, "2026-10-01T14:00:00+00:00", "2026-10-01T14:20:00+00:00", 200, "READY-FOR-CRITIC"),
    ("s1", "run-0006-critic", "T-0001", "fable", 2, "2026-10-01T15:00:00+00:00", "2026-10-01T15:10:00+00:00", 70, "APPROVE"),
    ("s1", "run-0007-implementer", "T-0001.1", "opus", 2, "2026-10-02T10:00:00+00:00", "2026-10-02T10:30:00+00:00", 600, "BLOCKED"),
    ("s1", "run-0008-implementer", "T-0001.1", "opus", 3, "2026-10-03T10:00:00+00:00", "2026-10-03T10:30:00+00:00", 400, "READY-FOR-REVIEW"),
    ("s1", "run-0009-reviewer", "T-0001.1", "fable", 3, "2026-10-03T11:00:00+00:00", "2026-10-03T11:05:00+00:00", 90, "REQUEST-CHANGES"),
    ("s1", "run-0010-reviewer", "T-0001.1", "fable", 3, "2026-10-03T12:00:00+00:00", "2026-10-03T12:05:00+00:00", 116, "KILLED"),
    ("s1", "run-0011-verifier", "T-0001.1", "opus", 3, "2026-10-03T11:00:00+00:00", "2026-10-03T11:10:00+00:00", 120, "SPEC-DEFECT"),
    ("s1", "run-0012-verifier", "T-0001.1", "fable", 3, "2026-10-03T13:00:00+00:00", "2026-10-03T13:10:00+00:00", 80, "VERIFIED"),
    ("s1", "run-0013-triage", "T-0002", "opus", 0, "2026-10-04T10:00:00+00:00", None, None, "running"),
    ("s1", "run-0014-reviewer", "T-0001.1", "fable", 3, "2026-10-09T10:00:00+00:00", "2026-10-09T10:05:00+00:00", 95, "APPROVE"),
    ("s2", "run-0001-triage", "T-0005", "opus", 0, "2026-10-01T10:00:00+00:00", "2026-10-01T10:05:00+00:00", 40, "ACCEPT"),
    ("s2", "run-0002-critic", "T-0005", "fable", 1, "2026-10-01T11:00:00+00:00", "2026-10-01T11:05:00+00:00", 30, "APPROVE"),
]
DRIFT = "BLOCKED from harness: spec drift: tests/test_a.py changed by 2ad4d8c52 since spec v3 was written at 37848dbb0"
# store, ts, event, ticket, extra fields
EVENTS = [
    ("s1", "2026-10-01T10:06:00+00:00", "ticket.parked", "T-0001", {"reason": "NEEDS-HUMAN from triage"}),
    ("s1", "2026-10-01T12:31:00+00:00", "spec.added", "T-0001", {"version": 1, "source": "run-0003-spec_writer"}),
    ("s1", "2026-10-01T14:21:00+00:00", "spec.added", "T-0001", {"version": 2, "source": "run-0005-spec_writer"}),
    ("s1", "2026-10-01T16:00:00+00:00", "approval.recorded", "T-0001", {"kind": "spec", "version": 2}),
    ("s1", "2026-10-02T10:31:00+00:00", "ticket.parked", "T-0001.1", {"reason": "BLOCKED from implementer"}),
    ("s1", "2026-10-02T12:00:00+00:00", "human.resolved", "T-0001.1", {"kind": "ruling"}),
    ("s1", "2026-10-02T13:00:00+00:00", "spec.added", "T-0001", {"version": 3, "source": "gate edit /x/answers/T-0001-gate-edit.md"}),
    ("s1", "2026-10-02T14:00:00+00:00", "ticket.parked", "T-0001.1", {"reason": "harness-bug: run start implementer: " + DRIFT}),
    ("s1", "2026-10-02T15:00:00+00:00", "park.corrected", "T-0001.1", {"previous": "harness-bug: run start implementer: " + DRIFT, "reason": DRIFT}),
    ("s1", "2026-10-03T11:11:00+00:00", "human.resolved", "T-0001.1", {"kind": "request-changes"}),
    ("s1", "2026-10-03T12:06:00+00:00", "ticket.parked", "T-0001.1", {"reason": "budget kill: reviewer"}),
    ("s1", "2026-10-03T14:00:00+00:00", "merge.refused", "T-0001.1", {"reason": "head does not contain main"}),
    ("s1", "2026-10-03T14:10:00+00:00", "merge.refused", "T-0001.1", {"reason": "head does not contain main"}),
    ("s1", "2026-10-03T14:20:00+00:00", "merge.refused", "T-0001.1", {"reason": "protected paths not declared"}),
    ("s1", "2026-10-03T15:00:00+00:00", "ticket.parked", "T-0001", {"reason": "archive: no spec store (factory init not run)\n{'ok': false}"}),
    ("s1", "2026-10-03T15:10:00+00:00", "ticket.parked", "T-0001", {"reason": "archive: "}),
    ("s1", "2026-10-03T15:20:00+00:00", "ticket.parked", "T-0001.1", {"reason": "sub-ticket closed by a human: T-0001.1"}),
    ("s1", "2026-10-03T15:30:00+00:00", "ticket.parked", "T-0002", {"reason": "operator hold: T-0002 waits on run-0009-reviewer"}),
    ("s1", "2026-10-03T15:40:00+00:00", "human.resolved", "T-0002", {"kind": "answer"}),
    ("s1", "2026-10-09T11:00:00+00:00", "ticket.parked", "T-0003", {"reason": "NEEDS-HUMAN from triage"}),
    ("s1", "2026-10-09T12:00:00+00:00", "park.corrected", "T-0001.1", {"previous": "budget kill: reviewer", "reason": "budget kill of reviewer after 900 s"}),
    ("s2", "2026-10-01T10:06:00+00:00", "ticket.parked", "T-0005", {"reason": "NEEDS-HUMAN from triage"}),
    ("s2", "2026-10-01T12:00:00+00:00", "approval.recorded", "T-0005", {"kind": "spec", "version": 1}),
]
RELAY = "[Workflow harness — user request]"
TASK = "[Workflow harness — computed task]"


def stats(cwd: Path, *argv: str, **extra: str) -> subprocess.CompletedProcess:
    """`bin/factory stats` from `cwd`, with no inherited instance, repo, store or marker."""
    env = {k: v for k, v in os.environ.items() if k not in STRIP}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", **extra})
    return subprocess.run([str(BIN), "stats", *argv], capture_output=True, text=True, env=env, cwd=cwd)


def section(text: str, letter: str) -> list[str]:
    """The table rows of one section, header and separator rows left out."""
    lines = text.split(f"\n## {letter}. ", 1)[1].split("\n## ", 1)[0].splitlines()[1:]
    rows = [ln for ln in lines if ln.startswith("| ")]
    return [r for r in rows if r.split(" | ")[0][2:] not in
            ("role", "park reason", "gate or merge decision", "caught by", "critic REVISE on the ticket")]


def _run(store: Path, run_id: str, ticket: str, model: str, version: int, started: str,
         finished: str | None, wall: int | None, status: str, *, quoted: bool) -> Path:
    d = store / "runs" / run_id
    d.mkdir(parents=True)
    q = (lambda v: f"'{v}'") if quoted else (lambda v: v)
    (d / "meta.yaml").write_text(
        f"run_id: {run_id}\nrole: {run_id.split('-', 2)[2]}\nticket: {ticket}\nmodel: {model}\nround: 0\n"
        f"spec_version: {version}\nstarted: {q(started)}\nfinished: {'null' if finished is None else q(finished)}\n"
        f"wall_s: {'null' if wall is None else wall}\nstatus: {status}\n")
    return d


def _event(store: Path, ts: str, event: str, ticket: str, extra: dict) -> None:
    (store / "log").mkdir(parents=True, exist_ok=True)
    with (store / "log" / "2026-10.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": ts, "event": event, "ticket": ticket, **extra}) + "\n")


def _jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")


def _msg(ts: str, text: str) -> dict:
    return {"type": "user", "timestamp": ts, "message": {"role": "user", "content": text}}


def _use(ts: str, mid: str, inp: int, read: int, create: int, out: int) -> dict:
    return {"type": "assistant", "timestamp": ts, "message": {
        "id": mid, "model": "claude-fable-5", "usage": {"input_tokens": inp, "cache_read_input_tokens": read,
                                                        "cache_creation_input_tokens": create, "output_tokens": out}}}


def _bash(n: int, command: str, error: bool) -> list[dict]:
    return [{"type": "assistant", "timestamp": f"2026-10-03T10:0{n}:00Z", "message": {"id": f"t{n}", "content": [
                {"type": "tool_use", "id": f"u{n}", "name": "Bash", "input": {"command": command}}]}},
            {"type": "user", "timestamp": f"2026-10-03T10:0{n}:30Z", "message": {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": f"u{n}", "is_error": error, "content": "x"}]}}]


def fixture(tmp_path: Path) -> Path:
    """Two stores, s1 (timestamps quoted, so YAML gives strings) and s2 (unquoted, so YAML gives
    datetimes), and transcripts under tx/."""
    f = tmp_path / "f"
    for s, *rest in RUNS:
        _run(f / s, *rest, quoted=s == "s1")
    for s, *rest in EVENTS:
        _event(f / s, *rest)
    s1 = f / "s1" / "runs"
    with (s1 / "run-0003-spec_writer" / "meta.yaml").open("a") as fh:
        fh.write("claude:\n  session_id: s-0003\n  total_cost_usd: 1.5\n  num_turns: 10\n  usage: {input_tokens: 10, "
                 "cache_read_input_tokens: 1000, cache_creation_input_tokens: 90, output_tokens: 50}\n")
    (s1 / "run-0004-critic" / "output.md").write_text(
        "[BLOCKING] 6 proposal.md, Problem\n- [SHOULD-FIX] 1 design.md\n* [BLOCKING] 2 design.md\nSTATUS: REVISE\n")
    (s1 / "run-0006-critic" / "output.md").write_text(
        "- [BLOCKING] 6 proposal.md, Problem: RESOLVED.\nSTATUS: APPROVE\n")
    (s1 / "run-0009-reviewer" / "output.md").write_text(
        "  1. [BLOCKING] reuse: a.py:1: copies b.py:2\nNo BLOCKING or SHOULD-FIX findings beyond that one.\n"
        "STATUS: REQUEST-CHANGES\n")
    (s1 / "run-0008-implementer" / "input.md").write_text(
        "## Where you work\nWorktree: `/w`. Gate commands (run each from your worktree, exactly as written; each "
        "is already wrapped): `(export HOME=/tmp/h; git diff --check main...HEAD)`, `(export HOME=/tmp/h; pytest -q tests)`\n")
    tx = f / "tx"
    (tx / "a").mkdir(parents=True)
    (tx / "a" / "agent-a1.meta.json").write_text("{}")
    _jsonl(tx / "a" / "agent-a1.jsonl", [
        _msg("2026-10-01T13:00:05Z", f"{RELAY} see {f}/s1/runs/run-0001-triage/output.md"),
        _msg("2026-10-01T13:00:06Z", f"{TASK} First read {f}/s1/runs/run-0004-critic/system-prompt.txt"),
        _use("2026-10-01T13:01:00Z", "m1", 5, 100, 0, 3), _use("2026-10-01T13:01:00Z", "m1", 5, 100, 0, 3),
        _use("2026-10-01T13:01:01Z", "m1", 5, 100, 0, 7),
        _use("2026-10-01T13:02:00Z", "m2", 1, 200, 4, 10), _use("2026-10-01T13:02:01Z", "m2", 1, 200, 4, 10)])
    _jsonl(tx / "b" / "agent-b1.jsonl", [
        _msg("2026-10-03T10:00:05Z", f"{TASK} Your input is {f}/s1/runs/run-0008-implementer/input.md"),
        *_bash(1, "(export HOME=/tmp/h; pytest -q tests) 2>&1 | tail -3", True),
        *_bash(2, "(export HOME=/tmp/h; pytest -q tests) 2>&1 | tail -3", False),
        *_bash(3, "git diff --check main...HEAD", False),
        _use("2026-10-03T10:09:00Z", "m9", 2, 50, 8, 4)])
    _jsonl(tx / "c" / "agent-c1.jsonl", [
        _msg("2026-10-01T10:00:05Z", f"{TASK} First read {f}/s2/runs/run-0001-triage/system-prompt.txt"),
        _use("2026-10-01T10:01:00Z", "m5", 1, 9, 0, 2)])
    _jsonl(tx / "d" / "s-0003.jsonl", [
        _msg("2026-10-01T12:00:05Z", f"Read {f}/s1/runs/run-0003-spec_writer/input.md"),
        _use("2026-10-01T12:01:00Z", "m7", 100, 100000, 0, 500)])
    return f


def run_all(tmp_path: Path, *argv: str) -> str:
    f = fixture(tmp_path)
    cp = stats(tmp_path, "--store", str(f / "s1"), "--store", str(f / "s2"), *argv)
    assert cp.returncode == 0, cp.stderr
    assert cp.stderr == ""
    return cp.stdout


# ----- the four sections ----------------------------------------------------------------------

def test_header_names_the_stores_the_window_and_the_runs_left_in_flight(tmp_path):
    text = run_all(tmp_path, "--until", "2026-10-08")
    f = (tmp_path / "f").resolve()
    lines = text.splitlines()
    assert lines[0] == "# factory stats"
    assert f"Stores: {f / 's1'}, {f / 's2'}" in lines
    window = next(ln for ln in lines if ln.startswith("Window: "))
    assert "2026-10-08T00:00:00+00:00" in window and "1 runs in flight left out" in window


def test_section_a_counts_runs_kills_changed_outcomes_blocking_findings_and_fixed_gates(tmp_path):
    text = run_all(tmp_path, "--transcripts", str(tmp_path / "f" / "tx"), "--until", "2026-10-08")
    assert section(text, "A") == [
        "| triage | opus | 3 | 0 | 0 | ACCEPT 2, NEEDS-HUMAN 1 | - | - |",
        "| spec_writer | opus | 2 | 0 | 0 | READY-FOR-CRITIC 2 | - | - |",
        # run-0004's `[BLOCKING]` and `* [BLOCKING]` count; run-0006's RESOLVED line does not
        "| critic | fable | 3 | 0 | 1 | APPROVE 2, REVISE 1 | 2 | - |",
        "| implementer | opus | 2 | 0 | 1 | BLOCKED 1, READY-FOR-REVIEW 1 | - | 1 in 1 read, 1 not recorded |",
        # `  1. [BLOCKING]` counts; "No BLOCKING or SHOULD-FIX findings" does not
        "| reviewer | fable | 1 | 1 | 1 | REQUEST-CHANGES 1 | 1 | - |",
        "| verifier | fable | 1 | 0 | 0 | VERIFIED 1 | - | - |",
        "| verifier | opus | 1 | 0 | 1 | SPEC-DEFECT 1 | - | - |",
    ]


def test_section_a_without_transcripts_records_no_gate_failures(tmp_path):
    text = run_all(tmp_path, "--until", "2026-10-08")
    row = next(r for r in section(text, "A") if r.startswith("| implementer |"))
    assert row.endswith("| - | 0 in 0 read, 2 not recorded |")


def test_section_b_groups_parks_and_counts_gate_and_merge_decisions(tmp_path):
    text = run_all(tmp_path, "--until", "2026-10-08")
    assert section(text, "B") == [
        "| NEEDS-HUMAN from triage | 2 |",
        "| BLOCKED from harness: spec drift | 1 |",
        "| BLOCKED from implementer | 1 |",
        "| archive | 1 |",
        "| archive: no spec store (factory init not run) | 1 |",
        "| budget kill: reviewer | 1 |",
        "| operator hold: <ticket> waits on <run> | 1 |",
        "| sub-ticket closed by a human: <ticket> | 1 |",
        "| all parks | 9 |",
        "| spec approved | 2 |",
        "| spec changes requested | 1 |",
        "| resolved: answer | 1 |",
        "| resolved: ruling | 1 |",
        "| merge refused: head does not contain main | 2 |",
        "| merge refused: protected paths not declared | 1 |",
        "| archive refused | 2 |",
    ]


def test_section_c_ties_each_catch_to_the_runs_that_wrote_and_critiqued_its_spec(tmp_path):
    text = run_all(tmp_path, "--until", "2026-10-08")
    assert section(text, "C") == [
        "| run-0007-implementer | BLOCKED | T-0001.1 | 2 | run-0005-spec_writer | run-0006-critic | 1 |",
        "| run-0011-verifier | SPEC-DEFECT | T-0001.1 | 3 | human | none | 1 |",
        "| yes | 1 | 1 |",
        "| no | 1 | 0 |",
    ]


def test_section_c_names_unknown_for_a_version_with_no_spec_added_event(tmp_path):
    f = fixture(tmp_path)
    _run(f / "s1", "run-0015-verifier", "T-0001.2", "opus", 7, "2026-10-04T10:00:00+00:00",
         "2026-10-04T10:10:00+00:00", 60, "SPEC-DEFECT", quoted=True)
    cp = stats(tmp_path, "--store", str(f / "s1"), "--until", "2026-10-08")
    assert cp.returncode == 0, cp.stderr
    assert "| run-0015-verifier | SPEC-DEFECT | T-0001.2 | 7 | unknown | none | 1 |" in section(cp.stdout, "C")


def test_section_d_takes_cost_from_the_record_else_the_store_runs_own_transcript(tmp_path):
    text = run_all(tmp_path, "--transcripts", str(tmp_path / "f" / "tx"), "--until", "2026-10-08")
    assert section(text, "D") == [
        "| triage | opus | 3 | 190 | 10 | 2 | 0.00 | record 0, transcript 1, none 2 |",
        "| spec_writer | opus | 2 | 500 | 1100 | 50 | 1.50 | record 1, transcript 0, none 1 |",
        "| critic | fable | 3 | 160 | 310 | 17 | 0.00 | record 0, transcript 1, none 2 |",
        "| implementer | opus | 2 | 1000 | 60 | 4 | 0.00 | record 0, transcript 1, none 1 |",
        "| reviewer | fable | 2 | 206 | 0 | 0 | 0.00 | record 0, transcript 0, none 2 |",
        "| verifier | fable | 1 | 80 | 0 | 0 | 0.00 | record 0, transcript 0, none 1 |",
        "| verifier | opus | 1 | 120 | 0 | 0 | 0.00 | record 0, transcript 0, none 1 |",
    ]


def test_rows_order_known_roles_first_then_other_roles_by_name(tmp_path):
    f = fixture(tmp_path)
    for rid in ("run-0020-zeta", "run-0021-alpha"):
        _run(f / "s2", rid, "T-0005", "opus", 0, "2026-10-02T10:00:00+00:00", "2026-10-02T10:01:00+00:00", 1,
             "DONE", quoted=False)
    cp = stats(tmp_path, "--store", str(f / "s2"))
    assert cp.returncode == 0, cp.stderr
    assert [r.split(" | ")[0][2:] for r in section(cp.stdout, "A")] == ["triage", "critic", "alpha", "zeta"]


# ----- the window ------------------------------------------------------------------------------

def test_since_bounds_the_count_and_the_store_is_unchanged(tmp_path):
    f = fixture(tmp_path)
    before = tree(f)
    cp = stats(tmp_path, "--store", str(f / "s1"), "--since", "2026-10-03", "--transcripts", str(f / "tx"))
    assert cp.returncode == 0, cp.stderr
    assert "| reviewer | fable | 2 | 1 | 1 | APPROVE 1, REQUEST-CHANGES 1 | 1 | - |" in section(cp.stdout, "A")
    assert tree(f) == before


def test_since_is_inclusive_and_until_exclusive(tmp_path):
    f = fixture(tmp_path)
    # run-0009-reviewer and run-0011-verifier start at 2026-10-03T11:00 exactly
    cp = stats(tmp_path, "--store", str(f / "s1"), "--until", "2026-10-03T11:00")
    assert cp.returncode == 0, cp.stderr
    roles = [r.split(" | ")[0][2:] for r in section(cp.stdout, "A")]
    assert "reviewer" not in roles and "verifier" not in roles
    cp = stats(tmp_path, "--store", str(f / "s1"), "--since", "2026-10-03T11:00", "--until", "2026-10-03T11:00:01")
    assert cp.returncode == 0, cp.stderr
    assert section(cp.stdout, "A") == ["| reviewer | fable | 1 | 0 | 1 | REQUEST-CHANGES 1 | 1 | - |",
                                       "| verifier | opus | 1 | 0 | 1 | SPEC-DEFECT 1 | - | - |"]


def test_events_are_windowed_by_ts(tmp_path):
    f = fixture(tmp_path)
    cp = stats(tmp_path, "--store", str(f / "s1"), "--since", "2026-10-03T14:05", "--until", "2026-10-03T14:15")
    assert cp.returncode == 0, cp.stderr
    b = section(cp.stdout, "B")
    assert "| all parks | 0 |" in b and "| merge refused: head does not contain main | 1 |" in b
    assert "| spec approved | 0 |" in b and "| archive refused | 0 |" in b


# ----- park normalisation and corrections ------------------------------------------------------

def parks_of(tmp_path: Path, parks: list[tuple[str, str, str]], corrections=(), *argv: str) -> list[str]:
    s = tmp_path / "store"
    for ts, ticket, reason in parks:
        _event(s, ts, "ticket.parked", ticket, {"reason": reason})
    for ts, ticket, previous, reason in corrections:
        _event(s, ts, "park.corrected", ticket, {"previous": previous, "reason": reason})
    cp = stats(tmp_path, "--store", str(s), *argv)
    assert cp.returncode == 0, cp.stderr
    rows = section(cp.stdout, "B")
    return rows[:rows.index(next(r for r in rows if r.startswith("| all parks |")))]


def test_each_normalisation_step(tmp_path):
    ts = "2026-10-01T10:00:00+00:00"
    assert parks_of(tmp_path, [
        (ts, "T-0001", "first line only\nsecond line: dropped"),               # 1. first line
        (ts, "T-0001", "held for run-0012-critic"),                            # 2. run id
        (ts, "T-0001", "waits on T-0003.2"),                                   # 2. ticket id
        (ts, "T-0001", "drift at 2ad4d8c52 vs 1234567"),                       # 2. sha: hex with a letter
        (ts, "T-0001", "one: two: three: four"),                               # 3. two fields
        (ts, "T-0001", "  spaced:  "),                                         # 4. trim, trailing colon
    ]) == [
        "| drift at <sha> vs 1234567 | 1 |",
        "| first line only | 1 |",
        "| held for <run> | 1 |",
        "| one: two | 1 |",
        "| spaced | 1 |",
        "| waits on <ticket> | 1 |",
    ]


def test_corrections_apply_to_the_latest_earlier_matching_park_before_until(tmp_path):
    parks = [("2026-10-01T10:00:00+00:00", "T-0001", "old: reason"),
             ("2026-10-02T10:00:00+00:00", "T-0001", "old: reason"),
             ("2026-10-02T10:00:00+00:00", "T-0002", "late: one"),
             ("2026-10-02T10:00:00+00:00", "T-0003", "kept: as is")]
    corrections = [("2026-10-03T10:00:00+00:00", "T-0001", "old: reason", "new: reason"),     # matches
                   ("2026-10-09T10:00:00+00:00", "T-0002", "late: one", "after: until"),      # after --until
                   ("2026-10-03T10:00:00+00:00", "T-0003", "no such park", "never: used"),    # matches no park
                   ("2026-10-01T09:00:00+00:00", "T-0001", "old: reason", "before: park")]    # no earlier park
    assert parks_of(tmp_path, parks, corrections, "--until", "2026-10-08") == [
        "| kept: as is | 1 |", "| late: one | 1 |", "| new: reason | 1 |", "| old: reason | 1 |"]


def test_a_correction_dated_after_until_applies_when_until_is_later(tmp_path):
    parks = [("2026-10-02T10:00:00+00:00", "T-0002", "late: one")]
    corrections = [("2026-10-09T10:00:00+00:00", "T-0002", "late: one", "after: until")]
    assert parks_of(tmp_path, parks, corrections) == ["| after: until | 1 |"]


# ----- refusals --------------------------------------------------------------------------------

def assert_refused(cp, detail: str) -> None:
    assert cp.returncode == 2, (cp.returncode, cp.stdout, cp.stderr)
    assert detail in cp.stderr
    assert js(cp) == {"ok": False, "error": cp.stderr.strip()}


def test_refused_when_no_store_is_found(tmp_path):
    assert_refused(stats(tmp_path), "factory stats: no store found")


def test_refused_for_a_path_that_is_not_a_store(tmp_path):
    (tmp_path / "empty").mkdir()
    assert_refused(stats(tmp_path, "--store", str(tmp_path / "empty")), "has neither runs/ nor log/")


def test_refused_for_an_unparsable_when(tmp_path):
    f = fixture(tmp_path)
    for flag in ("--since", "--until"):
        assert_refused(stats(tmp_path, "--store", str(f / "s1"), flag, "last tuesday"),
                       f"{flag} 'last tuesday' is not an ISO date or date-time")


def test_relative_paths_are_taken_from_the_callers_directory(tmp_path):
    fixture(tmp_path)
    cp = stats(tmp_path / "f", "--store", "s1", "--transcripts", "tx")
    assert cp.returncode == 0, cp.stderr
    assert f"Stores: {(tmp_path / 'f' / 's1').resolve()}" in cp.stdout.splitlines()


def test_factory_state_names_the_store_when_no_store_is_given(tmp_path):
    f = fixture(tmp_path)
    cp = stats(tmp_path, FACTORY_STATE=str(f / "s2"))
    assert cp.returncode == 0, cp.stderr
    assert f"Stores: {(f / 's2').resolve()}" in cp.stdout.splitlines()


# ----- a live store: run in flight, inside runs/, unaccepted harness -----------------------------

def test_reads_an_own_store_with_a_run_in_flight_from_its_runs_under_another_lock(target):  # noqa: F811
    rid = start_triage(target)
    (target / ".factory" / "harness.lock").write_text("0" * 40 + "\n")
    own = state(target).resolve()
    before = snapshot(target)
    for cwd in (target, own / "runs" / rid):
        cp = stats(cwd)
        assert cp.returncode == 0, cp.stderr
        assert f"Stores: {own}" in cp.stdout.splitlines()
        assert "1 runs in flight left out" in cp.stdout
        # --accept-harness is refused, as for `init` and `paths` (T-0058): stats never checks the lock,
        # so the refusal names `config` as the command that accepts a revision, and rewrites nothing
        env = {k: v for k, v in os.environ.items() if k not in STRIP}
        cp = subprocess.run([str(BIN), "--accept-harness", "0" * 40, "stats"], capture_output=True, text=True,
                            cwd=cwd, env={**env, "PYTHONDONTWRITEBYTECODE": "1"})
        assert cp.returncode == 2, cp.stderr
        assert f"factory --accept-harness {'0' * 40} config" in cp.stderr
    assert snapshot(target) == before
    # the lock is in force: an ordinary read is refused
    assert factory_cli(target, "ticket", "show", "T-0001").returncode == 2
