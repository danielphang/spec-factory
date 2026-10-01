"""P0 intake skeleton: the CLI guards and the parser, on a throwaway store (FACTORY_STATE).

Black-box through `bin/factory`, as the P0 acceptance items are written.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
BIN = REPO / "bin" / "factory"


def run(store: Path, *argv: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    env = {**os.environ, "FACTORY_STATE": str(store), "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO, input=stdin)


def js(cp: subprocess.CompletedProcess) -> dict:
    return json.loads(cp.stdout.strip().splitlines()[-1])


def ticket(store: Path, tid: str) -> dict:
    return yaml.safe_load((store / "tickets" / f"{tid}.yaml").read_text())


TRAILER = "\nSTATUS: {s}\nCONFIDENCE: high, fixture\nESCALATIONS: none\n"


@pytest.fixture
def store(tmp_path: Path) -> Path:
    return tmp_path / "state"


@pytest.fixture
def req(tmp_path: Path) -> Path:
    p = tmp_path / "SPEC-99_fixture.md"
    p.write_text("# SPEC-99: Fixture\n\nThe bot should do the thing.\n")
    return p


def test_p0_1_ticket_new_creates_a_ready_for_triage_ticket(store, req):
    cp = run(store, "ticket", "new", "--file", str(req))
    assert cp.returncode == 0, cp.stderr
    assert js(cp)["id"] == "T-0001"
    t = ticket(store, "T-0001")
    assert t["status"] == "ready-for-triage"
    assert t["round"] == {"spec": 0, "pr": 0}
    assert (store / "requests" / "T-0001.md").read_text().startswith("# SPEC-99")
    assert sys.version_info >= (3, 11)


def test_p0_8_transition_refuses_a_non_routing_edge(store, req):
    run(store, "ticket", "new", "--file", str(req))
    cp = run(store, "ticket", "transition", "T-0001", "--to", "ready-for-implementer", "--by", "t")
    assert cp.returncode == 2
    assert "not a routing edge" in cp.stderr
    assert ticket(store, "T-0001")["status"] == "ready-for-triage"
    log = list((store / "log").glob("*.jsonl"))
    assert all("ticket.transition" not in p.read_text() for p in log)


def test_p0_3_round_counter_is_only_moved_by_transition_and_stops_at_max(store, req):
    run(store, "ticket", "new", "--file", str(req))
    assert run(store, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t").returncode == 0
    cp = run(store, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
    assert cp.returncode == 0, cp.stderr
    assert js(cp)["round"]["spec"] == 1
    cp = run(store, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t", "--round", "spec:+1")
    assert cp.returncode == 0 and js(cp)["round"]["spec"] == 2
    assert run(store, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init").returncode == 0
    assert ticket(store, "T-0001")["round"]["spec"] == 2, "init never lowers or raises a counter already set"
    cp = run(store, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t", "--round", "spec:+1")
    assert cp.returncode == 2
    assert "round.spec 2 is at max_rounds 2" in cp.stderr
    assert ticket(store, "T-0001")["status"] == "ready-for-critic"


def test_run_start_refuses_wrong_state_and_double_dispatch(store, req):
    run(store, "ticket", "new", "--file", str(req))
    cp = run(store, "run", "start", "--role", "critic", "--ticket", "T-0001")
    assert cp.returncode == 2 and "T-0001 is ready-for-triage, not ready-for-critic" in cp.stderr
    assert not (store / "runs").exists() or not any((store / "runs").iterdir())
    cp = run(store, "run", "start", "--role", "triage", "--ticket", "T-0001", "--model", "opus")
    assert cp.returncode == 0, cp.stderr
    rid = js(cp)["run_id"]
    meta = yaml.safe_load((store / "runs" / rid / "meta.yaml").read_text())
    assert meta["role"] == "triage" and meta["model"] == "opus" and meta["started"]
    assert ticket(store, "T-0001")["in_flight"] == [rid]
    cp = run(store, "run", "start", "--role", "triage", "--ticket", "T-0001")
    assert cp.returncode == 2 and "already has run" in cp.stderr


def test_run_compose_then_finish_parses_status_and_clears_in_flight(store, req):
    run(store, "ticket", "new", "--file", str(req))
    rid = js(run(store, "run", "start", "--role", "triage", "--ticket", "T-0001"))["run_id"]
    cp = run(store, "run", "compose", rid)
    assert cp.returncode == 0, cp.stderr
    inp = (store / "runs" / rid / "input.md").read_text()
    assert "The bot should do the thing." in inp and "Output file" in inp
    meta = yaml.safe_load((store / "runs" / rid / "meta.yaml").read_text())
    assert meta["input_sources"] == ["requests/T-0001.md"]
    out = "Type: feature\nTitle: Do the thing\nSummary: x\nEvidence: none\nAssumptions: none\n" + TRAILER.format(s="ACCEPT")
    (store / "runs" / rid / "output.md").write_text(out)
    cp = run(store, "run", "finish", rid)
    assert cp.returncode == 0, cp.stderr
    assert js(cp)["status"] == "ACCEPT"
    t = ticket(store, "T-0001")
    assert t["in_flight"] == [] and t["title"] == "Do the thing" and t["type"] == "feature"


def test_run_finish_without_output_is_killed(store, req):
    run(store, "ticket", "new", "--file", str(req))
    rid = js(run(store, "run", "start", "--role", "triage", "--ticket", "T-0001"))["run_id"]
    run(store, "run", "compose", rid)
    cp = run(store, "run", "finish", rid, "--status-override", "KILLED")
    assert cp.returncode == 0 and js(cp)["status"] == "KILLED"
    assert yaml.safe_load((store / "runs" / rid / "meta.yaml").read_text())["status"] == "KILLED"


def test_status_parse_last_status_line_wins_and_needs_both_followers(tmp_path, store):
    p = tmp_path / "m.md"
    p.write_text("body\nSTATUS: APPROVE\nmore\nSTATUS: REVISE\nCONFIDENCE: high, ok\nESCALATIONS:\n- one\n- two\n")
    cp = run(store, "status", "parse", str(p))
    assert js(cp) == {"status": "REVISE", "confidence": "high, ok", "escalations": ["one", "two"]}
    p.write_text("body\nSTATUS: REVISE\nESCALATIONS: none\n")
    assert js(run(store, "status", "parse", str(p)))["status"] is None


def test_spec_add_critic_round2_input_carries_findings_and_previous_version(store, req, tmp_path):
    run(store, "ticket", "new", "--file", str(req))
    run(store, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
    # writer round 1
    rid = js(run(store, "run", "start", "--role", "spec_writer", "--ticket", "T-0001"))["run_id"]
    run(store, "run", "compose", rid)
    (store / "runs" / rid / "output.md").write_text("## Problem\nv1 body\n" + TRAILER.format(s="READY-FOR-CRITIC"))
    run(store, "run", "finish", rid)
    assert run(store, "spec", "add", "T-0001", "--from-run", rid).returncode == 0
    assert (store / "specs" / "T-0001" / "v1.md").read_text() == "## Problem\nv1 body\n"
    assert (store / "specs" / "T-0001.md").read_text() == "## Problem\nv1 body\n"
    run(store, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
    # critic round 1
    cid = js(run(store, "run", "start", "--role", "critic", "--ticket", "T-0001"))["run_id"]
    run(store, "run", "compose", cid)
    meta = yaml.safe_load((store / "runs" / cid / "meta.yaml").read_text())
    assert meta["input_sources"] == ["specs/T-0001/v1.md"]
    (store / "runs" / cid / "output.md").write_text("Findings:\n[BLOCKING] 2 Acceptance\nProblem: FINDING-ONE\n" + TRAILER.format(s="REVISE"))
    run(store, "run", "finish", cid)
    run(store, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t", "--round", "spec:+1")
    # writer round 2 sees the findings and v1
    wid = js(run(store, "run", "start", "--role", "spec_writer", "--ticket", "T-0001"))["run_id"]
    run(store, "run", "compose", wid)
    winp = (store / "runs" / wid / "input.md").read_text()
    assert "FINDING-ONE" in winp and "v1 body" in winp
    (store / "runs" / wid / "output.md").write_text("## Problem\nv2 body\n## Responses\n- FIXED x\n" + TRAILER.format(s="READY-FOR-CRITIC"))
    run(store, "run", "finish", wid)
    run(store, "spec", "add", "T-0001", "--from-run", wid)
    run(store, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
    # critic round 2 sees responses, prior findings, v1
    c2 = js(run(store, "run", "start", "--role", "critic", "--ticket", "T-0001"))["run_id"]
    run(store, "run", "compose", c2)
    cinp = (store / "runs" / c2 / "input.md").read_text()
    assert "## Responses" in cinp and "FINDING-ONE" in cinp and "v1 body" in cinp
    meta2 = yaml.safe_load((store / "runs" / c2 / "meta.yaml").read_text())
    assert meta2["input_sources"] == ["specs/T-0001/v2.md", f"runs/{cid}/output.md", "specs/T-0001/v1.md"]


def test_approve_spec_and_resolve_answer(store, req, tmp_path):
    run(store, "ticket", "new", "--file", str(req))
    run(store, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
    rid = js(run(store, "run", "start", "--role", "spec_writer", "--ticket", "T-0001"))["run_id"]
    run(store, "run", "compose", rid)
    (store / "runs" / rid / "output.md").write_text("## Problem\nbody\n" + TRAILER.format(s="READY-FOR-CRITIC"))
    run(store, "run", "finish", rid)
    run(store, "spec", "add", "T-0001", "--from-run", rid)
    run(store, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
    run(store, "ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t")
    cp = run(store, "approve-spec", "T-0001")
    assert cp.returncode == 0, cp.stderr
    t = ticket(store, "T-0001")
    assert t["status"] == "ready-for-planner" and t["spec"]["approved_version"] == 1
    # resolve --answer only applies to a waiting-requester / NEEDS-HUMAN park
    cp = run(store, "resolve", "T-0001", "--answer", str(req))
    assert cp.returncode == 2
    # a parked CLARIFY path (same file again: --force bypasses the duplicate-content refusal)
    run(store, "ticket", "new", "--file", str(req), "--force")
    run(store, "ticket", "transition", "T-0002", "--to", "waiting-requester", "--by", "t")
    ans = tmp_path / "a.md"
    ans.write_text("macOS 14\n")
    cp = run(store, "resolve", "T-0002", "--answer", str(ans))
    assert cp.returncode == 0, cp.stderr
    assert ticket(store, "T-0002")["status"] == "ready-for-triage"
    assert "## Answer 1" in (store / "requests" / "T-0002.md").read_text()
    rid = js(run(store, "run", "start", "--role", "triage", "--ticket", "T-0002"))["run_id"]
    run(store, "run", "compose", rid)
    assert "macOS 14" in (store / "runs" / rid / "input.md").read_text()


def test_status_parse_accepts_a_wrapped_confidence_line(tmp_path, store):
    p = tmp_path / "w.md"
    p.write_text("body\nSTATUS: NEEDS-HUMAN\nCONFIDENCE: high — every claim is a grep on this\ncheckout; one scope call open.\nESCALATIONS:\n1. first\n2. second\n")
    r = js(run(store, "status", "parse", str(p)))
    assert r["status"] == "NEEDS-HUMAN"
    assert r["confidence"].endswith("one scope call open.")
    assert r["escalations"] == ["1. first", "2. second"]
