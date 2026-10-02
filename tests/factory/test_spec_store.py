"""Spec store (doc §Harness, Spec store; build spec part B "Spec store", K, items 88–90) and the
compose additions from spec-factory T-0003 and T-0008, black-box through `bin/factory`."""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
BIN = REPO / "bin" / "factory"
TRAILER = "\nSTATUS: {s}\nCONFIDENCE: high, fixture\nESCALATIONS: none\n"


def run(store: Path, *argv: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "FACTORY_STATE": str(store), "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)


def js(cp):
    return json.loads(cp.stdout.strip().splitlines()[-1])


def meta(store: Path, rid: str) -> dict:
    return yaml.safe_load((store / "runs" / rid / "meta.yaml").read_text())


def finish(store: Path, rid: str, body: str, status: str) -> None:
    (store / "runs" / rid / "output.md").write_text(body + TRAILER.format(s=status))
    assert run(store, "run", "finish", rid).returncode == 0


@pytest.fixture
def store(tmp_path: Path) -> Path:
    s = tmp_path / "state"
    req = tmp_path / "r.md"
    req.write_text("# SPEC-99: Fixture\n\nThe bot should do the thing.\n")
    assert run(s, "ticket", "new", "--file", str(req)).returncode == 0
    assert run(s, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t").returncode == 0
    return s


def writer_run(store: Path) -> str:
    rid = js(run(store, "run", "start", "--role", "spec_writer", "--ticket", "T-0001"))["run_id"]
    assert run(store, "run", "compose", rid).returncode == 0
    return rid


# ----- compose: current truth, and the asker's previous output (T-0003) --------------------

def test_writer_and_critic_receive_current_truth_as_input_sources(store):
    (store / "openspec" / "specs" / "status-parser").mkdir(parents=True)
    (store / "openspec" / "specs" / "status-parser" / "spec.md").write_text(
        "# status-parser\n\n## Requirements\n\n### Requirement: trailer-read\nThe parser SHALL read labels.\n")
    rid = writer_run(store)
    assert "### Requirement: trailer-read" in (store / "runs" / rid / "input.md").read_text()
    assert meta(store, rid)["input_sources"] == ["requests/T-0001.md", "openspec/specs/status-parser/spec.md"]
    finish(store, rid, "=== proposal.md\n## Problem\nx\n", "READY-FOR-CRITIC")
    run(store, "spec", "add", "T-0001", "--from-run", rid)
    run(store, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
    cid = js(run(store, "run", "start", "--role", "critic", "--ticket", "T-0001"))["run_id"]
    run(store, "run", "compose", cid)
    assert meta(store, cid)["input_sources"] == ["specs/T-0001/v1.md", "openspec/specs/status-parser/spec.md"]


def test_first_writer_run_has_no_current_truth_and_no_earlier_output_when_store_is_empty(store):
    rid = writer_run(store)
    assert meta(store, rid)["input_sources"] == ["requests/T-0001.md"]


def test_writer_re_run_after_an_answer_gets_its_own_previous_output(store, tmp_path):
    rid = writer_run(store)
    finish(store, rid, "## Problem\ndraft\n## Open questions\n- A or B?\n", "NEEDS-HUMAN")
    run(store, "spec", "add", "T-0001", "--from-run", rid)
    assert run(store, "ticket", "park", "T-0001", "--reason", "NEEDS-HUMAN from spec writer", "--outputs", rid).returncode == 0
    ans = tmp_path / "ans.md"
    ans.write_text("B.\n")
    assert run(store, "resolve", "T-0001", "--answer", str(ans)).returncode == 0
    wid = writer_run(store)
    inp = (store / "runs" / wid / "input.md").read_text()
    assert "B." in inp and "- A or B?" in inp
    assert f"runs/{rid}/output.md" in meta(store, wid)["input_sources"]


def test_writer_round_2_after_critic_does_not_get_a_previous_output_section(store):
    rid = writer_run(store)
    finish(store, rid, "## Problem\nv1\n", "READY-FOR-CRITIC")
    run(store, "spec", "add", "T-0001", "--from-run", rid)
    run(store, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
    cid = js(run(store, "run", "start", "--role", "critic", "--ticket", "T-0001"))["run_id"]
    run(store, "run", "compose", cid)
    finish(store, cid, "[BLOCKING] 2 x\n", "REVISE")
    run(store, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t", "--round", "spec:+1")
    wid = writer_run(store)
    assert f"runs/{rid}/output.md" not in meta(store, wid)["input_sources"]


# ----- spec store: init, pin at the gate, tasks, archive (build items 88–90) -------------------

FOUR_PART = """=== proposal.md
## Problem
The parser parks valid verdicts.
## Decisions
- Trailer read by labels.
- none-plus-prose routes as none.
## Risk
none
=== design.md
## Proposed change
A. Read labels.
=== specs/status-parser/spec.md
## ADDED Requirements
### Requirement: trailer-read
The parser SHALL read the trailer by its labels.
#### Scenario: wrapped confidence
- WHEN `factory status parse t.md`
- THEN status is NEEDS-HUMAN
=== verification.md
## Acceptance
- wrapped confidence → NEW; today it parks
## Responses
none
"""


def to_gate(store: Path, text: str, n_critics: int = 1) -> None:
    rid = writer_run(store)
    finish(store, rid, text, "READY-FOR-CRITIC")
    run(store, "spec", "add", "T-0001", "--from-run", rid)
    run(store, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
    for _ in range(n_critics):
        cid = js(run(store, "run", "start", "--role", "critic", "--ticket", "T-0001"))["run_id"]
        run(store, "run", "compose", cid)
        finish(store, cid, "[NIT] 2 wording\n", "APPROVE")
    run(store, "ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t")


def log_text(store: Path) -> str:
    return "".join(p.read_text() for p in (store / "log").glob("*.jsonl"))


def test_init_creates_the_tree_and_is_idempotent(store):
    cp = run(store, "init")
    assert cp.returncode == 0, cp.stderr
    assert (store / "openspec" / "config.yaml").read_text() == "schema: spec-factory\n"
    assert "name: spec-factory" in (store / "openspec" / "schemas" / "spec-factory" / "schema.yaml").read_text()
    assert (store / "openspec" / "specs").is_dir() and (store / "decisions.md").read_text() == ""
    assert run(store, "init").returncode == 0 and js(run(store, "init"))["written"] == []


def test_item_88_gate_writes_the_change_folder_with_critic_rounds(store):
    run(store, "init")
    to_gate(store, FOUR_PART)
    cp = run(store, "approve-spec", "T-0001", "--version", "1")
    assert cp.returncode == 0, cp.stderr
    d = store / "openspec" / "changes" / "T-0001"
    assert sorted(str(p.relative_to(d)) for p in d.rglob("*") if p.is_file()) == [
        "design.md", "proposal.md", "specs/status-parser/spec.md", "verification.md"]
    assert (d / "design.md").read_text() == "## Proposed change\nA. Read labels.\n"
    assert (d / "specs" / "status-parser" / "spec.md").read_text().startswith("## ADDED Requirements\n### Requirement: trailer-read")
    v = (d / "verification.md").read_text()
    assert v.startswith("## Acceptance\n- wrapped confidence → NEW; today it parks\n## Responses\nnone\n")
    assert "## Critic rounds" in v and v.count("### round 1 · spec v1 · run-") == 1 and "[NIT] 2 wording" in v
    assert '"event": "change.pinned"' in log_text(store)
    assert list((store / "openspec" / "specs").iterdir()) == [] and (store / "decisions.md").read_text() == ""


def test_item_88_gate_refuses_a_delta_that_does_not_apply_and_a_malformed_version(store, tmp_path):
    run(store, "init")
    to_gate(store, FOUR_PART)
    bad = FOUR_PART.replace("## ADDED Requirements", "## MODIFIED Requirements").replace("trailer-read", "no-such-req")
    f = tmp_path / "v2.md"
    f.write_text(bad)
    cp = run(store, "approve-spec", "T-0001", "--edit", str(f))
    assert cp.returncode == 2 and "no-such-req" in cp.stderr
    t = yaml.safe_load((store / "tickets" / "T-0001.yaml").read_text())
    assert t["spec"] == {"version": 1, "approved_version": None} and t["status"] == "awaiting-spec-gate"
    assert not (store / "approvals" / "T-0001" / "spec-v2.yaml").exists()
    assert not (store / "openspec" / "changes" / "T-0001").exists()
    # malformed: no delta part; and a scenario without a label
    f.write_text("=== proposal.md\n## Problem\nx\n=== verification.md\n## Acceptance\n")
    cp = run(store, "approve-spec", "T-0001", "--edit", str(f))
    assert cp.returncode == 2 and "no delta part" in cp.stderr
    f.write_text(FOUR_PART.replace("- wrapped confidence → NEW; today it parks\n", ""))
    cp = run(store, "approve-spec", "T-0001", "--edit", str(f))
    assert cp.returncode == 2 and "no NEW/REGRESSION label" in cp.stderr


def test_old_format_spec_still_pins_in_a_store_without_init(store):
    to_gate(store, "## Problem\nold shape\n")
    cp = run(store, "approve-spec", "T-0001")
    assert cp.returncode == 0, cp.stderr
    assert js(cp)["change"] == [] and not (store / "openspec").exists()


def planned(store: Path) -> str:
    pid = js(run(store, "run", "start", "--role", "planner", "--ticket", "T-0001"))["run_id"]
    run(store, "run", "compose", pid)
    finish(store, pid, "# Plan\n## Sub-tickets\n- T-0001.1 do it\n## Coverage map\n- wrapped confidence → T-0001.1\n", "PLANNED")
    return pid


def test_spec_tasks_writes_the_planner_output_without_its_trailer(store):
    run(store, "init")
    to_gate(store, FOUR_PART)
    run(store, "approve-spec", "T-0001")
    pid = planned(store)
    cp = run(store, "spec", "tasks", "T-0001", "--run", pid)
    assert cp.returncode == 0, cp.stderr
    tasks = (store / "openspec" / "changes" / "T-0001" / "tasks.md").read_text()
    assert tasks.startswith("# Plan\n") and "STATUS:" not in tasks
    wid = [p.name for p in (store / "runs").iterdir() if "spec_writer" in p.name][0]
    cp = run(store, "spec", "tasks", "T-0001", "--run", wid)
    assert cp.returncode == 2 and "not a PLANNED planner run" in cp.stderr


def test_spec_tasks_is_a_no_op_without_a_spec_store(store):
    to_gate(store, "## Problem\nold shape\n")
    run(store, "approve-spec", "T-0001")
    pid = planned(store)
    cp = run(store, "spec", "tasks", "T-0001", "--run", pid)
    assert cp.returncode == 0 and "skipped" in js(cp)


def test_item_89_archive_applies_the_delta_moves_the_folder_and_appends_decisions(store):
    run(store, "init")
    to_gate(store, FOUR_PART)
    run(store, "approve-spec", "T-0001")
    run(store, "spec", "tasks", "T-0001", "--run", planned(store))
    cp = run(store, "archive", "T-0001")
    assert cp.returncode == 0, cp.stderr
    assert not (store / "openspec" / "changes" / "T-0001").exists()
    arch = list((store / "openspec" / "changes" / "archive").iterdir())
    assert len(arch) == 1 and arch[0].name.endswith("-T-0001")
    assert sorted(p.name for p in arch[0].iterdir()) == ["design.md", "proposal.md", "specs", "tasks.md", "verification.md"]
    assert (arch[0] / "verification.md").read_text().rstrip().endswith("## Verifier results\n\nnone")
    truth = (store / "openspec" / "specs" / "status-parser" / "spec.md").read_text()
    assert truth.startswith("# status-parser\n\n## Requirements\n") and "### Requirement: trailer-read" in truth and "#### Scenario: wrapped confidence" in truth
    dec = (store / "decisions.md").read_text().splitlines()
    assert len(dec) == 2 and all(" T-0001 " in ln for ln in dec) and dec[0].endswith("Trailer read by labels.")
    assert '"event": "change.archived"' in log_text(store)


def test_item_89_archive_refuses_when_the_delta_no_longer_applies(store, tmp_path):
    run(store, "init")
    # a second ticket whose delta ADDs the same requirement, pinned before T-0001 archives
    req = tmp_path / "r2.md"
    req.write_text("# SPEC-98: Second\n\nAlso the thing.\n")
    run(store, "ticket", "new", "--file", str(req))
    to_gate(store, FOUR_PART)
    run(store, "approve-spec", "T-0001")
    # pin T-0002 with the same ADDED name while current truth is still empty
    run(store, "ticket", "transition", "T-0002", "--to", "ready-for-spec-writer", "--by", "t")
    rid = js(run(store, "run", "start", "--role", "spec_writer", "--ticket", "T-0002"))["run_id"]
    run(store, "run", "compose", rid)
    finish(store, rid, FOUR_PART, "READY-FOR-CRITIC")
    run(store, "spec", "add", "T-0002", "--from-run", rid)
    run(store, "ticket", "transition", "T-0002", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
    run(store, "ticket", "transition", "T-0002", "--to", "awaiting-spec-gate", "--by", "t")
    assert run(store, "approve-spec", "T-0002").returncode == 0
    assert run(store, "archive", "T-0001").returncode == 0
    before = (store / "openspec" / "specs" / "status-parser" / "spec.md").read_text()
    cp = run(store, "archive", "T-0002")
    assert cp.returncode == 2 and "already in current truth" in cp.stderr
    assert (store / "openspec" / "specs" / "status-parser" / "spec.md").read_text() == before
    assert (store / "openspec" / "changes" / "T-0002" / "proposal.md").exists()
    assert len((store / "decisions.md").read_text().splitlines()) == 2


def test_item_90_after_archive_a_new_ticket_s_writer_and_critic_see_current_truth(store, tmp_path):
    run(store, "init")
    to_gate(store, FOUR_PART)
    run(store, "approve-spec", "T-0001")
    run(store, "archive", "T-0001")
    req = tmp_path / "r3.md"
    req.write_text("# SPEC-97: Third\n\nAnother thing.\n")
    run(store, "ticket", "new", "--file", str(req))
    run(store, "ticket", "transition", "T-0002", "--to", "ready-for-spec-writer", "--by", "t")
    rid = js(run(store, "run", "start", "--role", "spec_writer", "--ticket", "T-0002"))["run_id"]
    run(store, "run", "compose", rid)
    assert "### Requirement: trailer-read" in (store / "runs" / rid / "input.md").read_text()
    assert "openspec/specs/status-parser/spec.md" in meta(store, rid)["input_sources"]


def test_modified_and_removed_rewrite_current_truth_whole(store, tmp_path):
    run(store, "init")
    to_gate(store, FOUR_PART)
    run(store, "approve-spec", "T-0001")
    run(store, "archive", "T-0001")
    req = tmp_path / "r4.md"
    req.write_text("# SPEC-96: Modify\n\nChange it.\n")
    run(store, "ticket", "new", "--file", str(req))
    run(store, "ticket", "transition", "T-0002", "--to", "ready-for-spec-writer", "--by", "t")
    delta = ("=== proposal.md\n## Problem\nx\n## Decisions\nnone\n=== design.md\n## Proposed change\nB.\n"
             "=== specs/status-parser/spec.md\n## MODIFIED Requirements\n### Requirement: trailer-read\n"
             "The parser MUST read the trailer by its labels, trimmed.\n#### Scenario: trimmed head\n- WHEN `x`\n- THEN y\n"
             "## ADDED Requirements\n### Requirement: none-head\nA none head SHALL route as none.\n#### Scenario: none prose\n- WHEN `z`\n- THEN w\n"
             "=== verification.md\n## Acceptance\n- trimmed head → REGRESSION\n- none prose → NEW; fails today\n")
    rid = js(run(store, "run", "start", "--role", "spec_writer", "--ticket", "T-0002"))["run_id"]
    run(store, "run", "compose", rid)
    finish(store, rid, delta, "READY-FOR-CRITIC")
    run(store, "spec", "add", "T-0002", "--from-run", rid)
    run(store, "ticket", "transition", "T-0002", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
    run(store, "ticket", "transition", "T-0002", "--to", "awaiting-spec-gate", "--by", "t")
    assert run(store, "approve-spec", "T-0002").returncode == 0
    assert run(store, "archive", "T-0002").returncode == 0
    truth = (store / "openspec" / "specs" / "status-parser" / "spec.md").read_text()
    assert "trimmed." in truth and "wrapped confidence" not in truth and "### Requirement: none-head" in truth
    assert truth.count("### Requirement:") == 2
    assert (store / "decisions.md").read_text().splitlines().__len__() == 2  # "none" adds nothing
