"""`init` puts a new store on its own branch, `factory-store` (T-0025, part A; issue #46).

A missing own store becomes a git worktree of `factory-store` at the store path, ignored by the
integration checkout through the repo's exclude file, so a store commit never moves the
integration branch and the merge gate no longer sends a sub-ticket back for one. `init` refuses
from inside the store checkout, whatever it has checked out, and at a store path the integration
branch has ever tracked; every refusal writes nothing.

Black-box through `bin/factory` in scratch target repos, with the instance resolved from the
working directory (test_instance.cli strips the conftest's FACTORY_* variables). Commits carry
their identity in GIT_AUTHOR_* / GIT_COMMITTER_*, because the suite runs under a throwaway HOME.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from .test_instance import cli, git_repo, js, tree

BRANCH = "factory-store"
IDENT = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
RULE = "role runs may not write the live store"


def git(cwd: Path, *argv: str, check: bool = True) -> str:
    env = {**os.environ, **IDENT}
    cp = subprocess.run(["git", *argv], cwd=cwd, capture_output=True, text=True, env=env)
    if check:
        assert cp.returncode == 0, (argv, cp.stderr)
    return cp.stdout.strip()


def state(t: Path) -> Path:
    return t / ".factory" / "state"


def exclude(t: Path) -> Path:
    p = Path(git(t, "rev-parse", "--git-path", "info/exclude"))
    return p if p.is_absolute() else t / p


def files(t: Path) -> dict[str, bytes]:
    """Every file under the target, its git directory aside, plus the exclude file."""
    snap = {k: v for k, v in tree(t).items() if not k.startswith(".git/")}
    ex = exclude(t)
    snap["<exclude>"] = ex.read_bytes() if ex.exists() else b""
    return snap


def init(t: Path, *argv: str, **env: str):
    return cli(t, "init", *argv, **env)


@pytest.fixture
def target(tmp_path: Path) -> Path:
    t = git_repo(tmp_path / "target")
    cp = init(t, "--repo-name", "demo")
    assert cp.returncode == 0, cp.stderr
    return t


def request(tmp_path: Path) -> str:
    p = tmp_path / "r.md"
    p.write_text("# demo\n\nDo the thing.\n")
    return str(p)


def start_triage(t: Path, tmp_path: Path) -> Path:
    assert cli(t, "ticket", "new", "--file", request(tmp_path)).returncode == 0
    cp = cli(t, "run", "start", "--role", "triage", "--ticket", "T-0001")
    assert cp.returncode == 0, cp.stderr
    return state(t) / "runs" / js(cp)["run_id"] / "scratch"


def ticket_status(cwd: Path) -> str | None:
    cp = cli(cwd, "ticket", "show", "T-0001", "--json")
    return js(cp).get("state") if cp.returncode == 0 else None


# ----- a new store ----------------------------------------------------------------------------

def test_a_new_store_is_the_checkout_of_its_branch_unseen_by_the_integration_checkout(tmp_path):
    t = git_repo(tmp_path / "target")
    cp = init(t, "--repo-name", "demo")
    assert cp.returncode == 0, cp.stderr
    assert js(cp)["store_branch"] == BRANCH
    assert git(state(t), "symbolic-ref", "HEAD") == f"refs/heads/{BRANCH}"
    assert (state(t) / "decisions.md").is_file() and (state(t) / ".gitignore").is_file()
    seen = git(t, "status", "--porcelain", "--untracked-files=all").splitlines()
    assert seen and not [ln for ln in seen if ".factory/state" in ln], seen
    assert "/.factory/state/" in exclude(t).read_text().splitlines()


def test_a_store_commit_leaves_the_integration_branch_where_it_was(target):
    git(target, "add", "-A")
    git(target, "commit", "-q", "-m", "instance")
    main = git(target, "rev-parse", "main")
    git(state(target), "add", "-A")
    git(state(target), "commit", "-q", "-m", "store: first")
    assert git(target, "rev-parse", "main") == main
    assert git(target, "rev-parse", f"{BRANCH}~0") == git(state(target), "rev-parse", "HEAD")
    assert git(target, "ls-files", ".factory/state") == ""


def test_a_clone_restores_the_store_from_the_branch(target, tmp_path):
    git(target, "add", "-A")
    git(target, "commit", "-q", "-m", "instance")
    git(state(target), "add", "-A")
    git(state(target), "commit", "-q", "-m", "store: first")
    clone = tmp_path / "clone"
    git(tmp_path, "clone", "-q", str(target), str(clone))
    assert not state(clone).exists()
    cp = init(clone)
    assert cp.returncode == 0, cp.stderr
    assert js(cp)["store_branch"] == BRANCH
    assert git(state(clone), "symbolic-ref", "--short", "HEAD") == BRANCH
    assert git(state(clone), "rev-parse", "--abbrev-ref", "@{upstream}") == f"origin/{BRANCH}"
    assert (state(clone) / "decisions.md").read_bytes() == (state(target) / "decisions.md").read_bytes()
    assert js(cp)["written"] == []


def test_two_remotes_carrying_the_branch_are_refused_naming_both(target, tmp_path):
    git(target, "add", "-A")
    git(target, "commit", "-q", "-m", "instance")
    git(state(target), "add", "-A")
    git(state(target), "commit", "-q", "-m", "store: first")
    clone = tmp_path / "clone"
    git(tmp_path, "clone", "-q", str(target), str(clone))
    git(clone, "remote", "add", "nas", str(target))
    git(clone, "fetch", "-q", "nas")
    before = files(clone)
    cp = init(clone)
    assert cp.returncode == 2, cp.stderr
    assert f"origin/{BRANCH}" in cp.stderr and f"nas/{BRANCH}" in cp.stderr
    assert len(cp.stderr.strip().splitlines()) == 1
    assert not state(clone).exists() and files(clone) == before
    assert git(clone, "branch", "--list", BRANCH) == ""


@pytest.mark.parametrize("with_store", [False, True], ids=["decoy-only", "decoy-and-store"])
def test_a_remote_branch_whose_name_only_ends_in_the_store_branch_is_not_the_store(target, tmp_path, with_store):
    """`refs/remotes/*/factory-store`, one path segment for the remote (A.3.2): `origin/x/factory-store`
    is a code branch, neither the store to check out nor a second remote carrying it."""
    git(target, "add", "-A")
    git(target, "commit", "-q", "-m", "instance")
    if with_store:
        git(state(target), "add", "-A")
        git(state(target), "commit", "-q", "-m", "store: first")
    git(target, "checkout", "-q", "-b", f"x/{BRANCH}")
    (target / "code.txt").write_text("code\n")
    git(target, "add", "code.txt")
    git(target, "commit", "-q", "-m", "a code branch")
    git(target, "checkout", "-q", "main")
    clone = tmp_path / "clone"
    git(tmp_path, "clone", "-q", str(target), str(clone))
    assert git(clone, "rev-parse", "-q", "--verify", f"refs/remotes/origin/x/{BRANCH}")
    cp = init(clone)
    assert cp.returncode == 0, cp.stderr
    assert js(cp)["store_branch"] == BRANCH
    assert not (state(clone) / "code.txt").exists()
    if with_store:
        assert git(state(clone), "rev-parse", "--abbrev-ref", "@{upstream}") == f"origin/{BRANCH}"
    else:  # a new orphan: the branch has no commit yet
        assert git(clone, "rev-parse", "-q", "--verify", f"refs/heads/{BRANCH}", check=False) == ""


def test_an_existing_instance_on_an_unborn_branch_counts_as_never_tracked(tmp_path):
    """A.3.1: with no integration_branch configured, an unborn branch at the repo root has tracked
    nothing, so a missing store is created rather than refused with git's error."""
    t = tmp_path / "target"
    t.mkdir()
    git(t, "init", "-q", "-b", "main")
    assert init(t, "--repo-name", "demo").returncode == 0
    subprocess.run(["rm", "-rf", str(state(t))], check=True)
    git(t, "worktree", "prune")
    cp = init(t)
    assert cp.returncode == 0, cp.stderr
    assert js(cp)["store_branch"] == BRANCH
    assert git(state(t), "symbolic-ref", "--short", "HEAD") == BRANCH


