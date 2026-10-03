"""`ticket new` reads a request's YAML frontmatter: its title becomes the ticket title, and a
header that does not parse is refused before anything is written.

The frontmatter is optional. Requests imported from issues carry one (`title:`, `labels:`); an
unquoted title containing `: ` is not valid YAML, and before this check such files were imported
silently and only failed later, in an editor's preview.
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


def run(store: Path, *argv: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "FACTORY_STATE": str(store), "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)


@pytest.fixture
def store(tmp_path: Path) -> Path:
    return tmp_path / "state"


def request(tmp_path: Path, text: str) -> Path:
    p = tmp_path / "19_some_issue.md"
    p.write_text(text)
    return p


def test_frontmatter_title_becomes_the_ticket_title(store, tmp_path):
    req = request(tmp_path, '---\ntitle: "Repo layout: the harness moves home"\nlabels: p0, harness\n---\n**Where:** here.\n')
    cp = run(store, "ticket", "new", "--file", str(req))
    assert cp.returncode == 0, cp.stderr
    assert json.loads(cp.stdout)["title"] == "Repo layout: the harness moves home"
    t = yaml.safe_load((store / "tickets" / "T-0001.yaml").read_text())
    assert t["title"] == "Repo layout: the harness moves home"


@pytest.mark.parametrize("header", [
    "---\ntitle: Repo layout: the harness moves home\n---\nbody\n",  # unquoted ': ' in a value
    "---\ntitle: never closed\nbody\n",  # no closing ---
    "---\n- a list\n- not a mapping\n---\nbody\n",
])
def test_invalid_frontmatter_is_refused_and_nothing_is_written(store, tmp_path, header):
    req = request(tmp_path, header)
    cp = run(store, "ticket", "new", "--file", str(req))
    assert cp.returncode == 2
    assert "frontmatter" in cp.stderr
    assert not (store / "tickets").exists() or not list((store / "tickets").glob("T-*.yaml"))
    assert not (store / "requests" / "T-0001.md").exists()


def test_without_frontmatter_the_title_is_the_first_heading_then_the_file_name(store, tmp_path):
    cp = run(store, "ticket", "new", "--file", str(request(tmp_path, "# Fixture heading\n\nbody\n")))
    assert json.loads(cp.stdout)["title"] == "Fixture heading"
    other = tmp_path / "plain.md"
    other.write_text("no heading here\n")
    cp = run(store, "ticket", "new", "--file", str(other))
    assert json.loads(cp.stdout)["title"] == "plain"
