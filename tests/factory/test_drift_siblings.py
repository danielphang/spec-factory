"""The spec drift check and a merged sibling (spec-factory T-0041). Part A: the test rule skips a
first-parent commit that is the recorded merge (`merge.main_after`) of a merged sub-ticket of the
same parent, from any of its plans; a later direct commit, or a merge that is no sub-ticket's, is
still drift. Part B: `resolve --ruling` accepts a `harness-bug: run start implementer:` park from
`ready-for-implementer` and returns the sub-ticket to its implementer, same round; every other
harness-bug park stays refused.

Each case builds the spec's t0027-amend.sh fixture (test_spec_amend's `f`): a throwaway store with a
spec store and a scratch target whose main holds src/greet.py and src/other.py. T-0001's v1, whose
design names `src/greet.py`, is approved.
"""
from __future__ import annotations

import subprocess

import pytest
import yaml

from ._fixtures import (  # noqa: F401  (f is the t0027-amend.sh store fixture)
    V2,
    Fixture,
    drifted,
    f,
    head,
    implementer_runs,
    land,
    start,
    started,
)

ST1_THEN_ST2 = "ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: ST-1\nParallel-safe: yes\n"
ONE = "ST-1 / First\nDepends on: none\nParallel-safe: yes\n"


def git(f: Fixture, *argv: str) -> None:
    subprocess.run(["git", "-C", str(f.target), "-c", "user.email=f@x", "-c", "user.name=f", *argv], check=True)


def merge_branch(f: Fixture, branch: str, *files: str) -> str:
    """A branch off main that lands FILES, merged back with --no-ff; returns the merge commit."""
    git(f, "checkout", "-qb", branch)
    _land_on(f, branch, *files)
    git(f, "checkout", "-q", "main")
    git(f, "merge", "-q", "--no-ff", "-m", f"Merge {branch}", branch)
    return head(f)


def _land_on(f: Fixture, branch: str, *files: str) -> None:
    """One commit on the checked-out branch that appends a line to each file."""
    for rel in files:
        p = f.target / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a") as fh:
            fh.write(f"# {rel} on {branch}\n")
    git(f, "add", "-A")
    git(f, "commit", "-qm", f"{branch}: {' '.join(files)}")


def merge_sibling(f: Fixture, tid: str = "T-0001.1") -> str:
    """ST-1's branch adds tests/test_greet.py and changes src/greet.py; merged --no-ff and recorded
    as TID's merge, as `factory merge` records it. Returns the merge commit."""
    before = head(f)
    after = merge_branch(f, "st1", "src/greet.py", "tests/test_greet.py")
    f.ok("ticket", "set", tid, "status=merged", f"merge.base_before='{before}'", f"merge.main_after='{after}'")
    return after


def two_parts_with_st1_merged(f: Fixture) -> str:
    f.plan(ST1_THEN_ST2)
    merged = merge_sibling(f)
    f.ok("ticket", "set", "T-0001.2", "status=ready-for-implementer")
    return merged


# ----- part A: a merged sibling's merge is not drift ----------------------------------------------

def test_a_merged_siblings_merge_is_not_drift(f):
    two_parts_with_st1_merged(f)
    started(start(f, "T-0001.2"))
    assert len(implementer_runs(f)) == 1


def test_a_later_direct_commit_beside_a_named_file_is_still_drift_naming_only_its_test(f):
    two_parts_with_st1_merged(f)
    later = land(f, "src/greet.py", "tests/test_other.py")
    error = drifted(f, start(f, "T-0001.2"), "T-0001.2")
    assert f"tests/test_other.py changed by {later[:9]} " in error
    assert "test_greet.py" not in error and error.count("changed by") == 1


def test_a_later_direct_commit_to_the_siblings_test_is_drift_naming_that_commit(f):
    merged = two_parts_with_st1_merged(f)
    later = land(f, "src/greet.py", "tests/test_greet.py")
    error = drifted(f, start(f, "T-0001.2"), "T-0001.2")
    assert f"tests/test_greet.py changed by {later[:9]} " in error
    assert merged[:9] not in error and error.count("changed by") == 1


