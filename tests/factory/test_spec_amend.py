"""`factory spec amend` (T-0027 part A): a human amends a pinned spec whose intent is unchanged.
The amended version becomes the approved one, the change folder is re-pinned with the planner's
tasks.md kept, sub-tickets neither merged nor closed move to it, and the amendment is recorded under
approvals/ and logged. Each refusal exits 2 and writes nothing.

Each case builds the spec's t0027-amend.sh fixture: a throwaway store with a spec store
(FACTORY_STATE) and a scratch target repository (FACTORY_REPO). T-0001's v1 is approved; its one
requirement "Greets" has one scenario, "Greeting is printed", running `echo hi`. v2 changes only that
scenario; v3 also changes the Decisions line.
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

SPEC = """=== proposal.md
## Problem
{problem}
## Decisions
- {decision}
=== design.md
## Proposed change
Edit `src/greet.py`.
## Tests to change
none
=== specs/demo/spec.md
## ADDED Requirements
### Requirement: Greets
{statement}

#### Scenario: Greeting is printed
- WHEN `{cmd}`
- THEN it prints `{out}`
{extra}=== verification.md
## Acceptance
- Greeting is printed → NEW
{labels}"""

TWO = "ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: none\nParallel-safe: yes\n"


def spec(decision="Greet by default.", cmd="echo hi", out="hi", problem="x", statement="The tool SHALL greet.",
         extra="", labels="") -> str:
    return SPEC.format(decision=decision, cmd=cmd, out=out, problem=problem, statement=statement, extra=extra,
                       labels=labels)


V1, V2 = spec(), spec(cmd="echo hello", out="hello")


class Fixture:
    def __init__(self, tmp_path: Path):
        self.tmp = tmp_path
        self.store = tmp_path / "store"
        self.target = tmp_path / "t"
        self.env = {**os.environ, "FACTORY_STATE": str(self.store), "FACTORY_REPO": str(self.target),
                    "FACTORY_INTEGRATION_BRANCH": "main", "PYTHONDONTWRITEBYTECODE": "1"}

    def cli(self, *argv: str) -> subprocess.CompletedProcess:
        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)

    def ok(self, *argv: str) -> dict:
        cp = self.cli(*argv)
        assert cp.returncode == 0, cp.stderr
        return json.loads(cp.stdout.strip().splitlines()[-1])

    def file(self, name: str, text: str) -> str:
        p = self.tmp / name
        p.write_text(text)
        return str(p)

    def ticket(self, tid: str) -> dict:
        return yaml.safe_load((self.store / "tickets" / f"{tid}.yaml").read_text())

    def plan(self, text: str = TWO) -> None:
        self.ok("subticket", "add", "T-0001", "--file", self.file("plan.md", text))
        self.ok("ticket", "transition", "T-0001", "--to", "planned", "--by", "t")

    def amend(self, text: str, reason: str = "Seed the greeting.", intent: str = "unchanged",
              tid: str = "T-0001") -> subprocess.CompletedProcess:
        return self.cli("spec", "amend", tid, "--file", self.file("amend.md", text), "--reason", reason,
                        "--intent", intent)

    def snapshot(self) -> dict[str, bytes]:
        return {str(p.relative_to(self.store)): p.read_bytes() for p in sorted(self.store.rglob("*")) if p.is_file()}

    def change(self, rel: str) -> Path:
        return self.store / "openspec" / "changes" / "T-0001" / rel


@pytest.fixture
def f(tmp_path: Path) -> Fixture:
    f = Fixture(tmp_path)
    subprocess.run(["git", "init", "-q", "-b", "main", str(f.target)], check=True)
    for rel in ("src/greet.py", "src/other.py"):
        (f.target / rel).parent.mkdir(parents=True, exist_ok=True)
        (f.target / rel).write_text(f"# {rel}\n")
    subprocess.run(["git", "-C", str(f.target), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(f.target), "-c", "user.email=f@x", "-c", "user.name=f", "commit", "-qm", "land"],
                   check=True)
    f.ok("init")
    f.ok("ticket", "new", "--file", f.file("req.md", "# Fixture\n\nGreet.\n"))
    f.ok("ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
    f.ok("spec", "add", "T-0001", "--file", f.file("v1.md", V1))
    f.ok("ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
    f.ok("ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t")
    f.ok("approve-spec", "T-0001")
    return f


def refused(f: Fixture, cp: subprocess.CompletedProcess, before: dict[str, bytes]) -> str:
    """Assert a refusal that wrote nothing; return its error."""
    assert cp.returncode == 2, cp.stdout + cp.stderr
    res = json.loads(cp.stdout.strip().splitlines()[-1])
    assert res["ok"] is False
    assert f.snapshot() == before
    return res["error"]


# ----- the writes ---------------------------------------------------------------------------

def test_amendment_repins_keeps_tasks_and_moves_unmerged_subtickets(f):
    f.plan()
    f.ok("ticket", "set", "T-0001.1", "status=merged")
    f.change("tasks.md").write_text("planner tasks\n")
    cp = f.amend(V2)
    assert cp.returncode == 0, cp.stderr
    assert json.loads(cp.stdout.strip().splitlines()[-1]) == {
        "ok": True, "id": "T-0001", "version": 2, "record": "approvals/T-0001/amendment-1.md"}
    parent = f.ticket("T-0001")
    assert parent["spec"] == {"version": 2, "approved_version": 2}
    assert parent["status"] == "planned"  # an amendment changes no ticket state
    assert (f.store / "specs" / "T-0001" / "v2.md").read_text() == V2
    assert "echo hello" in f.change("specs/demo/spec.md").read_text()
    assert f.change("tasks.md").read_text() == "planner tasks\n"
    assert "## Critic rounds" in f.change("verification.md").read_text()  # re-pinned as the gate pins
    first, second = f.ticket("T-0001.1"), f.ticket("T-0001.2")
    assert first["status"] == "merged" and first["spec"] == {"version": 1, "approved_version": 1}
    assert second["spec"] == {"version": 2, "approved_version": 2}
    assert first["planned_from"] == second["planned_from"] == 1
    assert not list((f.store / "approvals" / "T-0001").glob("spec-v2*"))  # no gate approval file


def test_amendment_without_tasks_md_writes_none(f):
    assert f.amend(V2).returncode == 0
    assert not f.change("tasks.md").exists()


def test_record_lists_changed_scenarios_merged_subtickets_reason_and_diff(f):
    f.plan()
    f.ok("ticket", "set", "T-0001.1", "status=merged")
    v = spec(cmd="echo hello", out="hello",
             extra="\n#### Scenario: Waves\n- WHEN `echo wave`\n- THEN it prints `wave`\n",
             labels="- Waves → NEW\n")
    assert f.amend(v).returncode == 0
    rec = (f.store / "approvals" / "T-0001" / "amendment-1.md").read_text()
    lines = rec.splitlines()
    assert lines[0] == "# T-0001: spec amended, v1 to v2"
    assert lines[2].startswith("By ") and "Reason: Seed the greeting." in lines and "Intent: unchanged" in lines
    scen = rec.split("## Scenarios changed\n\n")[1].split("\n\n")[0]
    assert scen == "- changed: Greeting is printed\n- added: Waves"
    merged = rec.split("## Sub-tickets merged before this amendment\n\n")[1].split("\n\n")[0]
    assert merged == "- T-0001.1 / First: merged"
    diff = rec.split("## Diff\n\n")[1]
    assert diff.startswith("```diff\n--- specs/T-0001/v1.md\n+++ specs/T-0001/v2.md\n")
    assert "-- WHEN `echo hi`" in diff and "+- WHEN `echo hello`" in diff and diff.endswith("\n```\n")
    ev = [json.loads(ln) for ln in f.cli("log", "tail", "--event", "spec.amended").stdout.splitlines()]
    assert len(ev) == 1
    assert {k: ev[0][k] for k in ("ticket", "previous", "version", "reason", "record")} == {
        "ticket": "T-0001", "previous": 1, "version": 2, "reason": "Seed the greeting.",
        "record": "approvals/T-0001/amendment-1.md"}
    assert ev[0]["by"]


def test_record_with_no_merged_subtickets_and_removed_scenario_says_so(f):
    f.amend(spec(extra="\n#### Scenario: Waves\n- WHEN `echo wave`\n- THEN it prints `wave`\n",
                 labels="- Waves → NEW\n"))
    assert f.amend(V1, reason="Drop the wave.").returncode == 0
    rec = (f.store / "approvals" / "T-0001" / "amendment-2.md").read_text()
    assert "## Scenarios changed\n\n- removed: Waves\n\n" in rec
    assert "## Sub-tickets merged before this amendment\n\nnone\n\n" in rec


def test_record_number_follows_a_hand_written_amendment(f):
    (f.store / "approvals" / "T-0001" / "amendment-1.md").write_text("hand-written\n")
    assert json.loads(f.amend(V2).stdout.strip().splitlines()[-1])["record"] == "approvals/T-0001/amendment-2.md"
    assert (f.store / "approvals" / "T-0001" / "amendment-1.md").read_text() == "hand-written\n"


def test_later_implementer_run_receives_the_amended_spec(f):
    f.plan()
    assert f.amend(V2).returncode == 0
    rid = f.ok("run", "start", "--role", "implementer", "--ticket", "T-0001.2")["run_id"]
    f.ok("run", "compose", rid)
    text = (f.store / "runs" / rid / "input.md").read_text()
    assert "Parent spec (v2, pinned)" in text and "echo hello" in text and "`echo hi`" not in text
    assert yaml.safe_load((f.store / "runs" / rid / "meta.yaml").read_text())["spec_version"] == 2


def test_archive_after_amendment_writes_the_amended_scenario(f):
    assert f.amend(V2).returncode == 0
    f.ok("archive", "T-0001")
    truth = (f.store / "openspec" / "specs" / "demo" / "spec.md").read_text()
    assert "echo hello" in truth and "`echo hi`" not in truth


# ----- the refusals, in order -----------------------------------------------------------------

def test_subticket_is_refused_naming_the_parent(f):
    f.plan()
    before = f.snapshot()
    assert "spec amend T-0001" in refused(f, f.amend(V2, tid="T-0001.1"), before)


def test_ticket_with_no_approved_version_is_refused(f):
    f.ok("ticket", "new", "--file", f.file("req2.md", "# Second\n\nWave.\n"))
    before = f.snapshot()
    assert "no approved spec" in refused(f, f.amend(V2, tid="T-0002"), before)


def test_ticket_at_the_gate_is_pointed_to_approve_spec_edit(f):
    f.ok("ticket", "park", "T-0001", "--reason", "x")
    f.ok("resolve", "T-0001", "--to", "spec-gate")
    before = f.snapshot()
    assert "approve-spec T-0001 --edit" in refused(f, f.amend(V2), before)


def test_closed_ticket_is_refused(f):
    f.ok("ticket", "set", "T-0001", "status=closed")
    before = f.snapshot()
    assert "closed" in refused(f, f.amend(V2), before)


@pytest.mark.parametrize("reason", ["", "   ", "two\nlines"])
def test_reason_that_is_not_one_line_is_refused(f, reason):
    before = f.snapshot()
    assert "--reason" in refused(f, f.amend(V2, reason=reason), before)


def test_run_in_flight_on_a_subticket_is_refused_naming_it(f):
    f.plan("ST-1 / First\nDepends on: none\nParallel-safe: yes\n")
    rid = f.ok("run", "start", "--role", "implementer", "--ticket", "T-0001.1")["run_id"]
    before = f.snapshot()
    assert rid in refused(f, f.amend(V2), before)


def test_run_in_flight_on_the_parent_is_refused_naming_it(f):
    rid = f.ok("run", "start", "--role", "planner", "--ticket", "T-0001")["run_id"]
    before = f.snapshot()
    assert rid in refused(f, f.amend(V2), before)


def test_intent_changed_is_refused_with_the_restart_note(f):
    f.plan()
    f.ok("ticket", "set", "T-0001.1", "status=merged", "merge.main_after=0123456789abcdef")
    f.ok("ticket", "set", "T-0001.2", "branch=factory/T-0001.2")
    before = f.snapshot()
    err = refused(f, f.amend(V2, intent="changed"), before)
    assert err.startswith("intent changed: ") and "Decisions line" not in err
    assert "Restart instead of amending." in err
    assert "T-0001.1 / First (merge 012345678)" in err
    assert "T-0001.2 / Second: ready-for-implementer, branch factory/T-0001.2" in err
    for cmd in ("factory ticket park T-0001", "factory resolve T-0001 --to spec-gate",
                "factory approve-spec T-0001 --edit F", "factory resolve T-0001 --close", "factory ticket new"):
        assert cmd in err


def test_restart_note_with_no_subtickets_says_none(f):
    err = refused(f, f.amend(V2, intent="changed"), f.snapshot())
    assert "integration branch: none." in err and "a restart discards: none." in err


def test_closed_subticket_is_left_out_of_the_restart_note(f):
    f.plan()
    f.ok("ticket", "set", "T-0001.2", "status=closed")
    err = refused(f, f.amend(V2, intent="changed"), f.snapshot())
    assert "T-0001.2" not in err and "T-0001.1 / First: ready-for-implementer" in err


@pytest.mark.parametrize("version, change", [
    (spec(decision="Greet only when asked."), "Decisions line removed: Greet by default.; "
                                              "Decisions line added: Greet only when asked."),
    (spec(problem="y"), "the Problem section"),
    (spec(statement="The tool SHALL wave."), "requirement restated: demo ADDED Greets"),
])
def test_intent_found_changed_is_refused_naming_each_change(f, version, change):
    before = f.snapshot()
    err = refused(f, f.amend(version), before)
    assert err.startswith(f"intent changed ({change}). --intent unchanged keeps")
    assert "Restart instead of amending." in err


def test_archived_change_is_refused(f):
    assert f.amend(V2).returncode == 0
    f.ok("archive", "T-0001")
    before = f.snapshot()
    assert "archived" in refused(f, f.amend(V1, reason="Too late."), before)


def test_malformed_amendment_is_refused_with_the_validator_error(f):
    before = f.snapshot()
    err = refused(f, f.amend(V2.replace("- Greeting is printed → NEW\n", "")), before)
    assert err.startswith("spec not amended: ") and "has no NEW/REGRESSION label" in err


def test_amendment_whose_delta_does_not_apply_is_refused(f):
    truth = f.store / "openspec" / "specs" / "demo" / "spec.md"
    truth.parent.mkdir(parents=True)
    truth.write_text("# demo\n\n## Requirements\n\n### Requirement: Greets\nOld.\n")
    before = f.snapshot()
    err = refused(f, f.amend(V2), before)
    assert "ADDED 'Greets' is already in current truth (demo)" in err


# ----- the intent check -----------------------------------------------------------------------

def test_scenarios_whitespace_design_and_tests_to_change_keep_intent(f):
    v = V1.replace("Edit `src/greet.py`.", "Edit `src/greet.py` and `src/other.py`.").replace(
        "## Tests to change\nnone", "## Tests to change\n- `tests/test_greet.py`").replace(
        "The tool SHALL greet.", "The   tool\nSHALL greet.  ").replace("echo hi", "echo hello")
    cp = f.amend(v)
    assert cp.returncode == 0, cp.stdout


def test_requirement_added_removed_and_operation_changed_are_named(f):
    renamed = V1.replace("### Requirement: Greets", "### Requirement: Says hello")
    assert "intent changed (requirement removed: demo ADDED Greets; requirement added: demo ADDED Says hello)" \
        in refused(f, f.amend(renamed), f.snapshot())
    moved = V1.replace("## ADDED Requirements", "## MODIFIED Requirements")
    assert "intent changed (requirement removed: demo ADDED Greets; requirement added: demo MODIFIED Greets)" \
        in refused(f, f.amend(moved), f.snapshot())


def test_scenario_heading_inside_a_fence_is_not_a_scenario(f):
    assert f.amend(spec(extra="\n```\n#### Scenario: Not one\n```\n")).returncode == 0
    rec = (f.store / "approvals" / "T-0001" / "amendment-1.md").read_text()
    assert "## Scenarios changed\n\n- changed: Greeting is printed\n\n" in rec
    assert "## Diff\n\n````diff\n" in rec and rec.endswith("\n````\n")  # the spec's own ``` stays inside
