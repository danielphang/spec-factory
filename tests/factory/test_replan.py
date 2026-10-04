"""Re-plan after a failed parent-close check (spec-factory T-0023, part I, item H9).

`resolve PARENT --replan F` sends a parked parent whose sub-tickets all merged back to the planner
with F as its next ruling; the planner's input then lists the parent's existing sub-tickets. A
later plan's sub-tickets take the next free ids, may depend on an existing sub-ticket, and may not
reuse one's id. A first plan is unchanged: numbered from `.1`, and no sub-ticket section.

Black-box through `bin/factory` on a throwaway store (FACTORY_STATE), as test_decision_log.py does.
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
NOTE = "Re-plan: add one fix for the case-insensitive path.\n"
SECTION = "## Sub-tickets already under T-0001"
FIRST_PLAN = "ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: ST-1\nParallel-safe: yes\n"


def run(store: Path, *argv: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "FACTORY_STATE": str(store), "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)


def js(cp: subprocess.CompletedProcess) -> dict:
    assert cp.returncode == 0, cp.stderr
    return json.loads(cp.stdout.strip().splitlines()[-1])


def ticket(store: Path, tid: str) -> dict:
    return yaml.safe_load((store / "tickets" / f"{tid}.yaml").read_text())


def files(d: Path) -> list[str]:
    return sorted(str(p.relative_to(d)) for p in d.rglob("*") if p.is_file()) if d.exists() else []


def add_plan(store: Path, tmp_path: Path, text: str, name: str = "plan.md") -> subprocess.CompletedProcess:
    (tmp_path / name).write_text(text)
    return run(store, "subticket", "add", "T-0001", "--file", str(tmp_path / name))


@pytest.fixture
def store(tmp_path: Path) -> Path:
    """T-0001 past the spec gate (no spec store), with no sub-tickets yet."""
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
def closed(store: Path, tmp_path: Path) -> Path:
    """T-0001 split into T-0001.1 and T-0001.2, both merged, then parked by a FAILED parent-close run."""
    js(add_plan(store, tmp_path, FIRST_PLAN, "plan1.md"))
    js(run(store, "ticket", "set", "T-0001.1", "status=merged"))
    js(run(store, "ticket", "set", "T-0001.2", "status=merged"))
    js(run(store, "ticket", "transition", "T-0001", "--to", "planned", "--by", "t"))
    js(run(store, "ticket", "transition", "T-0001", "--to", "ready-for-parent-verify", "--by", "t"))
    js(run(store, "ticket", "park", "T-0001", "--reason", "FAILED from parent-close verifier"))
    return store


def note(tmp_path: Path) -> Path:
    p = tmp_path / "note.md"
    p.write_text(NOTE)
    return p


def planner_input(store: Path) -> tuple[list[str], str]:
    rid = js(run(store, "run", "start", "--role", "planner", "--ticket", "T-0001"))["run_id"]
    sources = js(run(store, "run", "compose", rid))["sources"]
    return sources, (store / "runs" / rid / "input.md").read_text()


# ----- resolve --replan ----------------------------------------------------------------------

def test_a_replan_sends_the_parent_to_its_planner_with_the_note_and_the_sub_ticket_list(closed, tmp_path):
    rounds = ticket(closed, "T-0001")["round"]
    res = js(run(closed, "resolve", "T-0001", "--replan", str(note(tmp_path))))
    assert res == {"ok": True, "id": "T-0001", "state": "ready-for-planner", "kind": "replan",
                   "ruling": "approvals/T-0001/ruling-1.md"}
    t = ticket(closed, "T-0001")
    assert t["status"] == "ready-for-planner" and t["parked"] is None
    assert t["round"] == rounds
    assert t["history"][-1]["resolve"] == "replan" and t["history"][-1]["ruling"] == "approvals/T-0001/ruling-1.md"
    assert (closed / "approvals" / "T-0001" / "ruling-1.md").read_text() == NOTE
    assert yaml.safe_load((closed / "approvals" / "T-0001" / "resolve-1.yaml").read_text())["kind"] == "replan"
    assert [ticket(closed, s)["status"] for s in ("T-0001.1", "T-0001.2")] == ["merged", "merged"]

    sources, text = planner_input(closed)
    assert sources[-1] == "approvals/T-0001/ruling-1.md"
    assert "## Human ruling\n\n" + NOTE.rstrip() in text
    assert text.index("## Human ruling") < text.index(SECTION)
    assert text.endswith(f"{SECTION}\n\nA new plan's sub-tickets are numbered after these. A `Depends on:` line may "
                         "name any of these ids.\n\n- T-0001.1 / First: merged\n- T-0001.2 / Second: merged\n")


def test_a_replan_is_refused_while_a_sub_ticket_is_not_merged_and_writes_nothing(closed, tmp_path):
    js(run(closed, "ticket", "set", "T-0001.2", "status=closed"))
    before = files(closed / "approvals")
    cp = run(closed, "resolve", "T-0001", "--replan", str(note(tmp_path)))
    assert cp.returncode == 2
    assert "--replan needs every sub-ticket merged: T-0001.2 is closed" in cp.stderr
    assert ticket(closed, "T-0001")["status"] == "parked"
    assert files(closed / "approvals") == before


def test_a_replan_names_every_sub_ticket_that_is_not_merged(closed, tmp_path):
    js(run(closed, "ticket", "set", "T-0001.1", "status=closed"))
    js(run(closed, "ticket", "set", "T-0001.2", "status=parked"))
    cp = run(closed, "resolve", "T-0001", "--replan", str(note(tmp_path)))
    assert cp.returncode == 2
    assert "--replan needs every sub-ticket merged: T-0001.1 is closed, T-0001.2 is parked" in cp.stderr


def test_a_replan_is_refused_for_a_parent_with_no_sub_tickets(store, tmp_path):
    js(run(store, "ticket", "park", "T-0001", "--reason", "FAILED from parent-close verifier"))
    before = files(store / "approvals")
    cp = run(store, "resolve", "T-0001", "--replan", str(note(tmp_path)))
    assert cp.returncode == 2
    assert "--replan applies to a parent with sub-tickets; T-0001 has none" in cp.stderr
    assert ticket(store, "T-0001")["status"] == "parked"
    assert files(store / "approvals") == before


def test_a_replan_is_refused_unless_the_parent_is_parked(closed, tmp_path):
    js(run(closed, "ticket", "set", "T-0001", "status=ready-for-parent-verify", "parked=null"))
    cp = run(closed, "resolve", "T-0001", "--replan", str(note(tmp_path)))
    assert cp.returncode == 2
    assert "--replan applies to a parked parent; T-0001 is ready-for-parent-verify" in cp.stderr
    assert not list((closed / "approvals" / "T-0001").glob("ruling-*"))


def test_decision_is_refused_with_replan(closed, tmp_path):
    cp = run(closed, "resolve", "T-0001", "--replan", str(note(tmp_path)), "--close", "--decision", "x")
    assert cp.returncode == 2
    assert "--decision applies only with --answer or --close" in cp.stderr
    assert ticket(closed, "T-0001")["status"] == "parked"


def test_resolve_with_no_mode_lists_replan(closed):
    cp = run(closed, "resolve", "T-0001")
    assert cp.returncode == 2
    assert "--redispatch | --replan F | --close" in cp.stderr


# ----- planner input -------------------------------------------------------------------------

def test_a_first_plans_planner_input_has_no_sub_ticket_section(store):
    js(run(store, "ticket", "set", "T-0001", "status=ready-for-planner"))
    sources, text = planner_input(store)
    assert sources == ["specs/T-0001/v1.md"]
    assert "Sub-tickets already under" not in text


# ----- a later plan's numbering --------------------------------------------------------------

def test_a_first_plan_is_still_numbered_from_one(store, tmp_path):
    subs = js(add_plan(store, tmp_path, FIRST_PLAN))["subtickets"]
    assert [(s["id"], s["label"], s["depends_on"]) for s in subs] == [
        ("T-0001.1", "ST-1", []), ("T-0001.2", "ST-2", ["T-0001.1"])]


def test_a_later_plan_takes_the_next_free_ids_and_may_depend_on_a_merged_sibling(closed, tmp_path):
    js(run(closed, "resolve", "T-0001", "--replan", str(note(tmp_path))))
    plan = ("ST-1 / Fix the bypass\nDepends on: T-0001.2\nParallel-safe: yes\n\n"
            "ST-2 / Cover it\nDepends on: ST-1, .1\nParallel-safe: yes\n")
    subs = js(add_plan(closed, tmp_path, plan, "plan2.md"))["subtickets"]
    assert [(s["id"], s["label"], s["depends_on"]) for s in subs] == [
        ("T-0001.3", "ST-1", ["T-0001.2"]), ("T-0001.4", "ST-2", ["T-0001.3", "T-0001.1"])]
    assert ticket(closed, "T-0001.3")["status"] == "waiting-dependencies"
    assert [ticket(closed, s)["status"] for s in ("T-0001.1", "T-0001.2")] == ["merged", "merged"]
    js(run(closed, "ticket", "transition", "T-0001", "--to", "planned", "--by", "t"))
    assert js(run(closed, "ticket", "ready-implementers", "T-0001"))["ready"] == ["T-0001.3"]


def test_numbering_follows_the_highest_existing_index(closed, tmp_path):
    (closed / "tickets" / "T-0001.2.yaml").rename(closed / "tickets" / "T-0001.7.yaml")
    t = ticket(closed, "T-0001.7")
    t["id"] = "T-0001.7"
    (closed / "tickets" / "T-0001.7.yaml").write_text(yaml.safe_dump(t))
    subs = js(add_plan(closed, tmp_path, "ST-1 / Next\nDepends on: none\nParallel-safe: yes\n"))["subtickets"]
    assert [s["id"] for s in subs] == ["T-0001.8"]


def test_a_plan_that_reuses_an_existing_sub_ticket_id_is_refused_and_writes_nothing(closed, tmp_path):
    before = files(closed / "tickets") + files(closed / "specs")
    cp = add_plan(closed, tmp_path, "T-0001.1 / Again\nDepends on: none\nParallel-safe: yes\n", "plan3.md")
    assert cp.returncode == 2
    assert "T-0001.1: T-0001.1 is already a sub-ticket of T-0001; give the new sub-ticket another id" in cp.stderr
    assert files(closed / "tickets") + files(closed / "specs") == before


def test_a_dependency_on_a_sub_ticket_that_does_not_exist_is_still_refused(closed, tmp_path):
    cp = add_plan(closed, tmp_path, "ST-1 / Fix\nDepends on: T-0001.9\nParallel-safe: yes\n")
    assert cp.returncode == 2
    assert "ST-1: depends on T-0001.9, which is not a sub-ticket of this plan" in cp.stderr
    assert not (closed / "tickets" / "T-0001.3.yaml").exists()
