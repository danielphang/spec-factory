"""What the build needs at its start (issue #33): `subticket add` with no source takes the planner run
the parent's recorded plan names, `ready-implementers` lists every sub-ticket so the build can see a
parent with none, and the verifier's `Gate suite:` line is read under heading and emphasis marks."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from .test_subtickets import PLAN_LETTERS, js, run, ticket


def approved_parent(store: Path, tmp_path: Path) -> str:
    """A parent past the spec gate (old-format spec; no spec store), with no plan yet."""
    req = tmp_path / "r.md"
    req.write_text("# Fixture\n\nThe bot should do the thing.\n")
    tid = js(run(store, "ticket", "new", "--file", str(req)))["id"]
    spec = tmp_path / "s.md"
    spec.write_text("## Problem\nx\n")
    js(run(store, "ticket", "transition", tid, "--to", "ready-for-spec-writer", "--by", "t"))
    js(run(store, "spec", "add", tid, "--file", str(spec)))
    js(run(store, "ticket", "transition", tid, "--to", "ready-for-critic", "--by", "t", "--round", "spec:init"))
    js(run(store, "ticket", "transition", tid, "--to", "awaiting-spec-gate", "--by", "t"))
    js(run(store, "approve-spec", tid))
    return tid


def planner_run(store: Path, tid: str, plan: str) -> str:
    rid = js(run(store, "run", "start", "--role", "planner", "--ticket", tid))["run_id"]
    js(run(store, "run", "compose", rid))
    (store / "runs" / rid / "output.md").write_text(plan)
    js(run(store, "run", "finish", rid))
    return rid


def ticket_files(store: Path) -> list[str]:
    return sorted(p.name for p in (store / "tickets").iterdir())


def test_subticket_add_without_a_source_uses_the_recorded_planner_run(tmp_path):
    store = tmp_path / "state"
    tid = approved_parent(store, tmp_path)
    rid = planner_run(store, tid, PLAN_LETTERS)
    js(run(store, "plan", "add", tid, "--from-run", rid))
    out = js(run(store, "subticket", "add", tid))
    assert out["ok"] is True and [s["id"] for s in out["subtickets"]] == ["T-0001.1", "T-0001.2", "T-0001.3"]
    assert ticket(store, "T-0001.1")["source"] == f"plan:{rid}"


def test_subticket_add_without_a_source_takes_the_latest_plan(tmp_path):
    store = tmp_path / "state"
    tid = approved_parent(store, tmp_path)
    first = planner_run(store, tid, PLAN_LETTERS)
    js(run(store, "plan", "add", tid, "--from-run", first))
    second = planner_run(store, tid, PLAN_LETTERS)
    js(run(store, "plan", "add", tid, "--from-run", second))
    js(run(store, "subticket", "add", tid))
    assert ticket(store, "T-0001.1")["source"] == f"plan:{second}"


@pytest.mark.parametrize("plan_from", ["none", "file"])
def test_subticket_add_without_a_source_refuses_with_no_recorded_planner_run(tmp_path, plan_from):
    store = tmp_path / "state"
    tid = approved_parent(store, tmp_path)
    if plan_from == "file":
        plan = tmp_path / "plan.md"
        plan.write_text(PLAN_LETTERS)
        js(run(store, "plan", "add", tid, "--file", str(plan)))
    log_before = sorted((p.name, p.read_text()) for p in (store / "log").glob("*.jsonl"))
    cp = run(store, "subticket", "add", tid)
    assert cp.returncode == 2, cp.stderr
    assert "no recorded planner run found for T-0001" in cp.stderr and "TypeError" not in cp.stderr
    assert ticket_files(store) == ["T-0001.yaml"]
    assert sorted((p.name, p.read_text()) for p in (store / "log").glob("*.jsonl")) == log_before


def test_ready_implementers_lists_every_sub_ticket_in_id_order(tmp_path):
    store = tmp_path / "state"
    tid = approved_parent(store, tmp_path)
    rid = planner_run(store, tid, PLAN_LETTERS)
    js(run(store, "plan", "add", tid, "--from-run", rid))
    js(run(store, "ticket", "transition", tid, "--to", "planned", "--by", "t"))
    assert js(run(store, "ticket", "ready-implementers", tid))["subtickets"] == []
    js(run(store, "subticket", "add", tid))
    t = ticket(store, "T-0001.1")
    t["status"] = "merged"  # a finished sub-ticket is still listed
    (store / "tickets" / "T-0001.1.yaml").write_text(yaml.safe_dump(t, sort_keys=False))
    r = js(run(store, "ticket", "ready-implementers", tid))
    assert r["subtickets"] == ["T-0001.1", "T-0001.2", "T-0001.3"]
    assert r["remaining"] == ["T-0001.2", "T-0001.3"]


HEAD = "a" * 40


@pytest.mark.parametrize("line, status, detail", [
    ("## Gate suite: PASS", "PASS", None),
    ("**Gate suite:** PASS", "PASS", None),
    ("### **Gate suite: PASS**", "PASS", None),
    ("**Gate suite: FAIL** 2 failed", "FAIL", "2 failed"),
    ("  Gate suite: PASS", "PASS", None),
    ("Gate suite: PASS", "PASS", None),
    ("Gate suite: FAIL 1 failed", "FAIL", "1 failed"),
    ("The Gate suite: PASS line was missing", "FAIL", "missing Gate suite line"),
    ("- Gate suite: PASS", "FAIL", "missing Gate suite line"),
])
def test_the_gate_line_is_read_under_heading_and_emphasis_marks_only(tmp_path, line, status, detail):
    store = tmp_path / "state"
    req = tmp_path / "r.md"
    req.write_text("# Fixture\n\nThe bot should do the thing.\n")
    tid = js(run(store, "ticket", "new", "--file", str(req)))["id"]
    out = tmp_path / "v.md"
    out.write_text(f"Commit: {HEAD}\n{line}\nSTATUS: VERIFIED\nCONFIDENCE: high\nESCALATIONS: none\n")
    js(run(store, "results", "record", tid, "--head", HEAD, "--role", "verifier", "--output", str(out)))
    ci = yaml.safe_load((store / "results" / HEAD / "ci.yaml").read_text())
    assert (ci["status"], ci.get("detail")) == (status, detail)