def test_a_store_path_the_integration_branch_once_tracked_is_refused(tmp_path):
    t = git_repo(tmp_path / "target")
    state(t).mkdir(parents=True)
    (state(t) / "old.md").write_text("old\n")
    git(t, "add", "-A")
    git(t, "commit", "-q", "-m", "old store")
    git(t, "rm", "-q", "-r", ".factory/state")
    git(t, "commit", "-q", "-m", "store removed")
    removed = git(t, "rev-parse", "HEAD")
    before = files(t)
    cp = init(t, "--repo-name", "demo")
    assert cp.returncode == 2, cp.stderr
    assert ".factory/state" in cp.stderr and removed in cp.stderr and "state_dir" in cp.stderr
    assert len(cp.stderr.strip().splitlines()) == 1
    assert not (t / ".factory").exists() and files(t) == before
    assert git(t, "branch", "--list", BRANCH) == ""


def test_a_failed_worktree_step_writes_no_instance_file(tmp_path):
    t = git_repo(tmp_path / "target")
    git(t, "branch", BRANCH)
    git(t, "worktree", "add", "-q", str(tmp_path / "elsewhere"), BRANCH)
    before = files(t)
    cp = init(t, "--repo-name", "demo")
    assert cp.returncode == 2, cp.stderr
    assert "factory init: cannot check out the store" in cp.stderr
    assert not (t / ".factory").exists() and not (t / ".claude").exists() and files(t) == before


