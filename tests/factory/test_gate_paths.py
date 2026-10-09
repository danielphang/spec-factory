"""A gate command may declare the git pathspecs it covers (T-0028 part A).

A reviewer or verifier run on a sub-ticket whose diff touches none of a command's paths is told the
command is SKIPPED, with the reason, instead of being asked to run it; the run's meta.yaml and the
`ci` result row record the skip. The implementer still gets every command. A malformed entry refuses
every build role's run start before a run is created.

Black-box through `bin/factory`, on a throwaway store, a copy of the suite's fixture instance with
its own `gate_commands`, and a scratch target repo, as the spec's t0028-sub.sh fixture builds them.
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
FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
UNSCOPED = "git diff --check main...HEAD"
SCOPED = "sh -c 'exit 7'"


class Target:
    """T-0001.1 at checks-in-flight, its one commit changing `changed`; I is its implementer run."""

    def __init__(self, tmp_path: Path, gate: str, changed: str = "docs/b.md"):
        self.tmp = tmp_path
        self.root = tmp_path / "store"
        self.inst = tmp_path / "inst"
        self.repo = tmp_path / "t"
        shutil.copytree(FIXTURE_INSTANCE, self.inst)
        self.set_gate(gate)
        self.env = {**os.environ, "FACTORY_INSTANCE": str(self.inst), "FACTORY_STATE": str(self.root),
                    "FACTORY_REPO": str(self.repo), "FACTORY_INTEGRATION_BRANCH": "main",
                    "PYTHONDONTWRITEBYTECODE": "1"}
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "f@x")
        self.git("config", "user.name", "f")
        for rel, body in (("src/a.txt", "a\n"), ("docs/b.md", "b\n")):
            (self.repo / rel).parent.mkdir(exist_ok=True)
            (self.repo / rel).write_text(body)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "init")
        (tmp_path / "req.md").write_text("# F\n\nDo x.\n")
        (tmp_path / "spec.md").write_text("## Problem\nx\n")
        (tmp_path / "plan.md").write_text("ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n")
        self.ok("ticket", "new", "--file", str(tmp_path / "req.md"))
        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
        self.ok("spec", "add", "T-0001", "--file", str(tmp_path / "spec.md"))
        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
        self.ok("ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t")
        self.ok("approve-spec", "T-0001")
        self.ok("subticket", "add", "T-0001", "--file", str(tmp_path / "plan.md"))
        self.implementer = self.ok("run", "start", "--role", "implementer", "--ticket", "T-0001.1")["run_id"]
        wt = self.root / "worktrees" / "T-0001.1"
        with (wt / changed).open("a") as f:
            f.write("more\n")
        self.git("commit", "-q", "-am", "change", cwd=wt)
        self.ok("run", "finish", self.implementer, "--status-override", "READY-FOR-REVIEW")
        self.head = self.ok("ticket", "head", "T-0001.1")["head"]
        self.ok("ticket", "transition", "T-0001.1", "--to", "checks-in-flight", "--by", "t", "--round", "pr:init")

    def set_gate(self, gate: str) -> None:
        """The fixture instance's config with its one-line `gate_commands` replaced by `gate`."""
        lines = (FIXTURE_INSTANCE / "instance.yaml").read_text().splitlines(keepends=True)
        (self.inst / "instance.yaml").write_text("".join(ln for ln in lines if not ln.startswith("gate_commands:")) + gate)

    def git(self, *argv: str, cwd: Path | None = None) -> str:
        cp = subprocess.run(["git", *argv], cwd=cwd or self.repo, capture_output=True, text=True)
        assert cp.returncode == 0, cp.stderr
        return cp.stdout.strip()

    def cli(self, *argv: str) -> subprocess.CompletedProcess:
        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)

    def ok(self, *argv: str) -> dict:
        cp = self.cli(*argv)
        assert cp.returncode == 0, f"{' '.join(argv)}: {cp.stderr}"
        return json.loads(cp.stdout.strip().splitlines()[-1])

    def composed(self, rid: str) -> tuple[str, dict]:
        self.ok("run", "compose", rid)
        d = self.root / "runs" / rid
        return (d / "input.md").read_text(), yaml.safe_load((d / "meta.yaml").read_text())

    def checker(self, role: str = "verifier") -> tuple[str, str, dict]:
        rid = self.ok("run", "start", "--role", role, "--ticket", "T-0001.1")["run_id"]
        text, meta = self.composed(rid)
        return rid, text, meta


