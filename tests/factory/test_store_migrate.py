"""`factory store migrate --to PATH` moves an existing store onto its branch (T-0025, part B; issue #46).

The store of an instance made before the store branch is a plain directory tracked on the
integration branch. `store migrate` starts `factory-store` from the store's last committed tree,
checks it out at PATH (a path the integration branch has never tracked), copies the files git
ignores there (run scratch directories, tripwire baselines), verifies the copy, and only then
untracks and deletes the old directory and points `state_dir` at PATH. Every refusal comes before
the first write; a copy that does not match is undone and exits 1.

Black-box through the CLI in scratch target repos, with the instance resolved from the working
directory (test_instance.cli). Commits carry their identity in GIT_AUTHOR_* / GIT_COMMITTER_*,
because the suite runs under a throwaway HOME. These are part C's B items; they live in their own
file because T-0025-A's test_store_branch.py is an existing test file by now.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from .test_instance import REPO, STRIP, cli, git_repo, js, tree
from .test_store_branch import BRANCH, IDENT, exclude, git, request, state

NEW = ".factory/store"
SCRATCH = "runs/run-0001-triage/scratch"


def new(t: Path) -> Path:
    return t / NEW


def migrate(t: Path, to: str = NEW, **env: str):
    return cli(t, "store", "migrate", "--to", to, **{**IDENT, **env})


def snapshot(t: Path) -> dict:
    """Everything a refusal must leave as it was: the files under the target (its git directory
    aside), the exclude file, every ref and every worktree."""
    snap = {k: v for k, v in tree(t).items() if not k.startswith(".git/")}
    ex = exclude(t)
    snap["<exclude>"] = ex.read_bytes() if ex.exists() else b""
    snap["<refs>"] = git(t, "for-each-ref", "--format=%(refname) %(objectname)")
    snap["<worktrees>"] = git(t, "worktree", "list", "--porcelain")
    snap["<index>"] = git(t, "ls-files", "-s")
    return snap


@pytest.fixture
def old(tmp_path: Path) -> Path:
    """A target whose store is a plain directory tracked on main, as both real instances keep it,
    with one ticket and one ignored scratch file; main's last commit is the one that tracks it."""
    t = git_repo(tmp_path / "target")
    state(t).mkdir(parents=True)
    cp = cli(t, "init", "--repo-name", "demo")
    assert cp.returncode == 0, cp.stderr
    assert js(cp)["store_branch"] is None
    assert cli(t, "ticket", "new", "--file", request(tmp_path)).returncode == 0
    git(t, "add", "-A")
    git(t, "commit", "-q", "-m", "instance, with its store on main")
    (state(t) / SCRATCH).mkdir(parents=True)
    (state(t) / SCRATCH / "n.txt").write_text("n\n")
    return t


def ticket_status(cwd: Path) -> str | None:
    cp = cli(cwd, "ticket", "show", "T-0001", "--json")
    return js(cp).get("state") if cp.returncode == 0 else None


# ----- the move -------------------------------------------------------------------------------

