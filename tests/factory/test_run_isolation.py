"""Role runs under a throwaway HOME (issue #36, part B): every composed input carries a
"Running code" section whose wrapper runs a command with HOME set to a fresh temporary directory,
gate commands reach build roles already wrapped, and the instance's `run_env` is exported after
HOME and may not set HOME itself.

Black-box through `bin/factory`, each case on a throwaway store (FACTORY_STATE) and, where it
changes `instance.yaml`, on a copy of the suite's fixture instance (FACTORY_INSTANCE).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
BIN = REPO / "bin" / "factory"
FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
WRAP = ('([ -z "${{VIRTUAL_ENV:-}}" ] || PATH=$(printf %s "$PATH" | tr : \'\\n\' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); '
        'unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"{vars}; {cmd})')
SECTION = ("\n## Running code\nRun every test, script or prototype through this wrapper, which gives it a "
           "fresh temporary HOME so it cannot write the operator's real home directory: `{wrapper}`. Put your "
           "command in place of <command>. This includes every test or check command the briefing above gives. "
           "A throwaway HOME does not stop a write to an absolute path: never run anything that could write a "
           "protected path outside the repository.\n")


class Store:
    def __init__(self, tmp_path: Path, run_env: str | None = None):
        self.tmp = tmp_path
        self.root = tmp_path / "state"
        self.env = {**os.environ, "FACTORY_STATE": str(self.root), "PYTHONDONTWRITEBYTECODE": "1"}
        if run_env is not None:
            inst = tmp_path / "inst"
            shutil.copytree(FIXTURE_INSTANCE, inst)
            with (inst / "instance.yaml").open("a", encoding="utf-8") as f:
                f.write(run_env)
            self.env["FACTORY_INSTANCE"] = str(inst)

    def cli(self, *argv: str) -> subprocess.CompletedProcess:
        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)

    def ok(self, *argv: str) -> dict:
        cp = self.cli(*argv)
        assert cp.returncode == 0, cp.stderr
        return json.loads(cp.stdout.strip().splitlines()[-1])

    def request(self) -> None:
        p = self.tmp / "req.md"
        p.write_text("# Fixture\n\nThe bot should do the thing.\n")
        self.ok("ticket", "new", "--file", str(p))

    def approved(self) -> None:
        """T-0001 past the spec gate, as the spec's t0019-parent.sh fixture leaves it."""
        self.request()
        spec = self.tmp / "spec.md"
        spec.write_text("## Problem\nx\n")
        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
        self.ok("spec", "add", "T-0001", "--file", str(spec))
        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
        self.ok("ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t")
        self.ok("approve-spec", "T-0001")

    def implementer_ready(self) -> None:
        """One sub-ticket of an approved T-0001, in a scratch target repo with a `main` branch."""
        self.approved()
        target = self.tmp / "target"
        target.mkdir()
        for argv in (["init", "-q", "-b", "main"],
                     ["-c", "user.email=f@x", "-c", "user.name=f", "commit", "-q", "--allow-empty", "-m", "init"]):
            subprocess.run(["git", "-C", str(target), *argv], check=True, capture_output=True)
        self.env.update({"FACTORY_REPO": str(target), "FACTORY_INTEGRATION_BRANCH": "main"})
        plan = self.tmp / "plan.md"
        plan.write_text("T-0001.1 / Do it\nDepends on: none\nParallel-safe: yes\n")
        self.ok("subticket", "add", "T-0001", "--file", str(plan))

    def start(self, role: str, tid: str) -> str:
        return self.ok("run", "start", "--role", role, "--ticket", tid)["run_id"]

    def compose(self, role: str, tid: str) -> tuple[str, dict]:
        run_id = self.start(role, tid)
        out = self.ok("run", "compose", run_id)
        return (self.root / "runs" / run_id / "input.md").read_text(encoding="utf-8"), out


def wrapper_in(text: str) -> str:
    """The backticked text holding `<command>` in the input's Running code section."""
    section = text.split("\n## Running code\n", 1)[1].split("\n## ", 1)[0]
    found = [s for s in section.split("`")[1::2] if "<command>" in s]
    assert len(found) == 1, section
    return found[0]


