"""`factory drive` and the live-store fence (T-0042): the driver is the dispatcher, so the fence
exempts it from its in-flight rule; it keeps the location rule, is fenced in full when given
`--accept-harness`, and guards its own ticket instead.

The same-ticket guard refuses `drive T`, exit 2 and nothing written, marked or not and on any store,
while T or one of its sub-tickets has a run in flight, or while `drive/T.yaml` has no `ended` and
names a live pid in `pid`.

Black-box through the CLI. Own-store cases use test_live_store_guard's scratch target; throwaway
store cases use test_drive's and test_drive_build's stores. Each puts test_drive's stand-in `claude`
first on PATH and counts its calls.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from .test_drive import STANDIN, Store
from .test_drive_build import BuildStore
from .test_instance import cli, js, tree
from .test_live_store_guard import (  # noqa: F401  (target is a fixture)
    assert_refused,
    request,
    snapshot,
    start_triage,
    state,
    target,
)

REJECT = {"triage": [{"write": "REJECT"}]}


class StandIn:
    """test_drive's stand-in `claude` in tmp_path/bin, and the environment that puts it on PATH."""

    def __init__(self, tmp_path: Path):
        bindir = tmp_path / "bin"
        bindir.mkdir()
        (bindir / "claude").write_text(STANDIN.format(python=sys.executable))
        (bindir / "claude").chmod(0o755)
        self.log = tmp_path / "claude.log"
        self.env = {"PATH": f"{bindir}{os.pathsep}{os.environ['PATH']}", "STANDIN_LOG": str(self.log)}

    def drive(self, cwd: Path, *argv: str, plays: dict | None = None, **extra: str):
        return cli(cwd, *argv, **self.env, STANDIN_PLAYS=json.dumps(plays or {}), **extra)

    def calls(self) -> list[dict]:
        return [json.loads(ln) for ln in self.log.read_text().splitlines()] if self.log.exists() else []


def guard_refused(cp, error: str) -> None:
    assert cp.returncode == 2, (cp.returncode, cp.stdout, cp.stderr)
    assert cp.stderr.strip() == error
    assert js(cp) == {"ok": False, "error": error}
    assert "FACTORY_DISPATCH" not in cp.stdout + cp.stderr


# ----- the exemption --------------------------------------------------------------------------

def test_an_unmarked_drive_starts_and_finishes_beside_another_tickets_run(target, tmp_path):
    rid = start_triage(target)
    assert cli(target, "ticket", "new", "--file", request(tmp_path), FACTORY_DISPATCH="1").returncode == 0
    c = StandIn(tmp_path)
    cp = c.drive(target, "drive", "T-0002", "--phase", "intake", plays=REJECT)
    assert cp.returncode == 0, cp.stderr
    assert js(cp)["state"] == "closed"
    assert js(cli(target, "ticket", "show", "T-0001", "--json"))["in_flight"] == [rid]
    calls = c.calls()
    assert len(calls) == 1 and calls[0]["dispatch"] is None
    assert Path(calls[0]["cwd"]).name.endswith("-triage") and Path(calls[0]["cwd"]).name != rid


def test_a_drive_given_accept_harness_is_refused_while_a_run_is_in_flight(target, tmp_path):
    rid = start_triage(target)
    assert cli(target, "ticket", "new", "--file", request(tmp_path), FACTORY_DISPATCH="1").returncode == 0
    lock = (target / ".factory" / "harness.lock").read_text().strip()
    c = StandIn(tmp_path)
    before = snapshot(target)
    assert_refused(c.drive(target, "--accept-harness", lock, "drive", "T-0002", plays=REJECT), f"in flight: {rid}")
    assert snapshot(target) == before and c.calls() == []


