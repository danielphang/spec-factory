"""The merge gate refuses a changed protected path the pinned spec does not declare (spec-factory
T-0033, issue #57). The pinned spec's Risk section declares protected paths on one line,
`Protected paths: none | `<path or glob>`, ...`; the operator approves it at the spec gate. At merge,
`factory merge` refuses each changed protected path that line does not declare, naming it, with an
error that starts `BLOCKED from merge gate: `, and the build parks the sub-ticket with that error.
`resolve --accept-paths F` accepts the paths for that sub-ticket and returns it to its checks;
`resolve --ruling F` sends it back to its implementer. A ruling on a reviewer's ESCALATE returns the
sub-ticket to its checks.

Black-box through `bin/factory`, each case on the spec's t0033-gate.sh fixture: a scratch instance
whose protected paths are `core/**`, `bin/tool` and `~/.secret/**`, a throwaway store and a scratch
target whose main holds core/a.py, core/b.py, bin/tool and docs/d.md.
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
FIXTURE = REPO / "tests" / "factory" / "fixtures" / "instance"

# Drives factory/workflows/build.js with a stub clerk: each command gets the reply of the longest key
# its `bin/factory` arguments start with (a list is used in turn, the last one repeating). Prints
# `park: <reason>` per park.
WF_DRIVER = r"""
import { readFileSync } from 'node:fs'
const R = { 'config': { out: { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } },
  'run start': { out: { ok: true, run_id: 'run-0009-x', worktree: '/w' } }, ...JSON.parse(process.argv[3]) }
