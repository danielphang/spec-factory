"""The workflow scripts under node with a stand-in clerk that miscopies, as the clerk did on real
runs (T-0054, issues #109 and #112).

- #109: the clerk relayed `factory config` with a role's model retyped. A launch copy (written by
  `factory launch-script`) asks no clerk for the configuration, so every role, and the clerk itself,
  runs on the instance's model; the script launched as it is still parks at the role's run start.
- #112: the clerk relayed a one-line JSON reply pretty-printed over several lines. Both scripts
  read it as that one value.
- A sub-ticket parked by #112 and returned with `resolve --to checks` is merged by the next build
  without another implementer run.

Each clerk command runs for real (sh -c, from this checkout) on a throwaway store; each role is a
stub that writes the STATUS its test gives it. Every test points TMPDIR inside its own tmp_path.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from ._cli import REPO, CliStore, approved_parent, git_repo

# node driver.mjs <script> <ticket>: runs that workflow script on <ticket> of $FACTORY_STATE.
# T_SWAP ({"<role>": "<model>"}) names those models in any clerk reply that lists `models`;
# T_PRETTY=1 relays every JSON reply pretty-printed; T_INSTANCE is passed as the `instance` argument;
# T_PLAYS ({"<role>": "<STATUS>"}) is the STATUS each role's run writes. An implementer commits one
# file in its worktree; a checker's output carries the run's head, the verifier's "Gate suite: PASS".
# Prints one JSON line: every agent call's label and model, each park, and the script's result.
DRIVER = r"""
import { readFileSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const [script, ticket] = process.argv.slice(2)
const swap = JSON.parse(process.env.T_SWAP || '{}')
const plays = JSON.parse(process.env.T_PLAYS || '{}')
const sh = (cmd, cwd) => spawnSync('sh', ['-c', cmd], { cwd, encoding: 'utf8' })
const src = readFileSync(script, 'utf8').replace(/^export const meta/m, 'const meta')
const calls = [], parks = []
const agent = async (prompt, opts) => {
  calls.push({ label: opts.label, model: opts.model })
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = sh(m[1], process.cwd())
    let stdout = cp.stdout, j = null
    try { j = JSON.parse(stdout.trim().split('\n').pop()) } catch (e) { j = null }
    if (j && j.models) { Object.assign(j.models, swap); stdout = JSON.stringify(j) + '\n' }
    if (j && process.env.T_PRETTY) stdout = JSON.stringify(j, null, 2) + '\n'
    return { stdout, exit: cp.status, stderr: cp.stderr }
  }
  const r = prompt.match(/(\S+\/runs\/run-\d+-([a-z_]+))\/input\.md/)
  const meta = readFileSync(`${r[1]}/meta.yaml`, 'utf8')
  const wt = (meta.match(/^worktree: '?([^'\n]+)/m) || [])[1]
  if (r[2] === 'implementer' && wt) sh('echo work > work.txt && git add work.txt && git -c user.email=f@x -c user.name=f commit -qm work', wt)
  const head = (meta.match(/^head: '?([0-9a-f]{40})/m) || [])[1]
  const text = (head && r[2] !== 'implementer' ? `Commit: ${head}\n` : '') + (r[2] === 'verifier' ? 'Gate suite: PASS\n' : '') +
    `STATUS: ${plays[r[2]] || 'NONE'}\nCONFIDENCE: high, stub\nESCALATIONS: none\n`
  writeFileSync(`${r[1]}/output.md`, text)
  return text
}
const log = (s) => { const q = String(s).match(/^(\S+) parked: (.*)$/s); if (q) parks.push(`${q[1]}: ${q[2]}`) }
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
const result = await fn({ ticket, repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
  integration: 'main', inlineRoles: true, ...(process.env.T_INSTANCE ? { instance: process.env.T_INSTANCE } : {}) },
  agent, log, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(JSON.stringify({ calls, parks, result }))
"""

CHECKS = {"reviewer": "APPROVE", "verifier": "VERIFIED"}
BUILD = {"implementer": "READY-FOR-REVIEW", **CHECKS}


@pytest.fixture(autouse=True)
def launch_tmp(tmp_path: Path, monkeypatch) -> Path:
    d = tmp_path / "tmp"
    d.mkdir()
    monkeypatch.setenv("TMPDIR", str(d))
    return d


class Store(CliStore):
    """A throwaway store whose tickets build in a scratch target repository."""

    def __init__(self, tmp_path: Path):
        self.tmp = tmp_path
        self.root = tmp_path / "store"
        self.target = git_repo(tmp_path / "t")
        self.env = {**os.environ, "FACTORY_STATE": str(self.root), "FACTORY_REPO": str(self.target),
                    "FACTORY_INTEGRATION_BRANCH": "main", "PYTHONDONTWRITEBYTECODE": "1"}

    def new_ticket(self) -> str:
        req = self.tmp / "req.md"
        req.write_text("# Fixture\n\nThe bot should do the thing.\n")
        return self.ok("ticket", "new", "--file", str(req))["id"]

    def planned(self) -> None:
        """T-0001 past the spec gate and planned as one sub-ticket, T-0001.1, ready for its implementer."""
        tid = self.new_ticket()
        (self.tmp / "spec.md").write_text("## Problem\nx\n")
        (self.tmp / "plan.md").write_text("ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n")
        approved_parent(self.ok, tid, self.tmp / "spec.md")
        self.ok("subticket", "add", tid, "--file", str(self.tmp / "plan.md"))
        self.ok("ticket", "transition", tid, "--to", "planned", "--by", "t")

    def at_checks(self) -> None:
        """T-0001.1 at checks-in-flight on a branch holding one commit, with no result rows."""
        self.planned()
        for argv in (["checkout", "-qb", "factory/T-0001.1"], ["commit", "-q", "--allow-empty", "-m", "work"],
                     ["checkout", "-q", "main"]):
            self.git(str(self.target), *argv)
        head = self.git(str(self.target), "rev-parse", "factory/T-0001.1")
        self.ok("ticket", "set", "T-0001.1", "status=checks-in-flight", "branch=factory/T-0001.1", f"head={head}")

    def implement(self, status: str) -> None:
        """One implementer run on T-0001.1, as the build runs it, ending with `status`."""
        rid = self.ok("run", "start", "--role", "implementer", "--ticket", "T-0001.1")["run_id"]
        wt = yaml.safe_load((self.root / "runs" / rid / "meta.yaml").read_text())["worktree"]
        (Path(wt) / "work.txt").write_text(rid)
        self.git(wt, "add", "work.txt")
        self.git(wt, "commit", "-qm", "work")
        (self.root / "runs" / rid / "output.md").write_text(f"STATUS: {status}\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
        self.ok("run", "finish", rid)

    def git(self, cwd: str, *argv: str) -> str:
        return subprocess.run(["git", "-C", cwd, "-c", "user.email=f@x", "-c", "user.name=f", *argv],
                              check=True, capture_output=True, text=True).stdout.strip()

    def launch_copy(self, name: str) -> str:
        script = self.ok("launch-script", name)["script"]
        assert Path(script).is_relative_to(self.tmp), script
        return script

    def drive(self, script: str, ticket: str, plays: dict, **env: str) -> dict:
        node = shutil.which("node")
        assert node, "node must be on PATH: this case runs a workflow script"
        driver = self.tmp / "driver.mjs"
        driver.write_text(DRIVER)
        cp = subprocess.run([node, str(driver), script, ticket], capture_output=True, text=True, cwd=REPO,
                            env={**self.env, "T_PLAYS": json.dumps(plays), **env})
        assert cp.returncode == 0, cp.stderr
        return json.loads(cp.stdout.strip().splitlines()[-1])

    def status(self, tid: str) -> str:
        return yaml.safe_load((self.root / "tickets" / f"{tid}.yaml").read_text())["status"]

    def run_models(self, tid: str) -> list[tuple[str, str]]:
        """(role, model) of each run of ticket `tid`, in run order."""
        runs = self.root / "runs"
        metas = [yaml.safe_load((d / "meta.yaml").read_text()) for d in sorted(runs.iterdir())] if runs.exists() else []
        return [(m["role"], m["model"]) for m in metas if m["ticket"] == tid]


def sub_parks(res: dict) -> list[str]:
    """The parks of T-0001.1. After it merges the build goes on to close T-0001 and parks it at
    `archive`: this throwaway store has no spec store."""
    return [p for p in res["parks"] if p.startswith("T-0001.1:")]


def role_of(label: str) -> str:
    return "clerk" if label.startswith("clerk:") else label.split()[0]


def test_a_build_from_its_launch_copy_runs_every_role_and_the_clerk_on_the_instances_model(tmp_path):
    s = Store(tmp_path)
    s.planned()
    models = s.ok("config")["models"]
    swap = {role: "sonnet" for role in ("implementer", "reviewer", "verifier", "clerk")}
    res = s.drive(s.launch_copy("build"), "T-0001", BUILD, T_SWAP=json.dumps(swap))
    assert sub_parks(res) == []
    assert {c["label"] for c in res["calls"] if not c["label"].startswith("clerk:") and c["label"].endswith(" T-0001.1")} == {
        "implementer T-0001.1", "reviewer T-0001.1", "verifier T-0001.1"}
    assert [c for c in res["calls"] if c["model"] != models[role_of(c["label"])]] == []
    assert s.status("T-0001.1") == "merged"
    assert s.run_models("T-0001.1") == [("implementer", "opus"), ("reviewer", "fable"), ("verifier", "opus")]


def test_the_build_script_launched_as_it_is_still_parks_on_a_retyped_model(tmp_path):
    s = Store(tmp_path)
    s.at_checks()
    res = s.drive(str(REPO / "factory" / "workflows" / "build.js"), "T-0001", CHECKS, T_SWAP='{"verifier": "fable"}')
    assert [p.rstrip("\n") for p in res["parks"]] == ["T-0001.1: harness-bug: run start verifier: model fable refused for verifier: the instance names opus"]
    assert s.status("T-0001.1") == "parked" and s.run_models("T-0001.1") == [("reviewer", "fable")]


def test_an_intake_from_its_launch_copy_runs_triage_on_the_instances_model(tmp_path):
    s = Store(tmp_path)
    tid = s.new_ticket()
    res = s.drive(s.launch_copy("intake"), tid, {"triage": "REJECT"}, T_SWAP='{"triage": "fable"}')
    assert [c for c in res["calls"] if not c["label"].startswith("clerk:")] == [{"label": f"triage {tid}", "model": "opus"}]
    assert s.status(tid) == "closed" and s.run_models(tid) == [("triage", "opus")]


@pytest.mark.parametrize("name", ["intake", "build"])
def test_a_launch_copy_launched_for_another_instance_runs_nothing(tmp_path, name):
    s = Store(tmp_path)
    s.at_checks()
    instance = s.ok("paths")["instance"]
    res = s.drive(s.launch_copy(name), "T-0001", CHECKS, T_INSTANCE=str(tmp_path / "other"))
    assert res["result"]["error"] == f"launch copy written for instance {instance}, launched with {tmp_path / 'other'}"
    assert res["calls"] == [] and s.status("T-0001.1") == "checks-in-flight" and s.run_models("T-0001.1") == []


def test_a_build_whose_every_reply_is_pretty_printed_merges(tmp_path):
    s = Store(tmp_path)
    s.planned()
    res = s.drive(str(REPO / "factory" / "workflows" / "build.js"), "T-0001", BUILD, T_PRETTY="1")
    assert sub_parks(res) == [] and s.status("T-0001.1") == "merged"
    assert s.run_models("T-0001.1") == [("implementer", "opus"), ("reviewer", "fable"), ("verifier", "opus")]


def test_an_intake_whose_every_reply_is_pretty_printed_closes(tmp_path):
    s = Store(tmp_path)
    tid = s.new_ticket()
    res = s.drive(str(REPO / "factory" / "workflows" / "intake.js"), tid, {"triage": "REJECT"}, T_PRETTY="1")
    assert res["result"]["state"] == "closed" and s.status(tid) == "closed"
    assert s.run_models(tid) == [("triage", "opus")]


def test_a_sub_ticket_returned_to_its_checks_is_merged_without_another_implementer_run(tmp_path):
    s = Store(tmp_path)
    s.planned()
    s.implement("READY-FOR-REVIEW")
    s.ok("ticket", "park", "T-0001.1", "--reason", "harness-bug: run finish implementer: exit 0, no JSON on stdout")
    s.ok("resolve", "T-0001.1", "--to", "checks")
    res = s.drive(str(REPO / "factory" / "workflows" / "build.js"), "T-0001", CHECKS)
    assert sub_parks(res) == [] and s.status("T-0001.1") == "merged"
    assert s.run_models("T-0001.1") == [("implementer", "opus"), ("reviewer", "fable"), ("verifier", "opus")]
