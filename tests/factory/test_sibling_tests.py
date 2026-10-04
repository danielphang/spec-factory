"""The sibling-tests check (issue #40, part B): a sub-ticket's "Tests to change" may list a test file
an earlier sibling of the same parent added, as `` `<file>` (added by <ID>) ``. Before each
implementer run, `run start` checks in git that a merged sibling's recorded merge added the file;
otherwise it refuses with an error that starts `BLOCKED from harness: `, writing nothing, and the
build parks the sub-ticket with that error so `resolve --ruling` returns it to its implementer.

Each case builds the spec's t0022-sib.sh fixture: a throwaway store (FACTORY_STATE) whose parent
T-0001 is planned as ST-1 and ST-2, and a scratch target repository (FACTORY_REPO) whose main holds
tests/test_old.py from before the plan, tests/test_interim.py from ST-1's recorded merge, and
tests/test_operator.py from a later direct commit that is no sibling's merge.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
BIN = REPO / "bin" / "factory"

PLAN = """ST-1 / Interim
Depends on: none
Parallel-safe: yes
Interim tests: `tests/test_interim.py`, broken by ST-2

ST-2 / Final
Depends on: ST-1
Parallel-safe: yes
Scope: B, which reads `tests/test_old.py` (added by the base commit)
Tests to change:
- `{path}` (added by ST-1): ST-2 replaces the interim behaviour
Protected paths: none
"""

# Drives factory/workflows/build.js on parent T-0001: each clerk command runs for real, each role run
# returns an empty output (a killed run). Prints each park as `park <id>: <reason>`.
BUILD_DRIVER = r"""
import { readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const src = readFileSync('factory/workflows/build.js', 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return ''
  const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
  return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
}
const log = (s) => { const p = String(s).match(/^(\S+) parked: (.*)$/s); if (p) console.log(`park ${p[1]}: ${p[2]}`) }
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
  integration: 'main', inlineRoles: true }, agent, log, () => {}, async (fs) => Promise.all(fs.map(f => f())))