def test_a_merge_that_is_no_subtickets_is_still_drift_naming_its_merge_commit(f):
    merged = two_parts_with_st1_merged(f)
    ext = merge_branch(f, "ext", "src/greet.py", "tests/test_merge.py")
    error = drifted(f, start(f, "T-0001.2"), "T-0001.2")
    assert f"tests/test_merge.py changed by {ext[:9]} " in error
    assert "test_greet.py" not in error and merged[:9] not in error and error.count("changed by") == 1


def test_an_unmerged_subtickets_recorded_merge_is_still_drift(f):
    """Only a merged sub-ticket's main_after is skipped: a stale record on one that has not merged
    does not hide a commit."""
    f.plan(ST1_THEN_ST2)
    merged = merge_sibling(f)
    f.ok("ticket", "set", "T-0001.1", "status=ready-for-implementer")
    f.ok("ticket", "set", "T-0001.2", "status=ready-for-implementer")
    error = drifted(f, start(f, "T-0001.2"), "T-0001.2")
    assert f"tests/test_greet.py changed by {merged[:9]} " in error


def test_a_merged_subticket_of_an_earlier_plan_is_not_drift(f):
    base = head(f)
    f.plan(ONE)
    merge_sibling(f)
    f.ok("ticket", "park", "T-0001", "--reason", "re-spec after ST-1")
    f.ok("resolve", "T-0001", "--to", "spec-gate")
    f.ok("approve-spec", "T-0001", "--edit", f.file("v2.md", V2))
    # count from before ST-1's merge, so the walk passes over it
    (f.store / "specs" / "T-0001" / "v2.yaml").write_text(yaml.safe_dump({"integration_head": base}))
    f.plan(ONE)
    assert f.ticket("T-0001.1")["planned_from"] == 1 and f.ticket("T-0001.2")["planned_from"] == 2
    started(start(f, "T-0001.2"))


# ----- part B: a ruling on an implementer's failed run start ---------------------------------------

RULING = "Ruling: the new test may change.\n"
REFUSAL = "--ruling applies to an ESCALATE or BLOCKED park, or a harness-bug park from an implementer's run start; "


def test_a_ruling_on_a_harness_bug_run_start_implementer_park_returns_it_and_the_implementer_starts(f):
    f.plan(ONE)
    land(f, "src/greet.py", "tests/test_greet.py")
    error = drifted(f, start(f))
    f.ok("ticket", "park", "T-0001.1", "--reason", f"harness-bug: run start implementer: {error}")
    round_before = f.ticket("T-0001.1")["round"]
    res = f.ok("resolve", "T-0001.1", "--ruling", f.file("r.md", RULING))
    assert res["state"] == "ready-for-implementer" and res["kind"] == "ruling"
    t = f.ticket("T-0001.1")
    assert t["status"] == "ready-for-implementer" and t["parked"] is None and t["round"] == round_before
    assert (f.store / "approvals" / "T-0001.1" / "ruling-1.md").read_text() == RULING
    started(start(f))
    assert len(implementer_runs(f)) == 1


@pytest.mark.parametrize("reason, status", [
    ("harness-bug: run start reviewer: x", "checks-in-flight"),
    ("harness-bug: run compose implementer: x", "ready-for-implementer"),
    ("harness-bug: run start implementer: x", "checks-in-flight"),
])
def test_a_ruling_on_any_other_harness_bug_park_is_refused_writing_nothing(f, reason, status):
    f.plan(ONE)
    if status != "ready-for-implementer":
        f.ok("ticket", "set", "T-0001.1", f"status={status}")
    f.ok("ticket", "park", "T-0001.1", "--reason", reason)
    ruling = f.file("r.md", RULING)
    before = f.snapshot()
    cp = f.cli("resolve", "T-0001.1", "--ruling", ruling)
    assert cp.returncode == 2
    assert f"{REFUSAL}T-0001.1 is parked ({reason})" in cp.stderr
    assert f.snapshot() == before
