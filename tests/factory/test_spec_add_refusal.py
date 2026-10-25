"""T-0057 (issue #105): `spec add` runs the format check `approve-spec` runs, where the store has
current truth (an `openspec/` tree), and a refused draft goes back to the spec writer as a new round.

Black-box through `bin/factory` on throwaway stores. The driver and the intake Workflow script are
each run on one ticket, with a stand-in `claude` that writes a spec body from a file, then the
trailer: the driver as `factory drive`, the script under node with every clerk command run for real.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from ._cli import REPO, js, run
from ._fixtures import FIXTURE_INSTANCE, Store

LABEL = "scenario 'the thing works' has no NEW/REGRESSION label in verification.md"
REFUSED = "## Your previous output, which the harness refused to store as a spec version"


def spec(label_lines: str, name: str = "the thing works") -> str:
    return ("=== proposal.md\n## Problem\nA thing is missing.\n=== specs/thing/spec.md\n## ADDED Requirements\n"
            f"### Requirement: The thing works\nThe thing SHALL work.\n#### Scenario: {name}\n- WHEN `true`\n"
            f"- THEN it exits 0\n=== verification.md\n## Acceptance\n{label_lines}")


GOOD = spec("- the thing works → NEW; fails today\n")
WRAPPED = spec("- the thing works\n  → NEW; fails today\n")
WORDED = spec("- the thing works → REGRESSION in its new form.\n")
TICKED = spec("- the `echo hi` thing works\n  → NEW; fails today\n", "the `echo hi` thing works")

# Plays the next entry of its role's list in $STANDIN_PLAYS (the last one repeats): {"body": file,
# "write": STATUS} writes output.md as the file's text, if given, then the trailer.
STANDIN = '''#!{python}
import json, os, pathlib, sys
cwd = pathlib.Path.cwd(); log = pathlib.Path(os.environ["STANDIN_LOG"])
role = cwd.name.split("-", 2)[2]
plays = json.loads(os.environ.get("STANDIN_PLAYS") or "{{}}").get(role) or [{{"write": "UNKNOWN"}}]
nf = log.with_name(log.name + ".n-" + role)
n = int(nf.read_text()) + 1 if nf.exists() else 1
nf.write_text(str(n))
p = plays[min(n, len(plays)) - 1]
text = (pathlib.Path(p["body"]).read_text() if "body" in p else "") + \\
    "\\nSTATUS: %s\\nCONFIDENCE: high, stand-in\\nESCALATIONS: none\\n" % p["write"]
(cwd / "output.md").write_text(text)
print(json.dumps({{"type": "result", "is_error": False, "result": text, "session_id": "s-" + cwd.name,
                  "total_cost_usd": 0, "num_turns": 1, "usage": {{"output_tokens": 1}}}}))
'''

# The intake Workflow script under node: a clerk prompt runs its command with sh; a role prompt runs
# the stand-in from the run's directory and returns its reply's result.
WORKFLOW = r"""
import { readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const [script, ticket, instance, claude] = process.argv.slice(2)
const src = readFileSync(script, 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  const dir = prompt.match(/(\S+\/runs\/run-\d+-[a-z_]+)\/input\.md/)[1]
  return JSON.parse(spawnSync(claude, [], { cwd: dir, encoding: 'utf8' }).stdout).result
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
const res = await fn({ ticket, repo: process.cwd(), instance, state: process.env.FACTORY_STATE, inlineRoles: true },
  agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(JSON.stringify(res))
"""


def bodies(tmp_path: Path) -> dict[str, str]:
    paths = {}
    tmp_path.mkdir(parents=True, exist_ok=True)
    for name, text in (("good", GOOD), ("wrapped", WRAPPED), ("worded", WORDED), ("ticked", TICKED)):
        (tmp_path / f"{name}.md").write_text(text)
        paths[name] = str(tmp_path / f"{name}.md")
    return paths


def writer_store(tmp_path: Path) -> Store:
    """The driver's store with current truth enabled and T-0001 ready for its spec writer."""
    s = Store(tmp_path)
    (s.root / "openspec" / "specs").mkdir(parents=True)
    (tmp_path / "bin" / "claude").write_text(STANDIN.format(python=sys.executable))
    s.ok("ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
    return s


def plays(paths: dict[str, str], writer: list[str], critic: list[str] = ()) -> dict:
    """Plays from "<body>:<STATUS>" entries."""
    def entry(e: str) -> dict:
        body, st = e.split(":")
        return {"body": paths[body], "write": st}
    return {"spec_writer": [entry(e) for e in writer], "critic": [{"write": c} for c in critic]}


def intake(s: Store, side: str, p: dict) -> dict:
    if side == "drive":
        cp, res = s.drive(p, "--phase", "intake")
        assert cp.returncode == 0, cp.stderr
        return res
    node = shutil.which("node")
    assert node, "node must be on PATH: this case runs factory/workflows/intake.js"
    (s.tmp / "wf.mjs").write_text(WORKFLOW)
    cp = subprocess.run([node, str(s.tmp / "wf.mjs"), str(REPO / "factory" / "workflows" / "intake.js"), "T-0001",
                         str(FIXTURE_INSTANCE), str(s.tmp / "bin" / "claude")],
                        capture_output=True, text=True, cwd=REPO, timeout=300,
                        env={**s.env, "STANDIN_PLAYS": json.dumps(p)})
    assert cp.returncode == 0, cp.stderr
    return json.loads(cp.stdout.strip().splitlines()[-1])


def versions(store: Path) -> int:
    d = store / "specs" / "T-0001"
    return len(list(d.glob("v*.md"))) if d.exists() else 0


def spec_added(store: Path) -> int:
    return sum(ln.count('"spec.added"') for p in (store / "log").glob("*.jsonl") for ln in p.read_text().splitlines())


def roles(s: Store) -> list[tuple[str, str]]:
    return [(m["role"], m["status"]) for m in s.runs()]


def test_spec_add_refuses_a_malformed_spec_and_writes_nothing_where_current_truth_is_enabled(tmp_path):
    paths, s = bodies(tmp_path), tmp_path / "state"
    req = tmp_path / "req.md"
    req.write_text("# F\n\nx\n")
    assert run(s, "ticket", "new", "--file", str(req)).returncode == 0
    (s / "openspec" / "specs").mkdir(parents=True)
    for name in ("wrapped", "worded"):
        cp = run(s, "spec", "add", "T-0001", "--file", paths[name])
        assert cp.returncode == 2 and cp.stderr.splitlines()[0] == f"spec not added: {LABEL}", name
        assert versions(s) == 0 and spec_added(s) == 0 and not (s / "specs" / "T-0001.md").exists(), name
    cp = run(s, "spec", "add", "T-0001", "--file", paths["good"])
    assert cp.returncode == 0, cp.stderr
    assert js(cp)["version"] == 1 and versions(s) == 1 and spec_added(s) == 1


def test_a_needs_human_draft_and_a_store_without_current_truth_keep_a_malformed_spec(tmp_path):
    paths = bodies(tmp_path)
    req = tmp_path / "req.md"
    req.write_text("# F\n\nx\n")
    bare = tmp_path / "bare"
    assert run(bare, "ticket", "new", "--file", str(req)).returncode == 0
    assert run(bare, "spec", "add", "T-0001", "--file", paths["wrapped"]).returncode == 0 and versions(bare) == 1
    s = tmp_path / "state"
    assert run(s, "ticket", "new", "--file", str(req)).returncode == 0
    (s / "openspec" / "specs").mkdir(parents=True)
    assert run(s, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t").returncode == 0
    for st, code in (("READY-FOR-CRITIC", 2), ("NEEDS-HUMAN", 0)):
        rid = js(run(s, "run", "start", "--role", "spec_writer", "--ticket", "T-0001"))["run_id"]
        (s / "runs" / rid / "output.md").write_text(WRAPPED + f"STATUS: {st}\nCONFIDENCE: low, t\nESCALATIONS: none\n")
        assert run(s, "run", "finish", rid).returncode == 0
        cp = run(s, "spec", "add", "T-0001", "--from-run", rid)
        assert cp.returncode == code, (st, cp.stderr)
    assert versions(s) == 1


def test_a_refused_draft_goes_back_to_the_writer_with_the_refusal_and_the_next_reaches_the_critic(tmp_path):
    for side in ("drive", "script"):
        paths = bodies(tmp_path / side)
        s = writer_store(tmp_path / side)
        res = intake(s, side, plays(paths, ["wrapped:READY-FOR-CRITIC", "good:READY-FOR-CRITIC"], ["APPROVE"]))
        assert res["state"] == "awaiting-spec-gate" and res["rounds"] == 2, (side, res)
        t = s.ticket()
        assert t["status"] == "awaiting-spec-gate" and t["round"]["spec"] == 2 and t["spec"]["version"] == 1, side
        assert roles(s) == [("spec_writer", "READY-FOR-CRITIC"), ("spec_writer", "READY-FOR-CRITIC"),
                            ("critic", "APPROVE")], side
        first, second = (s.root / "runs" / m["run_id"] for m in s.runs()[:2])
        assert REFUSED not in (first / "input.md").read_text(), side
        text = (second / "input.md").read_text()
        assert f"{REFUSED}\n\nThe harness refused it with: spec not added: {LABEL}\n\n" in text, side
        assert "- the thing works\n  → NEW; fails today\n" in text, side
        sources = yaml.safe_load((second / "meta.yaml").read_text())["input_sources"]
        assert f"runs/{first.name}/output.md" in sources, side


def test_a_refusal_in_the_last_round_parks_with_the_refusal_quoted_safely(tmp_path):
    ticked = "max rounds: spec not added: scenario 'the 'echo hi' thing works' has no NEW/REGRESSION label in verification.md"
    for side in ("drive", "script"):
        paths = bodies(tmp_path / side)
        s = writer_store(tmp_path / side)
        res = intake(s, side, plays(paths, ["ticked:READY-FOR-CRITIC"]))
        assert res == {"ticket": "T-0001", "state": "parked", "rounds": 2, "reason": "max rounds",
                       **({"ok": True} if side == "drive" else {})}, side
        t = s.ticket()
        assert t["parked"]["reason"] == ticked and t["round"]["spec"] == 2 and t["spec"]["version"] == 0, side
        assert roles(s) == [("spec_writer", "READY-FOR-CRITIC")] * 2, side
        assert t["parked"]["outputs"] == [s.runs()[1]["run_id"]], side


def test_a_refusal_after_a_revise_in_the_last_round_parks_without_another_writer_run(tmp_path):
    for side in ("drive", "script"):
        paths = bodies(tmp_path / side)
        s = writer_store(tmp_path / side)
        intake(s, side, plays(paths, ["good:READY-FOR-CRITIC", "worded:NEEDS-SPLIT"], ["REVISE"]))
        t = s.ticket()
        assert t["status"] == "parked" and t["parked"]["reason"] == f"max rounds: spec not added: {LABEL}", side
        assert t["round"]["spec"] == 2 and t["spec"]["version"] == 1, side
        assert roles(s) == [("spec_writer", "READY-FOR-CRITIC"), ("critic", "REVISE"), ("spec_writer", "NEEDS-SPLIT")]
