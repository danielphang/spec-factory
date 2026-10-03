"""Instances (design B): the resolver, `instance.yaml`, the briefing, the filled preamble, `init`,
`paths` and the harness revision, black-box through `bin/factory` in scratch target repos.

Each case strips the conftest's FACTORY_INSTANCE / FACTORY_REPO and any FACTORY_STATE, so the
harness resolves the instance the way it does for an operator: from the working directory.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
BIN = REPO / "bin" / "factory"
STRIP = ("FACTORY_INSTANCE", "FACTORY_REPO", "FACTORY_STATE", "FACTORY_INTEGRATION_BRANCH", "FACTORY_CWD")
NOT_FOUND = "no .factory/instance.yaml found from {cwd}; run factory init --repo-name NAME, or set FACTORY_INSTANCE"


def cli(cwd: Path, *argv: str, **extra: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k not in STRIP}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", **extra})
    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=cwd)


def js(cp: subprocess.CompletedProcess) -> dict:
    return json.loads(cp.stdout.strip().splitlines()[-1])


def git_repo(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    for argv in (["init", "-q", "-b", "main"],
                 ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "init"]):
        subprocess.run(["git", "-C", str(path), *argv], check=True, capture_output=True)
    return path


def tree(path: Path) -> dict[str, bytes]:
    return {str(p.relative_to(path)): p.read_bytes() for p in sorted(path.rglob("*")) if p.is_file()}


def harness_status() -> str:
    return subprocess.run(["git", "-C", str(REPO), "status", "--porcelain"], capture_output=True, text=True).stdout


def revision() -> str:
    return subprocess.run(["git", "-C", str(REPO), "log", "-1", "--format=%H", "--",
                           "factory", "bin/factory", "agents", "pyproject.toml", "uv.lock"],
                          capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture
def target(tmp_path: Path) -> Path:
    """A scratch target repo with an instance made by `factory init` from a subdirectory."""
    t = git_repo(tmp_path / "target")
    (t / "sub").mkdir()
    cp = cli(t / "sub", "init", "--repo-name", "demo")
    assert cp.returncode == 0, cp.stderr
    return t


@pytest.fixture
def request_file(tmp_path: Path) -> Path:
    p = tmp_path / "r.md"
    p.write_text("# demo\n\nDo the thing.\n")
    return p


# ----- init (B.5) -----------------------------------------------------------------------------

def test_init_creates_the_instance_at_the_git_top_level(tmp_path):
    t = git_repo(tmp_path / "target")
    (t / "a" / "b").mkdir(parents=True)
    cp = cli(t / "a" / "b", "init", "--repo-name", "demo")
    assert cp.returncode == 0, cp.stderr
    assert sorted(p.name for p in (t / ".factory").iterdir()) == ["context.md", "harness.lock", "instance.yaml", "state"]
    assert not (t / "a" / ".factory").exists() and not (t / "a" / "b" / ".factory").exists()
    agents = sorted((REPO / "agents").glob("factory-*.md"))
    assert len(agents) == 6
    assert {p.name: p.read_bytes() for p in agents} == tree(t / ".claude" / "agents")
    assert (cp.stdout + cp.stderr).count("restart the session so the agents register") == 1
    assert (t / ".factory" / "context.md").read_bytes() == (REPO / "factory" / "context.template.md").read_bytes()
    assert (t / ".factory" / "harness.lock").read_text() == revision() + "\n"
    state = t / ".factory" / "state"
    assert (state / "openspec" / "config.yaml").is_file() and (state / "decisions.md").is_file()
    assert {"worktrees/", "runs/*/wt/"} <= set((state / ".gitignore").read_text().splitlines())
    out = js(cp)
    assert out["ok"] is True and Path(out["instance"]) == (t / ".factory").resolve()


def test_init_writes_instance_yaml_from_the_template(target):
    cfg = yaml.safe_load((target / ".factory" / "instance.yaml").read_text())
    tpl = yaml.safe_load((REPO / "factory" / "instance.template.yaml").read_text())
    assert cfg["repo_name"] == "demo"
    assert Path(cfg["harness"]) == REPO and Path(cfg["harness"]).is_absolute()
    assert cfg["state_dir"] == ".factory/state"
    assert cfg["protected_paths"] == {"infra": [".factory/instance.yaml", ".factory/harness.lock", ".factory/context.md"]}
    assert cfg["gate_commands"] == []
    assert cfg["integration_branch"] is None and cfg["environment_files"] == [] and cfg["force_push_allowed"] is False
    assert "request_dir" not in cfg
    for key in ("placeholders", "max_rounds", "models", "ready_state", "routing"):
        assert cfg[key] == tpl[key], key
    assert set(cfg) == set(tpl)


def test_init_repo_name_with_yaml_specials_round_trips(tmp_path):
    t = git_repo(tmp_path / "target")
    name = 'spec-factory (the design repo at ~/dev/x: "main", #1)'
    assert cli(t, "init", "--repo-name", name).returncode == 0
    assert yaml.safe_load((t / ".factory" / "instance.yaml").read_text())["repo_name"] == name


def test_init_works_at_its_own_git_top_level_not_an_enclosing_instance(target):
    """A repo nested under a directory that has an instance gets its own; the walk-up then finds it."""
    inner = git_repo(target / "sub" / "inner")
    (inner / "deep").mkdir()
    cp = cli(inner / "deep", "init", "--repo-name", "inner")
    assert cp.returncode == 0, cp.stderr
    assert (inner / ".factory" / "instance.yaml").is_file() and (inner / ".claude" / "agents").is_dir()
    assert Path(js(cli(inner / "deep", "paths"))["instance"]) == (inner / ".factory").resolve()


def test_init_refused_outside_a_git_work_tree(tmp_path):
    d = tmp_path / "plain"
    d.mkdir()
    cp = cli(d, "init", "--repo-name", "x")
    assert cp.returncode == 2 and "not inside a git work tree" in cp.stderr
    assert list(d.iterdir()) == []


def test_init_without_repo_name_refused_and_writes_nothing(tmp_path):
    t = git_repo(tmp_path / "target")
    cp = cli(t, "init")
    assert cp.returncode == 2 and "--repo-name" in cp.stderr
    assert sorted(p.name for p in t.iterdir()) == [".git"]


def test_init_is_idempotent_and_creates_only_what_is_missing(target):
    before = tree(target / ".factory") | {f"claude/{k}": v for k, v in tree(target / ".claude").items()}
    for _ in range(2):
        cp = cli(target, "init")
        assert cp.returncode == 0, cp.stderr
        assert "restart the session" not in cp.stdout + cp.stderr
        assert js(cp)["written"] == [] and js(cp)["created"] == [] and js(cp)["agents"] == []
    assert tree(target / ".factory") | {f"claude/{k}": v for k, v in tree(target / ".claude").items()} == before

    (target / ".factory" / "context.md").unlink()
    (target / ".claude" / "agents" / "factory-planner.md").unlink()
    (target / ".factory" / "state" / "decisions.md").unlink()
    cp = cli(target, "init", "--repo-name", "ignored-when-instance-exists")
    assert cp.returncode == 0, cp.stderr
    assert (cp.stdout + cp.stderr).count("restart the session so the agents register") == 1
    out = js(cp)
    assert out["written"] == ["decisions.md"]
    assert [Path(p).name for p in out["created"]] == ["context.md"]
    assert [Path(p).name for p in out["agents"]] == ["factory-planner.md"]
    assert yaml.safe_load((target / ".factory" / "instance.yaml").read_text())["repo_name"] == "demo"
    after = tree(target / ".factory") | {f"claude/{k}": v for k, v in tree(target / ".claude").items()}
    logs = {k for k in before | after if k.startswith("state/log/")}  # the re-creation is logged
    assert {k: v for k, v in after.items() if k not in logs} == {k: v for k, v in before.items() if k not in logs}


def test_init_on_a_throwaway_store_initialises_only_that_store(target, tmp_path):
    """FACTORY_STATE elsewhere (as in every test): the instance's own pieces are left alone."""
    (target / ".factory" / "harness.lock").unlink()
    (target / ".claude" / "agents" / "factory-triage.md").unlink()
    s = tmp_path / "throwaway"
    cp = cli(target, "init", FACTORY_STATE=str(s))
    assert cp.returncode == 0, cp.stderr
    assert (s / "openspec" / "config.yaml").is_file() and (s / ".gitignore").is_file()
    assert not (target / ".factory" / "harness.lock").exists()
    assert not (target / ".claude" / "agents" / "factory-triage.md").exists()
    assert "restart the session" not in cp.stdout + cp.stderr


