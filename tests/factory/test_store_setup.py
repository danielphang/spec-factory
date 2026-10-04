"""Store and instance setup (spec-factory T-0023, parts C, E and F; items H3, H6 and H7).

- C: the store's `.gitattributes` marks run records `-whitespace`, so `git diff --check` skips the
  verbatim diffs and outputs they embed but still checks every other store file. `init` and every
  `run start` write it the way they write `.gitignore`.
- E: `init` refuses to create an instance while FACTORY_STATE names another store, and writes
  nothing; a compose with no `context.md` refuses with exit 2 and writes no input.
- F: a relative FACTORY_STATE, FACTORY_INSTANCE or FACTORY_REPO resolves against the caller's
  directory, not the harness checkout that `bin/factory` changes into.

Black-box through `bin/factory`. Every case uses a throwaway store or a command the harness lock
exempts (`init`, `paths`), so the file passes in a checkout with an uncommitted harness edit.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BIN = REPO / "bin" / "factory"
FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
STRIP = ("FACTORY_INSTANCE", "FACTORY_REPO", "FACTORY_STATE", "FACTORY_INTEGRATION_BRANCH", "FACTORY_CWD")
RULE = "runs/** -whitespace"


def cli(cwd: Path, *argv: str, **env: str) -> subprocess.CompletedProcess:
    """`bin/factory` from `cwd` with only the FACTORY_* variables given here."""
    e = {k: v for k, v in os.environ.items() if k not in STRIP}
    e.update({"PYTHONDONTWRITEBYTECODE": "1", **env})
    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=e, cwd=cwd)


def js(cp: subprocess.CompletedProcess) -> dict:
    assert cp.returncode == 0, cp.stderr
    return json.loads(cp.stdout.strip().splitlines()[-1])


def git(repo: Path, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), "-c", "user.email=f@x", "-c", "user.name=f", *argv],
                          capture_output=True, text=True)


def git_repo(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    assert git(path, "init", "-q", "-b", "main").returncode == 0
    assert git(path, "commit", "-q", "--allow-empty", "-m", "init").returncode == 0
    return path


def commit_all(repo: Path, msg: str) -> None:
    assert git(repo, "add", "-A").returncode == 0
    assert git(repo, "commit", "-q", "-m", msg).returncode == 0


def files(d: Path) -> list[str]:
    return sorted(str(p.relative_to(d)) for p in d.rglob("*") if p.is_file()) if d.exists() else []


def store_env(store: Path) -> dict:
    return {"FACTORY_INSTANCE": str(FIXTURE_INSTANCE), "FACTORY_STATE": str(store)}


def start_triage(tmp_path: Path, store: Path) -> subprocess.CompletedProcess:
    """A new ticket and a triage run start on `store`, with the suite's fixture instance."""
    (tmp_path / "req.md").write_text("# F\n\nDo x.\n")
    js(cli(REPO, "ticket", "new", "--file", str(tmp_path / "req.md"), **store_env(store)))
    return cli(REPO, "run", "start", "--role", "triage", "--ticket", "T-0001", **store_env(store))


# ----- C: run records are exempt from whitespace checks --------------------------------------

def test_init_writes_the_whitespace_rule_and_lists_it_first(tmp_path):
    s = tmp_path / "store"
    out = js(cli(REPO, "init", **store_env(s)))
    lines = (s / ".gitattributes").read_text().splitlines()
    assert lines.count(RULE) == 1 and lines[0].startswith("#") and len(lines) == 2
    assert out["written"][:2] == [".gitattributes", ".gitignore"]
    assert js(cli(REPO, "init", **store_env(s)))["written"] == []


def test_run_start_adds_the_whitespace_rule_to_a_store_without_one(tmp_path):
    s = tmp_path / "store"
    js(start_triage(tmp_path, s))
    assert (s / ".gitattributes").read_text().splitlines().count(RULE) == 1


def test_an_existing_gitattributes_keeps_its_lines_and_gains_the_rule_once(tmp_path):
    s = tmp_path / "store"
    s.mkdir()
    (s / ".gitattributes").write_text("# mine\n*.bin binary")  # no final newline
    js(start_triage(tmp_path, s))
    js(cli(REPO, "init", **store_env(s)))
    assert (s / ".gitattributes").read_text() == f"# mine\n*.bin binary\n{RULE}\n"


def test_an_existing_rule_is_not_duplicated(tmp_path):
    s = tmp_path / "store"
    s.mkdir()
    (s / ".gitattributes").write_text(f"{RULE}\n")
    js(start_triage(tmp_path, s))
    assert (s / ".gitattributes").read_text() == f"{RULE}\n"


