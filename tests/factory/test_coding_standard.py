"""The coding standard (issue #20): an implementer run's and a code-reviewer run's system prompt
name the running checkout's `docs/coding.md`, with `{coding standard}` filled; and the design
blocks this change edits that test_writing_standard.py does not cover (spec writer, implementer,
retro) stay verbatim copies of their `docs/prompts/` files.

Black-box through `bin/factory` in a scratch target repo, as test_writing_standard.py drives it.
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
STANDARD = REPO.resolve() / "docs" / "coding.md"
STRIP = ("FACTORY_INSTANCE", "FACTORY_REPO", "FACTORY_STATE", "FACTORY_INTEGRATION_BRANCH", "FACTORY_CWD")
FENCE = "`" * 3


def cli(cwd: Path, *argv: str, **extra: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k not in STRIP}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", **extra})
    cp = subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=cwd)
    assert cp.returncode == 0, (argv, cp.stderr)
    return cp


@pytest.fixture(scope="module")
def system_prompts(tmp_path_factory) -> dict[str, str]:
    """The system prompts of one implementer run and one reviewer run on the same ticket, started
    in a fresh scratch target on a throwaway store (FACTORY_STATE), as in the spec's scenario. The
    ticket's status is set by `ticket set` so that each role can start."""
    tmp = tmp_path_factory.mktemp("coding")
    t = tmp / "target"
    t.mkdir()
    for argv in (["init", "-q", "-b", "main"],
                 ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "init"]):
        subprocess.run(["git", "-C", str(t), *argv], check=True, capture_output=True)
    req = tmp / "r.md"
    req.write_text("# demo\n\nDo the thing.\n")
    store = {"FACTORY_STATE": str(tmp / "s")}
    cli(t, "init", "--repo-name", "demo")
    cli(t, "ticket", "new", "--file", str(req), **store)
    head = subprocess.run(["git", "-C", str(t), "rev-parse", "HEAD"], check=True, capture_output=True,
                          text=True).stdout.strip()
    prompts = {}
    for role, status in (("implementer", ["status=ready-for-implementer"]),
                         ("reviewer", ["status=checks-in-flight", "in_flight=[]", f"head={head}"])):
        cli(t, "ticket", "set", "T-0001", *status, **store)
        cp = cli(t, "run", "start", "--role", role, "--ticket", "T-0001", "--model", "opus", **store)
        run_id = json.loads(cp.stdout.strip().splitlines()[-1])["run_id"]
        prompts[role] = (tmp / "s" / "runs" / run_id / "system-prompt.txt").read_text()
    return prompts


@pytest.mark.parametrize("role, line", [
    ("implementer", "   Follow the coding standard at {path}."),
    ("reviewer", "7. The coding standard at {path}: a finding against it"),
])
def test_run_prompt_names_the_running_checkouts_coding_standard(system_prompts, role, line):
    assert STANDARD.is_absolute() and STANDARD.is_file() and STANDARD.stat().st_size > 0
    prompt = system_prompts[role]
    assert line.format(path=STANDARD) in prompt.split("\n")
    assert "{coding standard}" not in prompt


def _design_block(heading: str) -> str:
    """The text inside the first fenced `text` block under `## <heading>` in docs/design.md."""
    design = (REPO / "docs" / "design.md").read_text()
    m = re.search(rf"^## {re.escape(heading)}\n.*?^{FENCE}text\n(.*?)^{FENCE}$", design, re.M | re.S)
    assert m, heading
    return m.group(1)


@pytest.mark.parametrize("heading, copy", [
    ("2. Spec writer", "02-spec-writer.md"),
    ("5. Implementer", "05-implementer.md"),
    ("8. Retro", "08-retro.md"),
])
def test_changed_design_block_equals_its_prompt_copy(heading, copy):
    assert _design_block(heading) == (REPO / "docs" / "prompts" / copy).read_text()