def test_the_suite_conftest_init_writes_nothing_into_the_harness(tmp_path):
    """The imported tests run `init` with the conftest's fixture instance and FACTORY_REPO = the
    harness checkout: only their throwaway store may change."""
    fixture = REPO / "tests" / "factory" / "fixtures" / "instance"
    before_fixture, before_status = tree(fixture), harness_status()
    env = {k: v for k, v in os.environ.items() if k not in STRIP}
    env.update(PYTHONDONTWRITEBYTECODE="1", FACTORY_INSTANCE=str(fixture), FACTORY_REPO=str(REPO),
               FACTORY_STATE=str(tmp_path / "s"))
    cp = subprocess.run([str(BIN), "init"], capture_output=True, text=True, env=env, cwd=REPO)
    assert cp.returncode == 0, cp.stderr
    assert (tmp_path / "s" / "openspec").is_dir()
    assert tree(fixture) == before_fixture and harness_status() == before_status


# ----- resolver (B.1, B.2) --------------------------------------------------------------------

def test_store_command_from_a_subdirectory_uses_the_target_instance(target, request_file):
    before = harness_status()
    cp = cli(target / "sub", "ticket", "new", "--file", str(request_file))
    assert cp.returncode == 0, cp.stderr
    assert sorted(p.name for p in (target / ".factory" / "state" / "tickets").iterdir()) == ["T-0001.yaml"]
    assert harness_status() == before


