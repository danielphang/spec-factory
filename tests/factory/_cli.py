"""Helpers the harness suite shares: where the repository and `bin/factory` are, the wrappers that
call it, the JSON readers, the ticket reader, the two setups (an empty repository and a parent past
the spec gate) and `CliStore`, the base of the fixture classes. A test file imports them from here,
never from another test file. Not named `test_*`, so pytest does not collect it.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
BIN = REPO / "bin" / "factory"
CLEAN_CLI = Path(__file__).resolve().parent / "clean_harness_cli.py"
STRIP = ("FACTORY_INSTANCE", "FACTORY_REPO", "FACTORY_STATE", "FACTORY_INTEGRATION_BRANCH", "FACTORY_CWD",
         "FACTORY_DISPATCH")


def cli(cwd: Path, *argv: str, **extra: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k not in STRIP}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", **extra})
    # init and paths are exempt from the harness lock and keep exercising bin/factory's own hand-over
    # of the caller's directory; every other command runs the launcher that stubs only the
    # uncommitted-edit refusal (design C.4), so the suite runs in a checkout with an uncommitted edit.
    cmd = [str(BIN)] if argv[:1] in (("init",), ("paths",)) else [sys.executable, str(CLEAN_CLI)]
    return subprocess.run([*cmd, *argv], capture_output=True, text=True, env=env, cwd=cwd)


def run(store: Path, *argv: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    env = {**os.environ, "FACTORY_STATE": str(store), "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO, input=stdin)


def run_env(env: dict, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([str(BIN), *argv], capture_output=True, text=True,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **env}, cwd=REPO)


def js(cp: subprocess.CompletedProcess) -> dict:
    return json.loads(cp.stdout.strip().splitlines()[-1])


def js_ok(cp: subprocess.CompletedProcess) -> dict:
    assert cp.returncode == 0, cp.stderr
    return js(cp)


def ticket(store: Path, tid: str = "T-0001") -> dict:
    return yaml.safe_load((store / "tickets" / f"{tid}.yaml").read_text())


def tree(path: Path) -> dict[str, bytes]:
    return {str(p.relative_to(path)): p.read_bytes() for p in sorted(path.rglob("*")) if p.is_file()}


def git_repo(path: Path) -> Path:
    """A git repository at `path` on branch `main`, with one empty commit."""
    path.mkdir(parents=True, exist_ok=True)
    for argv in (["init", "-q", "-b", "main"],
                 ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "init"]):
        subprocess.run(["git", "-C", str(path), *argv], check=True, capture_output=True)
    return path


def approved_parent(ok, tid: str, spec: Path | str) -> str:
    """Take ticket `tid` past the spec gate with `spec` as its spec (old format; no spec store).
    `ok(*argv)` runs one factory command and fails the test on a non-zero exit."""
    ok("ticket", "transition", tid, "--to", "ready-for-spec-writer", "--by", "t")
    ok("spec", "add", tid, "--file", str(spec))
    ok("ticket", "transition", tid, "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
    ok("ticket", "transition", tid, "--to", "awaiting-spec-gate", "--by", "t")
    ok("approve-spec", tid)
    return tid


class CliStore:
    """One `cli` and `ok` for a fixture class that runs `bin/factory` in the environment `self.env`,
    which the subclass builds."""
    env: dict

    def cli(self, *argv: str) -> subprocess.CompletedProcess:
        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)

    def ok(self, *argv: str) -> dict:
        cp = self.cli(*argv)
        assert cp.returncode == 0, f"{' '.join(argv)}: {cp.stderr}"
        return js(cp)
