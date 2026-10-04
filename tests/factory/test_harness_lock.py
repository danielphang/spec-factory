"""The harness lock (design C.2-C.5), black-box through `bin/factory` in scratch target repos.

The lock guards only the instance's own store: every command except `init` and `paths` is refused
when `<instance>/harness.lock` does not name the running harness revision (C.2), or when the running
harness checkout has uncommitted changes to its own code (C.4). `--accept-harness SHA` (C.3) rewrites
the lock and logs it only when SHA is the running revision, and never overrides C.4.

Cases that run this checkout against an instance's own store are not about C.4, so `cli` runs every
command but `init` and `paths` through `clean_harness_cli.py`, a test-only launcher that stubs only
the C.4 refusal; the lock comparison (C.2, C.3) still runs, and the suite passes in a checkout with
an uncommitted edit. Cases that need a modified or newly committed harness, the C.4 refusal tests
among them, run a local clone's real `bin/factory`, so this checkout is never edited.

Each case strips the conftest's FACTORY_INSTANCE / FACTORY_REPO and any FACTORY_STATE, so the
harness resolves the instance from the working directory, as it does for an operator.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
CLEAN_CLI = Path(__file__).resolve().parent / "clean_harness_cli.py"
STRIP = ("FACTORY_INSTANCE", "FACTORY_REPO", "FACTORY_STATE", "FACTORY_INTEGRATION_BRANCH", "FACTORY_CWD")
HARNESS_PATHS = ("factory", "bin/factory", "agents", "pyproject.toml", "uv.lock")
ZERO = "0" * 40


def subcommand(argv: tuple[str, ...]) -> str | None:
    """The first argument that is not `--accept-harness` or its value."""
    args = iter(argv)
    for arg in args:
        if arg == "--accept-harness":
            next(args, None)
            continue
        return arg
    return None


def cli(harness: Path, cwd: Path, *argv: str, **extra: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k not in STRIP}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", **extra})
    if harness == REPO and subcommand(argv) not in ("init", "paths"):
        cmd = [sys.executable, str(CLEAN_CLI), *argv]
    else:
        cmd = [str(harness / "bin" / "factory"), *argv]
    return subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=cwd)


def git(path: Path, *argv: str) -> str:
    return subprocess.run(["git", "-C", str(path), "-c", "user.name=t", "-c", "user.email=t@t", *argv],
                          check=True, capture_output=True, text=True).stdout


def revision(harness: Path) -> str:
    return git(harness, "log", "-1", "--format=%H", "--", *HARNESS_PATHS).strip()


def tree(path: Path) -> dict[str, bytes]:
    return {str(p.relative_to(path)): p.read_bytes() for p in sorted(path.rglob("*")) if p.is_file()}


def js(cp: subprocess.CompletedProcess) -> dict:
    return json.loads(cp.stdout.strip().splitlines()[-1])


def make_target(path: Path, harness: Path) -> Path:
    path.mkdir(parents=True)
    git(path, "init", "-q", "-b", "main")
    git(path, "commit", "-q", "--allow-empty", "-m", "init")
    cp = cli(harness, path, "init", "--repo-name", "demo")
    assert cp.returncode == 0, cp.stderr
    return path


def lock(target: Path) -> Path:
    return target / ".factory" / "harness.lock"


def tickets(target: Path) -> list[str]:
    d = target / ".factory" / "state" / "tickets"
    return sorted(p.name for p in d.iterdir()) if d.exists() else []


def mismatch(rev: str, locked: str) -> str:
    return (f"harness {rev} is not the revision this instance accepted ({locked}); "
            f"rerun with --accept-harness {rev} to accept it")


@pytest.fixture
def target(tmp_path: Path) -> Path:
    return make_target(tmp_path / "target", REPO)


@pytest.fixture
def request_file(tmp_path: Path) -> Path:
    p = tmp_path / "r.md"
    p.write_text("# demo\n\nDo the thing.\n")
    return p


@pytest.fixture
def clone(tmp_path: Path) -> Path:
    """A local clone of this checkout's HEAD, running on this suite's interpreter environment."""
    c = tmp_path / "h"
    subprocess.run(["git", "clone", "-q", str(REPO), str(c)], check=True, capture_output=True)
    (c / ".venv").symlink_to(Path(sys.prefix))  # untracked, outside the harness paths
    assert (c / ".venv" / "bin" / "python").exists()
    return c


# ----- C.2: the lock must name the running revision -------------------------------------------

def test_fresh_init_lock_is_the_running_revision_and_commands_run(target, request_file):
    assert lock(target).read_text() == revision(REPO) + "\n"
    cp = cli(REPO, target, "ticket", "new", "--file", str(request_file))
    assert cp.returncode == 0, cp.stderr
    assert tickets(target) == ["T-0001.yaml"]


@pytest.mark.parametrize("content,shown", [(ZERO + "\n", ZERO), ("", "none"), (None, "none")],
                         ids=["other-revision", "empty", "missing"])
def test_unaccepted_lock_refused_and_nothing_written(target, request_file, content, shown):
    if content is None:
        lock(target).unlink()
    else:
        lock(target).write_text(content)
    before = tree(target)
    cp = cli(REPO, target, "ticket", "new", "--file", str(request_file))
    assert cp.returncode == 2
    assert cp.stderr.strip() == mismatch(revision(REPO), shown)
    assert tree(target) == before


def test_lock_compares_its_stripped_first_line(target, request_file):
    lock(target).write_text(f"  {revision(REPO)}  \nanything else\n")
    assert cli(REPO, target, "ticket", "new", "--file", str(request_file)).returncode == 0


@pytest.mark.parametrize("argv", [("ticket", "show", "T-0001"), ("config",), ("log", "tail"),
                                  ("ticket", "transition", "T-0001", "--to", "parked", "--by", "t"),
                                  ("run", "start", "--role", "triage", "--ticket", "T-0001")])
def test_every_store_command_is_refused_under_a_mismatch(target, request_file, argv):
    assert cli(REPO, target, "ticket", "new", "--file", str(request_file)).returncode == 0
    lock(target).write_text(ZERO + "\n")
    before = tree(target)
    cp = cli(REPO, target / ".factory", *argv)
    assert cp.returncode == 2, argv
    assert cp.stderr.strip() == mismatch(revision(REPO), ZERO)
    assert tree(target) == before


def test_init_and_paths_are_exempt_and_leave_the_lock(target):
    lock(target).write_text(ZERO + "\n")
    cp = cli(REPO, target, "paths")
    assert cp.returncode == 0, cp.stderr
    assert js(cp)["harness_revision"] == revision(REPO)
    cp = cli(REPO, target, "init")
    assert cp.returncode == 0, cp.stderr
    assert lock(target).read_text() == ZERO + "\n"


def test_throwaway_store_runs_whatever_the_lock_says(target, request_file, tmp_path):
    lock(target).write_text(ZERO + "\n")
    s = tmp_path / "throwaway"
    cp = cli(REPO, target, "ticket", "new", "--file", str(request_file), FACTORY_STATE=str(s))
    assert cp.returncode == 0, cp.stderr
    assert sorted(p.name for p in (s / "tickets").iterdir()) == ["T-0001.yaml"]
    assert tickets(target) == []


def test_factory_state_naming_the_own_store_is_still_checked(target, request_file):
    lock(target).write_text(ZERO + "\n")
    cp = cli(REPO, target, "ticket", "new", "--file", str(request_file),
             FACTORY_STATE=str(target / ".factory" / "state"))
    assert cp.returncode == 2 and "--accept-harness" in cp.stderr
    assert tickets(target) == []


# ----- C.3: --accept-harness ------------------------------------------------------------------

def test_accept_current_revision_rewrites_lock_logs_and_runs(target, request_file):
    lock(target).write_text(ZERO + "\n")
    rev = revision(REPO)
    cp = cli(REPO, target, "--accept-harness", rev, "ticket", "new", "--file", str(request_file))
    assert cp.returncode == 0, cp.stderr
    assert lock(target).read_text() == rev + "\n"
    assert tickets(target) == ["T-0001.yaml"]
    events = [json.loads(ln) for p in sorted((target / ".factory" / "state" / "log").glob("*.jsonl"))
              for ln in p.read_text().splitlines()]
    accepted = [e for e in events if e["event"] == "harness.accepted"]
    assert len(accepted) == 1
    assert accepted[0]["old"] == ZERO and accepted[0]["new"] == rev
    # the acceptance is logged before the command it runs
    assert events.index(accepted[0]) < next(i for i, e in enumerate(events) if e["event"] == "ticket.created")
    # accepted: later commands run without the option
    assert cli(REPO, target, "ticket", "show", "T-0001").returncode == 0


def test_accept_records_a_missing_lock_as_none(target):
    lock(target).unlink()
    rev = revision(REPO)
    cp = cli(REPO, target, "--accept-harness", rev, "config")
    assert cp.returncode == 0, cp.stderr
    assert lock(target).read_text() == rev + "\n"
    logs = (target / ".factory" / "state" / "log").glob("*.jsonl")
    accepted = [json.loads(ln) for p in logs for ln in p.read_text().splitlines()
                if json.loads(ln)["event"] == "harness.accepted"]
    assert [(e["old"], e["new"]) for e in accepted] == [(None, rev)]


@pytest.mark.parametrize("sha", ["1234567", ZERO, "short", "UPPER"], ids=["abbrev", "other-40", "junk", "uppercase"])
def test_accept_other_revision_refused_and_lock_unchanged(target, request_file, sha):
    rev = revision(REPO)
    if sha == "short":
        sha = rev[:12]
    elif sha == "UPPER":
        sha = rev.upper()
    lock(target).write_text(ZERO + "\n")
    before = tree(target)
    cp = cli(REPO, target, "--accept-harness", sha, "ticket", "new", "--file", str(request_file))
    assert cp.returncode == 2
    assert sha in cp.stderr and rev in cp.stderr
    assert tree(target) == before


# ----- C.4: uncommitted harness edits ----------------------------------------------------------

def test_modified_harness_refused_naming_the_paths(clone, tmp_path, request_file):
    t = make_target(tmp_path / "t", clone)
    with (clone / "factory" / "__init__.py").open("a") as fh:
        fh.write("# local edit\n")
    (clone / "agents" / "new-note.md").write_text("x\n")
    before = tree(t)
    cp = cli(clone, t, "ticket", "new", "--file", str(request_file))
    assert cp.returncode == 2
    lines = cp.stderr.strip().split("\n")
    assert lines[0] == f"harness {clone.resolve()} has uncommitted changes:"
    assert sorted(lines[1:]) == ["agents/new-note.md", "factory/__init__.py"]
    assert tree(t) == before


def test_accept_does_not_override_a_modified_harness(clone, tmp_path, request_file):
    t = make_target(tmp_path / "t", clone)
    rev = revision(clone)
    lock(t).write_text(ZERO + "\n")
    with (clone / "bin" / "factory").open("a") as fh:
        fh.write("# local edit\n")
    before = tree(t)
    cp = cli(clone, t, "--accept-harness", rev, "ticket", "new", "--file", str(request_file))
    assert cp.returncode == 2 and "bin/factory" in cp.stderr and "uncommitted changes" in cp.stderr
    assert tree(t) == before


def test_ignored_and_non_harness_changes_do_not_count(clone, tmp_path, request_file):
    t = make_target(tmp_path / "t", clone)
    (clone / "factory" / "__pycache__").mkdir(exist_ok=True)
    (clone / "factory" / "__pycache__" / "x.cpython-311.pyc").write_bytes(b"\0")  # .gitignore'd
    (clone / "README.md").write_text("edited\n")  # not a harness path
    (clone / "tests" / "factory" / "scratch.txt").write_text("x\n")
    cp = cli(clone, t, "ticket", "new", "--file", str(request_file))
    assert cp.returncode == 0, cp.stderr


def test_modified_harness_still_runs_throwaway_stores_init_and_paths(clone, tmp_path, request_file):
    t = make_target(tmp_path / "t", clone)
    with (clone / "factory" / "__init__.py").open("a") as fh:
        fh.write("# local edit\n")
    s = tmp_path / "throwaway"
    cp = cli(clone, t, "ticket", "new", "--file", str(request_file), FACTORY_STATE=str(s))
    assert cp.returncode == 0, cp.stderr
    assert cli(clone, t, "paths").returncode == 0
    assert cli(clone, t, "init").returncode == 0


# ----- the upgrade flow: the revision moves only with harness code (C.1 with C.2, C.3) ---------

def test_upgrade_needs_acceptance_but_other_commits_do_not(clone, tmp_path, request_file):
    t = make_target(tmp_path / "t", clone)
    (clone / "README.md").write_text("docs commit\n")
    git(clone, "commit", "-q", "-am", "docs only")
    assert cli(clone, t, "ticket", "new", "--file", str(request_file)).returncode == 0

    old = revision(clone)
    with (clone / "factory" / "__init__.py").open("a") as fh:
        fh.write("# upgrade\n")
    git(clone, "commit", "-q", "-am", "harness change")
    new = revision(clone)
    assert new != old
    cp = cli(clone, t, "ticket", "show", "T-0001")
    assert cp.returncode == 2 and cp.stderr.strip() == mismatch(new, old)
    assert cli(clone, t, "--accept-harness", new, "ticket", "show", "T-0001").returncode == 0
    assert lock(t).read_text() == new + "\n"
    assert cli(clone, t, "ticket", "show", "T-0001").returncode == 0
