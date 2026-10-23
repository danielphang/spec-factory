"""T-0058 (#88, #114, #115), black-box through `bin/factory`.

- #88: Claude Code's attribution footer below the ESCALATIONS line is dropped before rule (b), in
  `run finish` and `status parse`; a real item line and a line that only mentions Claude Code stay.
- #114: `factory init` lists an agent copy it cannot read under `stale_agents`, says so on stderr,
  exits 0 and leaves the copy as it is.
- #115: `--accept-harness` with `init`, `paths` or `stats` is refused with exit 2 and the `config`
  hint, and writes nothing, on an instance and where init would create one.
"""
from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

import pytest
import yaml

from ._cli import BIN, STRIP, cli, git_repo, js, run, tree
from ._fixtures import snapshot, target  # noqa: F401  (target is a fixture)

FOOTER = "\U0001f916 Generated with [Claude Code](https://claude.com/claude-code)"
SHA = "0123456789abcdef0123456789abcdef01234567"


# ----- #88: the attribution footer -----------------------------------------------------------------

def test_run_finish_drops_the_footer_below_a_none_trailer_and_queues_nothing(tmp_path):
    store = tmp_path / "state"
    req = tmp_path / "r.md"
    req.write_text("# F\n\nDo x.\n")
    run(store, "ticket", "new", "--file", str(req))
    rid = js(run(store, "run", "start", "--role", "triage", "--ticket", "T-0001"))["run_id"]
    run(store, "run", "compose", rid)
    # run-0418's tail: a none trailer, a blank line, the footer
    (store / "runs" / rid / "output.md").write_text(
        "Type: bug\nTitle: T\nSummary: s\nEvidence: e\nAssumptions: a\n"
        f"STATUS: ACCEPT\nCONFIDENCE: high, x\nESCALATIONS: none\n\n{FOOTER}\n", encoding="utf-8")
    cp = run(store, "run", "finish", rid)
    assert cp.returncode == 0, cp.stderr
    assert js(cp)["escalations"] == []
    meta = (store / "runs" / rid / "meta.yaml").read_text(encoding="utf-8")
    assert "Generated with" not in meta and yaml.safe_load(meta)["escalations"] == []
    log = "".join(p.read_text(encoding="utf-8") for p in (store / "log").glob("*.jsonl"))
    assert "escalation.queued" not in log


@pytest.mark.parametrize("tail, want", [
    (f"- the auth path needs review\n\n{FOOTER}\n", ["none", "the auth path needs review"]),
    (f"- {FOOTER}\n", []),  # a list marker before the footer is stripped first
    ("- Generated with Claude Code, says the footer\n", ["none", "Generated with Claude Code, says the footer"]),
    (f"{FOOTER} and more\n", ["none", f"{FOOTER} and more"]),
    ("\U0001f916 Generated with [Claude Code]()\n", ["none", "\U0001f916 Generated with [Claude Code]()"]),
], ids=["item-above-footer", "marked-footer", "mention-only", "footer-plus-text", "footer-no-link"])
def test_status_parse_drops_only_the_exact_footer(tmp_path, tail, want):
    p = tmp_path / "o.md"
    p.write_text(f"body\nSTATUS: APPROVE\nCONFIDENCE: high, ok\nESCALATIONS: none\n{tail}", encoding="utf-8")
    cp = run(tmp_path / "state", "status", "parse", str(p))
    assert cp.returncode == 0, cp.stderr
    assert js(cp)["escalations"] == want


# ----- #114: an agent copy init cannot read --------------------------------------------------------

def test_init_lists_an_unreadable_copy_exits_0_and_leaves_it(tmp_path):
    # assumes the suite runs as a user other than root, since root reads a file at mode 000
    t = git_repo(tmp_path / "target")
    assert cli(t, "init", "--repo-name", "demo").returncode == 0
    copy = t / ".claude" / "agents" / "factory-planner.md"
    kept = copy.read_bytes()
    copy.chmod(0)
    try:
        cp = cli(t, "init")
    finally:
        copy.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
    assert cp.returncode == 0, cp.stderr
    out = js(cp)
    assert out["ok"] is True
    assert [Path(p).name for p in out["stale_agents"]] == ["factory-planner.md"]
    assert out["agents"] == []
    assert copy.read_bytes() == kept
    lines = [ln for ln in cp.stderr.splitlines() if ln.strip()]
    assert len(lines) == 1, cp.stderr
    assert lines[0].startswith(f"factory init: {copy} could not be read (")
    assert lines[0].endswith("; left as it is")


# ----- #115: --accept-harness with the lock-free commands ------------------------------------------

def bare(cwd: Path, *argv: str) -> subprocess.CompletedProcess:
    """`bin/factory` itself: `stats` is not in `cli`'s list of commands that skip the lock stub."""
    env = {k: v for k, v in os.environ.items() if k not in STRIP}
    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, cwd=cwd,
                          env={**env, "PYTHONDONTWRITEBYTECODE": "1"})


@pytest.mark.parametrize("cmd", ["init", "paths", "stats"])
def test_accept_harness_with_a_lock_free_command_is_refused_and_writes_nothing(target, cmd):  # noqa: F811
    lock = (target / ".factory" / "harness.lock").read_text()
    before = snapshot(target)
    cp = bare(target, "--accept-harness", SHA, cmd)
    assert cp.returncode == 2, cp.stderr
    assert js(cp)["ok"] is False
    err = cp.stderr.strip()
    assert len(err.splitlines()) == 1, cp.stderr
    assert f"factory {cmd}" in err and "harness lock" in err
    assert err.endswith(f"factory --accept-harness {SHA} config")
    assert (target / ".factory" / "harness.lock").read_text() == lock
    assert snapshot(target) == before


def test_accept_harness_with_init_creates_no_instance(tmp_path):
    t = git_repo(tmp_path / "fresh")
    cp = bare(t, "--accept-harness", SHA, "init", "--repo-name", "demo")
    assert cp.returncode == 2, cp.stderr
    assert f"factory --accept-harness {SHA} config" in cp.stderr
    assert {k for k in tree(t) if not k.startswith(".git/")} == set()


def test_paths_and_stats_without_the_flag_still_run_under_another_lock(target):  # noqa: F811
    (target / ".factory" / "harness.lock").write_text("0" * 40 + "\n")
    for cmd in ("paths", "stats"):
        cp = bare(target, cmd)
        assert cp.returncode == 0, f"{cmd}: {cp.stderr}"