SCOPED_GATE = f'gate_commands:\n  - "{UNSCOPED}"\n  - {{command: "{SCOPED}", paths: ["src/"]}}\n'


def _gate_line(text: str) -> str:
    return next(ln for ln in text.splitlines() if ln.startswith("Worktree:"))


def _skipped_lines(text: str) -> list[str]:
    return [ln for ln in text.splitlines() if ln.startswith("SKIPPED")]


def test_a_scoped_command_is_skipped_for_a_diff_that_touches_none_of_its_paths(tmp_path):
    t = Target(tmp_path, SCOPED_GATE)
    rid, text, meta = t.checker()
    line = _gate_line(text)
    assert UNSCOPED in line and "exit 7" not in line
    base = meta["base"]
    reason = f"the diff {base[:9]}...{t.head[:9]} touches none of its paths: src/"
    assert _skipped_lines(text) == [f"SKIPPED by the harness for this diff, do not run: `{SCOPED}`: {reason}"]
    assert meta["gate_skipped"] == [{"command": SCOPED, "status": "SKIPPED", "reason": reason}]


def test_a_diff_that_touches_a_scoped_command_s_paths_runs_it(tmp_path):
    t = Target(tmp_path, SCOPED_GATE, changed="src/a.txt")
    _, text, meta = t.checker()
    line = _gate_line(text)
    assert UNSCOPED in line and "exit 7" in line
    assert _skipped_lines(text) == [] and meta["gate_skipped"] == []


def test_an_exclude_pathspec_skips_only_a_diff_inside_the_excluded_paths(tmp_path):
    """The Decisions' exclude form: a change outside every excluded path still runs the command."""
    gate = f'gate_commands: [{{command: "{SCOPED}", paths: [":(exclude)docs/"]}}]\n'
    inside = Target(tmp_path / "docs", gate)
    _, text, _ = inside.checker()
    assert "none (every gate command is skipped below)" in _gate_line(text)
    assert len(_skipped_lines(text)) == 1
    outside = Target(tmp_path / "src", gate, changed="src/a.txt")
    _, text, _ = outside.checker()
    assert "exit 7" in _gate_line(text) and _skipped_lines(text) == []


def test_the_implementer_gets_every_command_and_no_skipped_line(tmp_path):
    t = Target(tmp_path, SCOPED_GATE)
    text, meta = t.composed(t.implementer)
    line = _gate_line(text)
    assert UNSCOPED in line and "exit 7" in line
    assert _skipped_lines(text) == [] and meta["gate_skipped"] == []