# ----- init from inside the store -------------------------------------------------------------

@pytest.mark.parametrize("detached", [False, True], ids=["on-branch", "detached"])
def test_init_from_inside_the_store_is_refused_and_writes_nothing(target, tmp_path, detached):
    if detached:
        git(state(target), "add", "-A")
        git(state(target), "commit", "-q", "-m", "store: first")
        git(state(target), "checkout", "-q", "--detach")
    scratch = start_triage(target, tmp_path)
    before = files(target)
    cp = init(scratch, "--repo-name", "x")
    assert cp.returncode == 2, cp.stderr
    assert "run init from the repository root" in cp.stderr and len(cp.stderr.strip().splitlines()) == 1
    assert (f"inside the store {state(target).resolve()} of the instance" if detached
            else f"inside the store checkout {state(target).resolve()} (branch {BRANCH})") in cp.stderr
    assert files(target) == before and not (state(target) / ".factory").exists()
    assert ticket_status(scratch) == "ready-for-triage"


def test_with_factory_instance_set_a1_does_not_apply(target, tmp_path):
    """A.1 applies only with FACTORY_INSTANCE unset. With it set and FACTORY_STATE naming a
    throwaway store, init from a run's scratch directory initialises that store; with the own store,
    #45's location rule still refuses it."""
    scratch = start_triage(target, tmp_path)
    inst = str(target / ".factory")
    before = files(target)
    other = tmp_path / "throwaway"
    cp = init(scratch, FACTORY_INSTANCE=inst, FACTORY_STATE=str(other))
    assert cp.returncode == 0, cp.stderr
    assert (other / "decisions.md").is_file() and js(cp)["store_branch"] is None
    cp = init(scratch, FACTORY_INSTANCE=inst, FACTORY_DISPATCH="1")
    assert cp.returncode == 2 and RULE in cp.stderr and "called from inside its runs/" in cp.stderr
    assert files(target) == before


def test_init_in_a_separate_repository_under_a_runs_scratch_directory_makes_its_instance(target, tmp_path):
    scratch = start_triage(target, tmp_path)
    other = git_repo(scratch / "other")
    before = {k: v for k, v in files(target).items() if "/scratch/other/" not in k}
    cp = init(other, "--repo-name", "other")
    assert cp.returncode == 0, cp.stderr
    assert (other / ".factory" / "instance.yaml").is_file() and js(cp)["store_branch"] == BRANCH
    assert {k: v for k, v in files(target).items() if "/scratch/other/" not in k} == before
    assert ticket_status(target) == "ready-for-triage"


