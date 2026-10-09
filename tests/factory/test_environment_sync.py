"""The running-code wrapper drops an inherited virtual environment, and the instance's
`environment_sync` runs in each build checkout at run start (T-0031).

Black-box through `bin/factory`, each case on a throwaway store (FACTORY_STATE), a scratch target
repo (FACTORY_REPO) and a copy of the suite's fixture instance (FACTORY_INSTANCE) with the keys
under test appended. A fake virtual environment, a directory holding `bin/python`, stands in for
the one a launching session activated.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
BIN = REPO / "bin" / "factory"
FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
GIT_ID = {"GIT_AUTHOR_NAME": "f", "GIT_AUTHOR_EMAIL": "f@x", "GIT_COMMITTER_NAME": "f", "GIT_COMMITTER_EMAIL": "f@x"}
DUMP = "env > synced.env"  # a sync that records the environment it ran in
FAIL = "echo sync-$((1+1)) >&2; echo out-line; exit $((2+1))"  # output and exit code are computed


class Target:
    """T-0001 approved and split into T-0001.1, ready for its implementer, on an instance whose
    `run_env` exports T31_CACHE and whose `environment_sync` is `sync` (None: the key is absent)."""

    def __init__(self, tmp_path: Path, sync: str | None):
        self.tmp = tmp_path
        self.root = tmp_path / "state"
        self.repo = tmp_path / "target"
        self.venv = tmp_path / "venv"
        (self.venv / "bin").mkdir(parents=True)
        (self.venv / "bin" / "python").write_text("#!/bin/sh\necho fake\n")
        (self.venv / "bin" / "python").chmod(0o755)
        inst = tmp_path / "inst"
        shutil.copytree(FIXTURE_INSTANCE, inst)
        with (inst / "instance.yaml").open("a", encoding="utf-8") as f:
            f.write("run_env: {T31_CACHE: /tmp/t31-cache}\n")
            if sync is not None:
                f.write(f"environment_sync: {json.dumps(sync)}\n")
        self.repo.mkdir()
        self.env = {**os.environ, **GIT_ID, "FACTORY_STATE": str(self.root), "FACTORY_INSTANCE": str(inst),
                    "FACTORY_REPO": str(self.repo), "FACTORY_INTEGRATION_BRANCH": "main",
                    "PYTHONDONTWRITEBYTECODE": "1"}
        self.git("init", "-q", "-b", "main")
        self.git("commit", "-q", "--allow-empty", "-m", "init")
        req, spec, plan = tmp_path / "req.md", tmp_path / "spec.md", tmp_path / "plan.md"
        req.write_text("# F\n\nDo x.\n")
        spec.write_text("## Problem\nx\n")
        plan.write_text("ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n")
        self.ok("ticket", "new", "--file", str(req))
        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
        self.ok("spec", "add", "T-0001", "--file", str(spec))
        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
        self.ok("ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t")
        self.ok("approve-spec", "T-0001")
        self.ok("subticket", "add", "T-0001", "--file", str(plan))

    def git(self, *argv: str, cwd: Path | None = None) -> str:
        cp = subprocess.run(["git", "-C", str(cwd or self.repo), *argv], capture_output=True, text=True,
                            env=self.env, check=True)
        return cp.stdout.strip()

    def cli(self, *argv: str, venv: bool = False) -> subprocess.CompletedProcess:
        """`bin/factory`, launched from a shell with the fake virtual environment activated when `venv`
        (VIRTUAL_ENV and its bin/ first on PATH; not PYTHONHOME, which would break the harness's own
        interpreter: the wrapper test covers PYTHONHOME)."""
        env = self.env
        if venv:
            env = {**env, "VIRTUAL_ENV": str(self.venv), "PATH": f"{self.venv}/bin:{env['PATH']}"}
        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)

    def ok(self, *argv: str, venv: bool = False) -> dict:
        cp = self.cli(*argv, venv=venv)
        assert cp.returncode == 0, cp.stderr
        return json.loads(cp.stdout.strip().splitlines()[-1])

    def start(self, role: str, tid: str) -> str:
        return self.ok("run", "start", "--role", role, "--ticket", tid, venv=True)["run_id"]

    def input_of(self, run_id: str) -> str:
        self.ok("run", "compose", run_id)
        return (self.root / "runs" / run_id / "input.md").read_text(encoding="utf-8")

    def meta(self, run_id: str) -> dict:
        return yaml.safe_load((self.root / "runs" / run_id / "meta.yaml").read_text(encoding="utf-8"))

    def ticket(self, tid: str) -> dict:
        return self.ok("ticket", "show", tid, "--json")

    def worktree(self) -> Path:
        return self.root / "worktrees" / "T-0001.1"

    def ready_for_checks(self) -> str:
        """A commit on T-0001.1's branch (in the implementer's worktree when one exists), and the
        ticket set to checks."""
        if self.worktree().is_dir():
            self.git("commit", "-q", "--allow-empty", "-m", "work", cwd=self.worktree())
            head = self.git("rev-parse", "HEAD", cwd=self.worktree())
        else:
            self.git("branch", "factory/T-0001.1", "main")
            self.git("checkout", "-q", "factory/T-0001.1")
            self.git("commit", "-q", "--allow-empty", "-m", "work")
            head = self.git("rev-parse", "HEAD")
            self.git("checkout", "-q", "main")
        self.ok("ticket", "set", "T-0001.1", "status=checks-in-flight", "branch=factory/T-0001.1", f"head={head}")
        return head

    def checker_checkouts(self) -> list[str]:
        return [ln for ln in self.git("worktree", "list").splitlines() if "/runs/" in ln]


def synced_env(path: Path) -> dict:
    """The `env > synced.env` dump as name -> value (single-line values only, which is all we read)."""
    out = {}
    for line in path.read_text().splitlines():
        name, sep, value = line.partition("=")
        if sep:
            out[name] = value
    return out


def assert_synced_clean(t: Target, dump: Path) -> None:
    env = synced_env(dump)
    assert "VIRTUAL_ENV" not in env and "PYTHONHOME" not in env, env
    assert f"{t.venv}/bin" not in env["PATH"].split(":")
    assert env["T31_CACHE"] == "/tmp/t31-cache", "the run_env exports reach the sync"
    assert env["HOME"] != os.environ["HOME"] and Path(env["HOME"]).is_dir(), "the sync gets a fresh HOME"


def sync_line(text: str) -> list[str]:
    where = text.split("\n## Where you work\n", 1)[1].split("\n## ", 1)[0]
    return [ln for ln in where.splitlines() if ln.startswith("Environment: ")]


def wrapper_in(text: str) -> str:
    section = text.split("\n## Running code\n", 1)[1].split("\n## ", 1)[0]
    found = [s for s in section.split("`")[1::2] if "<command>" in s]
    assert len(found) == 1, section
    return found[0]


PROBE = 'printf "%s|%s|%s\\n" "${VIRTUAL_ENV-unset}" "${PYTHONHOME-unset}" "$PATH"'


def test_the_composed_wrapper_drops_an_inherited_virtual_environment_and_keeps_the_rest_of_path(tmp_path):
    t = Target(tmp_path, None)
    text = t.input_of(t.start("implementer", "T-0001.1"))
    wrapped = wrapper_in(text).replace("<command>", PROBE)
    venv_bin = f"{t.venv}/bin"
    rest = f"/x/one:{venv_bin}x:/x/two:/usr/bin:/bin"  # `<venv>/binx` is not the exact entry, so it stays
    cp = subprocess.run(["sh", "-c", wrapped], capture_output=True, text=True, check=True,
                        env={"VIRTUAL_ENV": str(t.venv), "PYTHONHOME": str(t.venv), "PATH": f"{venv_bin}:{rest}",
                             "HOME": os.environ["HOME"]})
    assert cp.stdout == f"unset|unset|{rest}\n"
    plain = "/x/one:/x/two:/usr/bin:/bin"
    cp = subprocess.run(["sh", "-c", wrapped], capture_output=True, text=True, check=True,
                        env={"PATH": plain, "HOME": os.environ["HOME"]})
    assert cp.stdout == f"unset|unset|{plain}\n", "a PATH with no environment is unchanged"


def test_an_implementer_worktree_is_synced_at_every_dispatch_and_its_input_says_so(tmp_path):
    t = Target(tmp_path, DUMP)
    run_id = t.start("implementer", "T-0001.1")
    dump = t.worktree() / "synced.env"
    assert_synced_clean(t, dump)
    assert t.meta(run_id)["environment_sync"] == DUMP
    lines = sync_line(t.input_of(run_id))
    assert lines == [f"Environment: the harness ran this instance's environment sync, `{DUMP}`, in this checkout "
                     "through the running-code wrapper before you started, so the environment is already synced. "
                     "Do not sync it again unless your change alters the files it is built from."]
    t.ok("run", "finish", run_id, "--status-override", "KILLED")
    dump.unlink()
    again = t.start("implementer", "T-0001.1")
    assert dump.is_file(), "a later dispatch to the same worktree syncs again"
    assert t.meta(again)["environment_sync"] == DUMP


def test_a_reviewer_checkout_is_synced_before_the_reviewer_starts_and_its_input_says_so(tmp_path):
    t = Target(tmp_path, DUMP)
    t.ready_for_checks()
    run_id = t.start("reviewer", "T-0001.1")
    assert_synced_clean(t, t.root / "runs" / run_id / "wt" / "synced.env")
    assert t.meta(run_id)["environment_sync"] == DUMP
    assert len(sync_line(t.input_of(run_id))) == 1


def test_the_parent_close_verifier_checkout_is_synced(tmp_path):
    t = Target(tmp_path, DUMP)
    t.ok("ticket", "set", "T-0001", "status=ready-for-parent-verify")
    run_id = t.start("verifier", "T-0001")
    assert_synced_clean(t, t.root / "runs" / run_id / "wt" / "synced.env")
    assert t.meta(run_id)["environment_sync"] == DUMP
    assert len(sync_line(t.input_of(run_id))) == 1


def assert_refused_and_logged(t: Target, cp: subprocess.CompletedProcess) -> Path:
    assert cp.returncode == 2
    lines = cp.stderr.strip().splitlines()
    assert len(lines) == 1, cp.stderr
    line = lines[0]
    assert line.startswith("environment_sync failed (exit 3) in "), line
    assert not set(line) & set('`$"'), "the refusal carries no shell-expanding character"
    assert "sync-" not in line and "out-line" not in line and "echo" not in line, "nor the command or its output"
    log = Path(line.rsplit(" are in ", 1)[1])
    assert log.name == "environment-sync.log" and log.parent.parent == t.root / "runs"
    body = log.read_text()
    assert FAIL in body and "sync-2" in body and "out-line" in body and "exit: 3" in body
    assert sorted(p.name for p in log.parent.iterdir()) == ["environment-sync.log"], "no meta.yaml, no checkout"
    return log


def test_a_failed_sync_refuses_the_implementer_start_and_keeps_its_worktree(tmp_path):
    t = Target(tmp_path, FAIL)
    cp = t.cli("run", "start", "--role", "implementer", "--ticket", "T-0001.1", venv=True)
    assert_refused_and_logged(t, cp)
    assert t.ticket("T-0001.1")["in_flight"] == []
    assert t.worktree().is_dir(), "the implementer's worktree is kept for the next dispatch"


def test_a_failed_sync_refuses_the_reviewer_start_and_removes_its_checkout(tmp_path):
    t = Target(tmp_path, FAIL)
    t.ready_for_checks()
    cp = t.cli("run", "start", "--role", "reviewer", "--ticket", "T-0001.1", venv=True)
    log = assert_refused_and_logged(t, cp)
    assert not (log.parent / "wt").exists() and t.checker_checkouts() == []
    assert t.ticket("T-0001.1")["in_flight"] == []


@pytest.mark.parametrize("value", ["[uv, sync]", '""', "3"])
def test_a_malformed_environment_sync_is_refused_before_any_checkout_or_run(tmp_path, value):
    t = Target(tmp_path, None)
    inst = Path(t.env["FACTORY_INSTANCE"]) / "instance.yaml"
    inst.write_text(inst.read_text() + f"environment_sync: {value}\n")
    cp = t.cli("run", "start", "--role", "implementer", "--ticket", "T-0001.1", venv=True)
    assert cp.returncode == 2 and "environment_sync" in cp.stderr, cp.stderr
    assert not t.worktree().exists()
    assert not (t.root / "runs").exists() or list((t.root / "runs").iterdir()) == []


def test_without_the_key_nothing_runs_and_no_input_carries_the_line(tmp_path):
    t = Target(tmp_path, None)
    run_id = t.start("implementer", "T-0001.1")
    assert "environment_sync" not in t.meta(run_id) and sync_line(t.input_of(run_id)) == []
    assert t.git("status", "--porcelain", "--untracked-files=all", cwd=t.worktree()) == ""
    t.ok("run", "finish", run_id, "--status-override", "KILLED")
    t.ready_for_checks()
    rev = t.start("reviewer", "T-0001.1")
    assert "environment_sync" not in t.meta(rev) and sync_line(t.input_of(rev)) == []