@pytest.mark.parametrize("marker", [{}, {"FACTORY_DISPATCH": "1"}], ids=["unmarked", "marked"])
@pytest.mark.parametrize("where", ["runs", "worktrees"])
def test_a_drive_from_inside_the_store_is_refused(target, tmp_path, where, marker):
    rid = start_triage(target)
    assert cli(target, "ticket", "new", "--file", request(tmp_path), FACTORY_DISPATCH="1").returncode == 0
    assert cli(target, "run", "finish", rid, "--status-override", "KILLED", FACTORY_DISPATCH="1").returncode == 0
    cwd = state(target) / "runs" / rid / "scratch" if where == "runs" else state(target) / "worktrees" / "T-0002"
    cwd.mkdir(parents=True, exist_ok=True)
    c = StandIn(tmp_path)
    before = snapshot(target)
    assert_refused(c.drive(cwd, "drive", "T-0002", plays=REJECT, **marker), f"called from inside its {where}/")
    assert snapshot(target) == before and c.calls() == []


# ----- the same-ticket guard ------------------------------------------------------------------

@pytest.mark.parametrize("marker", [{}, {"FACTORY_DISPATCH": "1"}], ids=["unmarked", "marked"])
def test_a_drive_of_a_ticket_with_its_own_run_in_flight_is_refused(target, tmp_path, marker):
    rid = start_triage(target)
    c = StandIn(tmp_path)
    before = snapshot(target)
    cp = c.drive(target, "drive", "T-0001", plays={"triage": [{"write": "ACCEPT"}]}, **marker)
    guard_refused(cp, f"T-0001 has runs in flight on it or its sub-tickets: {rid}; drive it again once they finish")
    assert snapshot(target) == before and c.calls() == []


def test_a_drive_of_a_parent_whose_subticket_has_a_run_in_flight_is_refused(tmp_path):
    s = BuildStore(tmp_path)
    plan = tmp_path / "plan.md"
    plan.write_text("ST-1 / One\nDepends on: none\nParallel-safe: yes\n")
    s.ok("subticket", "add", "T-0001", "--file", str(plan))
    s.ok("ticket", "transition", "T-0001", "--to", "planned", "--by", "t")
    rid = s.ok("run", "start", "--role", "implementer", "--ticket", "T-0001.1")["run_id"]
    before = tree(s.root)
    cp = s.cli("drive", "T-0001", "--phase", "build", plays={"implementer": [{"write": "READY-FOR-REVIEW"}]})
    guard_refused(cp, f"T-0001 has runs in flight on it or its sub-tickets: {rid}; drive it again once they finish")
    assert tree(s.root) == before and s.calls() == []


def write_status(s: Store, pid, ended=None) -> Path:
    p = s.root / "drive" / "T-0001.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"ticket: T-0001\npid: {pid}\nended: {json.dumps(ended)}\n")
    return p


@pytest.mark.parametrize("pid", [os.getpid(), 1], ids=["own-user", "other-user-or-root"])
def test_a_recorded_live_driver_blocks_a_second_drive(tmp_path, pid):
    s = Store(tmp_path)
    p = write_status(s, pid)
    before = tree(s.root)
    cp, _ = s.drive(REJECT)
    guard_refused(cp, f"T-0001 is already being driven by pid {pid} ({p}); stop that driver or wait for it to end")
    assert tree(s.root) == before and s.calls() == []


def dead_pid() -> int:
    p = subprocess.Popen([sys.executable, "-c", "pass"])
    p.wait()
    return p.pid


@pytest.mark.parametrize("pid,ended", [("dead", None), (os.getpid(), {"ok": True}), ("abc", None), (0, None),
                                       (2**70, None)], ids=["dead", "ended", "not-a-pid", "zero", "out-of-range"])
def test_an_ended_dead_or_unusable_driver_record_does_not_block(tmp_path, pid, ended):
    s = Store(tmp_path)
    write_status(s, dead_pid() if pid == "dead" else pid, ended)
    cp, res = s.drive(REJECT)
    assert cp.returncode == 0, cp.stderr
    assert res["state"] == "closed" and len(s.calls()) == 1
