"""Helpers the harness suite shares: where the repository and `bin/factory` are, the wrappers that
call it, the JSON readers and the ticket reader. A test file imports them from here, never from
another test file. Not named `test_*`, so pytest does not collect it.
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
