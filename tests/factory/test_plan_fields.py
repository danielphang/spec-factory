"""Plan field lines (issue #36, parts C and F2): a planner's `Depends on:` and `Parallel-safe:`
lines are read when they start with a `- ` or `* ` list bullet, with or without bold, and a plan
with a sub-ticket that has no `Depends on:` line is refused with that sub-ticket named.

Black-box through `bin/factory subticket add`, each case on a throwaway store (FACTORY_STATE) whose
T-0001 has passed the spec gate, as the spec's t0019-parent.sh fixture leaves it.
"""
from __future__ import annotations

import subprocess

import pytest

from .test_build_startup import approved_parent, ticket_files
from .test_subtickets import js, run


@pytest.fixture
def store(tmp_path):
    root = tmp_path / "state"
    tid = approved_parent(root, tmp_path)

    def add(plan: str) -> subprocess.CompletedProcess:
        f = tmp_path / "plan.md"
        f.write_text(plan)
        return run(root, "subticket", "add", tid, "--file", str(f))

    add.root = root
    return add


def subtickets(cp: subprocess.CompletedProcess) -> list[tuple]:
    return [(s["label"], s["state"], s["depends_on"], s["parallel_safe"]) for s in js(cp)["subtickets"]]


@pytest.mark.parametrize("bullet", ["- ", "* "])
@pytest.mark.parametrize("bold", [False, True])
def test_bulleted_field_lines_keep_dependencies_and_parallel_safety(store, bullet, bold):
    def field(name: str, value: str) -> str:
        return f"{bullet}**{name}:** {value}" if bold else f"{bullet}{name}: {value}"

    plan = (f"## ST-1 / First\n{field('Depends on', 'none')}\n{field('Parallel-safe', 'no (alone)')}\n\n"
            f"## ST-2 / Second\n{field('Depends on', 'ST-1')}\n{field('Parallel-safe', 'yes')}\n")
    assert subtickets(store(plan)) == [
        ("ST-1", "ready-for-implementer", [], False),
        ("ST-2", "waiting-dependencies", ["T-0001.1"], True),
    ]


def test_a_bullet_never_starts_a_sub_ticket(store):
    plan = "## ST-1 / First\n- Depends on: none\n- ST-2 / a bullet that names a sibling\n"
    assert subtickets(store(plan)) == [("ST-1", "ready-for-implementer", [], False)]


def test_depends_on_none_still_means_no_dependencies(store):
    plan = "ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\n- **Depends on:** none.\n"
    assert subtickets(store(plan)) == [
        ("ST-1", "ready-for-implementer", [], True),
        ("ST-2", "ready-for-implementer", [], False),
    ]


@pytest.mark.parametrize("missing", ["ST-2", "ST-1"])
def test_a_sub_ticket_with_no_depends_on_line_is_refused_by_name(store, missing):
    blocks = {"ST-1": "## ST-1 / First\nDepends on: none\nParallel-safe: yes\n",
              "ST-2": "## ST-2 / Second\nDepends on: ST-1\nParallel-safe: yes\nScope: B\n"}
    blocks[missing] = blocks[missing].replace("Depends on: none\n", "").replace("Depends on: ST-1\n", "")
    cp = store(blocks["ST-1"] + "\n" + blocks["ST-2"])
    assert cp.returncode == 2
    assert missing in cp.stderr and 'Depends on:' in cp.stderr
    assert ticket_files(store.root) == ["T-0001.yaml"]
