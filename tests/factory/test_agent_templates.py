"""Role agent templates (`agents/*.md`): every template's frontmatter parses and carries the keys
Claude Code needs, and `factory init` reports an installed copy that differs from its template
without overwriting it.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from ._cli import REPO, cli, git_repo, js

TEMPLATES = sorted((REPO / "agents").glob("*.md"))


@pytest.mark.parametrize("template", TEMPLATES, ids=[p.name for p in TEMPLATES])
def test_template_frontmatter_parses_and_carries_the_agent_keys(template):
    lines = template.read_text(encoding="utf-8").splitlines()
    assert lines[:1] == ["---"], f"{template.name}: line 1 is not ---"
    assert "---" in lines[1:], f"{template.name}: frontmatter has no closing ---"
    header = yaml.safe_load("\n".join(lines[1:lines.index("---", 1)]))
    assert isinstance(header, dict), f"{template.name}: frontmatter is not a mapping"
    missing = {"name", "description", "model", "tools"} - set(header)
    assert not missing, f"{template.name}: frontmatter lacks {sorted(missing)}"


def initialised(tmp_path: Path) -> Path:
    t = git_repo(tmp_path / "target")
    cp = cli(t, "init", "--repo-name", "demo")
    assert cp.returncode == 0, cp.stderr
    return t


def test_init_lists_an_edited_copy_and_leaves_it(tmp_path):
    t = initialised(tmp_path)
    copy = t / ".claude" / "agents" / "factory-planner.md"
    copy.write_bytes(copy.read_bytes() + b"local edit\n")
    kept = copy.read_bytes()
    cp = cli(t, "init")
    assert cp.returncode == 0, cp.stderr
    out = js(cp)
    assert [Path(p).name for p in out["stale_agents"]] == ["factory-planner.md"]
    assert out["agents"] == []
    assert copy.read_bytes() == kept
    template = REPO / "agents" / "factory-planner.md"
    assert f"factory init: {copy} differs from its template {template}; left as it is" in cp.stderr
    assert "restart the session" not in cp.stdout + cp.stderr


def test_init_creates_a_deleted_copy_and_does_not_list_it(tmp_path):
    t = initialised(tmp_path)
    copy = t / ".claude" / "agents" / "factory-triage.md"
    copy.unlink()
    cp = cli(t, "init")
    assert cp.returncode == 0, cp.stderr
    out = js(cp)
    assert [Path(p).name for p in out["agents"]] == ["factory-triage.md"]
    assert out["stale_agents"] == []
    assert copy.read_bytes() == (REPO / "agents" / "factory-triage.md").read_bytes()
    assert "differs" not in cp.stderr


def test_init_with_matching_copies_lists_none(tmp_path):
    cp = cli(initialised(tmp_path), "init")
    assert cp.returncode == 0, cp.stderr
    assert js(cp)["stale_agents"] == [] and js(cp)["agents"] == []
    assert "differs" not in cp.stderr
