"""The writing standard (issue #23): every run's preamble names the running checkout's
`docs/writing.md`, and the three prompt blocks that mention the standard (preamble, spec critic,
code reviewer) stay verbatim copies of their design-doc blocks.

Black-box through `bin/factory` in a scratch target repo, the way test_instance.py drives it.
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
STANDARD = REPO.resolve() / "docs" / "writing.md"
STRIP = ("FACTORY_INSTANCE", "FACTORY_REPO", "FACTORY_STATE", "FACTORY_INTEGRATION_BRANCH", "FACTORY_CWD")
FENCE = "`" * 3


def cli(cwd: Path, *argv: str, **extra: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k not in STRIP}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", **extra})
    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=cwd)


@pytest.fixture
def system_prompt(tmp_path: Path) -> str:
    """The system prompt of one triage run started in a fresh scratch target, on a throwaway store
    (FACTORY_STATE) as in the spec's scenario, so it does not depend on a clean harness checkout."""
    t = tmp_path / "target"
    t.mkdir()
    for argv in (["init", "-q", "-b", "main"],
                 ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "init"]):
        subprocess.run(["git", "-C", str(t), *argv], check=True, capture_output=True)
    req = tmp_path / "r.md"
    req.write_text("# demo\n\nDo the thing.\n")
    store = tmp_path / "s"
    cp = cli(t, "init", "--repo-name", "demo")
    assert cp.returncode == 0, cp.stderr
    cp = cli(t, "ticket", "new", "--file", str(req), FACTORY_STATE=str(store))
    assert cp.returncode == 0, cp.stderr
    cp = cli(t, "run", "start", "--role", "triage", "--ticket", "T-0001", "--model", "opus",
             FACTORY_STATE=str(store))
    assert cp.returncode == 0, cp.stderr
    run_id = json.loads(cp.stdout.strip().splitlines()[-1])["run_id"]
    return (store / "runs" / run_id / "system-prompt.txt").read_text()


def test_system_prompt_names_the_running_checkouts_standard(system_prompt):
    assert STANDARD.is_absolute() and STANDARD.is_file() and STANDARD.stat().st_size > 0
    line = next(ln for ln in system_prompt.split("\n") if "to the writing standard at " in ln)
    assert line == f"person reads to the writing standard at {STANDARD}. Those"


def test_no_writing_standard_placeholder_is_left_unfilled(system_prompt):
    assert "{writing standard}" not in system_prompt


def _design_block(heading: str) -> str:
    """The text inside the first fenced `text` block under `## <heading>` in docs/design.md."""
    design = (REPO / "docs" / "design.md").read_text()
    m = re.search(rf"^## {re.escape(heading)}\n.*?^{FENCE}text\n(.*?)^{FENCE}$", design, re.M | re.S)
    assert m, heading
    return m.group(1)


@pytest.mark.parametrize("heading, copy", [
    ("Shared preamble (every agent)", "00-preamble.md"),
    ("3. Spec critic", "03-spec-critic.md"),
    ("6. Code reviewer", "06-code-reviewer.md"),
])
def test_design_block_equals_its_prompt_copy(heading, copy):
    assert _design_block(heading) == (REPO / "docs" / "prompts" / copy).read_text()
