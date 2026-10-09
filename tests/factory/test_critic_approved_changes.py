"""The critic's list of approved changes not yet archived (T-0027 part B).

On a store with a spec store, a critic run's input carries `## Approved changes not yet archived`:
one entry per change folder under `openspec/changes/` whose ticket is neither closed nor back in the
spec loop, other than the reviewed ticket's own, each with its title, state, folder, the
requirements its deltas change and its Decisions lines. Each listed `proposal.md` is an input
source. The body is `none` with no such change, and the section is left out without a spec store.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
BIN = REPO / "bin" / "factory"
HEADING = "## Approved changes not yet archived"


def spec(decision: str, requirement: str) -> str:
    return (f"=== proposal.md\n## Problem\nx\n## Decisions\n- {decision}\n"
            "=== design.md\n## Proposed change\nEdit `src/greet.py`.\n## Tests to change\nnone\n"
            f"=== specs/demo/spec.md\n## ADDED Requirements\n### Requirement: {requirement}\nThe tool SHALL act.\n\n"
            "#### Scenario: It acts\n- WHEN `echo hi`\n- THEN it prints `hi`\n"
            "=== verification.md\n## Acceptance\n- It acts → NEW\n")


class Store:
    def __init__(self, tmp_path: Path, spec_store: bool = True):
        self.tmp = tmp_path
        self.root = tmp_path / "store"
        target = tmp_path / "t"
        subprocess.run(["git", "init", "-q", "-b", "main", str(target)], check=True)
        self.env = {**os.environ, "FACTORY_STATE": str(self.root), "FACTORY_REPO": str(target),
                    "FACTORY_INTEGRATION_BRANCH": "main", "PYTHONDONTWRITEBYTECODE": "1"}
        if spec_store:
            self.ok("init")

    def ok(self, *argv: str) -> dict:
        cp = subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)
        assert cp.returncode == 0, cp.stdout + cp.stderr
        return json.loads(cp.stdout.strip().splitlines()[-1])

    def ticket(self, tid: str, title: str, text: str) -> None:
        """A new ticket `tid` with spec v1 `text`, at ready-for-critic."""
        req, sp = self.tmp / f"{tid}-req.md", self.tmp / f"{tid}-spec.md"
        req.write_text(f"# {title}\n\nDo it.\n")
        sp.write_text(text)
        assert self.ok("ticket", "new", "--file", str(req))["id"] == tid
        self.ok("ticket", "transition", tid, "--to", "ready-for-spec-writer", "--by", "t")
        self.ok("spec", "add", tid, "--file", str(sp))
        self.ok("ticket", "transition", tid, "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")

    def approve(self, tid: str) -> None:
        self.ok("ticket", "transition", tid, "--to", "awaiting-spec-gate", "--by", "t")
        self.ok("approve-spec", tid)

    def critic(self, tid: str) -> tuple[str, list[str]]:
        rid = self.ok("run", "start", "--role", "critic", "--ticket", tid)["run_id"]
        return self.compose(rid)

    def compose(self, rid: str) -> tuple[str, list[str]]:
        sources = self.ok("run", "compose", rid)["sources"]
        return (self.root / "runs" / rid / "input.md").read_text(), sources


def section(text: str) -> list[str] | None:
    """The section's lines, heading first, up to the next `## ` heading; None when it is absent."""
    lines = text.splitlines()
    if HEADING not in lines:
        return None
    i = lines.index(HEADING)
    rest = lines[i + 1:]
    end = next((k for k, ln in enumerate(rest) if ln.startswith("## ")), len(rest))
    return [HEADING] + rest[:end]


@pytest.fixture
def two(tmp_path) -> Store:
    """T-0001 "Greeter" approved and pinned (ready-for-planner); T-0002 "Waver" at ready-for-critic."""
    s = Store(tmp_path)
    s.ticket("T-0001", "Greeter", spec("Greet by default.", "Greets"))
    s.approve("T-0001")
    s.ticket("T-0002", "Waver", spec("Wave at night.", "Waves"))
    return s


def test_the_critic_gets_each_other_approved_change_with_its_requirements_and_decisions(two):
    rid = two.ok("run", "start", "--role", "critic", "--ticket", "T-0002")["run_id"]
    text, sources = two.compose(rid)
    folder = two.root / "openspec" / "changes" / "T-0001"
    sec = section(text)
    assert sec is not None
    body = [ln for ln in sec[1:] if ln.strip()]
    assert body[0].startswith("### T-0001: Greeter (") and body[0].endswith(")")
    assert body[1:] == [f"Change folder: `{folder}`", "Changes: demo: ADDED Greets", "Decisions:",
                        "- Greet by default."]
    assert not any(ln.startswith("### T-0002") for ln in sec)  # the reviewed ticket is not listed
    assert "openspec/changes/T-0001/proposal.md" in sources
    # it follows the spec under review, as part of the critic's context
    assert text.index(HEADING) > text.index("## Spec under review (v1)")


