"""`factory launch-script intake|build` (T-0054, issue #109): a launch copy of a workflow script.

A launch copy is the script with its line `const LAUNCH = null` replaced by one JSON object: the
instance's models, round limits and store as `factory config` prints them, the harness revision and
the instance. The command writes it read-only into a new `factory-launch-*` directory under the
temporary directory, and nothing to the checkout or the store. It is refused wherever `config` is,
runs unmarked while a run is in flight, as `config` does, and first removes launch copies more than
an hour old.

Every test points TMPDIR inside its own tmp_path (the autouse fixture below), and `launch` fails a
test whose copy lands anywhere else, so no test leaves a copy in the real temporary directory.
"""
from __future__ import annotations

import difflib
import json
import os
import stat
import time
from pathlib import Path

import pytest

from ._cli import REPO, cli, git_repo, js, run, tree
from ._fixtures import assert_refused, snapshot, start_triage, target  # noqa: F401  (target is a fixture)
from ._fixtures import other_request as request

PREFIX = "const LAUNCH = "


@pytest.fixture(autouse=True)
def launch_tmp(tmp_path: Path, monkeypatch) -> Path:
    d = tmp_path / "tmp"
    d.mkdir()
    monkeypatch.setenv("TMPDIR", str(d))
    return d


def launch(cp, launch_tmp: Path) -> Path:
    assert cp.returncode == 0, cp.stderr
    script = Path(js(cp)["script"])
    assert script.is_relative_to(launch_tmp), script
    return script


def copies(launch_tmp: Path) -> list[str]:
    return sorted(p.name for p in launch_tmp.glob("factory-launch-*"))


def store_with_a_ticket(tmp_path: Path) -> Path:
    store = tmp_path / "store"
    (tmp_path / "r.md").write_text("# F\n\nDo x.\n")
    assert run(store, "ticket", "new", "--file", str(tmp_path / "r.md")).returncode == 0
    return store


@pytest.mark.parametrize("name", ["intake", "build"])
def test_a_launch_copy_is_its_script_with_one_line_set_to_the_instances_values(tmp_path, launch_tmp, name):
    store = store_with_a_ticket(tmp_path)
    before, checkout = tree(store), run(store, "paths")
    cp = run(store, "launch-script", name)
    script = launch(cp, launch_tmp)
    src = REPO / "factory" / "workflows" / f"{name}.js"
    paths, config = js(checkout), js(run(store, "config"))
    assert script.name == f"{name}.js" and script.parent.parent == launch_tmp and script.parent.name.startswith("factory-launch-")
    assert os.listdir(script.parent) == [f"{name}.js"]
    diff = [ln for ln in difflib.unified_diff(src.read_text().splitlines(), script.read_text().splitlines(), lineterm="", n=0)
            if ln[:1] in "+-" and not ln.startswith(("+++", "---"))]
    assert diff[0] == "-const LAUNCH = null" and len(diff) == 2 and diff[1].startswith("+" + PREFIX)
    assert json.loads(diff[1][1 + len(PREFIX):]) == {
        "written_by": "factory launch-script", "source": str(src), "harness_revision": paths["harness_revision"],
        "instance": paths["instance"], "models": config["models"], "max_rounds": config["max_rounds"],
        "state_dir": config["state_dir"]}
    assert stat.S_IMODE(script.stat().st_mode) == 0o444
    assert js(cp) == {"ok": True, "script": str(script), "source": str(src),
                      "harness_revision": paths["harness_revision"], "instance": paths["instance"]}
    assert tree(store) == before


def test_launch_script_is_refused_with_configs_error_where_the_lock_does_not_name_the_running_harness(tmp_path, launch_tmp):
    t = git_repo(tmp_path / "tgt")
    assert cli(t, "init", "--repo-name", "demo").returncode == 0
    (t / ".factory" / "harness.lock").write_text("0" * 40 + "\n")
    config, cp = cli(t, "config"), cli(t, "launch-script", "build")
    assert config.returncode == 2 and cp.returncode == 2
    assert cp.stderr == config.stderr and "is not the revision this instance accepted" in cp.stderr
    assert copies(launch_tmp) == []


def test_launch_script_runs_unmarked_while_a_run_is_in_flight_and_changes_nothing_in_the_target(target, tmp_path, launch_tmp):
    rid = start_triage(target)
    before = snapshot(target)
    launch(cli(target, "launch-script", "build"), launch_tmp)
    assert_refused(cli(target, "ticket", "new", "--file", request(tmp_path)), f"in flight: {rid}")
    assert snapshot(target) == before and len(copies(launch_tmp)) == 1


def test_launch_script_removes_only_launch_copies_over_an_hour_old(tmp_path, launch_tmp):
    store = store_with_a_ticket(tmp_path)
    old = launch(run(store, "launch-script", "build"), launch_tmp).parent
    fresh = launch(run(store, "launch-script", "intake"), launch_tmp).parent
    other = launch_tmp / "factory-launch-other"  # an old directory that holds no launch copy
    other.mkdir()
    (other / "build.js").write_text("x\n")
    extra = launch_tmp / "factory-launch-extra"  # an old launch copy with a second file beside it
    extra.mkdir()
    (extra / "build.js").write_bytes((old / "build.js").read_bytes())
    (extra / "notes.txt").write_text("x\n")
    hour_ago = time.time() - 3700
    for d in (old, other, extra):
        os.utime(d, (hour_ago, hour_ago))
    new = launch(run(store, "launch-script", "build"), launch_tmp).parent
    assert not old.exists()
    assert fresh.exists() and other.exists() and extra.exists() and new.exists()
    assert copies(launch_tmp) == sorted(d.name for d in (fresh, other, extra, new))
