"""Instance and store setup: `factory init`, `factory store migrate` and `factory paths`."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from factory import gitops, instance, specstore, store
from factory.common import _in_flight, fence, out
from factory.store import Refused


def _git_toplevel(cwd: Path) -> Path:
    cp = subprocess.run(["git", "-C", str(cwd), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if cp.returncode != 0 or not cp.stdout.strip():
        raise Refused(f"factory init: {cwd} is not inside a git work tree")
    return Path(cp.stdout.strip()).resolve()


def _new_instance_yaml(repo_name: str) -> str:
    """factory/instance.template.yaml with the per-instance values filled (design B.5)."""
    text = instance.INSTANCE_TEMPLATE.read_text(encoding="utf-8")
    for key, val in (("__REPO_NAME__", repo_name), ("__HARNESS__", str(instance.HARNESS))):
        if key not in text:
            raise Refused(f"{instance.INSTANCE_TEMPLATE} has no {key}")
        text = text.replace(key, json.dumps(val, ensure_ascii=False))
    return text


def _revision() -> str:
    rev = instance.harness_revision()
    if rev is None:
        raise Refused(f"factory init: cannot read the harness revision of {instance.HARNESS} (not a git checkout?)")
    return rev


def _refuse_inside_store(cwd: Path, top: Path) -> None:
    """Refuse `init` from inside the store checkout, where it would build a second instance inside
    the live store (design A.1). Called only with FACTORY_INSTANCE unset."""
    if gitops.git(top, "symbolic-ref", "-q", "HEAD", check=False) == f"refs/heads/{gitops.STORE_BRANCH}":  # unborn too
        raise Refused(f"factory init: {cwd} is inside the store checkout {top} (branch {gitops.STORE_BRANCH}); "
                      "run init from the repository root")
    # Whatever the store has checked out (a detached HEAD, another branch): the instance found by
    # walking up names its store, and a checkout of the same repository at or under it is that store.
    found = instance.find()
    if found is None:
        return
    try:
        cfg = instance.load_config(found)
    except (OSError, yaml.YAMLError):  # an unreadable config names no store: nothing to compare
        return
    if not isinstance(cfg, dict) or not isinstance(cfg.get("state_dir"), str):
        return
    own = instance.own_state_root(found, cfg)
    if top == own or (top.is_relative_to(own)
                      and gitops.common_dir(top) == gitops.common_dir(instance.repo_root(found))):
        raise Refused(f"factory init: {cwd} is inside the store {own} of the instance {found}; "
                      "run init from the repository root")


def _head_branch(repo: Path) -> str:
    """The branch checked out at `repo`, or HEAD when it is detached."""
    return gitops.git(repo, "symbolic-ref", "-q", "--short", "HEAD", check=False) or "HEAD"


def _add_store_checkout(repo: Path, root: Path, branch: str, cfg_path: Path) -> None:
    """Make the missing own store `root` a checkout of the store branch (design A.3): refused at a
    path `branch` has ever tracked; the branch comes from a local branch, else the one remote that
    carries it, else a new orphan, which needs no commit and so no git identity."""
    store_branch = gitops.STORE_BRANCH
    rel = root.relative_to(repo).as_posix() if root.is_relative_to(repo) else None
    if rel is not None:
        sha = gitops.last_tracked(repo, branch, rel)
        if sha:
            raise Refused(f"factory init: {branch} has tracked files under {rel} (last in commit {sha}); a checkout "
                          f"of any older commit would overwrite a store kept there; set another state_dir in {cfg_path}")
    local = bool(gitops.git(repo, "rev-parse", "-q", "--verify", f"refs/heads/{store_branch}", check=False))
    remotes = [] if local else gitops.remote_branches(repo, store_branch)
    if len(remotes) > 1:
        raise Refused(f"factory init: no local branch {store_branch}, and more than one remote carries it "
                      f"({', '.join(remotes)}); run git branch {store_branch} <remote>/{store_branch} for the one "
                      "to use, then init again")
    if local:
        args = ["worktree", "add", "-q", str(root), store_branch]
    elif remotes:
        args = ["worktree", "add", "-q", "--track", "-b", store_branch, str(root), remotes[0]]
    else:
        args = ["worktree", "add", "-q", "--orphan", "-b", store_branch, str(root)]
    try:
        gitops.git(repo, *args)
    except Refused as e:
        raise Refused(f"factory init: cannot check out the store at {root}: {e}") from None
    if rel is not None:
        _exclude_store(repo, rel)


def _exclude_store(repo: Path, rel: str) -> None:
    """The integration checkout ignores the store at `rel` through the repo's exclude file."""
    exclude = Path(gitops.git(repo, "rev-parse", "--git-path", "info/exclude"))
    exclude = exclude if exclude.is_absolute() else repo / exclude
    have = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
    line = f"/{rel}/"
    if line not in have.splitlines():
        store.write_text(exclude, have + ("" if not have or have.endswith("\n") else "\n") + line + "\n")