def test_the_entry_names_the_ticket_state(two):
    two.ok("ticket", "set", "T-0001", "status=planned")
    sec = section(two.critic("T-0002")[0])
    assert "### T-0001: Greeter (planned)" in sec


def test_an_archived_change_leaves_the_list_and_the_body_reads_none(two):
    two.ok("archive", "T-0001")
    text, sources = two.critic("T-0002")
    assert [ln for ln in section(text) if ln.strip()] == [HEADING, "none"]
    assert not any("proposal.md" in s for s in sources)


@pytest.mark.parametrize("status", ["closed", "ready-for-spec-writer", "ready-for-critic", "awaiting-spec-gate"])
def test_a_closed_ticket_or_one_back_in_the_spec_loop_is_left_out(two, status):
    two.ok("ticket", "set", "T-0001", f"status={status}")
    text, sources = two.critic("T-0002")
    assert [ln for ln in section(text) if ln.strip()] == [HEADING, "none"]
    assert "openspec/changes/T-0001/proposal.md" not in sources


def test_a_change_sent_back_to_the_spec_writer_leaves_the_list(two):
    rid = two.ok("run", "start", "--role", "critic", "--ticket", "T-0002")["run_id"]
    assert "### T-0001: Greeter" in "\n".join(section(two.compose(rid)[0]))
    notes = two.tmp / "notes.md"
    notes.write_text("redo\n")
    two.ok("ticket", "park", "T-0001", "--reason", "x")
    two.ok("resolve", "T-0001", "--to", "spec-gate")
    two.ok("request-changes", "T-0001", "--notes", str(notes))
    assert [ln for ln in section(two.compose(rid)[0]) if ln.strip()] == [HEADING, "none"]


def test_a_folder_with_no_ticket_and_the_archive_folder_are_skipped(two):
    two.ok("archive", "T-0001")
    stray = two.root / "openspec" / "changes" / "T-0099"
    stray.mkdir()
    (stray / "proposal.md").write_text("## Problem\nx\n## Decisions\n- stray\n")
    text, sources = two.critic("T-0002")
    assert [ln for ln in section(text) if ln.strip()] == [HEADING, "none"]
    assert not any(src.startswith("openspec/changes/") for src in sources)


def test_entries_follow_folder_name_order_and_an_empty_delta_reads_none(two):
    two.ticket("T-0003", "Third", spec("Third decision.", "Thirds"))
    two.approve("T-0003")
    demo = two.root / "openspec" / "changes" / "T-0003" / "specs" / "demo" / "spec.md"
    demo.write_text("## ADDED Requirements\n")
    sec = section(two.critic("T-0002")[0])
    heads = [ln for ln in sec if ln.startswith("### ")]
    assert [h.split(":")[0] for h in heads] == ["### T-0001", "### T-0003"]
    i = sec.index(next(h for h in heads if h.startswith("### T-0003")))
    assert sec[i + 2] == "Changes: none"


def test_with_no_other_change_the_body_reads_none(tmp_path):
    s = Store(tmp_path)
    s.ticket("T-0001", "Only", spec("Only decision.", "Only"))
    text, sources = s.critic("T-0001")
    assert [ln for ln in section(text) if ln.strip()] == [HEADING, "none"]
    assert not any(src.startswith("openspec/changes/") for src in sources)


def test_without_a_spec_store_the_section_is_left_out(tmp_path):
    s = Store(tmp_path, spec_store=False)
    s.ticket("T-0001", "Only", spec("Only decision.", "Only"))
    assert not (s.root / "openspec" / "changes").exists()
    text, _ = s.critic("T-0001")
    assert section(text) is None


def test_a_critic_run_s_system_prompt_carries_the_cross_ticket_rule(tmp_path):
    s = Store(tmp_path)
    s.ticket("T-0001", "Only", spec("Only decision.", "Only"))
    rid = s.ok("run", "start", "--role", "critic", "--ticket", "T-0001")["run_id"]
    prompt = " ".join((s.root / "runs" / rid / "system-prompt.txt").read_text().split())
    assert ("For each scenario, check whether it depends on behaviour that an approved change not yet archived "
            "(listed in your input) changes. If so, its setup must hold whichever of the two merges first; if it "
            "would not, that is BLOCKING: name that ticket and its decision.") in prompt
