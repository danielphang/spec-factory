"""A run's token record from its transcript (T-0056 part A).

- `run finish --transcripts DIR` keeps, under the run's `claude:` key, the tokens of the one
  transcript under DIR whose first user message names the run's directory and whose first timestamp
  is at or after the run started, each message id counted once, with no dollars. It opens only
  files modified at or after the run started.
- A reply with usage is kept as before; an unusable reply takes the transcript, and keeps
  `claude: null` when there is none.
- build.js passes `--transcripts` on both of its `run finish` commands, the normal one and the
  KILLED one after a thrown agent call, so the run records its agent's transcript.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml

from ._cli import REPO, run
from ._cli import js_ok as js
from ._fixtures import f  # noqa: F401  (f is the t0027-amend.sh store fixture)

TASK = "[Workflow harness — computed task]"
OUTPUT = "Type: bug\nTitle: T\nSummary: s\nEvidence: e\nAssumptions: a\nSTATUS: ACCEPT\nCONFIDENCE: high, x\nESCALATIONS: none\n"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _transcript(path: Path, ts: str, named: str, *calls: tuple[str, int, int, int, int]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [{"type": "user", "timestamp": ts,
              "message": {"role": "user", "content": f"{TASK} Your entire input is the file {named}/input.md"}}]
    lines += [{"type": "assistant", "timestamp": ts,
               "message": {"id": mid, "usage": {"input_tokens": i, "cache_read_input_tokens": r,
                                                "cache_creation_input_tokens": c, "output_tokens": o}}}
              for mid, i, r, c, o in calls]
    path.write_text("".join(json.dumps(x) + "\n" for x in lines))
    return path


def _triage(tmp_path: Path) -> tuple[Path, str]:
    store = tmp_path / "store"
    if not (store / "tickets").is_dir():
        (tmp_path / "req.md").write_text("# F\n\nDo x.\n")
        js(run(store, "ticket", "new", "--file", str(tmp_path / "req.md")))
    rid = js(run(store, "run", "start", "--role", "triage", "--ticket", "T-0001"))["run_id"]
    (store / "runs" / rid / "output.md").write_text(OUTPUT)
    return store, rid


def _claude(store: Path, rid: str):
    return yaml.safe_load((store / "runs" / rid / "meta.yaml").read_text())["claude"]


def test_run_finish_records_the_runs_transcript_and_passes_over_its_two_decoys(tmp_path):
    store, rid = _triage(tmp_path)
    x = tmp_path / "cc" / "projects"
    mine = _transcript(x / "p" / "s" / "subagents" / "workflows" / "wf" / "agent-1.jsonl", _now(),
                       f"{store}/runs/{rid}", ("m1", 5, 100, 0, 3), ("m1", 5, 100, 0, 3), ("m2", 1, 200, 4, 10))
    _transcript(x / "p" / "s" / "agent-2.jsonl", _now(), f"{store}/runs/run-9999-triage", ("m3", 1000, 0, 0, 1000))
    _transcript(x / "p" / "old.jsonl", "2026-01-01T00:00:00Z", f"{store}/runs/{rid}", ("m4", 1000, 0, 0, 1000))
    js(run(store, "run", "finish", rid, "--transcripts", str(x)))
    assert _claude(store, rid) == {"source": "transcript", "transcript": str(mine), "total_cost_usd": None,
                                   "usage": {"input_tokens": 6, "cache_read_input_tokens": 300,
                                             "cache_creation_input_tokens": 4, "output_tokens": 13}}


def test_run_finish_opens_no_transcript_modified_before_the_run_started(tmp_path):
    store, rid = _triage(tmp_path)
    x = tmp_path / "cc" / "projects"
    tf = _transcript(x / "p" / "agent-1.jsonl", _now(), f"{store}/runs/{rid}", ("m1", 1, 2, 3, 4))
    os.utime(tf, (0, 0))
    js(run(store, "run", "finish", rid, "--transcripts", str(x)))
    assert "claude" not in yaml.safe_load((store / "runs" / rid / "meta.yaml").read_text())


def test_a_reply_with_usage_wins_over_the_transcript(tmp_path):
    store, rid = _triage(tmp_path)
    x = tmp_path / "cc" / "projects"
    _transcript(x / "p" / "agent-1.jsonl", _now(), f"{store}/runs/{rid}", ("m1", 1000, 0, 0, 1000))
    reply = {"session_id": "s2", "total_cost_usd": 0.5, "num_turns": 2, "usage": {"input_tokens": 1, "output_tokens": 2}}
    (tmp_path / "reply.json").write_text(json.dumps(reply))
    js(run(store, "run", "finish", rid, "--reply", str(tmp_path / "reply.json"), "--transcripts", str(x)))
    assert _claude(store, rid) == reply


def test_an_unusable_reply_takes_the_transcript_and_keeps_null_without_one(tmp_path):
    (tmp_path / "reply.json").write_text("not json\n")
    x = tmp_path / "cc" / "projects"
    store, r1 = _triage(tmp_path)
    js(run(store, "run", "finish", r1, "--reply", str(tmp_path / "reply.json"), "--transcripts", str(x)))
    assert _claude(store, r1) is None
    _, r2 = _triage(tmp_path)
    _transcript(x / "p" / "agent-1.jsonl", _now(), f"{store}/runs/{r2}", ("m1", 2, 20, 0, 1))
    js(run(store, "run", "finish", r2, "--reply", str(tmp_path / "reply.json"), "--transcripts", str(x)))
    assert _claude(store, r2)["usage"] == {"input_tokens": 2, "cache_read_input_tokens": 20,
                                           "cache_creation_input_tokens": 0, "output_tokens": 1}


# build.js under node, as _fixtures.BUILD_DRIVER drives it, with a role call that writes its transcript
# under $CLAUDE_CONFIG_DIR/projects (as Claude Code does) and then returns nothing, or throws when
# T0056_THROW is set. Each `run finish` clerk command is printed as it runs.
DRIVER = r"""
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const src = readFileSync('factory/workflows/build.js', 'utf8').replace(/^export const meta/m, 'const meta')
let n = 0
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    if (/ run finish /.test(m[1])) console.log(`finish: ${m[1]}`)
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  n += 1
  const dir = `${process.env.CLAUDE_CONFIG_DIR}/projects/p/s/subagents/workflows/wf`
  mkdirSync(dir, { recursive: true })
  const ts = new Date().toISOString()
  writeFileSync(`${dir}/agent-${n}.jsonl`,
    JSON.stringify({ type: 'user', timestamp: ts, message: { role: 'user', content: `[Workflow harness — computed task] ${prompt}` } }) + '\n' +
    JSON.stringify({ type: 'assistant', timestamp: ts, message: { id: `m${n}`, usage: { input_tokens: 7, cache_read_input_tokens: 70, cache_creation_input_tokens: 0, output_tokens: 3 } } }) + '\n')
  if (process.env.T0056_THROW) throw new Error('stand-in failure')
  return ''
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
  integration: 'main', inlineRoles: true }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