def _store_hint(repo: Path, root: Path) -> None:
    """An existing own store that is not the store branch's checkout is left alone (design A.5)."""
    top = gitops.git(root, "rev-parse", "--show-toplevel", check=False)
    if top and Path(top).resolve() == root.resolve() and gitops.common_dir(root) == gitops.common_dir(repo):
        if _head_branch(root) == "HEAD":
            print(f"the store worktree {root} is on a detached HEAD; check out {gitops.STORE_BRANCH} there",
                  file=sys.stderr)
        return
    print(f"the store {root} is not on its branch {gitops.STORE_BRANCH}; factory store migrate --to PATH moves it",
          file=sys.stderr)


def init_cmd(a):
    """Create whatever of the instance is missing (design B.5); idempotent. The instance is
    FACTORY_INSTANCE, else `.factory/` at the git top level of the working directory, which may not
    be inside the store checkout (A.1). Its pieces (instance.yaml, context.md, harness.lock, agent
    files) are written only when the store in use is the instance's own: a run on a throwaway store
    (FACTORY_STATE elsewhere, as every test does) initialises that store and nothing else. So
    creating an instance while FACTORY_STATE names another store is refused before anything is
    written: it would leave an instance.yaml with no context.md. A missing own store becomes a git
    worktree of the store branch (A.3) before any instance file is written, so a refusal or a
    failed git step leaves nothing behind."""
    cwd = instance.caller_cwd()
    top = _git_toplevel(cwd)
    if instance.env_path("FACTORY_INSTANCE") is None:
        _refuse_inside_store(cwd, top)
    inst = instance.env_path("FACTORY_INSTANCE") or top / instance.DIRNAME
    created: list[str] = []
    cfg_path = inst / instance.CONFIG_NAME
    new_text = None
    if cfg_path.exists():
        cfg = instance.load_config(inst)
    else:
        if not a.repo_name:
            raise Refused(f"factory init: {cfg_path} does not exist; pass --repo-name NAME to create it")
        new_text = _new_instance_yaml(a.repo_name)
        cfg = yaml.safe_load(new_text)
    root = instance.state_root(inst, cfg)
    fence(inst, cfg, root)
    own = instance.is_own_store(inst, cfg, root)
    if new_text is not None:
        if not own:
            raise Refused(f"factory init: {inst} has no {instance.CONFIG_NAME}, and FACTORY_STATE names another "
                          f"store ({root}); create the instance with FACTORY_STATE unset, then init that store")
        _revision()  # refuse before writing anything if the lock cannot be written
    repo = instance.repo_root(inst)
    existed = root.exists()
    if own and not existed:
        if new_text is None and (os.environ.get("FACTORY_INTEGRATION_BRANCH") or cfg.get("integration_branch")):
            branch = gitops.integration_branch(cfg, repo)
        else:  # its own fallback, rev-parse --abbrev-ref HEAD, fails on an unborn branch, never tracked (A.3.1)
            branch = _head_branch(repo)
        _add_store_checkout(repo, root, branch, cfg_path)
    if new_text is not None:
        store.write_text(cfg_path, new_text)
        created.append(str(cfg_path))
    agents: list[str] = []
    stale: list[str] = []
    store_branch = None
    if own:
        ctx = inst / "context.md"
        if not ctx.exists():
            store.write_text(ctx, instance.CONTEXT_TEMPLATE.read_text(encoding="utf-8"))
            created.append(str(ctx))
        lock = inst / "harness.lock"
        if not lock.exists():
            store.write_text(lock, _revision() + "\n")
            created.append(str(lock))
        dest = repo / ".claude" / "agents"
        for src in sorted(instance.AGENTS.glob("factory-*.md")):
            if not (dest / src.name).exists():
                (dest / src.name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dest / src.name)
                agents.append(str(dest / src.name))
            else:
                # reported, never overwritten; a copy that cannot be read is listed too (T-0058, #114)
                try:
                    differs = not (dest / src.name).is_file() or (dest / src.name).read_bytes() != src.read_bytes()
                except OSError as e:
                    stale.append(str(dest / src.name))
                    print(f"factory init: {dest / src.name} could not be read ({e.strerror or e}); left as it is",
                          file=sys.stderr)
                    continue
                if differs:
                    stale.append(str(dest / src.name))
                    print(f"factory init: {dest / src.name} differs from its template {src}; left as it is",
                          file=sys.stderr)
        checkout = gitops.checkout_of(repo, gitops.STORE_BRANCH)
        if checkout is not None and checkout.resolve() == root:
            store_branch = gitops.STORE_BRANCH
        elif existed:
            _store_hint(repo, root)
    had_gitignore, had_gitattributes = (root / ".gitignore").exists(), (root / ".gitattributes").exists()
    store.ensure_gitignore(root)
    store.ensure_gitattributes(root)
    written = specstore.init(root)
    if not had_gitignore:
        written.insert(0, ".gitignore")
    if not had_gitattributes:
        written.insert(0, ".gitattributes")
    if written or created or agents:
        store.log_event(root, "store.initialised", files=written, instance=created, agents=agents)
    if agents:
        print("restart the session so the agents register", file=sys.stderr)
    out({"ok": True, "written": written, "active": True, "instance": str(inst), "state": str(root),
         "created": created, "agents": agents, "stale_agents": stale, "store_branch": store_branch})


