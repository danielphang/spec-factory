"""`factory resolve <id> --to checks` (T-0054, issue #112): the route back to its checks for a
sub-ticket parked by a harness-bug after its implementer finished.

On the real run the clerk relayed `run finish`'s one-line JSON over several lines, the build found
no JSON, and it parked the sub-ticket from ready-for-implementer although its implementer run had
finished READY-FOR-REVIEW. The route reads the branch tip into the ticket as `ticket head` does,
applies the build's `pr:init` round step and moves it to checks-in-flight. Every other park, and a
ticket that is not parked, is refused with nothing written.

Black-box through `bin/factory` on a throwaway store whose sub-ticket T-0001.1 builds in a scratch
target repository.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest
import yaml

from ._cli import CliStore, approved_parent, git_repo

PARK = "harness-bug: run finish implementer: exit 0, no JSON on stdout"
REFUSAL = "--to checks applies to"


class SubTicket(CliStore):
    """T-0001 past the spec gate and planned as one sub-ticket, T-0001.1, ready for its implementer
    with no branch yet."""

    def __init__(self, tmp_path: Path):
        self.root = tmp_path / "store"
        self.target = git_repo(tmp_path / "t")
        self.env = {**os.environ, "FACTORY_STATE": str(self.root), "FACTORY_REPO": str(self.target),
                    "FACTORY_INTEGRATION_BRANCH": "main", "PYTHONDONTWRITEBYTECODE": "1"}
        (tmp_path / "req.md").write_text("# Fixture\n\nThe bot should do the thing.\n")
        (tmp_path / "spec.md").write_text("## Problem\nx\n")
        (tmp_path / "plan.md").write_text("ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n")
        self.ok("ticket", "new", "--file", str(tmp_path / "req.md"))
        approved_parent(self.ok, "T-0001", tmp_path / "spec.md")
        self.ok("subticket", "add", "T-0001", "--file", str(tmp_path / "plan.md"))
        self.ok("ticket", "transition", "T-0001", "--to", "planned", "--by", "t")

    def implement(self, status: str) -> str:
        """One implementer run on T-0001.1, as the build runs it: one commit on its branch and an
        output with `status`. Returns the run id."""
        rid = self.ok("run", "start", "--role", "implementer", "--ticket", "T-0001.1")["run_id"]
        wt = yaml.safe_load((self.root / "runs" / rid / "meta.yaml").read_text())["worktree"]
        (Path(wt) / "work.txt").write_text(rid)
        for argv in (["add", "work.txt"], ["-c", "user.email=f@x", "-c", "user.name=f", "commit", "-qm", "work"]):
            subprocess.run(["git", "-C", wt, *argv], check=True, capture_output=True)
        (self.root / "runs" / rid / "output.md").write_text(f"STATUS: {status}\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
        self.ok("run", "finish", rid)
        return rid

    def tip(self) -> str:
        return subprocess.run(["git", "-C", str(self.target), "rev-parse", "factory/T-0001.1"],
                              check=True, capture_output=True, text=True).stdout.strip()

    def ticket(self) -> dict:
        return yaml.safe_load((self.root / "tickets" / "T-0001.1.yaml").read_text())

    def events(self) -> list[dict]:
        return [json.loads(ln) for p in sorted((self.root / "log").glob("*.jsonl")) for ln in p.read_text().splitlines()]

    def snapshot(self) -> dict[str, bytes]:
        return {str(p.relative_to(self.root)): p.read_bytes() for p in sorted(self.root.rglob("*"))
                if p.is_file() and "worktrees" not in p.relative_to(self.root).parts}


def test_a_harness_bug_park_after_a_finished_implementer_returns_to_its_checks_at_the_branch_tip(tmp_path):
    s = SubTicket(tmp_path)
    s.implement("READY-FOR-REVIEW")
    s.ok("ticket", "park", "T-0001.1", "--reason", PARK)
    out = s.ok("resolve", "T-0001.1", "--to", "checks")
    t = s.ticket()
    assert out["state"] == "checks-in-flight" and out["kind"] == "to-checks" and out["head"] == s.tip()
    assert t["status"] == "checks-in-flight" and t["parked"] is None
    assert t["head"] == s.tip() and t["round"]["pr"] == 1
    assert t["history"][-1]["from"] == "parked" and t["history"][-1]["resolve"] == "to-checks"
    rec = yaml.safe_load((s.root / "approvals" / "T-0001.1" / "resolve-1.yaml").read_text())
    assert (rec["kind"], rec["from"], rec["to"], rec["head"]) == ("to-checks", "parked", "checks-in-flight", s.tip())
    last = s.events()[-1]
    assert (last["event"], last["kind"], last["to"]) == ("human.resolved", "to-checks", "checks-in-flight")


def test_a_later_round_is_unchanged_by_the_route(tmp_path):
    s = SubTicket(tmp_path)
    s.implement("READY-FOR-REVIEW")
    s.ok("ticket", "transition", "T-0001.1", "--to", "checks-in-flight", "--by", "t", "--round", "pr:init")
    s.ok("ticket", "transition", "T-0001.1", "--to", "ready-for-implementer", "--by", "t", "--round", "pr:+1")
    s.implement("READY-FOR-REVIEW")
    s.ok("ticket", "park", "T-0001.1", "--reason", PARK)
    s.ok("resolve", "T-0001.1", "--to", "checks")
    t = s.ticket()
    assert t["status"] == "checks-in-flight" and t["round"]["pr"] == 2 and t["head"] == s.tip()


def _blocked(s: SubTicket) -> None:
    s.implement("BLOCKED")
    s.ok("ticket", "park", "T-0001.1", "--reason", PARK)


def _revised(s: SubTicket) -> None:
    # checked and sent back; the next implementer run then failed to start, so the newest
    # implementer run predates the sub-ticket's return to ready-for-implementer
    s.implement("READY-FOR-REVIEW")
    s.ok("ticket", "transition", "T-0001.1", "--to", "checks-in-flight", "--by", "t", "--round", "pr:init")
    s.ok("ticket", "transition", "T-0001.1", "--to", "ready-for-implementer", "--by", "t", "--round", "pr:+1")
    s.ok("ticket", "park", "T-0001.1", "--reason", "harness-bug: run start implementer: x")


def _from_checks(s: SubTicket) -> None:
    s.implement("READY-FOR-REVIEW")
    s.ok("ticket", "transition", "T-0001.1", "--to", "checks-in-flight", "--by", "t", "--round", "pr:init")
    s.ok("ticket", "park", "T-0001.1", "--reason", "harness-bug: results record reviewer: x")


def _tripwire(s: SubTicket) -> None:
    rid = s.implement("READY-FOR-REVIEW")
    s.ok("ticket", "park", "T-0001.1", "--reason", f"tripwire: /x changed during {rid}")


def _unparked(s: SubTicket) -> None:
    s.implement("READY-FOR-REVIEW")


@pytest.mark.parametrize("setup", [_blocked, _revised, _from_checks, _tripwire, _unparked],
                         ids=["blocked", "revised", "checks", "tripwire", "unparked"])
def test_every_other_ticket_is_refused_and_nothing_is_written(tmp_path, setup):
    s = SubTicket(tmp_path)
    setup(s)
    status, before = s.ticket()["status"], s.snapshot()
    cp = s.cli("resolve", "T-0001.1", "--to", "checks")
    assert cp.returncode == 2, (cp.stdout, cp.stderr)
    assert REFUSAL in cp.stderr and f"T-0001.1 is {status}" in cp.stderr
    assert s.snapshot() == before


def test_any_other_to_value_names_both_routes(tmp_path):
    s = SubTicket(tmp_path)
    cp = s.cli("resolve", "T-0001.1", "--to", "planner")
    assert cp.returncode == 2 and "--to accepts only spec-gate or checks" in cp.stderr