# ----- an existing store ----------------------------------------------------------------------

def test_an_existing_plain_store_is_left_alone_and_pointed_to_store_migrate(tmp_path):
    t = git_repo(tmp_path / "target")
    state(t).mkdir(parents=True)
    cp = init(t, "--repo-name", "demo")
    assert cp.returncode == 0, cp.stderr
    assert js(cp)["store_branch"] is None
    assert "factory store migrate --to PATH" in cp.stderr
    assert not (state(t) / ".git").exists() and git(t, "branch", "--list", BRANCH) == ""
    assert "/.factory/state/" not in (exclude(t).read_text() if exclude(t).exists() else "")
    before = files(t)
    again = init(t)
    assert again.returncode == 0 and js(again)["store_branch"] is None and "store migrate" in again.stderr
    assert files(t) == before


def test_a_detached_store_worktree_is_left_alone_with_its_own_hint(target):
    git(state(target), "add", "-A")
    git(state(target), "commit", "-q", "-m", "store: first")
    git(state(target), "checkout", "-q", "--detach")
    before = files(target)
    cp = init(target)
    assert cp.returncode == 0, cp.stderr
    assert js(cp)["store_branch"] is None
    assert "detached HEAD" in cp.stderr and "store migrate" not in cp.stderr
    assert files(target) == before


def test_a_second_init_is_a_no_op(target):
    before = files(target)
    cp = init(target)
    assert cp.returncode == 0, cp.stderr
    out = js(cp)
    assert (out["written"], out["created"], out["agents"], out["store_branch"]) == ([], [], [], BRANCH)
    assert files(target) == before
    assert exclude(target).read_text().splitlines().count("/.factory/state/") == 1


# ----- the merge gate -------------------------------------------------------------------------

@pytest.fixture
def checked(target, tmp_path) -> Path:
    """T-0001 on branch factory/T-0001 with gate PASS, reviewer APPROVE and verifier VERIFIED on its
    head, the instance committed on main."""
    git(target, "add", "-A")
    git(target, "commit", "-q", "-m", "instance")
    git(target, "checkout", "-q", "-b", "factory/T-0001")
    (target / "x.txt").write_text("x\n")
    git(target, "add", "x.txt")
    git(target, "commit", "-q", "-m", "work")
    head = git(target, "rev-parse", "HEAD")
    git(target, "checkout", "-q", "main")
    assert cli(target, "ticket", "new", "--file", request(tmp_path)).returncode == 0
    assert cli(target, "ticket", "set", "T-0001", "status=checks-in-flight", "branch=factory/T-0001",
               f"head={head}").returncode == 0
    for role, body, rid in (("verifier", "Gate suite: PASS\nSTATUS: VERIFIED", "run-0001-verifier"),
                            ("reviewer", "STATUS: APPROVE", "run-0002-reviewer")):
        p = tmp_path / f"{role}.md"
        p.write_text(f"Commit: {head}\n{body}\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
        cp = cli(target, "results", "record", "T-0001", "--head", head, "--role", role, "--output", str(p), "--run", rid)
        assert cp.returncode == 0, cp.stderr
    return target


def test_a_sub_ticket_merges_after_a_store_commit(checked):
    git(state(checked), "add", "-A")
    git(state(checked), "commit", "-q", "-m", "store: rows recorded")
    cp = cli(checked, "merge", "T-0001", **IDENT)
    assert cp.returncode == 0, cp.stderr
    assert js(cp)["state"] == "merged"


def test_a_sub_ticket_is_still_refused_after_a_code_commit(checked):
    (checked / "y.txt").write_text("y\n")
    git(checked, "add", "y.txt")
    git(checked, "commit", "-q", "-m", "code on main")
    cp = cli(checked, "merge", "T-0001", **IDENT)
    assert cp.returncode == 2 and "head does not contain main" in cp.stderr
