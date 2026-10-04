"""`resolve --ruling` on an implementer's BLOCKED park (spec-factory T-0023, part A, item H1): the
ruling becomes the sub-ticket's next ruling file, the sub-ticket returns to its implementer at the
same round, and the implementer's next input carries the ruling. ESCALATE rulings route as before.

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
RULING = "Ruling: take the second approach.\n"


def run(env: dict, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([str(BIN), *argv], capture_output=True, text=True,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **env}, cwd=REPO)


def js(cp: subprocess.CompletedProcess) -> dict:
    assert cp.returncode == 0, cp.stderr
    return json.loads(cp.stdout.strip().splitlines()[-1])


def ticket(store: Path, tid: str) -> dict:
    return yaml.safe_load((store / "tickets" / f"{tid}.yaml").read_text())


@pytest.fixture
def env(tmp_path: Path) -> dict:
    """A scratch store and target repo: T-0001 past the spec gate (no spec store)."""
    store = tmp_path / "store"
    target = tmp_path / "target"
    subprocess.run(["git", "init", "-q", "-b", "main", str(target)], check=True)
    subprocess.run(["git", "-C", str(target), "-c", "user.email=f@x", "-c", "user.name=f",
                    "commit", "-q", "--allow-empty", "-m", "init"], check=True)
    e = {"FACTORY_STATE": str(store), "FACTORY_REPO": str(target), "FACTORY_INTEGRATION_BRANCH": "main"}
    (tmp_path / "req.md").write_text("# Fixture\n\nThe bot should do the thing.\n")
    (tmp_path / "spec.md").write_text("## Problem\nx\n")
    js(run(e, "ticket", "new", "--file", str(tmp_path / "req.md")))
    js(run(e, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t"))
    js(run(e, "spec", "add", "T-0001", "--file", str(tmp_path / "spec.md")))
    js(run(e, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init"))
    return e


def approved(env: dict, tmp_path: Path) -> Path:
    """T-0001 approved and split into one sub-ticket, T-0001.1; returns the store."""
    js(run(env, "ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t"))
    js(run(env, "approve-spec", "T-0001"))
    (tmp_path / "plan.md").write_text("ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n")
    js(run(env, "subticket", "add", "T-0001", "--file", str(tmp_path / "plan.md")))
    return Path(env["FACTORY_STATE"])


def write_ruling(tmp_path: Path) -> Path:
    p = tmp_path / "r.md"
    p.write_text(RULING)
    return p


def test_a_ruling_on_a_blocked_park_returns_the_sub_ticket_to_its_implementer(env, tmp_path):
    store = approved(env, tmp_path)
    js(run(env, "ticket", "set", "T-0001.1", "round.pr=1"))
    js(run(env, "ticket", "park", "T-0001.1", "--reason", "BLOCKED from implementer"))
    res = js(run(env, "resolve", "T-0001.1", "--ruling", str(write_ruling(tmp_path))))
    assert res["state"] == "ready-for-implementer" and res["kind"] == "ruling"
    assert res["ruling"] == "approvals/T-0001.1/ruling-1.md"
    t = ticket(store, "T-0001.1")
    assert t["status"] == "ready-for-implementer"
    assert t["parked"] is None
    assert t["round"]["pr"] == 1  # same round: a ruling is not a review round
    assert (store / "approvals" / "T-0001.1" / "ruling-1.md").read_text() == RULING

    rid = js(run(env, "run", "start", "--role", "implementer", "--ticket", "T-0001.1"))["run_id"]
    sources = js(run(env, "run", "compose", rid))["sources"]
    assert "approvals/T-0001.1/ruling-1.md" in sources
    text = (store / "runs" / rid / "input.md").read_text()
    assert "## Human ruling\n\n" + RULING.rstrip() in text


def test_a_second_blocked_ruling_takes_the_next_ruling_number(env, tmp_path):
    store = approved(env, tmp_path)
    for n in (1, 2):
        js(run(env, "ticket", "park", "T-0001.1", "--reason", "BLOCKED from implementer"))
        assert js(run(env, "resolve", "T-0001.1", "--ruling", str(write_ruling(tmp_path))))["ruling"] == \
            f"approvals/T-0001.1/ruling-{n}.md"
    assert sorted(p.name for p in (store / "approvals" / "T-0001.1").glob("ruling-*")) == ["ruling-1.md", "ruling-2.md"]


@pytest.mark.parametrize("reason, to", [("ESCALATE from critic", "ready-for-critic"),
                                        ("ESCALATE from planner", "ready-for-planner")])
def test_escalate_rulings_route_as_before(env, tmp_path, reason, to):
    store = Path(env["FACTORY_STATE"])
    js(run(env, "ticket", "park", "T-0001", "--reason", reason))
    assert js(run(env, "resolve", "T-0001", "--ruling", str(write_ruling(tmp_path))))["state"] == to
    assert ticket(store, "T-0001")["status"] == to
    assert (store / "approvals" / "T-0001" / "ruling-1.md").read_text() == RULING


def test_a_needs_human_park_still_asks_for_an_answer(env, tmp_path):
    store = Path(env["FACTORY_STATE"])
    js(run(env, "ticket", "park", "T-0001", "--reason", "NEEDS-HUMAN from spec writer"))
    cp = run(env, "resolve", "T-0001", "--ruling", str(write_ruling(tmp_path)))
    assert cp.returncode == 2
    assert "use --answer" in cp.stderr
    assert ticket(store, "T-0001")["status"] == "parked"
    assert not list((store / "approvals" / "T-0001").glob("ruling-*"))


@pytest.mark.parametrize("park", ["budget kill: reviewer", None])
def test_a_ruling_on_any_other_state_is_refused_and_names_both_park_kinds(env, tmp_path, park):
    store = Path(env["FACTORY_STATE"])
    if park:
        js(run(env, "ticket", "park", "T-0001", "--reason", park))
    cp = run(env, "resolve", "T-0001", "--ruling", str(write_ruling(tmp_path)))
    assert cp.returncode == 2
    state = "parked" if park else "ready-for-critic"
    assert f"--ruling applies to an ESCALATE or BLOCKED park; T-0001 is {state} ({park or 'no park'})" in cp.stderr
    assert ticket(store, "T-0001")["status"] == state
    assert not list((store / "approvals" / "T-0001").glob("ruling-*"))