@pytest.mark.parametrize("gate", ["PASS", "FAIL"])
def test_the_ci_row_records_the_skip_and_its_status_still_comes_from_the_gate_suite_line(tmp_path, gate):
    t = Target(tmp_path, SCOPED_GATE)
    rid, _, meta = t.checker()
    out = tmp_path / "v.md"
    out.write_text(f"Commit: {t.head}\nGate suite: {gate}\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
    t.ok("results", "record", "T-0001.1", "--head", t.head, "--role", "verifier", "--output", str(out), "--run", rid)
    ci = yaml.safe_load((t.root / "results" / t.head / "ci.yaml").read_text())
    assert ci["status"] == gate and ci["skipped"] == meta["gate_skipped"]
    assert "skipped" not in yaml.safe_load((t.root / "results" / t.head / "verifier.yaml").read_text())


def test_a_ci_row_without_a_skip_has_no_skipped_key(tmp_path):
    t = Target(tmp_path, SCOPED_GATE, changed="src/a.txt")
    rid, _, _ = t.checker()
    out = tmp_path / "v.md"
    out.write_text(f"Commit: {t.head}\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
    t.ok("results", "record", "T-0001.1", "--head", t.head, "--role", "verifier", "--output", str(out), "--run", rid)
    assert "skipped" not in yaml.safe_load((t.root / "results" / t.head / "ci.yaml").read_text())


@pytest.mark.parametrize("role", ["implementer", "reviewer", "verifier"])
def test_a_malformed_entry_refuses_every_build_role_s_run_start_and_creates_no_run(tmp_path, role):
    t = Target(tmp_path, SCOPED_GATE)
    if role == "implementer":  # back to the implementer's ready state
        t.ok("ticket", "transition", "T-0001.1", "--to", "ready-for-implementer", "--by", "t")
    t.set_gate('gate_commands: [{command: "true", path: ["src/"]}]\n')
    before = sorted(p.name for p in (t.root / "runs").iterdir())
    cp = t.cli("run", "start", "--role", role, "--ticket", "T-0001.1")
    assert cp.returncode == 2 and "gate_commands entry 0" in cp.stderr and "path" in cp.stderr
    assert sorted(p.name for p in (t.root / "runs").iterdir()) == before


@pytest.fixture(scope="module")
def checks_in_flight(tmp_path_factory):
    """One sub-ticket at checks-in-flight, shared: each refusal below leaves the store unchanged."""
    return Target(tmp_path_factory.mktemp("gate"), SCOPED_GATE)


@pytest.mark.parametrize(("entries", "named"), [
    ("[7]", "entry 0: 7 is neither a string nor a mapping"),
    ("[[a]]", "entry 0: ['a'] is neither a string nor a mapping"),
    ('[{command: "true", path: ["src/"]}]', "entry 0: unknown key path"),
    ('[{paths: ["src/"]}]', "entry 0: command must be a non-empty string"),
    ('[{command: ""}]', "entry 0: command must be a non-empty string"),
    ("[{command: 3}]", "entry 0: command must be a non-empty string"),
    ('[{command: "true", paths: "src/"}]', "entry 0: paths must be a non-empty list"),
    ('[{command: "true", paths: []}]', "entry 0: paths must be a non-empty list"),
    ('[{command: "true", paths: null}]', "entry 0: paths must be a non-empty list"),
    ('[{command: "true", paths: ["src/", ""]}]', "entry 0: paths must be a non-empty list"),
    ('[{command: "true", paths: ["src/", 3]}]', "entry 0: paths must be a non-empty list"),
    ('["ok", {command: "true", paths: []}]', "entry 1: paths must be a non-empty list"),
])
def test_each_malformed_entry_is_refused_by_its_index(checks_in_flight, entries, named):
    t = checks_in_flight
    t.set_gate(f"gate_commands: {entries}\n")
    before = sorted(p.name for p in (t.root / "runs").iterdir())
    cp = t.cli("run", "start", "--role", "reviewer", "--ticket", "T-0001.1")
    assert cp.returncode == 2 and f"gate_commands {named}" in cp.stderr, cp.stderr
    assert "a command that always runs omits paths" in cp.stderr
    assert sorted(p.name for p in (t.root / "runs").iterdir()) == before


@pytest.mark.parametrize("gate", ["gate_commands:\n", "", f'gate_commands: [{{command: "{UNSCOPED}"}}]\n'])
def test_a_null_absent_or_unscoped_mapping_gate_runs_as_a_string_list_does(tmp_path, gate):
    t = Target(tmp_path, SCOPED_GATE)
    t.set_gate(gate)
    _, text, meta = t.checker()
    want = (f"`([ -z \"${{VIRTUAL_ENV:-}}\" ] || PATH=$(printf %s \"$PATH\" | tr : '\\n' | grep -vxF \"$VIRTUAL_ENV/bin\" | paste -sd: -); "
            f"unset VIRTUAL_ENV PYTHONHOME; export HOME=\"$(cd \"$(mktemp -d)\" && pwd -P)\"; {UNSCOPED})`" if UNSCOPED in gate else "")
    assert _gate_line(text).endswith("each is already wrapped): " + want)
    assert _skipped_lines(text) == [] and meta["gate_skipped"] == []


def test_an_unscoped_copy_of_a_skipped_command_still_runs(tmp_path):
    t = Target(tmp_path, f'gate_commands:\n  - "{SCOPED}"\n  - {{command: "{SCOPED}", paths: ["src/"]}}\n')
    _, text, meta = t.checker()
    assert "exit 7" in _gate_line(text) and len(_skipped_lines(text)) == 1
    assert [s["command"] for s in meta["gate_skipped"]] == [SCOPED]
