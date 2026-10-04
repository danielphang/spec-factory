"""`resolve --redispatch` keeps the result rows that passed (spec-factory T-0023, part D, item H4).

A redispatch re-runs a sub-ticket's checks on the same commit after the cause of its park was fixed
outside the ticket. It sets aside, under `results/<head>/superseded-<n>/`, only the rows that did not
pass: the reviewer's row unless it is APPROVE, and the verifier's and gate (`ci`) rows together
unless they are VERIFIED and PASS, because one verifier run writes both. `results show` then names
the checkers the build still has to run.

Black-box through `bin/factory` on a throwaway store (FACTORY_STATE), as test_resolve_rulings.py does.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
BIN = REPO / "bin" / "factory"
HEAD = "ab" * 20
ST = "T-0001.1"


def run(env: dict, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([str(BIN), *argv], capture_output=True, text=True,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **env}, cwd=REPO)


def js(cp: subprocess.CompletedProcess) -> dict:
    assert cp.returncode == 0, cp.stderr
    return json.loads(cp.stdout.strip().splitlines()[-1])


@pytest.fixture
def env(tmp_path: Path) -> dict:
    """A scratch store: T-0001 approved and split into T-0001.1, which is in its checks on HEAD."""
    e = {"FACTORY_STATE": str(tmp_path / "store")}
    (tmp_path / "req.md").write_text("# Fixture\n\nThe bot should do the thing.\n")
    (tmp_path / "spec.md").write_text("## Problem\nx\n")
    (tmp_path / "plan.md").write_text("ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n")
    js(run(e, "ticket", "new", "--file", str(tmp_path / "req.md")))
    js(run(e, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t"))
    js(run(e, "spec", "add", "T-0001", "--file", str(tmp_path / "spec.md")))
    js(run(e, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init"))
    js(run(e, "ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t"))
    js(run(e, "approve-spec", "T-0001"))
    js(run(e, "subticket", "add", "T-0001", "--file", str(tmp_path / "plan.md")))
    js(run(e, "ticket", "set", ST, "status=checks-in-flight", f"head={HEAD}"))
    return e


def record(env: dict, tmp_path: Path, role: str, body: str | None, run_id: str) -> None:
    """One checker's result on HEAD; body None records a killed run."""
    if body is None:
        js(run(env, "results", "record", ST, "--head", HEAD, "--role", role, "--killed", "--run", run_id))
        return
    out = tmp_path / f"{role}.md"
    out.write_text(f"Commit: {HEAD}\n{body}CONFIDENCE: high, fixture\nESCALATIONS: none\n")
    js(run(env, "results", "record", ST, "--head", HEAD, "--role", role, "--output", str(out), "--run", run_id))


def redispatch(env: dict, reason: str) -> dict:
    js(run(env, "ticket", "park", ST, "--reason", reason))
    return js(run(env, "resolve", ST, "--redispatch"))


def rows(env: dict) -> tuple[dict, list[str]]:
    shown = js(run(env, "results", "show", ST))
    return shown["rows"], shown["missing"]


def results_dir(env: dict) -> Path:
    return Path(env["FACTORY_STATE"]) / "results" / HEAD


def superseded_events(env: dict) -> list[dict]:
    log = Path(env["FACTORY_STATE"]) / "log"
    events = [json.loads(ln) for p in sorted(log.glob("*.jsonl")) for ln in p.read_text().splitlines()]
    return [e for e in events if e.get("event") == "results.superseded"]


def test_a_killed_reviewer_is_set_aside_and_the_passing_verifier_rows_are_kept(env, tmp_path):
    record(env, tmp_path, "verifier", "Gate suite: PASS\nSTATUS: VERIFIED\n", "run-0002-verifier")
    record(env, tmp_path, "reviewer", None, "run-0003-reviewer")
    res = redispatch(env, "budget kill: reviewer")
    assert res["state"] == "checks-in-flight" and res["superseded"] == ["reviewer"]
    assert rows(env) == ({"verifier": "VERIFIED", "ci": "PASS"}, ["reviewer"])
    assert sorted(p.name for p in (results_dir(env) / "superseded-1").iterdir()) == ["reviewer.yaml"]
    assert superseded_events(env)[-1]["roles"] == ["reviewer"]


def test_a_spec_defect_verifier_is_set_aside_with_its_gate_row_and_the_approval_is_kept(env, tmp_path):
    record(env, tmp_path, "verifier", "Gate suite: FAIL\nSTATUS: SPEC-DEFECT\n", "run-0002-verifier")
    record(env, tmp_path, "reviewer", "STATUS: APPROVE\n", "run-0003-reviewer")
    res = redispatch(env, "SPEC-DEFECT from verifier")
    assert sorted(res["superseded"]) == ["ci", "verifier"]
    assert rows(env) == ({"reviewer": "APPROVE"}, ["verifier", "ci"])
    assert sorted(p.name for p in (results_dir(env) / "superseded-1").iterdir()) == ["ci.yaml", "verifier.yaml"]


def test_a_verified_run_with_a_failed_gate_row_is_set_aside_whole(env, tmp_path):
    """One verifier run writes both rows, so a wrong gate row re-runs the verifier."""
    record(env, tmp_path, "verifier", "Gate suite: FAIL\nSTATUS: VERIFIED\n", "run-0002-verifier")
    record(env, tmp_path, "reviewer", "STATUS: APPROVE\n", "run-0003-reviewer")
    res = redispatch(env, "harness-bug: gate parser")
    assert sorted(res["superseded"]) == ["ci", "verifier"]
    assert rows(env) == ({"reviewer": "APPROVE"}, ["verifier", "ci"])


def test_all_rows_passing_moves_nothing_and_creates_no_directory(env, tmp_path):
    record(env, tmp_path, "verifier", "Gate suite: PASS\nSTATUS: VERIFIED\n", "run-0002-verifier")
    record(env, tmp_path, "reviewer", "STATUS: APPROVE\n", "run-0003-reviewer")
    res = redispatch(env, "harness-bug: join")
    assert res["state"] == "checks-in-flight" and res["superseded"] == []
    assert rows(env) == ({"reviewer": "APPROVE", "verifier": "VERIFIED", "ci": "PASS"}, [])
    assert not list(results_dir(env).glob("superseded-*"))
    assert superseded_events(env)[-1]["roles"] == []


def test_no_rows_at_all_moves_nothing(env):
    res = redispatch(env, "budget kill: reviewer")
    assert res["state"] == "checks-in-flight" and res["superseded"] == []
    assert rows(env) == ({}, ["reviewer", "verifier", "ci"])
    assert not results_dir(env).exists()


def test_a_second_redispatch_takes_the_next_superseded_number(env, tmp_path):
    record(env, tmp_path, "verifier", "Gate suite: PASS\nSTATUS: VERIFIED\n", "run-0002-verifier")
    record(env, tmp_path, "reviewer", None, "run-0003-reviewer")
    redispatch(env, "budget kill: reviewer")
    record(env, tmp_path, "reviewer", None, "run-0004-reviewer")
    res = redispatch(env, "budget kill: reviewer")
    assert res["superseded"] == ["reviewer"]
    assert sorted(p.name for p in results_dir(env).iterdir()) == ["ci.yaml", "superseded-1", "superseded-2", "verifier.yaml"]