def test_triage_input_carries_the_section_right_after_the_output_file(tmp_path):
    s = Store(tmp_path)
    s.request()
    text, out = s.compose("triage", "T-0001")
    _, rest = text.split("\n## Output file\n", 1)
    assert rest.split("\n", 1)[1].startswith(SECTION.format(wrapper=WRAP.format(vars="", cmd="<command>")))
    assert text.count("\n## Running code\n") == 1
    assert out["sources"] == ["requests/T-0001.md"], "the section is not a store source"


def test_planner_and_implementer_inputs_carry_the_section_once(tmp_path):
    s = Store(tmp_path)
    s.implementer_ready()
    for role, tid in (("planner", "T-0001"), ("implementer", "T-0001.1")):
        text, _ = s.compose(role, tid)
        assert text.count("\n## Running code\n") == 1, role
        assert wrapper_in(text) == WRAP.format(vars="", cmd="<command>"), role


def test_implementer_gate_commands_come_wrapped(tmp_path):
    s = Store(tmp_path)
    s.implementer_ready()
    text, _ = s.compose("implementer", "T-0001.1")
    where = text.split("\n## Where you work\n", 1)[1].split("\n## ", 1)[0]
    # the suite's fixture instance has one gate command
    assert ("Gate commands (run each from your worktree, exactly as written; each is already wrapped): `"
            + WRAP.format(vars="", cmd="git diff --check main...HEAD") + "`\n") in where + "\n"
    assert "`git diff --check main...HEAD`" not in where


def test_run_env_is_exported_after_home_in_file_order_and_quoted(tmp_path):
    s = Store(tmp_path, run_env="run_env: {ZED: '/tmp/a b', ALPHA: \"it's\", N_1: 3}\n")
    s.implementer_ready()
    vars_ = " ZED='/tmp/a b' ALPHA='it'\"'\"'s' N_1=3"
    text, _ = s.compose("implementer", "T-0001.1")
    assert wrapper_in(text) == WRAP.format(vars=vars_, cmd="<command>")
    assert "`" + WRAP.format(vars=vars_, cmd="git diff --check main...HEAD") + "`" in text


@pytest.mark.parametrize("value", ["run_env:\n", "run_env: {}\n"])
def test_empty_or_null_run_env_exports_nothing(tmp_path, value):
    s = Store(tmp_path, run_env=value)
    s.request()
    text, _ = s.compose("triage", "T-0001")
    assert wrapper_in(text) == WRAP.format(vars="", cmd="<command>")


@pytest.mark.parametrize(("value", "named"), [
    ("run_env: {HOME: /tmp/t0019-home}\n", "HOME"),
    ("run_env: {OK: x, 1BAD: y}\n", "1BAD"),
    ("run_env: {'A-B': y}\n", "A-B"),
    ("run_env: [UV_CACHE_DIR]\n", "list"),
])
def test_bad_run_env_is_refused_and_no_input_is_written(tmp_path, value, named):
    s = Store(tmp_path, run_env=value)
    s.request()
    run_id = s.start("triage", "T-0001")
    cp = s.cli("run", "compose", run_id)
    assert cp.returncode == 2
    assert "run_env" in cp.stderr and named in cp.stderr, cp.stderr
    assert not (s.root / "runs" / run_id / "input.md").exists()


def test_a_command_run_through_the_wrapper_gets_a_fresh_home_and_run_env(tmp_path):
    s = Store(tmp_path, run_env="run_env: {T0019_CACHE: '/tmp/t0019 cache'}\n")
    s.request()
    text, _ = s.compose("triage", "T-0001")
    # A compound command: the export reaches both halves, and each run gets its own HOME.
    probe = 'touch "$HOME/probe" && echo "$HOME|$T0019_CACHE|$(ls "$HOME")"'
    script = wrapper_in(text).replace("<command>", probe)
    fake_home = tmp_path / "real-home"
    fake_home.mkdir()
    env = {**os.environ, "HOME": str(fake_home)}
    env.pop("T0019_CACHE", None)
    first, second = (subprocess.run(["sh", "-c", script], capture_output=True, text=True, env=env, check=True)
                     .stdout.strip().split("|") for _ in range(2))
    assert first[1:] == ["/tmp/t0019 cache", "probe"]
    assert first[0] != str(fake_home) and second[0] != first[0]
    assert Path(first[0]).is_dir() and Path(first[0]) == Path(first[0]).resolve()
    assert list(fake_home.iterdir()) == []