"""


class Fixture:
    def __init__(self, tmp_path: Path):
        self.tmp = tmp_path
        self.store = tmp_path / "store"
        self.target = tmp_path / "t"
        self.env = {**os.environ, "FACTORY_STATE": str(self.store), "FACTORY_REPO": str(self.target),
                    "FACTORY_INTEGRATION_BRANCH": "main", "PYTHONDONTWRITEBYTECODE": "1"}

    def cli(self, *argv: str) -> subprocess.CompletedProcess:
        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)

    def ok(self, *argv: str) -> dict:
        cp = self.cli(*argv)
        assert cp.returncode == 0, cp.stderr
        return json.loads(cp.stdout.strip().splitlines()[-1])

    def git(self, *argv: str) -> str:
        cp = subprocess.run(["git", "-c", "user.email=f@x", "-c", "user.name=f", *argv], cwd=self.target,
                            capture_output=True, text=True, check=True)
        return cp.stdout.strip()

    def commit(self, msg: str, **files: str | None) -> str:
        for name, body in files.items():
            p = self.target / "tests" / f"{name}.py"
            if body is None:
                p.unlink()
            else:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(body)
        self.git("add", "-A")
        self.git("commit", "-qm", msg)
        return self.git("rev-parse", "HEAD")

    def status(self, tid: str) -> str:
        return yaml.safe_load((self.store / "tickets" / f"{tid}.yaml").read_text())["status"]

    def runs(self) -> list[str]:
        d = self.store / "runs"
        return sorted(p.name for p in d.iterdir()) if d.exists() else []

    def branch(self) -> str:
        return self.git("branch", "--list", "factory/T-0001.2")


def build(tmp_path: Path, path: str, merged: bool = True, readd: bool = False, plan_text: str | None = None) -> Fixture:
    """The t0022-sib.sh fixture with `path` listed under ST-2's Tests to change. `merged=False` leaves
    T-0001.1 unmerged and the parent with no parent_base. `readd=True` adds two direct commits after
    ST-1's merge: one deletes tests/test_interim.py, the next adds it again. `plan_text` replaces the
    plan."""
    f = Fixture(tmp_path)
    req, spec = tmp_path / "req.md", tmp_path / "spec.md"
    req.write_text("# Fixture\n\nThe bot should do the thing.\n")
    spec.write_text("## Problem\nx\n")
    f.ok("ticket", "new", "--file", str(req))
    f.ok("ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
    f.ok("spec", "add", "T-0001", "--file", str(spec))
    f.ok("ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
    f.ok("ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t")
    f.ok("approve-spec", "T-0001")
    subprocess.run(["git", "init", "-q", "-b", "main", str(f.target)], check=True)
    base = f.commit("base", test_old="def test_old(): pass\n")
    f.git("checkout", "-qb", "sib")
    f.commit("interim", test_interim="def test_interim(): pass\n")
    f.git("checkout", "-q", "main")
    f.git("merge", "-q", "--no-ff", "-m", "Merge ST-1", "sib")
    after = f.git("rev-parse", "HEAD")
    f.commit("operator", test_operator="def test_operator(): pass\n")
    if readd:
        f.commit("drop interim", test_interim=None)
        f.commit("re-add interim", test_interim="def test_interim(): assert True\n")
    plan = tmp_path / "plan.md"
    plan.write_text(plan_text or PLAN.format(path=path))
    f.ok("subticket", "add", "T-0001", "--file", str(plan))
    f.ok("ticket", "transition", "T-0001", "--to", "planned", "--by", "t")
    if merged:
        f.ok("ticket", "set", "T-0001.1", "status=merged", f"merge.base_before='{base}'", f"merge.main_after='{after}'")
        f.ok("ticket", "set", "T-0001", f"parent_base='{base}'")
    f.ok("ticket", "set", "T-0001.2", "status=ready-for-implementer")
    return f


def start(f: Fixture) -> subprocess.CompletedProcess:
    return f.cli("run", "start", "--role", "implementer", "--ticket", "T-0001.2")


def assert_refused(f: Fixture, cp: subprocess.CompletedProcess, path: str) -> str:
    assert cp.returncode == 2, cp.stderr
    error = json.loads(cp.stdout.strip().splitlines()[-1])["error"]
    assert error.startswith("BLOCKED from harness: ") and path in error and "T-0001" in error
    assert f.runs() == [] and f.branch() == "" and f.status("T-0001.2") == "ready-for-implementer"
    assert yaml.safe_load((f.store / "tickets" / "T-0001.2.yaml").read_text())["in_flight"] == []
    return error


@pytest.mark.parametrize("path", ["tests/test_interim.py", "tests/test_interim.py::test_interim"])
def test_a_test_file_a_merged_sibling_added_may_be_listed_and_a_mention_outside_the_field_is_ignored(tmp_path, path):
    f = build(tmp_path, path)
    cp = start(f)
    assert cp.returncode == 0, cp.stderr
    assert f.status("T-0001.2") == "ready-for-implementer"
    assert [r for r in f.runs() if r.endswith("-implementer")] != []


@pytest.mark.parametrize("path", ["tests/test_old.py", "tests/test_operator.py", "tests/test_never.py"])
def test_a_listed_test_that_predates_the_plan_came_from_no_sibling_or_was_never_added_is_refused(tmp_path, path):
    f = build(tmp_path, path)
    error = assert_refused(f, start(f), path)
    assert "since " in error


def test_a_listed_test_is_refused_while_no_sibling_has_merged(tmp_path):
    f = build(tmp_path, "tests/test_interim.py", merged=False)
    error = assert_refused(f, start(f), "tests/test_interim.py")
    assert "(no sibling has merged)" in error


def test_a_file_a_sibling_added_then_deleted_and_re_added_counts_by_its_first_add(tmp_path):
    f = build(tmp_path, "tests/test_interim.py", readd=True)
    cp = start(f)
    assert cp.returncode == 0, cp.stderr


def test_the_build_parks_the_blocked_sub_ticket_with_the_harness_reason_and_a_ruling_sends_it_back(tmp_path):
    node = shutil.which("node")
    assert node, "node must be on PATH: this case runs factory/workflows/build.js"
    f = build(tmp_path, "tests/test_old.py")
    driver = tmp_path / "t0022-build.mjs"
    driver.write_text(BUILD_DRIVER)
    cp = subprocess.run([node, str(driver)], capture_output=True, text=True, env=f.env, cwd=REPO)
    parks = [ln for ln in cp.stdout.splitlines() if ln.startswith("park ")]
    assert len(parks) == 1 and parks[0].startswith("park T-0001.2: BLOCKED from harness: "), cp.stdout + cp.stderr
    assert "tests/test_old.py" in parks[0]
    parked = yaml.safe_load((f.store / "tickets" / "T-0001.2.yaml").read_text())
    assert parked["status"] == "parked" and parked["parked"]["reason"].startswith("BLOCKED from harness: ")
    ruling = tmp_path / "r.md"
    ruling.write_text("Ruling: x\n")
    f.ok("resolve", "T-0001.2", "--ruling", str(ruling))
    assert f.status("T-0001.2") == "ready-for-implementer"


def test_a_mention_in_the_parallel_safe_line_is_not_a_sibling_entry(tmp_path):
    # The form of a stored sub-ticket (Nanobot T-0002.6): `(added by ...)` in its Parallel-safe line,
    # here naming a file that predates the plan, which a Tests to change entry would have to refuse.
    plan = PLAN.split("ST-2 / Final")[0] + (
        "ST-2 / Final\n"
        "- Depends on: ST-1\n"
        "- Parallel-safe: yes with ST-1. It edits `tests/test_old.py` (added by ST-1), and no sibling edits it.\n"
        "- Tests to change: none\n"
        "- Protected paths: none\n")
    f = build(tmp_path, "", plan_text=plan)
    cp = start(f)
    assert cp.returncode == 0, cp.stderr


def test_the_field_ends_at_the_next_plan_field_or_heading_and_takes_bold_bullets_and_test_suffixes(tmp_path):
    # Inside the field: two entries for one sibling-added file (bold field name, `::<test>` suffixes)
    # pass, and a line naming no plan field still belongs to it, so its file is checked and refused.
    # Outside it: the same form naming a file that predates the plan, in the Protected paths field
    # before it and in the plan's shared context, which the store appends under a heading.
    plan = "Grounding: `tests/test_old.py` (added by ST-1)\n\n" + PLAN.split("ST-2 / Final")[0] + (
        "## ST-2 / Final\n"
        "**Depends on:** ST-1\n"
        "**Parallel-safe:** yes\n"
        "**Protected paths:** `tests/test_old.py` (added by ST-1)\n"
        "**Tests to change:**\n"
        "- `tests/test_interim.py::test_interim` (added by ST-1): reason\n"
        "- `tests/test_interim.py::test_other` (added by ST-1): reason\n"
        "  Reason: also `tests/test_never.py` (added by ST-1)\n")
    f = build(tmp_path, "", plan_text=plan)
    text = (f.store / "specs" / "T-0001.2" / "subticket.md").read_text()
    assert "## Shared plan context" in text and text.count("`tests/test_old.py` (added by ST-1)") == 2
    error = assert_refused(f, start(f), "tests/test_never.py")
    assert "tests/test_old.py" not in error and "tests/test_interim.py" not in error