def test_git_diff_check_skips_a_committed_run_record_but_not_another_store_file(tmp_path):
    r = git_repo(tmp_path / "r")
    s = r / "store"
    js(cli(REPO, "init", **store_env(s)))
    commit_all(r, "store")
    (s / "runs" / "run-0001-verifier").mkdir(parents=True)
    (s / "runs" / "run-0001-verifier" / "diff.patch").write_text("context \n x\n")
    commit_all(r, "record")
    assert git(r, "diff", "--check", "HEAD~1", "HEAD").returncode == 0
    (s / "notes.md").write_text("x \n")
    commit_all(r, "notes")
    cp = git(r, "diff", "--check", "HEAD~1", "HEAD")
    assert cp.returncode == 2 and "store/notes.md" in cp.stdout


# ----- E: no half instance; a missing briefing refuses -----------------------------------------

def test_init_refuses_to_create_an_instance_on_a_throwaway_store_and_writes_nothing(tmp_path):
    t = git_repo(tmp_path / "tgt")
    s = tmp_path / "s"
    cp = cli(t, "init", "--repo-name", "demo", FACTORY_STATE=str(s))
    assert cp.returncode == 2, cp.stderr
    assert "has no instance.yaml, and FACTORY_STATE names another store" in cp.stderr
    assert str(s.resolve()) in cp.stderr and "create the instance with FACTORY_STATE unset" in cp.stderr
    assert sorted(p.name for p in t.iterdir()) == [".git"] and not s.exists()


def test_init_with_factory_state_naming_the_own_store_still_creates_the_instance(tmp_path):
    t = git_repo(tmp_path / "tgt")
    out = js(cli(t, "init", "--repo-name", "demo", FACTORY_STATE=str(t / ".factory" / "state")))
    assert {Path(p).name for p in out["created"]} == {"instance.yaml", "context.md", "harness.lock"}
    assert (t / ".factory" / "state" / ".gitattributes").is_file()


def test_compose_without_a_briefing_refuses_and_writes_no_input(tmp_path):
    inst = tmp_path / "inst"
    shutil.copytree(FIXTURE_INSTANCE, inst)
    (inst / "context.md").unlink()
    s = tmp_path / "store"
    env = {"FACTORY_INSTANCE": str(inst), "FACTORY_STATE": str(s)}
    (tmp_path / "req.md").write_text("# F\n\nDo x.\n")
    js(cli(REPO, "ticket", "new", "--file", str(tmp_path / "req.md"), **env))
    rid = js(cli(REPO, "run", "start", "--role", "triage", "--ticket", "T-0001", **env))["run_id"]
    cp = cli(REPO, "run", "compose", rid, **env)
    assert cp.returncode == 2, cp.stderr
    assert f"{inst / 'context.md'} is missing: it is the role-context block every role reads first" in cp.stderr
    assert "Traceback" not in cp.stderr
    assert not (s / "runs" / rid / "input.md").exists()


# ----- F: relative environment paths resolve from the caller's directory -----------------------

def test_a_relative_factory_state_resolves_from_the_callers_directory(tmp_path):
    out = js(cli(tmp_path, "paths", FACTORY_INSTANCE=str(FIXTURE_INSTANCE), FACTORY_STATE="rel/store"))
    assert out["state"] == str((tmp_path / "rel" / "store").resolve())


def test_a_relative_factory_instance_resolves_from_the_callers_directory(tmp_path):
    out = js(cli(FIXTURE_INSTANCE.parent, "paths", FACTORY_INSTANCE=FIXTURE_INSTANCE.name))
    assert out["instance"] == str(FIXTURE_INSTANCE.resolve())


def test_a_relative_factory_repo_resolves_from_the_callers_directory(tmp_path):
    out = js(cli(tmp_path, "paths", FACTORY_INSTANCE=str(FIXTURE_INSTANCE), FACTORY_REPO="rel"))
    assert out["state"] == str((tmp_path / "rel" / ".factory" / "state").resolve())


def test_an_absolute_factory_state_is_used_as_given(tmp_path):
    s = tmp_path / "abs"
    out = js(cli(Path("/"), "paths", FACTORY_INSTANCE=str(FIXTURE_INSTANCE), FACTORY_STATE=str(s)))
    assert out["state"] == str(s.resolve())


def test_init_takes_a_relative_factory_instance_from_the_callers_directory(tmp_path):
    """Created with an absolute FACTORY_INSTANCE, then found by init through a relative one. Without
    the fix the relative name points into the harness checkout, where no instance exists, and init
    refuses for want of --repo-name, writing nothing."""
    t = git_repo(tmp_path / "tgt")
    js(cli(t, "init", "--repo-name", "demo", FACTORY_INSTANCE=str(t / "inst-x")))
    out = js(cli(t, "init", FACTORY_INSTANCE="inst-x"))
    assert out["instance"] == str((t / "inst-x").resolve()) and out["created"] == []
