"""A role run that leaves no output is EMPTY-OUTPUT, never a budget kill (T-0032 part C).

The CLI half, black-box through `bin/factory` on a throwaway store: `run finish` labels a run with a
missing or blank `output.md` EMPTY-OUTPUT, an explicit `--status-override KILLED` still records
KILLED, and `run last-message` keeps the agent's last message for an EMPTY-OUTPUT run only. The
workflow half (one re-dispatch, then a park) is checked by the spec's node scenarios.
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


class Store:
    """A throwaway store with one ticket, T-0001, and one triage run started on it."""

    def __init__(self, tmp_path: Path):
        self.root = tmp_path / "state"
        self.env = {**os.environ, "FACTORY_STATE": str(self.root), "PYTHONDONTWRITEBYTECODE": "1"}
        req = tmp_path / "req.md"
        req.write_text("# F\n\nDo x.\n")
        self.ok("ticket", "new", "--file", str(req))
        self.rid = self.ok("run", "start", "--role", "triage", "--ticket", "T-0001")["run_id"]
        self.ok("run", "compose", self.rid)
        self.run_dir = self.root / "runs" / self.rid

    def cli(self, *argv: str) -> subprocess.CompletedProcess:
        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)

    def ok(self, *argv: str) -> dict:
        cp = self.cli(*argv)
        assert cp.returncode == 0, cp.stderr
        return json.loads(cp.stdout.strip().splitlines()[-1])

    def meta(self) -> dict:
        return yaml.safe_load((self.run_dir / "meta.yaml").read_text())

    def events(self) -> list[str]:
        return [json.loads(ln)["event"] for p in sorted((self.root / "log").glob("*.jsonl"))
                for ln in p.read_text().splitlines() if ln.strip()]


@pytest.mark.parametrize("output", [None, "", "  \n\n"])
def test_run_finish_with_no_or_blank_output_is_empty_output(tmp_path, output):
    s = Store(tmp_path)
    if output is not None:
        (s.run_dir / "output.md").write_text(output)
    assert s.ok("run", "finish", s.rid)["status"] == "EMPTY-OUTPUT"
    assert s.meta()["status"] == "EMPTY-OUTPUT"
    assert "run.finished" in s.events() and "run.killed" not in s.events()


def test_status_override_killed_still_records_killed(tmp_path):
    s = Store(tmp_path)
    assert s.ok("run", "finish", s.rid, "--status-override", "KILLED")["status"] == "KILLED"
    assert s.meta()["status"] == "KILLED"
    assert "run.killed" in s.events()


def test_last_message_is_kept_for_an_empty_output_run(tmp_path):
    s = Store(tmp_path)
    s.ok("run", "finish", s.rid)
    text = "The suite is still running; I'll write the review when it ends.\nsecond line"
    res = s.ok("run", "last-message", s.rid, f"--text={text}")
    assert res == {"ok": True, "run_id": s.rid, "last_message": f"runs/{s.rid}/last-message.md"}
    assert (s.run_dir / "last-message.md").read_text() == text + "\n"


def test_last_message_is_refused_for_a_run_that_wrote_its_output(tmp_path):
    s = Store(tmp_path)
    (s.run_dir / "output.md").write_text("Type: bug\nTitle: x\n\nSTATUS: ACCEPT\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
    assert s.ok("run", "finish", s.rid)["status"] == "ACCEPT"
    cp = s.cli("run", "last-message", s.rid, "--text=anything")
    assert cp.returncode == 2 and "EMPTY-OUTPUT" in cp.stderr
    assert not (s.run_dir / "last-message.md").exists()
