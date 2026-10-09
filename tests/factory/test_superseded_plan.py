"""Superseded plans (spec-factory T-0038, issue #77).

Each sub-ticket records `planned_from`, the parent's approved spec version it was planned from.
Once a parent has a sub-ticket planned from a later version, its older sub-tickets that have not
merged are superseded: kept with their ids and records, but no longer dispatched, parking the
parent or holding back its final check, close or re-plan. Merged ones stay merged and count.

Black-box through `bin/factory` on a throwaway store (FACTORY_STATE), as test_replan.py does.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
BIN = REPO / "bin" / "factory"
OLD_PLAN = ("ST-1 / Base\nDepends on: none\nParallel-safe: yes\n\nST-2 / Dropped\nDepends on: none\nParallel-safe: yes\n\n"
            "ST-3 / Unstarted\nDepends on: ST-2\nParallel-safe: yes\n")
NEW_PLAN = "ST-1 / Redo\nDepends on: T-0001.1\nParallel-safe: yes\n"
SUPERSEDES_LINE = ("Not merged and planned from an earlier approved version, so a new plan supersedes them and may "
                   "not depend on them: T-0001.2, T-0001.3")


def run(store: Path, *argv: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "FACTORY_STATE": str(store), "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)


def js(cp: subprocess.CompletedProcess) -> dict:
    assert cp.returncode == 0, cp.stderr
    return json.loads(cp.stdout.strip().splitlines()[-1])


def ticket(store: Path, tid: str) -> dict:
    return yaml.safe_load((store / "tickets" / f"{tid}.yaml").read_text())


def add_plan(store: Path, tmp_path: Path, text: str, name: str) -> subprocess.CompletedProcess:
    (tmp_path / name).write_text(text)
    return run(store, "subticket", "add", "T-0001", "--file", str(tmp_path / name))


def events(store: Path, name: str) -> list[dict]:
    lines = [json.loads(ln) for p in sorted((store / "log").glob("*.jsonl")) for ln in p.read_text().splitlines()]
    return [e for e in lines if e["event"] == name]


@pytest.fixture
def store(tmp_path: Path) -> Path:
    """T-0001 past the spec gate at approved v1 (no spec store), with no sub-tickets yet."""
    s = tmp_path / "store"
    (tmp_path / "req.md").write_text("# Fixture\n\nThe bot should do the thing.\n")
    (tmp_path / "spec.md").write_text("## Problem\nx\n")
    js(run(s, "ticket", "new", "--file", str(tmp_path / "req.md")))
    js(run(s, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t"))
    js(run(s, "spec", "add", "T-0001", "--file", str(tmp_path / "spec.md")))
    js(run(s, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init"))
    js(run(s, "ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t"))
    js(run(s, "approve-spec", "T-0001"))
    return s


@pytest.fixture
def respecced(store: Path, tmp_path: Path) -> Path:
    """Planned at v1 as T-0001.1 (merged), .2 (closed by a human) and .3 (never started), then sent
    back to the spec gate and approved again, edited, as v2: ready for its planner again."""
    js(add_plan(store, tmp_path, OLD_PLAN, "plan1.md"))
    js(run(store, "ticket", "transition", "T-0001", "--to", "planned", "--by", "t"))
    js(run(store, "ticket", "set", "T-0001.1", "status=merged"))
    js(run(store, "ticket", "transition", "T-0001.2", "--to", "closed", "--by", "t"))
    js(run(store, "ticket", "park", "T-0001", "--reason", "sub-ticket closed by a human: T-0001.2"))
    js(run(store, "resolve", "T-0001", "--to", "spec-gate"))
    (tmp_path / "spec2.md").write_text("## Problem\nx, amended\n")
    js(run(store, "approve-spec", "T-0001", "--edit", str(tmp_path / "spec2.md")))
    return store


def replan(store: Path, tmp_path: Path) -> dict:
    res = js(add_plan(store, tmp_path, NEW_PLAN, "plan2.md"))
    js(run(store, "ticket", "transition", "T-0001", "--to", "planned", "--by", "t"))
    return res


def test_each_sub_ticket_records_the_approved_version_it_was_planned_from(respecced, tmp_path):
    replan(respecced, tmp_path)
    assert [ticket(respecced, f"T-0001.{i}")["planned_from"] for i in (1, 2, 3, 4)] == [1, 1, 1, 2]


def test_a_re_plan_supersedes_the_old_unmerged_sub_tickets_and_keeps_their_records(respecced, tmp_path):
    assert replan(respecced, tmp_path)["superseded"] == ["T-0001.2", "T-0001.3"]
    r = js(run(respecced, "ticket", "ready-implementers", "T-0001"))
    assert r["ready"] == ["T-0001.4"] and r["closed"] == [] and r["remaining"] == ["T-0001.4"]
    assert r["superseded"] == ["T-0001.2", "T-0001.3"]
    assert r["subtickets"] == ["T-0001.1", "T-0001.2", "T-0001.3", "T-0001.4"]
    assert ticket(respecced, "T-0001.2")["status"] == "closed"
    assert ticket(respecced, "T-0001.3")["status"] == "waiting-dependencies"
    [e] = events(respecced, "subtickets.superseded")
    assert (e["ticket"], e["subtickets"], e["approved_version"]) == ("T-0001", ["T-0001.2", "T-0001.3"], 2)


def test_the_final_check_counts_only_the_current_plan(respecced, tmp_path):
    replan(respecced, tmp_path)
    assert js(run(respecced, "ticket", "parent-check", "T-0001"))["state"] == "planned"
    js(run(respecced, "ticket", "set", "T-0001.4", "status=merged"))
    r = js(run(respecced, "ticket", "parent-check", "T-0001"))
    assert r["state"] == "ready-for-parent-verify"
    assert r["subtickets"] == {"T-0001.1": "merged", "T-0001.4": "merged"}
    assert r["superseded"] == ["T-0001.2", "T-0001.3"]


def test_a_re_plan_past_superseded_sub_tickets_is_accepted(respecced, tmp_path):
    replan(respecced, tmp_path)
    js(run(respecced, "ticket", "set", "T-0001.4", "status=merged"))
    js(run(respecced, "ticket", "parent-check", "T-0001"))
    js(run(respecced, "ticket", "park", "T-0001", "--reason", "FAILED from parent-close verifier"))
    (tmp_path / "note.md").write_text("Re-plan: one more fix.\n")
    assert js(run(respecced, "resolve", "T-0001", "--replan", str(tmp_path / "note.md")))["state"] == "ready-for-planner"


def test_a_plan_that_depends_on_a_sub_ticket_it_supersedes_is_refused_and_writes_nothing(respecced, tmp_path):
    before = sorted(p.name for p in (respecced / "tickets").iterdir())
    cp = add_plan(respecced, tmp_path, "ST-1 / Redo\nDepends on: T-0001.3\nParallel-safe: yes\n", "plan3.md")
    assert cp.returncode == 2
    assert "T-0001.4 (ST-1) depends on T-0001.3, which this plan supersedes" in cp.stderr
    assert sorted(p.name for p in (respecced / "tickets").iterdir()) == before


def test_the_planner_input_names_the_sub_tickets_a_new_plan_supersedes(respecced):
    rid = js(run(respecced, "run", "start", "--role", "planner", "--ticket", "T-0001"))["run_id"]
    js(run(respecced, "run", "compose", rid))
    text = (respecced / "runs" / rid / "input.md").read_text()
    assert "- T-0001.3 / Unstarted: waiting-dependencies\n\n" + SUPERSEDES_LINE + "\n" in text


def test_a_second_plan_at_the_same_approved_version_supersedes_nothing(store, tmp_path):
    js(add_plan(store, tmp_path, "ST-1 / First\nDepends on: none\nParallel-safe: yes\n", "plan1.md"))
    assert js(add_plan(store, tmp_path, "ST-1 / Extra\nDepends on: none\nParallel-safe: yes\n", "plan2.md"))["superseded"] == []
    r = js(run(store, "ticket", "ready-implementers", "T-0001"))
    assert r["superseded"] == [] and r["ready"] == ["T-0001.1", "T-0001.2"]
    assert events(store, "subtickets.superseded") == []


def test_a_moved_spec_record_does_not_change_the_plan_a_sub_ticket_belongs_to(respecced, tmp_path):
    js(run(respecced, "ticket", "set", "T-0001.3", "spec.version=2", "spec.approved_version=2"))
    replan(respecced, tmp_path)
    assert js(run(respecced, "ticket", "ready-implementers", "T-0001"))["superseded"] == ["T-0001.2", "T-0001.3"]


def test_a_record_without_planned_from_falls_back_to_its_spec_version(respecced, tmp_path):
    replan(respecced, tmp_path)
    for i in (1, 2, 3, 4):
        js(run(respecced, "ticket", "set", f"T-0001.{i}", "planned_from="))
    assert js(run(respecced, "ticket", "ready-implementers", "T-0001"))["superseded"] == ["T-0001.2", "T-0001.3"]