STATE_DIR_LINE = re.compile(r"^(state_dir:[ \t]*)([^#\n]*?)([ \t]*(?:#.*)?)$", re.M)


def _ignored_files(where: Path) -> list[str]:
    """Every file git ignores under the directory `where`, relative to it. Git lists a nested
    repository (a role's clone in its scratch directory) as its directory: its files are listed
    here one by one. Empty directories are not files and are not listed."""
    # factory: empty directories are not carried (git lists no such entry); copy whole trees if a
    # role's scratch ever needs one
    files = []
    listed = gitops.git(where, "ls-files", "--others", "--ignored", "--exclude-standard", "-z", "--", ".")
    for entry in filter(None, listed.split("\0")):
        if entry.endswith("/"):
            files += sorted(p.relative_to(where).as_posix() for p in (where / entry).rglob("*")
                            if p.is_symlink() or p.is_file())
        else:
            files.append(entry)
    return files


def _copy_mismatch(old: Path, new: Path, listed: list[str]) -> str | None:
    """The first way the copy at `new` differs from `old` (design B step 4), or None."""
    for f in listed:
        src, dst = old / f, new / f
        if src.is_symlink():
            same = dst.is_symlink() and os.readlink(dst) == os.readlink(src)
        else:
            same = dst.is_file() and not dst.is_symlink() and dst.read_bytes() == src.read_bytes()
        if not same:
            return f"{f} differs"
    copied = _ignored_files(new)
    if len(copied) != len(listed):
        return f"{len(copied)} ignored files at the new path, {len(listed)} listed"
    status = gitops.git(new, "status", "--porcelain")
    return f"git status there is not clean ({status.splitlines()[0].strip()})" if status else None


