"""Git operations for the build half, local-commit stand-in for the PR loop (operator decision
2026-10-02: no remote, no CI; the merge gate is the gate suite plus the two checkers, then a
local --no-ff merge into the integration branch).

The target repo is `repo_root` (FACTORY_REPO, else the parent of the instance directory). Worktrees
live under <store>/worktrees/<run or ticket id>. Nothing here pushes.
"""
from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

from factory import instance, store


def repo_root(cfg: dict | None = None) -> Path:
    return instance.repo_root()


def integration_branch(cfg: dict, repo: Path) -> str:
    env = os.environ.get("FACTORY_INTEGRATION_BRANCH")
    if env:
        return env
    if cfg.get("integration_branch"):
        return cfg["integration_branch"]
    return git(repo, "rev-parse", "--abbrev-ref", "HEAD")


def git(cwd: Path, *args: str, check: bool = True) -> str:
    cp = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and cp.returncode != 0:
        raise store.Refused(f"git {' '.join(args)}: {cp.stderr.strip() or cp.stdout.strip()}")
    return cp.stdout.strip()


def rev(repo: Path, ref: str) -> str:
    return git(repo, "rev-parse", ref)


def branch_of(tid: str) -> str:
    return f"factory/{tid}"


def add_worktree(repo: Path, path: Path, branch: str, start: str, new_branch: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if new_branch:
        git(repo, "worktree", "add", "-q", "-b", branch, str(path), start)
    else:
        git(repo, "worktree", "add", "-q", str(path), branch)


def add_detached_worktree(repo: Path, path: Path, sha: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    git(repo, "worktree", "add", "-q", "--detach", str(path), sha)


def remove_worktree(repo: Path, path: Path) -> None:
    if path.exists():
        git(repo, "worktree", "remove", "--force", str(path), check=False)
    git(repo, "worktree", "prune", check=False)


def copy_environment_files(cfg: dict, repo: Path, dest: Path) -> list[str]:
    """Copy config `environment_files` from the integration checkout into `dest` (overwriting), so the
    branch under test resolves the same environment. Returns the files copied."""
    src = checkout_of(repo, integration_branch(cfg, repo)) or repo
    copied = []
    for rel in cfg.get("environment_files") or []:
        f = src / rel
        if f.is_file():
            (dest / rel).parent.mkdir(parents=True, exist_ok=True)
            (dest / rel).write_bytes(f.read_bytes())
            copied.append(rel)
    return copied


def head_contains(repo: Path, head: str, base: str) -> bool:
    return subprocess.run(["git", "merge-base", "--is-ancestor", base, head], cwd=repo).returncode == 0


def diff(repo: Path, base: str, head: str) -> str:
    return git(repo, "diff", f"{base}...{head}")


def changed_files(repo: Path, base: str, head: str) -> list[str]:
    out = git(repo, "diff", "--name-only", f"{base}...{head}")
    return [ln for ln in out.splitlines() if ln]


def checkout_of(repo: Path, branch: str) -> Path | None:
    """The worktree that has `branch` checked out, if any (`git worktree list --porcelain`)."""
    path = None
    for line in git(repo, "worktree", "list", "--porcelain").splitlines():
        if line.startswith("worktree "):
            path = Path(line.split(" ", 1)[1])
        elif line == f"branch refs/heads/{branch}" and path is not None:
            return path
    return None


STORE_BRANCH = "factory-store"


def common_dir(path: Path) -> str | None:
    """The absolute git common directory of the repository at `path`, None outside one: two
    checkouts of one repository share it, a separate repository has its own."""
    return git(path, "rev-parse", "--path-format=absolute", "--git-common-dir", check=False) or None


def last_tracked(repo: Path, ref: str, path: str) -> str | None:
    """The last commit in `ref`'s history that touched a file under `path` (relative to `repo`),
    or None. A ref with no commit yet (an unborn branch) has tracked nothing."""
    if not git(repo, "rev-parse", "-q", "--verify", f"{ref}^{{commit}}", check=False):
        return None
    return git(repo, "log", "-1", "--format=%H", ref, "--", path) or None


def remote_branches(repo: Path, branch: str) -> list[str]:
    """Every remote-tracking ref `refs/remotes/*/<branch>`, as `<remote>/<branch>`. Git's `*` stops at
    a slash, so a branch under a namespace (`origin/x/<branch>`) is not one."""
    refs = git(repo, "for-each-ref", "--format=%(refname)", f"refs/remotes/*/{branch}").splitlines()
    return [r.removeprefix("refs/remotes/") for r in refs]


class MergeLock:
    """One merge at a time per target repo: a lock directory (mkdir is atomic). Two sibling
    sub-tickets that reach the merge gate together must not run `git merge` in one checkout at once."""

    STALE_S = 600.0

    def __init__(self, repo: Path, wait_s: float = 120.0):
        self.path = Path(git(repo, "rev-parse", "--git-common-dir"))
        if not self.path.is_absolute():
            self.path = repo / self.path
        self.path = self.path / "factory-merge.lock"
        self.wait_s = wait_s

    def __enter__(self):
        deadline = time.monotonic() + self.wait_s
        while True:
            try:
                self.path.mkdir()
                return self
            except FileExistsError:
                try:  # a merge that died leaves its lock; one older than STALE_S is broken
                    if time.time() - self.path.stat().st_mtime > self.STALE_S:
                        self.path.rmdir()
                        continue
                except OSError:
                    continue
                if time.monotonic() > deadline:
                    raise store.Refused(f"merge lock held for more than {int(self.wait_s)}s: {self.path}") from None
                time.sleep(0.2)

    def __exit__(self, *exc):
        try:
            self.path.rmdir()
        except OSError:
            pass


def merge_no_ff(repo: Path, sha: str, into: str, message: str) -> tuple[str, str]:
    """Merge the commit `sha` (the head the checkers saw, not a branch name) into `into` with
    --no-ff. Where `into` is checked out, the merge runs in that checkout (git refuses if local
    changes would be overwritten: a refusal, not a loss, and a failed merge is aborted); otherwise
    in a temporary worktree. The caller holds MergeLock. Returns (before, after) SHAs of `into`."""
    before = rev(repo, into)
    co = checkout_of(repo, into)
    temp = None
    if co is None:
        temp = repo / ".factory-merge-wt"
        remove_worktree(repo, temp)
        git(repo, "worktree", "add", "-q", str(temp), into)
        co = temp
    try:
        try:
            git(co, "merge", "--no-ff", "-m", message, sha)
        except store.Refused:
            git(co, "merge", "--abort", check=False)
            raise
        return before, rev(co, "HEAD")
    finally:
        if temp is not None:
            remove_worktree(repo, temp)


def run_gates(cwd: Path, commands: list[str]) -> tuple[bool, str]:
    """Run the repo's gate commands in `cwd`; (all passed, combined output)."""
    outs = []
    ok = True
    for cmd in commands:
        cp = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        outs.append(f"$ {cmd}\n{cp.stdout}{cp.stderr}".rstrip())
        if cp.returncode != 0:
            ok = False
    return ok, "\n\n".join(outs)