def test_command_outside_any_instance_refused_and_writes_nothing(tmp_path, request_file):
    d = tmp_path / "nowhere"
    d.mkdir()
    for argv in (("ticket", "show", "T-0001"), ("ticket", "new", "--file", str(request_file)), ("config",)):
        cp = cli(d, *argv)
        assert cp.returncode == 2, argv
        assert cp.stderr.strip() == NOT_FOUND.format(cwd=d.resolve()), cp.stderr
        assert list(d.iterdir()) == []


def test_no_fallback_even_with_a_store_named(tmp_path, request_file):
    """FACTORY_STATE alone does not stand in for an instance: config comes only from one."""
    d = tmp_path / "nowhere"
    d.mkdir()
    s = tmp_path / "s"
    cp = cli(d, "ticket", "new", "--file", str(request_file), FACTORY_STATE=str(s))
    assert cp.returncode == 2 and "instance.yaml" in cp.stderr
    assert not s.exists()


def test_factory_instance_overrides_the_working_directory(target, request_file, tmp_path):
    assert cli(target, "ticket", "new", "--file", str(request_file)).returncode == 0
    other = git_repo(tmp_path / "other")
    assert cli(other, "init", "--repo-name", "other").returncode == 0
    cp = cli(other, "ticket", "show", "T-0001", FACTORY_INSTANCE=str(target / ".factory"))
    assert cp.returncode == 0, cp.stderr
    assert yaml.safe_load(cp.stdout)["title"] == "demo"
    assert not (other / ".factory" / "state" / "tickets").exists()


def test_factory_instance_without_instance_yaml_refused(tmp_path):
    d = tmp_path / "empty"
    d.mkdir()
    cp = cli(tmp_path, "ticket", "show", "T-0001", FACTORY_INSTANCE=str(d))
    assert cp.returncode == 2 and "instance.yaml" in cp.stderr and str(d) in cp.stderr


def test_repo_root_is_the_instance_parent_and_factory_repo_overrides(target, tmp_path):
    """An instance directory under any name: state_dir resolves under its parent, or FACTORY_REPO."""
    alt = tmp_path / "elsewhere" / "inst"
    alt.mkdir(parents=True)
    (alt / "instance.yaml").write_bytes((target / ".factory" / "instance.yaml").read_bytes())
    (alt / "context.md").write_text("x\n")
    cp = cli(tmp_path, "config", FACTORY_INSTANCE=str(alt))
    assert cp.returncode == 0, cp.stderr
    assert Path(js(cp)["state_dir"]) == (tmp_path / "elsewhere" / ".factory" / "state").resolve()
    cp = cli(tmp_path, "config", FACTORY_INSTANCE=str(alt), FACTORY_REPO=str(target))
    assert Path(js(cp)["state_dir"]) == (target / ".factory" / "state").resolve()
    cp = cli(tmp_path, "config", FACTORY_INSTANCE=str(alt), FACTORY_STATE=str(tmp_path / "s"))
    assert Path(js(cp)["state_dir"]) == (tmp_path / "s").resolve()


# ----- briefing and preamble (B.3, B.4) -------------------------------------------------------

def _start_triage(target: Path, request_file: Path) -> Path:
    assert cli(target, "ticket", "new", "--file", str(request_file)).returncode == 0
    cp = cli(target, "run", "start", "--role", "triage", "--ticket", "T-0001", "--model", "opus")
    assert cp.returncode == 0, cp.stderr
    return target / ".factory" / "state" / "runs" / js(cp)["run_id"]


