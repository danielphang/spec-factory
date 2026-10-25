## ADDED Requirements

### Requirement: run finish records a run's tokens from its transcript when the run has no reply usage
`run finish RUN --transcripts DIR` MUST record under the run's `claude:` key, with `source: transcript`, the path of the one transcript under DIR that names the run's directory and starts after the run started, its input, cache-read, cache-creation and output tokens with each message counted once, and no dollars, when the run gets no usage from `--reply`; a reply with usage SHALL be recorded as before, and a transcript naming another run or dated before the run started SHALL NOT be taken.

#### Scenario: run finish records the transcript's tokens for a run with no reply, and keeps a reply's record
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell, through the briefing's wrapper. The first run's transcript repeats one message's record, as Claude Code writes them; beside it lie a transcript naming another run and one naming this run but dated 2026-01-01.
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/store; X=$T/cc/projects; printf '# F\n\nDo x.\n' > $T/req.md && bin/factory ticket new --file $T/req.md >/dev/null; st() { bin/factory run start --role triage --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'; }; u() { printf '{"type": "user", "timestamp": "%s", "message": {"role": "user", "content": "[Workflow harness — computed task] Your entire input is the file %s/runs/%s/input.md"}}\n' $1 $FACTORY_STATE $2; }; a() { printf '{"type": "assistant", "timestamp": "%s", "message": {"id": "%s", "usage": {"input_tokens": %s, "cache_read_input_tokens": %s, "cache_creation_input_tokens": %s, "output_tokens": %s}}}\n' "$@"; }; now() { date -u +%Y-%m-%dT%H:%M:%SZ; }; out() { printf 'Type: bug\nTitle: T\nSummary: s\nEvidence: e\nAssumptions: a\nSTATUS: ACCEPT\nCONFIDENCE: high, x\nESCALATIONS: none\n' > $FACTORY_STATE/runs/$1/output.md; }; show() { .venv/bin/python -c 'import sys, yaml; c = yaml.safe_load(open(sys.argv[1])).get("claude"); u = (c or {}).get("usage") or {}; print("none" if c is None else " ".join(str(v) for v in [c.get("source"), c.get("session_id"), c.get("total_cost_usd")] + [u.get(k) for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens", "output_tokens")] + [str(c.get("transcript") or "-").rsplit("/", 1)[-1]]))' $FACTORY_STATE/runs/$1/meta.yaml; }; R1=$(st); mkdir -p $X/p/s/subagents/workflows/wf; t=$(now); { u $t $R1; a $t m1 5 100 0 3; a $t m1 5 100 0 3; a $t m2 1 200 4 10; } > $X/p/s/subagents/workflows/wf/agent-1.jsonl; { u $t run-9999-triage; a $t m3 1000 0 0 1000; } > $X/p/s/agent-2.jsonl; { u 2026-01-01T00:00:00Z $R1; a 2026-01-01T00:00:00Z m4 1000 0 0 1000; } > $X/p/old.jsonl; out $R1; bin/factory run finish $R1 --transcripts $X >/dev/null 2>&1; f1=$?; R2=$(st); t=$(now); { u $t $R2; a $t m5 1000 0 0 1000; } > $X/p/s/agent-3.jsonl; printf '{"session_id": "s2", "total_cost_usd": 0.5, "num_turns": 2, "usage": {"input_tokens": 1, "output_tokens": 2}}\n' > $T/reply.json; out $R2; bin/factory run finish $R2 --reply $T/reply.json --transcripts $X >/dev/null 2>&1; f2=$?; echo "finish=$f1 $f2"; show $R1; show $R2; bin/factory stats --store $FACTORY_STATE | grep '^| triage |' | grep -o 'record [0-9]*, transcript [0-9]*, none [0-9]*')`
- THEN it prints exactly four lines: `finish=0 0`, then `transcript None None 6 300 4 13 agent-1.jsonl`, then `None s2 0.5 1 None None 2 -`, then `record 2, transcript 0, none 0`

### Requirement: A run a Workflow script starts carries its transcript's tokens
`factory/workflows/intake.js` and `factory/workflows/build.js` MUST pass `--transcripts` with the directory where Claude Code keeps transcripts (`$CLAUDE_CONFIG_DIR/projects`, else `$HOME/.claude/projects`) on every `run finish` they run, so that each run they finish records its agent's tokens.

#### Scenario: A run the intake script starts carries its transcript's tokens
- GIVEN the file written by the block below, run once at column 0 as shown

```sh
cat > ${TMPDIR:-/tmp}/t0056-wf.mjs <<'EOF'
// node t0056-wf.mjs, from the checkout under test: runs factory/workflows/intake.js on T-0001 of the
// store $FACTORY_STATE. Each clerk command runs for real (sh -c). Each role call stands in for a
// Workflow agent: it writes the role's output with STATUS NEEDS-HUMAN and, as Claude Code does, a
// transcript under $CLAUDE_CONFIG_DIR/projects whose first user message is the call's prompt and which
// records one model call: 7 input, 70 cache-read, 0 cache-creation and 3 output tokens.
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const src = readFileSync('factory/workflows/intake.js', 'utf8').replace(/^export const meta/m, 'const meta')
let n = 0
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  const run = prompt.match(/(\S+\/runs\/run-\d+-[a-z_]+)\/input\.md/)[1]
  const dir = `${process.env.CLAUDE_CONFIG_DIR}/projects/p/s/subagents/workflows/wf`
  mkdirSync(dir, { recursive: true })
  const ts = new Date().toISOString()
  n += 1
  writeFileSync(`${dir}/agent-${n}.jsonl`,
    JSON.stringify({ type: 'user', timestamp: ts, message: { role: 'user', content: `[Workflow harness — computed task] ${prompt}` } }) + '\n' +
    JSON.stringify({ type: 'assistant', timestamp: ts, message: { id: `m${n}`, usage: { input_tokens: 7, cache_read_input_tokens: 70, cache_creation_input_tokens: 0, output_tokens: 3 } } }) + '\n')
  const text = 'Question for human: which one?\nSTATUS: NEEDS-HUMAN\nCONFIDENCE: low, stub\nESCALATIONS: none\n'
  writeFileSync(`${run}/output.md`, text)
  return text
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: process.cwd(), state: process.env.FACTORY_STATE, inlineRoles: true }, agent,
  () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
EOF
```

- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/store CLAUDE_CONFIG_DIR=$T/cc; printf '# F\n\nDo x.\n' > $T/req.md && bin/factory ticket new --file $T/req.md >/dev/null && node ${TMPDIR:-/tmp}/t0056-wf.mjs >/dev/null 2>&1; echo "state=$(bin/factory ticket show T-0001 | sed -n 's/^status: //p')"; for m in $FACTORY_STATE/runs/*/meta.yaml; do .venv/bin/python -c 'import sys, yaml; m = yaml.safe_load(open(sys.argv[1])); c = m.get("claude"); u = (c or {}).get("usage") or {}; print(m["role"], "none" if c is None else " ".join(str(v) for v in [c.get("source")] + [u.get(k) for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens", "output_tokens")]))' $m; done)`
- THEN it prints exactly two lines: `state=parked`, then `triage transcript 7 70 0 3`

### Requirement: A drive run whose process gave no usable reply carries its transcript's tokens
`factory drive` MUST pass the same transcript directory on each `run finish` it runs, so that a run whose `claude` process printed no JSON reply, or that the driver stopped, records its transcript's tokens.

#### Scenario: A drive run whose claude process failed records its transcript's tokens
- GIVEN the stand-in written by the block below, run once at column 0 as shown

```sh
mkdir -p ${TMPDIR:-/tmp}/t0056-bin && cat > ${TMPDIR:-/tmp}/t0056-bin/claude <<'EOF'
#!/bin/sh
# Stands in for a `claude` process that fails: run from a role run's directory, it writes a transcript
# under $CLAUDE_CONFIG_DIR/projects whose first user message names the run's input and which records one
# model call (2 input, 20 cache-read, 0 cache-creation, 1 output tokens), then prints no JSON and exits 1.
d=$CLAUDE_CONFIG_DIR/projects/p && mkdir -p $d && t=$(date -u +%Y-%m-%dT%H:%M:%SZ)
printf '{"type": "user", "timestamp": "%s", "message": {"role": "user", "content": "Read %s/input.md"}}\n{"type": "assistant", "timestamp": "%s", "message": {"id": "m1", "usage": {"input_tokens": 2, "cache_read_input_tokens": 20, "cache_creation_input_tokens": 0, "output_tokens": 1}}}\n' $t "$PWD" $t > $d/s1.jsonl
echo 'not json'; echo 'stand-in failure' >&2; exit 1
EOF
chmod +x ${TMPDIR:-/tmp}/t0056-bin/claude
```

- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/store CLAUDE_CONFIG_DIR=$T/cc; printf '# F\n\nDo x.\n' > $T/req.md && bin/factory ticket new --file $T/req.md >/dev/null && PATH=${TMPDIR:-/tmp}/t0056-bin:$PATH bin/factory drive T-0001 --phase intake >/dev/null 2>&1; echo "state=$(bin/factory ticket show T-0001 | sed -n 's/^status: //p')"; for m in $FACTORY_STATE/runs/*/meta.yaml; do .venv/bin/python -c 'import sys, yaml; m = yaml.safe_load(open(sys.argv[1])); c = m.get("claude"); u = (c or {}).get("usage") or {}; print(m["role"], m["status"], "none" if c is None else " ".join(str(v) for v in [c.get("source")] + [u.get(k) for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens", "output_tokens")]))' $m; done)`
- THEN it prints exactly two lines: `state=parked`, then `triage KILLED transcript 2 20 0 1`