def test_migrate_carries_the_store_to_its_branch_at_the_new_path(old):
    pre = git(old, "rev-parse", "HEAD")
    nested = state(old) / SCRATCH / "clone"  # a role's throwaway repository in its scratch directory
    git_repo(nested)
    (nested / "f.txt").write_text("f\n")
    (state(old) / SCRATCH / "link").symlink_to("n.txt")
    ignored = {k: v for k, v in tree(state(old)).items() if k.startswith("runs/")}
    yaml_before = (old / ".factory" / "instance.yaml").read_text()

    cp = migrate(old)
    assert cp.returncode == 0, cp.stderr
    out = js(cp)
    assert out == {"ok": True, "from": ".factory/state", "to": NEW, "branch": BRANCH, "carried_from": pre,
                   "copied": len(ignored)}
    assert "commit" in cp.stderr and f"push origin {BRANCH}" in cp.stderr

    # the branch: one root commit whose tree is the store as last committed, its message naming that commit
    assert git(new(old), "symbolic-ref", "--short", "HEAD") == BRANCH
    assert git(old, "rev-parse", f"{BRANCH}^{{tree}}") == git(old, "rev-parse", f"{pre}:.factory/state")
    assert git(old, "rev-list", "--count", BRANCH) == "1"
    assert pre in git(old, "log", "-1", "--format=%B", BRANCH)
    # the ignored files, byte for byte, the nested repository's and the link included
    assert {k: v for k, v in tree(new(old)).items() if k.startswith("runs/")} == ignored
    assert os.readlink(new(old) / SCRATCH / "link") == "n.txt"
    # the integration checkout: nothing committed, the old path untracked and gone, the new one unseen
    assert git(old, "rev-parse", "HEAD") == pre
    assert not state(old).exists()
    assert git(old, "ls-files", ".factory/state") == ""
    assert f"/{NEW}/" in exclude(old).read_text().splitlines()
    status = git(old, "status", "--porcelain", "--untracked-files=all").splitlines()
    assert status and not [ln for ln in status if NEW in ln], status
    # state_dir: only the value changed, comments kept
    yaml_after = (old / ".factory" / "instance.yaml").read_text()
    assert yaml_after == yaml_before.replace("\nstate_dir: .factory/state\n", f"\nstate_dir: {NEW}\n")
    # later commands find the moved store, and its log records the move
    assert ticket_status(old) == "ready-for-triage"
    assert Path(js(cli(old, "paths"))["state"]).resolve() == new(old).resolve()
    events = [json.loads(ln) for p in sorted((new(old) / "log").glob("*.jsonl")) for ln in p.read_text().splitlines()]
    moved = [e for e in events if e["event"] == "store.migrated"]
    assert len(moved) == 1
    assert {k: moved[0][k] for k in ("from", "to", "branch", "carried_from", "copied")} == {
        k: out[k] for k in ("from", "to", "branch", "carried_from", "copied")}


def test_an_inline_comment_on_the_state_dir_line_is_kept(old):
    cfg = old / ".factory" / "instance.yaml"
    cfg.write_text(cfg.read_text().replace("\nstate_dir: .factory/state\n", "\nstate_dir: .factory/state  # the store\n"))
    git(old, "commit", "-q", "-a", "-m", "comment")
    cp = migrate(old)
    assert cp.returncode == 0, cp.stderr
    assert f"\nstate_dir: {NEW}  # the store\n" in cfg.read_text()
    assert yaml.safe_load(cfg.read_text())["state_dir"] == NEW


def test_a_checkout_of_the_pre_move_commit_leaves_the_new_store_untouched(old):
    pre = git(old, "rev-parse", "HEAD")
    assert migrate(old).returncode == 0
    git(old, "commit", "-q", "-a", "-m", "store moved to its branch")
    (new(old) / "live.md").write_text("live\n")
    before = tree(new(old))
    git(old, "checkout", "-q", pre)
    assert (state(old) / "decisions.md").is_file()  # the old copy is back while the old commit is out
    git(old, "checkout", "-q", "main")
    assert tree(new(old)) == before
    assert not state(old).exists()


# ----- a copy that does not match ---------------------------------------------------------------

# Runs the CLI with shutil.copy2 altering n.txt after copying it, so the copy differs between step 3
# and step 4. Test-only: the harness's own `factory` package collides with this test package's name
# inside pytest, so it runs in a subprocess, as clean_harness_cli.py does.
ALTERING_COPY = """
import os, shutil, sys
from pathlib import Path
os.environ["FACTORY_CWD"] = os.getcwd()
os.chdir(sys.argv[1])
sys.path.insert(0, sys.argv[1])
from factory import cli, instance
instance.harness_changes = lambda *a, **k: []
real = shutil.copy2
def altering(src, dst, *a, **k):
    done = real(src, dst, *a, **k)
    if Path(dst).name == "n.txt":
        Path(dst).write_text("altered\\n")
    return done
shutil.copy2 = altering
raise SystemExit(cli.main(sys.argv[2:]))
"""


def test_a_copy_that_does_not_match_is_undone_and_exits_1(old):
    before = snapshot(old)
    env = {k: v for k, v in os.environ.items() if k not in STRIP}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", **IDENT})
    cp = subprocess.run([sys.executable, "-c", ALTERING_COPY, str(REPO), "store", "migrate", "--to", NEW],
                        capture_output=True, text=True, env=env, cwd=old)
    assert cp.returncode == 1, (cp.stdout, cp.stderr)
    assert f"{SCRATCH}/n.txt" in cp.stderr
    assert snapshot(old) == before
    assert not new(old).exists()
    assert git(old, "branch", "--list", BRANCH) == ""
    assert git(old, "worktree", "list", "--porcelain").count("worktree ") == 1