def test_composed_input_opens_with_the_instance_context(target, request_file):
    (target / ".factory" / "context.md").write_text("CTX-MARKER for demo\nsecond line\n")
    run = _start_triage(target, request_file)
    cp = cli(target, "run", "compose", run.name)
    assert cp.returncode == 0, cp.stderr
    text = (run / "input.md").read_text()
    assert text.startswith("CTX-MARKER for demo\nsecond line\n## Output file\n")


def test_system_prompt_is_the_design_preamble_filled_from_the_instance(target, request_file):
    run = _start_triage(target, request_file)
    got = (run / "system-prompt.txt").read_text().split("\n")
    block = (REPO / "docs" / "prompts" / "00-preamble.md").read_text().rstrip().split("\n")
    assert got[0] == "You are one agent in a software pipeline: demo. Other agents check"
    i = block.index("  {auth, payments, migrations, infra, public API, dependencies}")
    assert got[i] == "  infra (.factory/instance.yaml, .factory/harness.lock, .factory/context.md)"
    assert [ln for n, ln in enumerate(got[:len(block)]) if n not in (0, i)] == \
        [ln for n, ln in enumerate(block) if n not in (0, i)]
    role = (REPO / "factory" / "prompts" / "triage.md").read_text()
    assert "\n".join(got).endswith("\n\n" + role)
    assert "{repo name}" not in "\n".join(got) and "{auth, payments" not in "\n".join(got)


def test_protected_path_line_lists_every_class(target, request_file):
    p = target / ".factory" / "instance.yaml"
    cfg = yaml.safe_load(p.read_text())
    cfg["protected_paths"] = {"infra": [".factory/**", "intake/**"], "harness": ["factory/**", "bin/factory"],
                              "credentials": "~/.secret/**"}
    p.write_text(yaml.safe_dump(cfg, sort_keys=False))
    run = _start_triage(target, request_file)
    assert ("  infra (.factory/**, intake/**), harness (factory/**, bin/factory), credentials (~/.secret/**)"
            in (run / "system-prompt.txt").read_text().split("\n"))


def test_harness_preamble_is_the_design_doc_block_and_green_overlay_is_gone():
    assert (REPO / "factory" / "prompts" / "preamble.md").read_bytes() == (REPO / "docs" / "prompts" / "00-preamble.md").read_bytes()
    assert not (REPO / "factory" / "config.yaml").exists()
    assert not (REPO / "factory" / "prompts" / "context.md").exists()


# ----- paths (B.6) and the harness revision (C.1) ---------------------------------------------

def test_paths_inside_an_instance(target):
    before = tree(target)
    cp = cli(target / "sub", "paths")
    assert cp.returncode == 0, cp.stderr
    p = js(cp)
    assert Path(p["harness"]) == REPO
    for k in ("harness", "bin", "intake_workflow", "build_workflow", "instance", "state"):
        assert Path(p[k]).is_absolute(), k
    assert Path(p["bin"]) == REPO / "bin" / "factory"
    assert Path(p["intake_workflow"]).is_file() and Path(p["build_workflow"]).is_file()
    assert p["harness_revision"] == revision() and len(p["harness_revision"]) == 40
    assert Path(p["instance"]) == (target / ".factory").resolve()
    assert Path(p["state"]) == (target / ".factory" / "state").resolve()
    assert tree(target) == before


def test_paths_outside_any_instance(tmp_path):
    d = tmp_path / "nowhere"
    d.mkdir()
    cp = cli(d, "paths")
    assert cp.returncode == 0, cp.stderr
    p = js(cp)
    assert p["instance"] is None and p["state"] is None
    assert Path(p["harness"]) == REPO and len(p["harness_revision"]) == 40
    assert list(d.iterdir()) == []


# ----- the suite's own instance (B.9) ---------------------------------------------------------

def test_conftest_points_the_suite_at_the_fixture_instance():
    fixture = (REPO / "tests" / "factory" / "fixtures" / "instance").resolve()
    assert Path(os.environ["FACTORY_INSTANCE"]).resolve() == fixture
    assert os.environ.get("FACTORY_REPO")
    cfg = yaml.safe_load((fixture / "instance.yaml").read_text())
    tpl = yaml.safe_load((REPO / "factory" / "instance.template.yaml").read_text())
    assert cfg["environment_files"] == ["uv.lock"] and cfg["gate_commands"] == ["git diff --check main...HEAD"]
    for key in ("state_dir", "protected_paths", "placeholders", "max_rounds", "integration_branch",
                "force_push_allowed", "models", "ready_state", "routing"):
        assert cfg[key] == tpl[key], key
    assert (fixture / "context.md").is_file()
