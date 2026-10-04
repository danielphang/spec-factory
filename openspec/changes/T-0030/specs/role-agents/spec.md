## ADDED Requirements
### Requirement: Every role has a registered agent definition that reads the run's prompt
`agents/` SHALL hold a definition for every agent type either workflow script asks for, each named as its file, and every role definition's body MUST point the agent at its run's `system-prompt.txt` and carry no copy of a role prompt.

#### Scenario: Every agent type the workflows ask for has a definition
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the eight fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0030-wf.mjs <<'EOF'
// node t0030-wf.mjs <workflow.js> '<replies JSON>' [inline]: runs one workflow script with a stub clerk, as
// t0023-wf.mjs does (same reply rules), with inlineRoles set when a third argument is given. Prints one
// line per role agent call, `<agentType> effort=<effort or none>`, in call order, then
// `clerk effort=<the distinct efforts of the clerk calls>`.
import { readFileSync } from 'node:fs'
const [file, replies, inline] = process.argv.slice(2)
const R = { 'config': { out: { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } },
  'run start': { out: { ok: true, run_id: 'run-0009-x', worktree: '/w' } }, ...JSON.parse(replies) }
const src = readFileSync(file, 'utf8').replace(/^export const meta/m, 'const meta')
const lines = [], clerkEffort = new Set()
const agent = async (prompt, opts = {}) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) { lines.push(`${opts.agentType} effort=${opts.effort ?? 'none'}`); return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n' }
  clerkEffort.add(opts.effort ?? 'none')
  const cmd = m[1].replace(/^.*?bin\/factory /s, '')
  const key = Object.keys(R).filter(k => cmd.startsWith(k)).sort((a, b) => b.length - a.length)[0]
  let r = key ? R[key] : { out: { ok: true } }
  if (Array.isArray(r)) r = r.length > 1 ? r.shift() : r[0]
  return { stdout: 'raw' in r ? r.raw : JSON.stringify(r.out), exit: r.exit || 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r', state: '/tmp/s', inlineRoles: !!inline }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(lines.join('\n'))
console.log(`clerk effort=${[...clerkEffort].sort().join(',')}`)
EOF
cat > ${TMPDIR:-/tmp}/t0030-intake.json <<'EOF'
{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}}}, "run finish": [{"out": {"ok": true, "status": "ACCEPT"}}, {"out": {"ok": true, "status": "READY-FOR-CRITIC"}}, {"out": {"ok": true, "status": "APPROVE"}}], "ticket transition": {"out": {"ok": true, "round": {"spec": 1}}}}
EOF
cat > ${TMPDIR:-/tmp}/t0030-build.json <<'EOF'
{"ticket show T-0001 ": {"out": {"ok": true, "state": "ready-for-planner"}}, "run finish": [{"out": {"ok": true, "status": "PLANNED"}}, {"out": {"ok": true, "status": "READY-FOR-REVIEW"}}, {"out": {"ok": true, "status": "APPROVE"}}], "ticket ready-implementers": [{"out": {"ok": true, "ready": ["T-0001.1"], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": [], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "ready-for-implementer"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}, "ticket parent-check": {"out": {"ok": true, "state": "planned"}}}
EOF
cat > ${TMPDIR:-/tmp}/t0030-throw.mjs <<'EOF'
// node t0030-throw.mjs <workflow.js> '<replies JSON>' [all]: as t0030-wf.mjs, but every role agent call throws
// the error Claude Code gives for an agent type this session has not registered; with `all`, clerk calls
// throw it too. Prints each `run finish` and `ticket park` command the workflow sends, in order, or, if
// the workflow itself stops, `stopped: <error> after <n> agent call(s)`.
import { readFileSync } from 'node:fs'
const [file, replies, all] = process.argv.slice(2)
const R = { 'config': { out: { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } },
  'run start': { out: { ok: true, run_id: 'run-0009-x', worktree: '/w' } }, ...JSON.parse(replies) }
const src = readFileSync(file, 'utf8').replace(/^export const meta/m, 'const meta')
const lines = []
let calls = 0
const agent = async (prompt, opts = {}) => {
  calls++
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m || all) throw new Error(`agent type '${opts.agentType}' not found`)
  const cmd = m[1].replace(/^.*?bin\/factory /s, '')
  if (/^(run finish|ticket park)/.test(cmd)) lines.push(cmd)
  const key = Object.keys(R).filter(k => cmd.startsWith(k)).sort((a, b) => b.length - a.length)[0]
  let r = key ? R[key] : { out: { ok: true } }
  if (Array.isArray(r)) r = r.length > 1 ? r.shift() : r[0]
  return { stdout: JSON.stringify(r.out), exit: r.exit || 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
try {
  await fn({ ticket: 'T-0001', repo: '/r', state: '/tmp/s' }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
  console.log(lines.join('\n'))
} catch (e) { console.log(`stopped: ${e.message} after ${calls} agent call(s)`) }
EOF
cat > ${TMPDIR:-/tmp}/t0030-e2e.mjs <<'EOF'
// node t0030-e2e.mjs <instance dir> [inline], from the checkout under test: runs factory/workflows/intake.js
// on ticket T-0001 of that instance's own store, as t0024-e2e.mjs does: every clerk command runs for
// real, and the triage role writes the stub output "STATUS: REJECT". Prints `role effort=<the effort
// the role's agent call received, or none>` and `clerk effort=<the clerk calls' efforts>`.
import { readFileSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const [inst, inline] = process.argv.slice(2)
const src = readFileSync('factory/workflows/intake.js', 'utf8').replace(/^export const meta/m, 'const meta')
const seen = [], clerk = new Set()
const agent = async (prompt, opts = {}) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    clerk.add(opts.effort ?? 'none')
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  seen.push(`role effort=${opts.effort ?? 'none'}`)
  const o = prompt.match(/Write your complete output to (\S+) and return/)
  const text = 'STATUS: REJECT\nCONFIDENCE: high, stub\nESCALATIONS: none\n'
  writeFileSync(o[1], text)
  return text
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: process.cwd(), instance: inst, inlineRoles: !!inline }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(`${seen.join(' ')} clerk effort=${[...clerk].sort().join(',')}`)
EOF
cat > ${TMPDIR:-/tmp}/t0030-spec.sh <<'EOF'
# Sourced from the repo root: a scratch store (FACTORY_STATE) whose T-0001 has an approved spec v1 with every
# section, one of them a Responses section, and one sub-ticket T-0001.1; a scratch target repo with a
# commit H30 on its branch side. Defines comp ROLE TICKET: starts a run, composes it, finishes it as KILLED
# and prints the path of its input.md; and marks ROLE FILE: prints which marked spec sections FILE holds.
T30=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T30/store
export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x
printf '# Fixture\n\nThe bot should do the thing.\n' > $T30/req.md
sed 's/^|//' > $T30/spec.md <<'SPEC'
|=== proposal.md
## Problem
PROBLEM-MARK the thing is missing.
## Evidence
EVIDENCE-MARK long captured output.
## Root cause
ROOTCAUSE-MARK in one function.
## Out of scope
OUTOFSCOPE-MARK nothing else.
## Decisions
DECISIONS-MARK one call.
## Risk
RISK-MARK small.
|=== design.md
## Proposed change
CHANGE-MARK do the thing.
## Tests to change
TESTS-MARK none
|=== specs/demo/spec.md
## ADDED Requirements
### Requirement: The thing
SCENARIO-MARK the thing SHALL happen.
|=== verification.md
## Acceptance
ACCEPTANCE-MARK the thing → NEW
## Responses
RESPONSES-MARK FIXED earlier finding.
STATUS: READY-FOR-CRITIC
SPEC
bin/factory ticket new --file $T30/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T30/spec.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
bin/factory approve-spec T-0001 >/dev/null
printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T30/plan.md
bin/factory subticket add T-0001 --file $T30/plan.md >/dev/null
git init -q -b main $T30/t && git -C $T30/t commit -q --allow-empty -m init
git -C $T30/t checkout -q -b side && echo x > $T30/t/x.txt && git -C $T30/t add x.txt && git -C $T30/t commit -q -m work
H30=$(git -C $T30/t rev-parse HEAD) && git -C $T30/t checkout -q main
export FACTORY_REPO=$T30/t FACTORY_INTEGRATION_BRANCH=main
comp() { R=$(bin/factory run start --role $1 --ticket $2 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null 2>&1 && bin/factory run finish $R --status-override KILLED >/dev/null 2>&1; echo $FACTORY_STATE/runs/${R:-none}/input.md; }
marks() { echo "$1: evidence=$(grep -c EVIDENCE-MARK $2) responses=$(grep -c RESPONSES-MARK $2) kept=$(grep -o -e PROBLEM-MARK -e ROOTCAUSE-MARK -e OUTOFSCOPE-MARK -e DECISIONS-MARK -e RISK-MARK -e CHANGE-MARK -e TESTS-MARK -e SCENARIO-MARK -e ACCEPTANCE-MARK $2 | sort -u | grep -c .) full=$(grep -cF "$FACTORY_STATE/specs/T-0001/v1.md" $2)"; }
EOF
cat > ${TMPDIR:-/tmp}/t0030-critic.sh <<'EOF'
# Sourced from the repo root, with $1 = small or rewrite: a scratch store whose T-0001 is at round 2
# with the critic next, holding spec v1 and v2 and one finished round-1 critic run. v1 is 200 lines
# "keep line N" and the line OLD-ONLY. For small, v2 is v1 with OLD-ONLY replaced by NEW-ONLY; for
# rewrite, every line of v2 differs from v1 ("other line N"). Prints the path of the composed
# input.md of a round-2 critic run.
T31=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T31/store
printf '# Fixture\n\nThe bot should do the thing.\n' > $T31/req.md
{ echo '## Problem'; seq 1 200 | sed 's/^/keep line /'; echo OLD-ONLY; echo 'STATUS: READY-FOR-CRITIC'; } > $T31/v1.md
if [ "$1" = small ]; then sed 's/^OLD-ONLY$/NEW-ONLY/' $T31/v1.md > $T31/v2.md; else sed 's/^keep line /other line /; s/^OLD-ONLY$/NEW-ONLY/; s/^## Problem$/## Problem (rewritten)/; s/^STATUS: READY-FOR-CRITIC$/STATUS:  READY-FOR-CRITIC/' $T31/v1.md > $T31/v2.md; fi
printf 'Findings: one.\nSTATUS: REVISE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n' > $T31/c1.md
bin/factory ticket new --file $T31/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T31/v1.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
R1=$(bin/factory run start --role critic --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
bin/factory run finish $R1 --output-file $T31/c1.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t --round spec:+1 >/dev/null
bin/factory spec add T-0001 --file $T31/v2.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
R2=$(bin/factory run start --role critic --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
bin/factory run compose $R2 >/dev/null && echo $FACTORY_STATE/runs/$R2/input.md
EOF
cat > ${TMPDIR:-/tmp}/t0030-fence.py <<'EOF'
# .venv/bin/python t0030-fence.py, from the repo root: for the reviewer, verifier and implementer agent
# definitions under agents/, reads the frontmatter's tool list and runs every PreToolUse hook whose
# matcher covers the Write tool against a Write of each test path, the way Claude Code would (JSON on
# stdin; exit 2 blocks). A run directory of each role is made under a scratch store. Prints one line per
# role: the file-editing tools it has, then for each path `allowed` or `blocked`.
import json, os, re, subprocess, tempfile, yaml
base = os.path.realpath(tempfile.mkdtemp())
for role, n, other in (("reviewer", "0042", "verifier"), ("verifier", "0043", "reviewer"), ("implementer", "0045", "reviewer")):
    f = f"agents/factory-{role}.md"
    if not os.path.exists(f):
        print(f"{role}: missing"); continue
    fm = yaml.safe_load(open(f, encoding="utf-8").read().split("---")[1]) or {}
    tools = fm.get("tools") or []
    tools = [t.strip() for t in tools.split(",")] if isinstance(tools, str) else tools
    hooks = [h["command"] for m in (fm.get("hooks") or {}).get("PreToolUse", [])
             if re.fullmatch(m.get("matcher") or ".*", "Write") for h in m.get("hooks", []) if h.get("type") == "command"]
    run = os.path.join(base, "store", "runs", f"run-{n}-{role}")
    os.makedirs(os.path.join(run, "scratch"), exist_ok=True); os.makedirs(os.path.join(run, "wt", "pkg"), exist_ok=True)
    paths = {"output": f"{run}/output.md", "scratch": f"{run}/scratch/notes.txt", "worktree": f"{run}/wt/pkg/code.py",
             "escape": f"{run}/scratch/../wt/pkg/code.py", "other_run": f"{base}/store/runs/run-0044-{other}/output.md",
             "repo": f"{base}/repo/pkg/code.py"}
    res = []
    for name, p in paths.items():
        inp = json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Write", "cwd": run,
                          "tool_input": {"file_path": p, "content": "x"}})
        blocked = any(subprocess.run(["sh", "-c", c], input=inp, text=True, capture_output=True).returncode == 2 for c in hooks)
        res.append(f"{name}={'blocked' if blocked else 'allowed'}")
    edit = ",".join(t for t in ("Edit", "MultiEdit", "NotebookEdit") if t in tools) or "none"
    print(f"{role}: bash={'Bash' in tools} write={'Write' in tools} edit_tools={edit} " + " ".join(res))
EOF
```

- WHEN `(for w in intake build; do node ${TMPDIR:-/tmp}/t0030-wf.mjs factory/workflows/$w.js "$(cat ${TMPDIR:-/tmp}/t0030-$w.json)"; done | grep -v '^clerk ' | sed 's/ .*//' | sort -u | while read a; do echo "$a=$(sed -n 's/^name: *//p' agents/$a.md 2>/dev/null | grep -cx "$a" | sed 's/^1$/defined/;s/^0$/missing/')"; done)`
- THEN it prints exactly `factory-implementer=defined`, `factory-planner=defined`, `factory-reviewer=defined`, `factory-spec-critic=defined`, `factory-spec-writer=defined`, `factory-triage=defined`, `factory-verifier=defined`, one per line

#### Scenario: Every role definition points at the run's prompt and copies none
- WHEN `(for a in triage spec-writer spec-critic planner implementer reviewer verifier; do echo "$a: points=$(grep -c 'system-prompt.txt' agents/factory-$a.md 2>/dev/null | awk '{print ($1 > 0)}') copy=$(grep -c '^ROLE:' agents/factory-$a.md 2>/dev/null)"; done)`
- THEN it prints exactly `triage: points=1 copy=0`, `spec-writer: points=1 copy=0`, `spec-critic: points=1 copy=0`, `planner: points=1 copy=0`, `implementer: points=1 copy=0`, `reviewer: points=1 copy=0`, `verifier: points=1 copy=0`, one per line

#### Scenario: init installs every definition and adds only missing ones
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1; ls .claude/agents | tr '\n' ' '; echo; rm -f .claude/agents/factory-implementer.md .claude/agents/factory-reviewer.md .claude/agents/factory-verifier.md; echo local >> .claude/agents/factory-planner.md; $B init 2>/dev/null | tail -1 | grep -o '"agents": \[[^]]*\]' | grep -o 'factory-[a-z-]*\.md' | tr '\n' ' '; echo; tail -1 .claude/agents/factory-planner.md)`
- THEN it prints `factory-clerk.md factory-implementer.md factory-planner.md factory-reviewer.md factory-spec-critic.md factory-spec-writer.md factory-stub.md factory-triage.md factory-verifier.md `, then `factory-implementer.md factory-reviewer.md factory-verifier.md `, then `local`

### Requirement: The reviewer and verifier may write only their run's output and scratch files with the file tools
The reviewer and verifier definitions MUST omit Edit, MultiEdit and NotebookEdit and keep Bash and Write, and their hooks MUST block a Write to any path other than their own role's run `output.md` or a file under that run's `scratch/`, after resolving `..`; the implementer definition SHALL keep Edit and Write with no such limit.

#### Scenario: A checker's Write is limited to its run's output file and scratch directory
Needs the GIVEN block of "Every agent type the workflows ask for has a definition" run once.
- WHEN `(.venv/bin/python ${TMPDIR:-/tmp}/t0030-fence.py)`
- THEN it prints exactly these three lines:
  `reviewer: bash=True write=True edit_tools=none output=allowed scratch=allowed worktree=blocked escape=blocked other_run=blocked repo=blocked`
  `verifier: bash=True write=True edit_tools=none output=allowed scratch=allowed worktree=blocked escape=blocked other_run=blocked repo=blocked`
  `implementer: bash=True write=True edit_tools=Edit output=allowed scratch=allowed worktree=allowed escape=allowed other_run=allowed repo=allowed`

