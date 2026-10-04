"""A spec that needs one sub-ticket becomes that sub-ticket without a planner run (T-0028 part B).

`factory plan whole-spec PARENT`, on a parent at ready-for-planner with an approved spec, creates
`<parent>.1` from the whole spec when the parent has no sub-ticket and no earlier planner run, its
latest spec-writer run did not end NEEDS-SPLIT, and its approved spec has no `##` or `###` heading
naming seams. Otherwise it reports `"planner": "needed"` and writes nothing. It refuses where a
planner run would. The one sub-ticket names every scenario, so the parent closes on its VERIFIED run.

Black-box through `bin/factory` on a throwaway store, as the spec's t0028-plan.sh fixture builds it;
the parent-close case uses the Shepherd fixture of test_parent_close_reuse.py.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from .test_parent_close_reuse import _build, _parent_verifier_runs
from .test_shepherd import Shepherd

REPO = Path(__file__).resolve().parents[2]
BIN = REPO / "bin" / "factory"
REASON = "one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run"
SPEC_WRITER_OUTPUT = """=== proposal.md
## Problem
x
=== design.md
## Proposed change
A. Do x.
{extra}
=== specs/demo/spec.md
## ADDED Requirements
### Requirement: X
It SHALL do x.
#### Scenario: First check
- WHEN `true`
- THEN it exits 0
#### Scenario: Second check
- WHEN `true`
- THEN it exits 0
=== verification.md
## Acceptance
- First check → NEW; fails today
- Second check → REGRESSION
STATUS: {status}
CONFIDENCE: high, fixture
ESCALATIONS: none
"""


class Parent:
    """T-0001 at ready-for-planner: one spec-writer run ending `status`, its output approved as v1."""

    def __init__(self, tmp_path: Path, status: str = "READY-FOR-CRITIC", extra: str = "", spec_store: bool = False):
        self.tmp = tmp_path
        self.root = tmp_path / "store"
        repo = tmp_path / "t"
        self.env = {**os.environ, "FACTORY_STATE": str(self.root), "FACTORY_REPO": str(repo),
                    "FACTORY_INTEGRATION_BRANCH": "main", "PYTHONDONTWRITEBYTECODE": "1"}
        subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "-c", "user.email=f@x", "-c", "user.name=f", "commit", "-q",
                        "--allow-empty", "-m", "init"], check=True)
        if spec_store:
            self.ok("init")
        (tmp_path / "req.md").write_text("# F\n\nDo x.\n")
        self.ok("ticket", "new", "--file", str(tmp_path / "req.md"))
        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
        w = self.ok("run", "start", "--role", "spec_writer", "--ticket", "T-0001")["run_id"]
        (self.root / "runs" / w / "output.md").write_text(SPEC_WRITER_OUTPUT.format(status=status, extra=extra))
        self.ok("run", "finish", w)
        self.ok("spec", "add", "T-0001", "--from-run", w)
        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
        self.ok("ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t")
        self.ok("approve-spec", "T-0001")

    def cli(self, *argv: str) -> subprocess.CompletedProcess:
        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)

    def ok(self, *argv: str) -> dict:
        cp = self.cli(*argv)
        assert cp.returncode == 0, f"{' '.join(argv)}: {cp.stderr}"
        return json.loads(cp.stdout.strip().splitlines()[-1])

    def tickets(self) -> list[str]:
        return sorted(p.name for p in (self.root / "tickets").iterdir())

    def events(self, name: str) -> list[dict]:
        return [e for p in sorted((self.root / "log").glob("*.jsonl")) for ln in p.read_text().splitlines()
                if (e := json.loads(ln))["event"] == name]

    def snapshot(self) -> dict[str, bytes]:
        return {str(p.relative_to(self.root)): p.read_bytes() for p in sorted(self.root.rglob("*")) if p.is_file()}


def test_a_qualifying_spec_becomes_one_ready_sub_ticket_naming_every_scenario(tmp_path):
    t = Parent(tmp_path)
    r = t.ok("plan", "whole-spec", "T-0001")
    assert r["planner"] == "skipped" and r["reason"] == REASON
    assert r["subtickets"] == [{"id": "T-0001.1", "label": "whole-spec", "state": "ready-for-implementer",
                                "depends_on": [], "parallel_safe": True}]
    assert t.tickets() == ["T-0001.1.yaml", "T-0001.yaml"]
    sub = yaml.safe_load((t.root / "tickets" / "T-0001.1.yaml").read_text())
    assert sub["type"] == "sub-ticket" and sub["parent"] == "T-0001" and sub["source"] == "plan:whole-spec"
    assert sub["spec"] == {"version": 1, "approved_version": 1}
    text = (t.root / "specs" / "T-0001.1" / "subticket.md").read_text()
    assert text.startswith("T-0001.1 / F\nDepends on: none\nParallel-safe: yes\n\n")
    assert "\n- First check\n- Second check\n" in text and REASON in text
    parent = yaml.safe_load((t.root / "tickets" / "T-0001.yaml").read_text())
    assert parent["plan"] == "plans/T-0001.md" and (t.root / "plans" / "T-0001.md").read_text() == text
    assert parent["status"] == "ready-for-planner", "the build moves the parent to planned, not this command"
    assert t.ok("ticket", "ready-implementers", "T-0001")["ready"] == ["T-0001.1"]
    (skip,) = t.events("plan.skipped")
    assert skip["ticket"] == "T-0001" and skip["subticket"] == "T-0001.1" and skip["reason"] == REASON
    assert not (t.root / "openspec").exists() and t.events("tasks.written") == []


def test_with_a_spec_store_the_text_is_also_the_change_folder_s_tasks(tmp_path):
    t = Parent(tmp_path, spec_store=True)
    t.ok("plan", "whole-spec", "T-0001")
    tasks = t.root / "openspec" / "changes" / "T-0001" / "tasks.md"
    assert tasks.read_text() == (t.root / "specs" / "T-0001.1" / "subticket.md").read_text()
    assert [e["ticket"] for e in t.events("tasks.written")] == ["T-0001"]


def test_a_missing_change_folder_under_a_spec_store_is_refused_as_spec_tasks_words_it(tmp_path):
    t = Parent(tmp_path, spec_store=True)
    shutil.rmtree(t.root / "openspec" / "changes" / "T-0001")
    before = t.snapshot()
    cp = t.cli("plan", "whole-spec", "T-0001")
    assert cp.returncode == 2 and "T-0001 has no change folder (no pinned version)" in cp.stderr
    assert t.snapshot() == before


@pytest.mark.parametrize(("status", "extra", "reason"), [
    ("NEEDS-SPLIT", "", "its spec writer marked it NEEDS-SPLIT"),
    ("READY-FOR-CRITIC", "### Size and seams", "its approved spec has a seam heading: ### Size and seams"),
    ("READY-FOR-CRITIC", "## Seam: the store", "its approved spec has a seam heading: ## Seam: the store"),
    ("READY-FOR-CRITIC", "## The SEAMS here", "its approved spec has a seam heading"),
])
def test_a_split_spec_needs_the_planner_and_nothing_is_written(tmp_path, status, extra, reason):
    t = Parent(tmp_path, status, extra)
    before = t.snapshot()
    r = t.ok("plan", "whole-spec", "T-0001")
    assert r["planner"] == "needed" and r["reason"].startswith(reason)
    assert t.snapshot() == before


@pytest.mark.parametrize("extra", ["#### Seams in a scenario-level heading", "```\n## Size and seams\n```",
                                   "## Seamstress", "Seams named in prose"])
def test_a_seam_word_that_is_no_seam_heading_still_skips_the_planner(tmp_path, extra):
    t = Parent(tmp_path, extra=extra)
    assert t.ok("plan", "whole-spec", "T-0001")["planner"] == "skipped"


def test_a_requirement_line_naming_seams_is_no_seam_heading(tmp_path):
    t = Parent(tmp_path)
    spec = t.root / "specs" / "T-0001" / "v1.md"
    spec.write_text(spec.read_text().replace("### Requirement: X", "### Requirement: X keeps its seams"))
    assert t.ok("plan", "whole-spec", "T-0001")["planner"] == "skipped"


def test_a_parent_a_planner_already_ran_on_needs_the_planner(tmp_path):
    t = Parent(tmp_path)
    p = t.ok("run", "start", "--role", "planner", "--ticket", "T-0001")["run_id"]
    t.ok("run", "finish", p, "--status-override", "ESCALATE")
    before = t.snapshot()
    r = t.ok("plan", "whole-spec", "T-0001")
    assert r == {"ok": True, "id": "T-0001", "planner": "needed", "reason": f"a planner already ran on it: {p}"}
    assert t.snapshot() == before


def test_a_parent_with_a_sub_ticket_needs_the_planner(tmp_path):
    t = Parent(tmp_path)
    (tmp_path / "plan.md").write_text("ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n")
    t.ok("subticket", "add", "T-0001", "--file", str(tmp_path / "plan.md"))
    r = t.ok("plan", "whole-spec", "T-0001")
    assert r["planner"] == "needed" and r["reason"] == "it already has sub-tickets: T-0001.1"
    assert t.tickets() == ["T-0001.1.yaml", "T-0001.yaml"]


def test_a_parent_not_ready_for_its_planner_is_refused(tmp_path):
    t = Parent(tmp_path)
    t.ok("ticket", "transition", "T-0001", "--to", "planned", "--by", "t")
    before = t.snapshot()
    cp = t.cli("plan", "whole-spec", "T-0001")
    assert cp.returncode == 2 and "T-0001 is planned, not ready-for-planner" in cp.stderr
    assert t.snapshot() == before


def test_a_parent_with_a_run_in_flight_is_refused(tmp_path):
    t = Parent(tmp_path)
    p = t.ok("run", "start", "--role", "planner", "--ticket", "T-0001")["run_id"]
    before = t.snapshot()
    cp = t.cli("plan", "whole-spec", "T-0001")
    assert cp.returncode == 2 and f"T-0001 already has run {p} in flight" in cp.stderr
    assert t.snapshot() == before


def test_a_parent_with_no_approved_spec_is_refused(tmp_path):
    t = Parent(tmp_path)
    t.ok("ticket", "set", "T-0001", "spec.approved_version=")
    before = t.snapshot()
    cp = t.cli("plan", "whole-spec", "T-0001")
    assert cp.returncode == 2 and "T-0001 has no approved spec" in cp.stderr
    assert t.snapshot() == before


def test_the_whole_spec_sub_ticket_s_verified_run_closes_the_parent(tmp_path):
    """Part C's rule, reached without a planner: one sub-ticket naming every scenario, merged with a
    VERIFIED run on the parent's base, stands for the parent-close run."""
    f = Shepherd(tmp_path, case="accept-approve", with_repo=True)
    f.human_runs("init")
    tid = f.request("# SPEC-99: Fixture\n\nThe bot should do the thing.\n")
    for role in ("triage", "spec_writer", "critic"):
        f.dispatch(role, tid)
    f.human_approves(tid)
    (st,) = [s["id"] for s in f.ok("plan", "whole-spec", tid)["subtickets"]]
    f.ok("ticket", "transition", tid, "--to", "planned", "--by", "workflow")
    assert not list((f.store / "runs").glob("*-planner"))
    ver = _build(f, st)
    pc = f.ok("ticket", "parent-check", tid)
    assert pc["state"] == "ready-for-parent-verify" and pc["reuse"] == ver.run_id
    assert _parent_verifier_runs(f, tid) == []
