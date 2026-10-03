"""A killed checker, recorded the way the build loop records it, parks as a budget kill.

build.js marks a run KILLED when the agent returns nothing (`build.js` runRole: `run finish
--status-override KILLED`, then `run cleanup`), and records every checker with
`results record ... --output <the run's output.md> --run <id>`, adding `--killed` for a killed
run. A killed run never wrote that output file. The shepherd's own killed path records without
`--output`, so this test drives the build loop's call shape directly.
"""
from __future__ import annotations

import pytest

from .test_shepherd import built_to_implementer


@pytest.mark.parametrize("role", ["verifier", "reviewer"])
def test_a_killed_checker_recorded_with_its_missing_output_parks_as_a_budget_kill(tmp_path, role):
    f, tid, (st,) = built_to_implementer(tmp_path)
    f.dispatch("implementer", st)
    other = "reviewer" if role == "verifier" else "verifier"
    f.dispatch(other, st)
    assert f.last_join["decision"] == "wait"  # the killed checker has not reported yet

    head = f.ok("ticket", "head", st)["head"]
    rid = f.ok("run", "start", "--role", role, "--ticket", st)["run_id"]
    f.ok("run", "compose", rid)
    assert f.ok("run", "finish", rid, "--status-override", "KILLED")["status"] == "KILLED"
    f.ok("run", "cleanup", rid)
    output = f.store / "runs" / rid / "output.md"
    assert not output.exists()  # a killed run wrote no output
    f.ok("results", "record", st, "--head", head, "--role", role, "--output", str(output), "--run", rid, "--killed")
    f.act_on_join(st, rid)

    assert f.results(st)[role] == "KILLED"
    assert f.state(st) == "parked" and f.ticket(st)["parked"]["reason"] == f"budget kill: {role}"
