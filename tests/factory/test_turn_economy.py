"""The reading rules for five more roles (issue #76): the triage, planner, implementer, code
reviewer and verifier prompts carry the critic's Turn economy bullet, word for word, in every copy
(the docs/design.md block, its docs/prompts/ file and the factory/prompts/ run copy), at the place
the spec gives it, without the spec writer's one-write sentence; and a run of each role receives it.

Black-box through `bin/factory` in a scratch target repo, as test_coding_standard.py drives it.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
BIN = REPO / "bin" / "factory"
STRIP = ("FACTORY_INSTANCE", "FACTORY_REPO", "FACTORY_STATE", "FACTORY_INTEGRATION_BRANCH", "FACTORY_CWD")
FENCE = "`" * 3

BULLET = [
    "- Turn economy: every turn re-sends everything read so far, so a",
    "  wasted turn or a long printout costs again on every later turn. Put",
    "  independent reads and commands in one turn. Once grep has found the",
    "  lines you need, read that line range, not the whole file. Send long",
    "  output to a file in your scratch directory and grep or tail it,",
    "  rather than printing it in full.",
]
# The critic's paragraph, joined into one line: what a run prompt must carry exactly once.
PARAGRAPH = " ".join(x.strip() for x in BULLET)[2:]
ONE_WRITE = "as few writes as you can"

DECLARED = "- A protected path the sub-ticket declares is not an escalation: the"
# role -> (design heading, docs/prompts file, the line the bullet sits next to, "before" | "after")
ROLES = {
    "triage": ("1. Triage", "01-triage.md",
               "  When unsure between ACCEPT and CLARIFY, choose CLARIFY.", "after"),
    "planner": ("4. Planner / decomposer", "04-planner.md",
                "  siblings to re-verify, so parallel sub-tickets are not free.", "after"),
    "implementer": ("5. Implementer", "05-implementer.md", DECLARED, "before"),
    "reviewer": ("6. Code reviewer", "06-code-reviewer.md",
                 "  one test or a grep, and cite its output with that finding.", "after"),
    "verifier": ("7. Verifier", "07-verifier.md", DECLARED, "before"),
}


def _design_block(heading: str) -> str:
    """The text inside the first fenced `text` block under `## <heading>` in docs/design.md."""
    design = (REPO / "docs" / "design.md").read_text()
    m = re.search(rf"^## {re.escape(heading)}\n.*?^{FENCE}text\n(.*?)^{FENCE}$", design, re.M | re.S)
    assert m, heading
    return m.group(1)


def _bullet_at(lines: list[str]) -> list[int]:
    return [i for i in range(len(lines)) if lines[i:i + len(BULLET)] == BULLET]


@pytest.mark.parametrize("role", sorted(ROLES))
def test_every_copy_carries_the_bullet_once_at_its_place(role):
    heading, doc, anchor, side = ROLES[role]
    block = _design_block(heading)
    documented = (REPO / "docs" / "prompts" / doc).read_text()
    assert block == documented, f"design block {heading!r} is not a verbatim copy of {doc}"
    for path in (REPO / "docs" / "prompts" / doc, REPO / "factory" / "prompts" / f"{role}.md"):
        lines = path.read_text().splitlines()
        at = _bullet_at(lines)
        assert len(at) == 1, (path, at)
        i = at[0]
        neighbour = lines[i + len(BULLET)] if side == "before" else lines[i - 1]
        assert neighbour == anchor, (path, side, neighbour)
        assert ONE_WRITE not in " ".join(lines), path


def _cli(cwd: Path, *argv: str, **extra: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k not in STRIP}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", **extra})
    cp = subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=cwd)
    assert cp.returncode == 0, (argv, cp.stderr)
    return cp


@pytest.fixture(scope="module")
def run_prompts(tmp_path_factory) -> dict[str, str]:
    """The system prompt of one run of each of the five roles, started on one ticket in a fresh
    scratch target with a throwaway store (FACTORY_STATE). `ticket set` gives the ticket the status
    each role starts from."""
    tmp = tmp_path_factory.mktemp("economy")
    t = tmp / "target"
    t.mkdir()
    for argv in (["init", "-q", "-b", "main"],
                 ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "init"]):
        subprocess.run(["git", "-C", str(t), *argv], check=True, capture_output=True)
    req = tmp / "r.md"
    req.write_text("# demo\n\nDo the thing.\n")
    store = {"FACTORY_STATE": str(tmp / "s")}
    _cli(t, "init", "--repo-name", "demo")
    _cli(t, "ticket", "new", "--file", str(req), **store)
    head = subprocess.run(["git", "-C", str(t), "rev-parse", "HEAD"], check=True, capture_output=True,
                          text=True).stdout.strip()
    checks = ["status=checks-in-flight", "in_flight=[]", f"head={head}"]
    prompts = {}
    for role, status in (("triage", ["status=ready-for-triage", "in_flight=[]"]),
                         ("planner", ["status=ready-for-planner", "in_flight=[]"]),
                         ("implementer", ["status=ready-for-implementer", "in_flight=[]"]),
                         ("reviewer", checks), ("verifier", checks)):
        _cli(t, "ticket", "set", "T-0001", *status, **store)
        cp = _cli(t, "run", "start", "--role", role, "--ticket", "T-0001", "--model", "opus", **store)
        run_id = json.loads(cp.stdout.strip().splitlines()[-1])["run_id"]
        prompts[role] = (tmp / "s" / "runs" / run_id / "system-prompt.txt").read_text()
    return prompts


@pytest.mark.parametrize("role", sorted(ROLES))
def test_a_run_of_the_role_receives_the_paragraph_once(run_prompts, role):
    flat = " ".join(run_prompts[role].split())
    assert "UNTRUSTED INPUT" in flat, role  # the preamble: the run started and its prompt was read
    assert flat.count(PARAGRAPH) == 1, role
    assert ONE_WRITE not in flat, role
