"""The live-store fence (T-0024): only the dispatcher writes an instance's own store during a run.

Two rules, both for every command outside the read-only list:
- location: a write run from inside the own store's `runs/` or `worktrees/` is refused, with or
  without `FACTORY_DISPATCH=1` and with or without a run in flight;
- in flight: while any run is in flight on the own store, a write without `FACTORY_DISPATCH=1` is
  refused.

Black-box through `bin/factory` in scratch target repos. The `cli` helper drops FACTORY_DISPATCH
from the inherited environment (test_instance.STRIP), so a runner that exported the marker cannot
change a result; a case that needs the marker passes it explicitly.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from .test_instance import cli, git_repo, js, tree

RULE = "role runs may not write the live store"


@pytest.fixture
def target(tmp_path: Path) -> Path:
    t = git_repo(tmp_path / "target")
    cp = cli(t, "init", "--repo-name", "demo")
    assert cp.returncode == 0, cp.stderr
    req = tmp_path / "r.md"
    req.write_text("# demo\n\nDo the thing.\n")
    assert cli(t, "ticket", "new", "--file", str(req)).returncode == 0
    return t


def state(target: Path) -> Path:
    return target / ".factory" / "state"


def start_triage(target: Path) -> str:
    cp = cli(target, "run", "start", "--role", "triage", "--ticket", "T-0001")
    assert cp.returncode == 0, cp.stderr
    return js(cp)["run_id"]


def snapshot(target: Path) -> dict[str, bytes]:
    return {**tree(target / ".factory"), **tree(target / ".claude")}


def request(tmp_path: Path) -> str:
    p = tmp_path / "r2.md"
    p.write_text("# other\n\nDo another thing.\n")
    return str(p)


def assert_refused(cp, *details: str) -> None:
    assert cp.returncode == 2, (cp.returncode, cp.stdout, cp.stderr)
    assert RULE in cp.stderr and "use a throwaway FACTORY_STATE" in cp.stderr
    assert "FACTORY_DISPATCH" not in cp.stderr + cp.stdout
    assert js(cp) == {"ok": False, "error": cp.stderr.strip()}
    for d in details:
        assert d in cp.stderr


# ----- in flight ------------------------------------------------------------------------------

def test_unmarked_writes_are_refused_while_a_run_is_in_flight(target, tmp_path):
    rid = start_triage(target)
    (target / "sub").mkdir()
    before = snapshot(target)
    for cwd in (target, target / "sub"):
        for argv in (("ticket", "new", "--file", request(tmp_path)),
                     ("ticket", "transition", "T-0001", "--to", "closed", "--by", "t"),
                     ("decision", "add", "T-0001", "x"),
                     ("ticket", "set", "T-0001", "title=y")):
            assert_refused(cli(cwd, *argv), f"{state(target).resolve()}; in flight: {rid}")
    assert snapshot(target) == before


def test_init_is_refused_while_a_run_is_in_flight_and_rewrites_nothing(target):
    start_triage(target)
    agents = target / ".claude"
    for p in sorted(agents.rglob("*"), reverse=True):
        p.unlink() if p.is_file() else p.rmdir()
    agents.rmdir()
    before = snapshot(target)
    assert_refused(cli(target, "init", "--repo-name", "x"))
    assert snapshot(target) == before and not agents.exists()


def test_a_harness_acceptance_is_refused_while_a_run_is_in_flight(target):
    start_triage(target)
    lock = (target / ".factory" / "harness.lock").read_text().strip()
    before = snapshot(target)
    assert_refused(cli(target, "--accept-harness", lock, "ticket", "show", "T-0001"))
    assert snapshot(target) == before


def test_reads_answer_while_a_run_is_in_flight(target):
    rid = start_triage(target)
    for cwd in (target, state(target) / "runs" / rid / "scratch"):
        for argv in (("ticket", "show", "T-0001"), ("config",), ("log", "tail"),
                     ("results", "show", "T-0001"), ("paths",)):
            cp = cli(cwd, *argv)
            assert cp.returncode == 0, (argv, cp.stderr)


def test_a_marked_write_from_the_repository_root_goes_through(target):
    rid = start_triage(target)
    assert cli(target, "decision", "add", "T-0001", "marked", FACTORY_DISPATCH="1").returncode == 0
    cp = cli(target, "run", "finish", rid, "--status-override", "KILLED", FACTORY_DISPATCH="1")
    assert cp.returncode == 0, cp.stderr
    assert js(cli(target, "ticket", "show", "T-0001", "--json"))["in_flight"] == []


def test_only_the_value_1_is_the_marker(target):
    start_triage(target)
    assert_refused(cli(target, "decision", "add", "T-0001", "x", FACTORY_DISPATCH="yes"))


def test_with_no_run_in_flight_unmarked_writes_go_through(target, tmp_path):
    rid = start_triage(target)
    assert cli(target, "run", "finish", rid, "--status-override", "KILLED", FACTORY_DISPATCH="1").returncode == 0
    assert cli(target, "ticket", "new", "--file", request(tmp_path)).returncode == 0
    assert cli(target, "decision", "add", "T-0001", "after").returncode == 0


def test_a_throwaway_store_is_not_fenced(target, tmp_path):
    rid = start_triage(target)
    other = tmp_path / "s"
    assert cli(target, "init", FACTORY_STATE=str(other)).returncode == 0
    scratch = state(target) / "runs" / rid / "scratch"
    cp = cli(scratch, "ticket", "new", "--file", request(tmp_path), FACTORY_STATE=str(other))
    assert cp.returncode == 0, cp.stderr


# ----- location -------------------------------------------------------------------------------

def test_marked_writes_from_a_runs_scratch_directory_are_refused(target, tmp_path):
    rid = start_triage(target)
    scratch = state(target) / "runs" / rid / "scratch"
    before = snapshot(target)
    for argv in (("decision", "add", "T-0001", "x"), ("init", "--repo-name", "x"),
                 ("ticket", "new", "--file", request(tmp_path))):
        assert_refused(cli(scratch, *argv, FACTORY_DISPATCH="1"),
                       f"{state(target).resolve()}; called from inside its runs/")
    assert snapshot(target) == before


def test_marked_writes_from_under_worktrees_are_refused(target, tmp_path):
    start_triage(target)
    wt = state(target) / "worktrees" / "T-0001" / "sub"
    wt.mkdir(parents=True)
    before = snapshot(target)
    for argv in (("ticket", "new", "--file", request(tmp_path)), ("init",)):
        assert_refused(cli(wt, *argv, FACTORY_DISPATCH="1"),
                       f"{state(target).resolve()}; called from inside its worktrees/")
    assert snapshot(target) == before


def test_writes_from_a_finished_runs_scratch_directory_are_refused(target, tmp_path):
    rid = start_triage(target)
    assert cli(target, "run", "finish", rid, "--status-override", "KILLED", FACTORY_DISPATCH="1").returncode == 0
    assert js(cli(target, "ticket", "show", "T-0001", "--json"))["in_flight"] == []
    scratch = state(target) / "runs" / rid / "scratch"
    before = snapshot(target)
    assert_refused(cli(scratch, "ticket", "new", "--file", request(tmp_path)), "called from inside its runs/")
    assert_refused(cli(scratch, "decision", "add", "T-0001", "x", FACTORY_DISPATCH="1"), "called from inside its runs/")
    assert snapshot(target) == before
