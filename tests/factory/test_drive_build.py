"""`factory drive`, part B (T-0040): the build phase, a port of factory/workflows/build.js.

Black-box through `bin/factory`, on part A's throwaway store (test_drive.Store) taken past the spec
gate, with a scratch git repository as the target. The stand-in `claude` here extends part A's: a
written output carries a `Commit:` line naming the run's head, and a verifier's a passing gate
suite, so the checkers' results can be recorded; each call also appends "<start> <end>" to
<log>.times, so a test can count the role processes that ran at once.
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import tempfile
import time

import yaml

from ._cli import BIN, REPO
from ._fixtures import BuildStore, Store

OK_PLAYS = {"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"write": "APPROVE"}],
            "verifier": [{"write": "VERIFIED"}]}


def roles_and_statuses(s: Store) -> list[tuple[str, str, str]]:
    return [(m["role"], m["ticket"], m["status"]) for m in s.runs()]


def test_an_approved_head_merges_then_the_parent_close_verifier_runs(tmp_path):
    s = BuildStore(tmp_path)
    cp, res = s.drive(OK_PLAYS, "--phase", "build")
    assert cp.returncode == 0, cp.stderr
    assert s.ticket("T-0001.1")["status"] == "merged"
    assert roles_and_statuses(s) == [("implementer", "T-0001.1", "READY-FOR-REVIEW"),
                                     ("reviewer", "T-0001.1", "APPROVE"), ("verifier", "T-0001.1", "VERIFIED"),
                                     ("verifier", "T-0001", "VERIFIED")]
    # The fixture has no spec store, so the archive is refused and the parent parks, as under build.js.
    assert res == {"ticket": "T-0001", "state": "parked", "ok": True}
    assert s.ticket()["parked"]["reason"].startswith("archive: ")


def test_a_reviewer_still_asking_for_changes_at_the_round_limit_parks_the_subticket(tmp_path):
    s = BuildStore(tmp_path)
    cp, res = s.drive({**OK_PLAYS, "reviewer": [{"write": "REQUEST-CHANGES"}]}, "--phase", "build")
    assert cp.returncode == 0, cp.stderr
    assert res == {"ticket": "T-0001", "state": "planned", "ok": True}
    assert s.ticket("T-0001.1")["status"] == "parked"
    assert [r for r, _, _ in roles_and_statuses(s)] == ["implementer", "reviewer", "verifier"] * 2
    assert s.ticket("T-0001.1")["round"]["pr"] == 2


def test_two_empty_reviews_park_the_subticket_after_the_verifier_has_recorded(tmp_path):
    s = BuildStore(tmp_path)
    cp, res = s.drive({**OK_PLAYS, "reviewer": [{"say": ""}], "verifier": [{"write": "SPEC-DEFECT"}]},
                      "--phase", "build")
    assert cp.returncode == 0, cp.stderr
    assert res["state"] == "planned"
    assert s.ticket("T-0001.1")["parked"]["reason"] == "EMPTY-OUTPUT from reviewer"
    assert sorted(roles_and_statuses(s)) == sorted([
        ("implementer", "T-0001.1", "READY-FOR-REVIEW"), ("reviewer", "T-0001.1", "EMPTY-OUTPUT"),
        ("reviewer", "T-0001.1", "EMPTY-OUTPUT"), ("verifier", "T-0001.1", "SPEC-DEFECT")])


def test_a_blocked_implementer_parks_its_subticket(tmp_path):
    s = BuildStore(tmp_path)
    cp, res = s.drive({"implementer": [{"write": "BLOCKED"}]})  # no --phase: ready-for-planner selects build
    assert cp.returncode == 0, cp.stderr
    assert res == {"ticket": "T-0001", "state": "planned", "ok": True}
    assert s.ticket("T-0001.1")["parked"]["reason"] == "BLOCKED from implementer"
    assert len(s.calls()) == 1


def test_a_failed_checker_ends_the_pass_only_after_the_other_has_recorded(tmp_path):
    s = BuildStore(tmp_path)
    cp, res = s.drive({**OK_PLAYS, "reviewer": [{"fail": "usage limit reached"}],
                       "verifier": [{"sleep": 1, "write": "VERIFIED"}]}, "--phase", "build")
    assert cp.returncode == 0, cp.stderr
    assert s.ticket("T-0001.1")["parked"]["reason"] == "agent call failed: reviewer: usage limit reached"
    assert sorted(roles_and_statuses(s)) == sorted([
        ("implementer", "T-0001.1", "READY-FOR-REVIEW"), ("reviewer", "T-0001.1", "KILLED"),
        ("verifier", "T-0001.1", "VERIFIED")])
    rows = [yaml.safe_load(p.read_text()) for p in s.root.glob("results/*/*.yaml")]
    assert ("verifier", "VERIFIED") in [(r.get("role"), r.get("status")) for r in rows]
    assert s.ticket("T-0001.1")["in_flight"] == []


def test_the_implementer_gets_edit_and_its_worktree_and_the_checkers_only_their_run(tmp_path):
    s = BuildStore(tmp_path)
    cp, _ = s.drive(OK_PLAYS, "--phase", "build")
    assert cp.returncode == 0, cp.stderr
    tmp = os.path.realpath(tempfile.gettempdir())
    metas = {m["run_id"]: m for m in s.runs()}
    assert len(s.calls()) == 4
    for c in s.calls():
        run = os.path.realpath(c["cwd"])
        m = metas[os.path.basename(run)]
        opts = dict(zip(c["argv"][2::2], c["argv"][3::2]))
        assert c["dispatch"] is None and opts["--model"] == m["model"] and opts["--permission-mode"] == "auto"
        rules = [f"Edit(/{run}/output.md)", f"Edit(/{run}/scratch/**)", f"Edit(/{tmp}/**)"]
        if m["role"] == "implementer":
            wt = os.path.realpath(m["worktree"])
            assert opts["--tools"].split(",")[-1] == "Edit" and opts["--add-dir"] == wt
            rules.append(f"Edit(/{wt}/**)")
        else:
            assert "Edit" not in opts["--tools"].split(",") and "--add-dir" not in opts
        assert [r for r in opts["--allowedTools"].split(",") if r.startswith("Edit")] == rules


def test_the_checkers_run_at_once_and_subtickets_up_to_the_parallel_limit(tmp_path):
    plays = {"reviewer": [{"sleep": 1.5, "write": "APPROVE"}], "verifier": [{"sleep": 1.5, "write": "SPEC-DEFECT"}]}
    for name, extra, most in (("one", ("--parallel", "1"), 2), ("default", (), 4)):
        (tmp_path / name).mkdir()
        s = BuildStore(tmp_path / name)
        s.two_subtickets_at_checks()
        cp, res = s.drive(plays, "--phase", "build", *extra)
        assert cp.returncode == 0, cp.stderr
        assert len(s.calls()) == 4 and s.most_at_once() == most, name
        assert [s.ticket(f"T-0001.{i}")["parked"]["reason"] for i in (1, 2)] == ["SPEC-DEFECT from verifier"] * 2


def test_build_step_lines_and_the_status_file_name_the_subticket_in_flight(tmp_path):
    s = BuildStore(tmp_path)
    s.two_subtickets_at_checks()
    env = {**s.env, "STANDIN_PLAYS": json.dumps({"reviewer": [{"sleep": 2, "write": "APPROVE"}],
                                                 "verifier": [{"sleep": 2, "write": "SPEC-DEFECT"}]})}
    p = subprocess.Popen([str(BIN), "drive", "T-0001"], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True, env=env, cwd=REPO)
    status = s.root / "drive" / "T-0001.yaml"
    seen: list[tuple[str, str]] = []
    deadline = time.monotonic() + 30
    while p.poll() is None and time.monotonic() < deadline:
        if status.exists():
            running = (yaml.safe_load(status.read_text()) or {}).get("running") or []
            if len(running) > len(seen):
                seen = sorted((r["ticket"], r["role"]) for r in running)
        time.sleep(0.05)
    out, _ = p.communicate(timeout=30)
    assert p.returncode == 0
    assert seen == [("T-0001.1", "reviewer"), ("T-0001.1", "verifier"),
                    ("T-0001.2", "reviewer"), ("T-0001.2", "verifier")]
    lines = out.strip().splitlines()
    assert all(ln.startswith(('T-0001 "Fixture": ', 'T-0001.1 "One": ', 'T-0001.2 "Two": ')) for ln in lines[:-1])
    assert 'T-0001.2 "Two": parked: SPEC-DEFECT from verifier' in lines
    assert json.loads(lines[-1])["state"] == "planned"
    assert yaml.safe_load(status.read_text())["running"] == []


def test_a_stop_during_the_checkers_kills_both_and_a_rerun_resumes_the_subticket(tmp_path):
    s = BuildStore(tmp_path)
    env = {**s.env, "STANDIN_PLAYS": json.dumps({**OK_PLAYS, "reviewer": [{"sleep": 60, "write": "APPROVE"}],
                                                 "verifier": [{"sleep": 60, "write": "VERIFIED"}]})}
    p = subprocess.Popen([str(BIN), "drive", "T-0001"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, env=env, cwd=REPO)
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline and len(s.calls()) < 3:
        time.sleep(0.05)
    time.sleep(0.5)
    p.send_signal(signal.SIGTERM)
    out, _ = p.communicate(timeout=30)
    assert p.returncode == 128 + signal.SIGTERM
    assert json.loads(out.strip().splitlines()[-1]) == {"ok": False, "ticket": "T-0001", "stopped": "SIGTERM"}
    assert sorted(roles_and_statuses(s))[1:] == [("reviewer", "T-0001.1", "KILLED"), ("verifier", "T-0001.1", "KILLED")]
    sub = s.ticket("T-0001.1")
    assert (sub["status"], sub["in_flight"], sub["parked"]) == ("checks-in-flight", [], None)
    cp, res = s.drive(OK_PLAYS)  # no --phase: planned selects build; both checkers re-run on the same head
    assert cp.returncode == 0, cp.stderr
    assert s.ticket("T-0001.1")["status"] == "merged" and len(s.calls()) == 6
