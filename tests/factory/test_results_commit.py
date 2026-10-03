"""`factory results record` files a checker's verdict only for the commit the checker names.

Each case drives `bin/factory` as a subprocess against a throwaway store (FACTORY_STATE), the
same way the scenarios in the change "checker-output-must-name-the-head" do: one ticket, a
head of forty zeros, one checker output, then look at the exit code, the rows written under
results/<head>/ and the `result.*` events in the log.
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
HEAD = "0" * 40
REVIEWER_TAIL = "Findings: none\nSTATUS: APPROVE\nCONFIDENCE: high\nESCALATIONS: none\n"
VERIFIER_TAIL = "Per criterion: none\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high\nESCALATIONS: none\n"


class Store:
    def __init__(self, tmp: Path):
        self.root = tmp / "store"
        self.tmp = tmp
        req = tmp / "r.md"
        req.write_text("# x\n\nthe thing\n")
        cp = self.cli("ticket", "new", "--file", str(req))
        assert cp.returncode == 0, cp.stderr
        self.tid = json.loads(cp.stdout.strip().splitlines()[-1])["id"]

    def cli(self, *argv: str) -> subprocess.CompletedProcess:
        env = {**os.environ, "FACTORY_STATE": str(self.root), "PYTHONDONTWRITEBYTECODE": "1"}
        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)

    def record(self, role: str, output: str | None, *extra: str) -> subprocess.CompletedProcess:
        argv = ["results", "record", self.tid, "--head", HEAD, "--role", role, "--run", "R1", *extra]
        if output is not None:
            o = self.tmp / "o.md"
            o.write_text(output)
            argv += ["--output", str(o)]
        return self.cli(*argv)

    def rows(self) -> list[str]:
        d = self.root / "results" / HEAD
        return sorted(p.name for p in d.iterdir()) if d.exists() else []

    def result_events(self) -> list[dict]:
        evs = []
        for p in sorted((self.root / "log").glob("*.jsonl")):
            evs += [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
        return [e for e in evs if e["event"].startswith("result.")]

    def status(self, role: str) -> str:
        return yaml.safe_load((self.root / "results" / HEAD / f"{role}.yaml").read_text())["status"]


@pytest.fixture
def s(tmp_path):
    return Store(tmp_path)


def _refused(s: Store, cp: subprocess.CompletedProcess, reason: str) -> None:
    assert cp.returncode == 2, cp.stderr
    assert reason in cp.stderr
    assert s.rows() == []
    assert s.result_events() == []


# ----- refused: nothing is written -----------------------------------------------------------

def test_no_commit_line_is_refused(s):
    cp = s.record("reviewer", REVIEWER_TAIL)
    _refused(s, cp, "no Commit: line")


def test_non_hex_commit_value_is_refused(s):
    cp = s.record("reviewer", "Commit: HEAD\n" + REVIEWER_TAIL)
    _refused(s, cp, "Commit: HEAD is not a commit id")


def test_later_commit_line_naming_another_commit_is_refused(s):
    cp = s.record("reviewer", f"Commit: {HEAD}\nFindings: none\nCommit: deadbeef00\nSTATUS: APPROVE\n")
    _refused(s, cp, "Commit: deadbeef00, not the head")


def test_verifier_without_commit_line_writes_no_ci_row(s):
    cp = s.record("verifier", VERIFIER_TAIL)
    _refused(s, cp, "no Commit: line")


def test_earlier_commit_line_naming_another_commit_is_refused(s):
    cp = s.record("reviewer", f"Commit: deadbeef00\nFindings: none\nCommit: {HEAD}\nSTATUS: APPROVE\n")
    _refused(s, cp, "Commit: deadbeef00, not the head")


# ----- accepted: the verdict is filed against the head ----------------------------------------

def test_full_head_sha_is_recorded(s):
    cp = s.record("reviewer", f"Commit: {HEAD}\n" + REVIEWER_TAIL)
    assert cp.returncode == 0, cp.stderr
    assert s.rows() == ["reviewer.yaml"]
    assert [e["event"] for e in s.result_events()] == ["result.recorded"]
    assert s.status("reviewer") == "APPROVE"


def test_abbreviated_sha_in_backticks_is_recorded(s):
    cp = s.record("verifier", "Commit: `0000000`\n" + VERIFIER_TAIL)
    assert cp.returncode == 0, cp.stderr
    assert s.rows() == ["ci.yaml", "verifier.yaml"]
    assert [e["event"] for e in s.result_events()] == ["result.recorded", "result.recorded"]
    assert s.status("verifier") == "VERIFIED" and s.status("ci") == "PASS"


# ----- --killed: unchanged, a KILLED row with or without a cut-off output ---------------------

def test_killed_without_output_records_killed(s):
    cp = s.record("verifier", None, "--killed")
    assert cp.returncode == 0, cp.stderr
    assert s.rows() == ["verifier.yaml"]
    assert s.status("verifier") == "KILLED"


def test_killed_with_cut_off_output_records_killed(s):
    cp = s.record("verifier", "Per criterion: (cut off)\n", "--killed")
    assert cp.returncode == 0, cp.stderr
    assert s.rows() == ["verifier.yaml"]
    assert s.status("verifier") == "KILLED"
