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