# ----- refusals ---------------------------------------------------------------------------------

def _throwaway_store(t: Path) -> dict:
    return {"FACTORY_STATE": str(t.parent / "throwaway")}


def _local_branch(t: Path) -> dict:
    git(t, "branch", BRANCH)
    return {}


def _off_the_integration_branch(t: Path) -> dict:
    git(t, "checkout", "-q", "-b", "other")
    return {"FACTORY_INTEGRATION_BRANCH": "main"}


def _detached(t: Path) -> dict:
    git(t, "checkout", "-q", "--detach")
    return {}


def _run_in_flight(t: Path) -> dict:
    cp = cli(t, "run", "start", "--role", "triage", "--ticket", "T-0001")
    assert cp.returncode == 0, cp.stderr
    git(t, "add", "-A")
    git(t, "commit", "-q", "-m", "run started")
    return {"FACTORY_DISPATCH": "1"}  # past #45's fence, so the refusal is migrate's own


def _worktree_under_store(t: Path) -> dict:
    git(t, "worktree", "add", "-q", "-b", "factory/T-0001", str(state(t) / "worktrees" / "T-0001"))
    return {}


def _uncommitted(t: Path) -> dict:
    with (state(t) / "decisions.md").open("a") as fh:
        fh.write("edit\n")
    return {}


def _untracked(t: Path) -> dict:
    (state(t) / "new.md").write_text("new\n")
    return {}


def _path_exists(t: Path) -> dict:
    new(t).mkdir(parents=True)
    return {}


def _path_once_tracked(t: Path) -> dict:
    new(t).mkdir(parents=True)
    (new(t) / "old.md").write_text("old\n")
    git(t, "add", "-A")
    git(t, "commit", "-q", "-m", "once tracked")
    git(t, "rm", "-q", "-r", NEW)
    git(t, "commit", "-q", "-m", "removed")
    return {}


def _no_state_dir_line(t: Path) -> dict:
    cfg = t / ".factory" / "instance.yaml"
    cfg.write_text(cfg.read_text().replace("\nstate_dir: ", '\n"state_dir": '))
    git(t, "commit", "-q", "-a", "-m", "quoted key")
    return {}


REFUSALS = [
    (_throwaway_store, NEW, "not the instance's own"),
    (_local_branch, NEW, f"branch {BRANCH} already exists"),
    (_off_the_integration_branch, NEW, "main is not checked out"),
    (_detached, NEW, "is not checked out"),
    (_run_in_flight, NEW, "runs in flight on the store: run-0002-triage"),  # run-0001 is the fixture's scratch
    (_worktree_under_store, NEW, "worktrees/T-0001"),
    (_uncommitted, NEW, ".factory/state/decisions.md"),
    (_untracked, NEW, ".factory/state/new.md"),
    (_path_exists, NEW, f"{NEW} exists"),
    (_path_once_tracked, NEW, f"has tracked files under {NEW}"),
    (_no_state_dir_line, NEW, "no state_dir: line"),
    (dict, ".factory/state/runs/moved", "inside the store"),
]


@pytest.mark.parametrize("given,to,names", REFUSALS,
                         ids=[g.__name__.strip("_") if g is not dict else "path_inside_the_store" for g, _, _ in REFUSALS])
def test_each_refusal_exits_2_and_writes_nothing(old, given, to, names):
    env = given(old) if given is not dict else {}
    before = snapshot(old)
    cp = migrate(old, to, **env)
    assert cp.returncode == 2, (cp.stdout, cp.stderr)
    assert "factory store migrate:" in cp.stderr and names in cp.stderr, cp.stderr
    assert snapshot(old) == before
    assert git(old, "branch", "--list", BRANCH) == (BRANCH if given is _local_branch else "")
    assert (old / to).exists() == (given is _path_exists)


def test_a_store_already_on_its_branch_is_refused(tmp_path):
    t = git_repo(tmp_path / "target")
    assert cli(t, "init", "--repo-name", "demo").returncode == 0
    before = snapshot(t)
    cp = migrate(t)
    assert cp.returncode == 2 and f"already the checkout of {BRANCH}" in cp.stderr, cp.stderr
    assert snapshot(t) == before
