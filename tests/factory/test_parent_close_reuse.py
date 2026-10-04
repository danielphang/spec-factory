"""A parent with one sub-ticket closes on that sub-ticket's VERIFIED run (T-0016 part C).

The rule (docs/design.md routing table, Merge gate row): when the parent has exactly one sub-ticket,
the integration branch has not moved since it merged, the sub-ticket's text names every scenario of
the parent's pinned spec, and its VERIFIED run checked the merged head against the parent's recorded
base, that run stands for the parent-close run. In every other case the parent still needs its own.
Driven through the store CLI with the Shepherd fixture, as build.js does in phase 3.
"""
from __future__ import annotations

import yaml

from .test_shepherd import built_to_implementer

TWO_COVERING = ("T-0001.1 / First\n  Depends on: none\n  Parallel-safe: yes\n  Acceptance: asked once\n\n"
                "T-0001.2 / Second\n  Depends on: T-0001.1\n  Parallel-safe: yes\n  Acceptance: asked once\n\n"
                "Coverage map: asked once → T-0001.1, T-0001.2\n")
UNCOVERED = ("T-0001.1 / Do the thing\n  Depends on: none\n  Parallel-safe: yes\n  Acceptance: the check\n\n"
             "Coverage map: the check → T-0001.1\n")


def _parent_verifier_runs(f, tid: str) -> list[str]:
    return [p.parent.name for p in (f.store / "runs").glob("*-verifier/meta.yaml")
            if yaml.safe_load(p.read_text())["ticket"] == tid]


def _build(f, st: str):
    f.dispatch("implementer", st, stub="accept-approve/implementer-1.md")
    f.dispatch("reviewer", st, stub="accept-approve/reviewer-1.md")
    ver = f.dispatch("verifier", st, stub="accept-approve/verifier-1.md")
    assert f.state(st) == "merged"
    return ver


def _assert_parent_close_still_required(f, tid: str) -> None:
    pc = f.ok("ticket", "parent-check", tid)
    assert pc["state"] == "ready-for-parent-verify" and pc["reuse"] is None
    cp = f.cli("ticket", "transition", tid, "--to", "closed", "--by", "workflow")
    assert cp.returncode == 2 and "closes after a VERIFIED parent-close run" in cp.stderr
    cp = f.cli("archive", tid)
    assert cp.returncode == 2 and "no VERIFIED parent-close verifier run" in cp.stderr
    assert f.state(tid) == "ready-for-parent-verify" and _parent_verifier_runs(f, tid) == []


def test_a_single_sub_ticket_parent_closes_and_archives_on_its_verified_run(tmp_path):
    f, tid, (st,) = built_to_implementer(tmp_path)
    ver = _build(f, st)
    pc = f.ok("ticket", "parent-check", tid)
    assert pc["state"] == "ready-for-parent-verify" and pc["reuse"] == ver.run_id
    # build.js phase 3 with `reuse` set: no verifier run, straight to archive, then the close
    f.ok("archive", tid)
    f.ok("ticket", "transition", tid, "--to", "closed", "--by", "workflow")
    t = f.ticket(tid)
    assert t["status"] == "closed" and t["history"][-1]["verified_by"] == ver.run_id
    assert _parent_verifier_runs(f, tid) == []
    truth = (f.store / "openspec" / "specs" / "thing" / "spec.md").read_text()
    assert "#### Scenario: asked once" in truth


def test_a_parent_close_run_is_still_required_when_main_moved_after_the_merge(tmp_path):
    f, tid, (st,) = built_to_implementer(tmp_path)
    _build(f, st)
    f.git("commit", "-q", "--allow-empty", "-m", "another change on main")
    _assert_parent_close_still_required(f, tid)


def test_a_parent_close_run_is_still_required_with_two_sub_tickets(tmp_path):
    f, tid, (a, b) = built_to_implementer(tmp_path, TWO_COVERING)
    _build(f, a)
    _build(f, b)
    assert f.repo_rev("main") == f.ticket(b)["merge"]["main_after"]  # main has not moved since the last merge
    _assert_parent_close_still_required(f, tid)


def test_a_parent_close_run_is_still_required_when_the_sub_ticket_misses_a_scenario(tmp_path):
    f, tid, (st,) = built_to_implementer(tmp_path, UNCOVERED)
    assert "asked once" not in (f.store / "specs" / st / "subticket.md").read_text()
    _build(f, st)
    _assert_parent_close_still_required(f, tid)


def test_a_parent_close_run_is_still_required_when_the_verified_run_had_another_base(tmp_path):
    """main moves to a commit the branch already contains after the verifier started: the merge goes
    through, but the VERIFIED run checked the head against a base older than the parent's."""
    f, tid, (st,) = built_to_implementer(tmp_path)
    f.dispatch("implementer", st, stub="accept-approve/implementer-1.md")
    first = f.ticket(st)["head"]
    wt = f.store / "worktrees" / st
    (wt / "more.txt").write_text("more\n")
    f.git("add", "more.txt", cwd=wt)
    f.git("commit", "-q", "-m", "more", cwd=wt)
    f.ok("ticket", "head", st)
    f.dispatch("reviewer", st, stub="accept-approve/reviewer-1.md")
    ver = f.dispatch("verifier", st, stub="accept-approve/verifier-1.md", route=False)
    f.git("merge", "-q", "--ff-only", first)
    f.route("verifier", st, ver.run_id, ver.status)
    assert f.state(st) == "merged"
    meta = yaml.safe_load((f.store / "runs" / ver.run_id / "meta.yaml").read_text())
    assert meta["status"] == "VERIFIED" and meta["head"] == f.ticket(st)["head"]
    assert meta["base"] != f.ticket(tid)["parent_base"] == first
    _assert_parent_close_still_required(f, tid)