"""


def _build(f, **env: str) -> list[str]:  # noqa: F811
    node = shutil.which("node")
    assert node, "node must be on PATH: this case runs factory/workflows/build.js"
    f.plan("ST-1 / Only\nDepends on: none\nParallel-safe: yes\n")
    driver = f.tmp / "t0056-build.mjs"
    driver.write_text(DRIVER)
    cp = subprocess.run([node, str(driver)], capture_output=True, text=True, cwd=REPO, timeout=120,
                        env={**f.env, "CLAUDE_CONFIG_DIR": str(f.tmp / "cc"), **env})
    finishes = [ln for ln in cp.stdout.splitlines() if ln.startswith("finish: ")]
    assert finishes, cp.stdout + cp.stderr
    return finishes


def _implementer_records(f) -> list[dict]:  # noqa: F811
    return [yaml.safe_load(p.read_text()) for p in sorted((f.store / "runs").glob("run-*-implementer/meta.yaml"))]


def test_build_js_passes_transcripts_on_the_normal_run_finish(f):  # noqa: F811
    finishes = _build(f)
    assert all(ln.endswith(' --transcripts "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects"') for ln in finishes), finishes
    metas = _implementer_records(f)
    # The empty output is re-dispatched once; each run records its own agent's transcript.
    assert [m["status"] for m in metas] == ["EMPTY-OUTPUT", "EMPTY-OUTPUT"] and len(finishes) == 2
    assert {m["claude"]["transcript"] for m in metas} == {str(f.tmp / "cc" / "projects" / "p" / "s" / "subagents" /
                                                              "workflows" / "wf" / f"agent-{n}.jsonl") for n in (1, 2)}
    assert all(m["claude"]["source"] == "transcript" and m["claude"]["usage"] == {
        "input_tokens": 7, "cache_read_input_tokens": 70, "cache_creation_input_tokens": 0, "output_tokens": 3}
        for m in metas)


def test_build_js_passes_transcripts_on_the_killed_run_finish(f):  # noqa: F811
    finishes = _build(f, T0056_THROW="1")
    assert len(finishes) == 1 and "--status-override KILLED --transcripts " in finishes[0], finishes
    [meta] = _implementer_records(f)
    assert meta["status"] == "KILLED"
    assert meta["claude"]["source"] == "transcript" and meta["claude"]["usage"]["output_tokens"] == 3