def store_migrate(a, root, cfg):
    """Move the instance's own store, a plain directory tracked on the integration branch, onto the
    store branch checked out at --to PATH (design B). Every refusal comes before the first write. A
    copy that does not match is undone and exits 1, before anything is deleted. Makes no commit on
    the integration branch and pushes nothing: the operator reviews and commits both sides."""
    def refuse(msg: str):
        raise Refused(f"factory store migrate: {msg}")

    inst = instance.require()
    repo = instance.repo_root(inst)
    sb = gitops.STORE_BRANCH
    if not instance.is_own_store(inst, cfg, root):
        refuse(f"the store in use, {root}, is not the instance's own (FACTORY_STATE names another); unset FACTORY_STATE")
    old, rel_old = root.resolve(), cfg["state_dir"]
    checkout = gitops.checkout_of(repo, sb)
    if checkout is not None and checkout.resolve() == old:
        refuse(f"the store {old} is already the checkout of {sb}")
    if checkout is not None or gitops.git(repo, "rev-parse", "-q", "--verify", f"refs/heads/{sb}", check=False):
        refuse(f"a local branch {sb} already exists; this command starts it from the store")
    branch, head = gitops.integration_branch(cfg, repo), _head_branch(repo)
    if head == "HEAD" or head != branch:
        refuse(f"the integration branch {'' if head == 'HEAD' else branch + ' '}is not checked out at {repo} "
               f"({'its HEAD is detached' if head == 'HEAD' else head + ' is'}); check it out first")
    runs = _in_flight(root)
    if runs:
        refuse(f"runs in flight on the store: {', '.join(runs)}; wait until they finish")
    under = [ln.split(" ", 1)[1] for ln in gitops.git(repo, "worktree", "list", "--porcelain").splitlines()
             if ln.startswith("worktree ") and Path(ln.split(" ", 1)[1]).resolve().is_relative_to(old)]
    if under:
        refuse(f"git worktrees under the store: {', '.join(under)}; remove them first")
    status = gitops.git(repo, "status", "--porcelain", "--untracked-files=all", "--", rel_old)
    if status:
        names = [ln.strip().split(None, 1)[1] for ln in status.splitlines()]
        refuse(f"uncommitted store files: {', '.join(names)}; commit them on {branch} first")
    new = (repo / a.to).resolve()
    if new.exists():
        refuse(f"{a.to} exists; choose a path that does not")
    if new.is_relative_to(old):
        refuse(f"{a.to} is inside the store {old}, which this command deletes once it has moved")
    rel_new = new.relative_to(repo).as_posix() if new.is_relative_to(repo) else None
    if rel_new is not None:
        sha = gitops.last_tracked(repo, branch, rel_new)  # init's never-tracked test (design A.3.1)
        if sha:
            refuse(f"{branch} has tracked files under {rel_new} (last in commit {sha}); a checkout of any older "
                   "commit would overwrite a store kept there; choose another path")
    cfg_path = inst / instance.CONFIG_NAME
    text = cfg_path.read_text(encoding="utf-8")
    m = STATE_DIR_LINE.search(text)
    if m is None:
        refuse(f"{cfg_path} has no state_dir: line to rewrite")
    tree = gitops.git(repo, "rev-parse", "-q", "--verify", f"{branch}:{rel_old}", check=False)
    if not tree or gitops.git(repo, "cat-file", "-t", tree) != "tree":
        refuse(f"the store {rel_old} is not tracked on {branch}")
    carried = gitops.rev(repo, branch)

    # 1-2. The branch, one root commit of the store as last committed, checked out at PATH.
    created = new  # the outermost directory this command creates, removed on undo
    while not created.parent.exists():
        created = created.parent
    msg = f"store: carried over from {branch} at {carried}; earlier history: git log {carried} -- {rel_old}"
    gitops.git(repo, "branch", sb, gitops.git(repo, "commit-tree", tree, "-m", msg))
    try:
        gitops.git(repo, "worktree", "add", "-q", str(new), sb)
        # 3. The files git ignores, which the branch does not carry: run scratch directories, tripwire baselines.
        listed = _ignored_files(old)
        for f in listed:
            (new / f).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(old / f, new / f, follow_symlinks=False)
        # 4. Verify before deleting anything.
        bad = _copy_mismatch(old, new, listed)
        if bad:
            raise RuntimeError(f"factory store migrate: the copy at {a.to} does not match: {bad}; "
                               f"removed the new worktree and branch {sb}, the store at {rel_old} is unchanged")
    except BaseException:
        gitops.git(repo, "worktree", "remove", "--force", str(new), check=False)
        gitops.git(repo, "worktree", "prune", check=False)
        gitops.git(repo, "branch", "-D", sb, check=False)
        shutil.rmtree(created, ignore_errors=True)
        raise
    # 5. The integration checkout: untrack the old path, ignore the new one, point state_dir at it.
    gitops.git(repo, "rm", "-r", "-q", "--cached", rel_old)
    if rel_new is not None:
        _exclude_store(repo, rel_new)
    store.write_text(cfg_path, text[:m.start(2)] + a.to + text[m.end(2):])
    shutil.rmtree(old)
    # 6.
    fields = {"from": rel_old, "to": a.to, "branch": sb, "carried_from": carried, "copied": len(listed)}
    store.log_event(new, "store.migrated", **fields)
    out({"ok": True, **fields})
    print(f"next: review git status and commit on {branch} (the old store untracked, state_dir now {a.to}); "
          f"then commit the store (git -C {a.to} add -A && git -C {a.to} commit) and push it "
          f"(git push origin {sb})", file=sys.stderr)


def paths_cmd(a):
    """Absolute paths a dispatcher needs (design B.6). Runs no lock check and writes nothing."""
    inst = instance.find()
    state = None
    if inst is not None:
        state = str(instance.state_root(inst, instance.load_config(inst)))
    h = instance.HARNESS
    out({"ok": True, "harness": str(h), "bin": str(h / "bin" / "factory"),
         "intake_workflow": str(h / "factory" / "workflows" / "intake.js"),
         "build_workflow": str(h / "factory" / "workflows" / "build.js"),
         "harness_revision": instance.harness_revision(),
         "instance": str(inst) if inst is not None else None, "state": state})