const src = readFileSync(process.argv[2], 'utf8').replace(/^export const meta/m, 'const meta')
const lines = []
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n'
  const cmd = m[1].replace(/^.*?bin\/factory /s, '')
  const p = cmd.match(/^ticket park \S+ --reason "([^"]*)"/)
  if (p) lines.push(`park: ${p[1]}`)
  const key = Object.keys(R).filter(k => cmd.startsWith(k)).sort((a, b) => b.length - a.length)[0]
  let r = key ? R[key] : { out: { ok: true } }
  if (Array.isArray(r)) r = r.length > 1 ? r.shift() : r[0]
  return { stdout: JSON.stringify(r.out), exit: r.exit || 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r', state: '/tmp/s' }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(lines.join('\n'))
"""


class Gate:
    """The t0033-gate.sh fixture. `risk` is the line T-0001's approved spec carries in its Risk
    section (None: T-0001 is never approved and has no sub-ticket; the commit lands on T-0001's own
    branch). `changes` as in the fixture: `p` appends to p, `p-` deletes p, `p>q` renames p to q."""

    def __init__(self, tmp_path: Path, risk: str | None, changes: str):
        self.tmp = tmp_path
        inst, self.store, self.target = tmp_path / "inst", tmp_path / "store", tmp_path / "t"
        inst.mkdir()
        shutil.copy(FIXTURE / "context.md", inst / "context.md")
        kept = [ln for ln in (FIXTURE / "instance.yaml").read_text().splitlines()
                if not ln.startswith(("protected_paths:", "  infra:"))]
        (inst / "instance.yaml").write_text("\n".join(kept + [
            "protected_paths:", '  harness: ["core/**", "bin/tool"]', '  credentials: ["~/.secret/**"]']) + "\n")
        self.env = {**os.environ, "FACTORY_INSTANCE": str(inst), "FACTORY_STATE": str(self.store),
                    "FACTORY_REPO": str(self.target), "FACTORY_INTEGRATION_BRANCH": "main",
                    "PYTHONDONTWRITEBYTECODE": "1"}
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.target)], check=True)
        for f in ("core/a.py", "core/b.py", "bin/tool", "docs/d.md"):
            (self.target / f).parent.mkdir(parents=True, exist_ok=True)
            (self.target / f).write_text("x\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "init")
        for tid, line in (("T-0001", risk), ("T-0002", "Protected paths: `core/b.py`")):
            self.spec(tid, line)
        self.sub = "T-0001"
        if risk is not None:
            plan = tmp_path / "plan.md"
            plan.write_text("ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n")
            self.ok("subticket", "add", "T-0001", "--file", str(plan))
            self.ok("ticket", "transition", "T-0001", "--to", "planned", "--by", "t")
            self.sub = "T-0001.1"
        branch = f"factory/{self.sub}"
        self.git("checkout", "-qb", branch)
        for c in changes.split():
            if ">" in c:
                src, dst = c.split(">")
                (self.target / dst).parent.mkdir(parents=True, exist_ok=True)
                self.git("mv", src, dst)
            elif c.endswith("-"):
                self.git("rm", "-q", c[:-1])
            else:
                (self.target / c).parent.mkdir(parents=True, exist_ok=True)
                with (self.target / c).open("a") as fh:
                    fh.write("y\n")
                self.git("add", c)
        self.git("commit", "-qm", "work")
        self.head = self.git("rev-parse", "HEAD")
        self.git("checkout", "-q", "main")
        self.main = self.git("rev-parse", "main")
        self.ok("ticket", "set", self.sub, "status=checks-in-flight", f"branch={branch}", f"head={self.head}")
        self.record("verifier", "Gate suite: PASS\nSTATUS: VERIFIED", "run-0001-verifier")
        self.record("reviewer", "STATUS: APPROVE", "run-0002-reviewer")

    def spec(self, tid: str, line: str | None) -> None:
        req, spec = self.tmp / "req.md", self.tmp / "spec.md"
        req.write_text(f"# F {tid}\n\nDo x.\n")
        spec.write_text(f"=== proposal.md\n## Problem\nx\n## Risk\nBlast radius: small.\n{line or ''}\n"
                        "=== design.md\n## Proposed change\nA. x\n")
        self.ok("ticket", "new", "--file", str(req))
        self.ok("ticket", "transition", tid, "--to", "ready-for-spec-writer", "--by", "t")
        self.ok("spec", "add", tid, "--file", str(spec))
        self.ok("ticket", "transition", tid, "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
        if line is not None:
            self.ok("ticket", "transition", tid, "--to", "awaiting-spec-gate", "--by", "t")
            self.ok("approve-spec", tid)

    def record(self, role: str, body: str, run: str) -> None:
        out = self.tmp / f"{run}.md"
        out.write_text(f"Commit: {self.head}\n{body}\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
        self.ok("results", "record", self.sub, "--head", self.head, "--role", role, "--output", str(out), "--run", run)

    def git(self, *argv: str) -> str:
        cp = subprocess.run(["git", "-c", "user.email=f@x", "-c", "user.name=f", *argv], cwd=self.target,
                            capture_output=True, text=True, check=True)
        return cp.stdout.strip()

    def cli(self, *argv: str) -> subprocess.CompletedProcess:
        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)

    def ok(self, *argv: str) -> dict:
        cp = self.cli(*argv)
        assert cp.returncode == 0, cp.stderr
        return json.loads(cp.stdout.strip().splitlines()[-1])

    def refused(self, *argv: str) -> str:
        cp = self.cli(*argv)
        assert cp.returncode == 2, cp.stdout + cp.stderr
        return json.loads(cp.stdout.strip().splitlines()[-1])["error"]

    def ticket(self, tid: str | None = None) -> dict:
        return yaml.safe_load((self.store / "tickets" / f"{tid or self.sub}.yaml").read_text())

    def park_with_merge_error(self) -> str:
        error = self.refused("merge", self.sub)
        self.ok("ticket", "park", self.sub, "--reason", error)
        return error

    def rows(self) -> list[str]:
        return sorted(p.name for p in (self.store / "results" / self.head).glob("*.yaml"))

    def ruling(self, text: str) -> str:
        f = self.tmp / "ruling.md"
        f.write_text(text)
        return str(f)


def test_an_undeclared_protected_path_is_refused_by_name_and_nothing_changes(tmp_path):
    g = Gate(tmp_path, "Protected paths: `core/a.py`", "core/a.py core/b.py bin/tool docs/d.md")
    before = g.ticket()
    error = g.refused("merge", g.sub)
    assert error == "BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: bin/tool, core/b.py"
    assert not any(c in error for c in "`$\"")
    assert g.git("rev-parse", "main") == g.main
    assert g.ticket() == before
    events = [json.loads(ln) for p in sorted((g.store / "log").glob("*.jsonl")) for ln in p.read_text().splitlines()]
    refused = [e for e in events if e["event"] == "merge.refused"]
    assert len(refused) == 1 and refused[0]["paths"] == ["bin/tool", "core/b.py"]
    assert refused[0]["reason"] == "protected paths not declared" and refused[0]["head"] == g.head


@pytest.mark.parametrize("risk, changes", [
    ("Protected paths: none", "core/b.py"),                 # T-0002 declares core/b.py, not T-0001
    ("Protected paths: none", "core/b.py>docs/b.py"),       # moved out of the protected tree
    ("Not touched: `core/b.py`", "core/b.py"),              # a Risk line in another form
    ("```\nProtected paths: `core/b.py`\n```", "core/b.py"),  # inside a fenced code block
    ("Protected paths: `core/{a,b}.py`", "core/b.py"),      # a brace list is one literal entry
])
def test_nothing_but_the_pinned_specs_own_declaration_line_declares_a_path(tmp_path, risk, changes):
    g = Gate(tmp_path, risk, changes)
    error = g.refused("merge", g.sub)
    assert error == "BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py"
    assert g.git("rev-parse", "main") == g.main


@pytest.mark.parametrize("risk, changes", [
    ("Protected paths: `core/**`, `bin/tool`", "core/a.py core/new/c.py bin/tool"),
    ("- Protected paths: `core/b.py`.", "core/b.py docs/d.md"),
    ("Protected paths: none", "docs/d.md docs/e.md"),
])
def test_a_declared_protected_path_or_an_unprotected_one_merges(tmp_path, risk, changes):
    g = Gate(tmp_path, risk, changes)
    assert g.ok("merge", g.sub)["state"] == "merged"
    assert g.git("rev-parse", "main") != g.main


def test_a_ticket_with_no_parent_and_no_approved_spec_declares_nothing(tmp_path):
    g = Gate(tmp_path, None, "core/a.py")
    assert g.refused("merge", g.sub) == (
        "BLOCKED from merge gate: protected paths not declared (T-0001 has no approved spec): core/a.py")


def test_the_build_parks_a_merge_gate_refusal_with_its_reason(tmp_path):
    node = shutil.which("node")
    assert node, "node must be on PATH: this case runs factory/workflows/build.js"
    error = "BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py"
    replies = {
        "ticket show T-0001 ": {"out": {"ok": True, "state": "planned"}},
        "ticket ready-implementers": [
            {"out": {"ok": True, "ready": [], "resumable": ["T-0001.1"], "remaining": ["T-0001.1"],
                     "subtickets": ["T-0001.1"], "closed": []}},
            {"out": {"ok": True, "ready": [], "resumable": [], "remaining": ["T-0001.1"],
                     "subtickets": ["T-0001.1"], "closed": []}}],
        "ticket show T-0001.1": {"out": {"ok": True, "state": "checks-in-flight"}},
        "ticket head": {"out": {"ok": True, "head": "ab" * 20}},
        "results show": {"out": {"ok": True, "rows": {"reviewer": "APPROVE", "verifier": "VERIFIED", "ci": "PASS"},
                                 "missing": []}},
        "ticket join": {"out": {"ok": True, "decision": "merge", "reason": "ci PASS + APPROVE + VERIFIED"}},
        "merge": {"out": {"ok": False, "error": error}, "exit": 2},
    }
    driver = tmp_path / "wf.mjs"
    driver.write_text(WF_DRIVER)
    cp = subprocess.run([node, str(driver), "factory/workflows/build.js", json.dumps(replies)],
                        capture_output=True, text=True, cwd=REPO)
    assert cp.stdout.strip() == f"park: {error}", cp.stdout + cp.stderr


def test_accepting_the_refused_paths_returns_the_sub_ticket_to_its_checks_and_it_merges(tmp_path):
    g = Gate(tmp_path, "Protected paths: `core/a.py`", "core/a.py core/b.py bin/tool")
    g.park_with_merge_error()
    pr = g.ticket()["round"]["pr"]
    g.ok("resolve", g.sub, "--accept-paths", g.ruling("Ruling: part of the approved design.\n"))
    t = g.ticket()
    assert t["status"] == "checks-in-flight" and t["parked"] is None and t["round"]["pr"] == pr
    assert t["accepted_paths"] == ["bin/tool", "core/b.py"]
    assert g.rows() == ["ci.yaml", "reviewer.yaml", "verifier.yaml"]
    assert (g.store / "approvals" / g.sub / "ruling-1.md").read_text() == "Ruling: part of the approved design.\n"
    assert g.ok("merge", g.sub)["state"] == "merged"


def test_accepting_paths_is_refused_on_any_other_park_and_writes_nothing(tmp_path):
    g = Gate(tmp_path, "Protected paths: none", "core/b.py")
    g.ok("ticket", "park", g.sub, "--reason", "ESCALATE from reviewer")
    before = g.ticket()
    error = g.refused("resolve", g.sub, "--accept-paths", g.ruling("Ruling: x\n"))
    assert error.startswith("--accept-paths applies to a merge gate park (BLOCKED from merge gate); T-0001.1 is parked")
    assert g.ticket() == before and not list((g.store / "approvals" / g.sub).glob("ruling-*"))


def test_accepting_paths_is_refused_when_the_head_is_not_the_branch_tip(tmp_path):
    g = Gate(tmp_path, "Protected paths: none", "core/b.py")
    g.park_with_merge_error()
    g.git("checkout", "-q", "factory/T-0001.1")
    g.git("commit", "-q", "--allow-empty", "-m", "later")
    g.git("checkout", "-q", "main")
    before = g.ticket()
    assert "is not the branch tip" in g.refused("resolve", g.sub, "--accept-paths", g.ruling("Ruling: x\n"))
    assert g.ticket() == before and not list((g.store / "approvals" / g.sub).glob("ruling-*"))


def test_accepting_paths_is_refused_when_no_undeclared_protected_path_remains(tmp_path):
    g = Gate(tmp_path, "Protected paths: none", "core/b.py")
    g.park_with_merge_error()
    g.ok("resolve", g.sub, "--accept-paths", g.ruling("Ruling: x\n"))
    g.ok("ticket", "park", g.sub, "--reason", "BLOCKED from merge gate: again")
    before = g.ticket()
    error = g.refused("resolve", g.sub, "--accept-paths", g.ruling("Ruling: y\n"))
    assert error == f"nothing to accept: T-0001.1 has no undeclared protected path at {g.head[:9]}"
    assert g.ticket() == before and len(list((g.store / "approvals" / g.sub).glob("ruling-*"))) == 1


def test_a_ruling_on_a_merge_gate_refusal_sends_the_sub_ticket_back_to_its_implementer(tmp_path):
    g = Gate(tmp_path, "Protected paths: none", "core/b.py")
    g.park_with_merge_error()
    pr = g.ticket()["round"]["pr"]
    g.ok("resolve", g.sub, "--ruling", g.ruling("Ruling: take core/b.py out of this change.\n"))
    t = g.ticket()
    assert t["status"] == "ready-for-implementer" and t["round"]["pr"] == pr and not t.get("accepted_paths")


def test_a_ruling_on_a_reviewer_escalation_returns_the_sub_ticket_to_its_checks(tmp_path):
    g = Gate(tmp_path, "Protected paths: none", "docs/d.md")
    g.record("reviewer", "STATUS: ESCALATE", "run-0003-reviewer")
    g.ok("ticket", "park", g.sub, "--reason", "ESCALATE from reviewer")
    pr = g.ticket()["round"]["pr"]
    g.ok("resolve", g.sub, "--ruling", g.ruling("Ruling: the escalation is settled.\n"))
    t = g.ticket()
    assert t["status"] == "checks-in-flight" and t["round"]["pr"] == pr
    assert g.rows() == ["ci.yaml", "verifier.yaml"]
    assert [p.name for p in (g.store / "results" / g.head / "superseded-1").iterdir()] == ["reviewer.yaml"]
    assert t["history"][-1]["superseded"] == ["reviewer"]
    assert (g.store / "approvals" / g.sub / "ruling-1.md").exists()
