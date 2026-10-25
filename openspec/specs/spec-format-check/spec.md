# spec-format-check

## Requirements

### Requirement: spec add refuses a malformed spec where current truth is enabled
When the store has an `openspec/` tree, `spec add` SHALL refuse, with exit 2 and nothing written, a spec that `approve-spec` would refuse as malformed or as not applying to current truth, with the error `spec not added: ` followed by the same errors; a well-formed spec MUST still be stored.

#### Scenario: spec add refuses a spec whose label wraps or is followed by a word, and stores a well-formed one
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0057-claude <<'EOF'
#!/usr/bin/env node
// Stands in for `claude`. Run from a role run's directory (runs/run-NNNN-<role>). Plays the next entry
// of its role's list in $T57_PLAYS (the last one repeats), counted in $T57_LOG.n-<role>, and appends
// "<role> <entry>" to $T57_LOG. An entry is a STATUS, or "<file>:<STATUS>": it writes output.md as the
// text of ${TMPDIR:-/tmp}/t0057-<file>.md, if given, then the trailer, and replies with the same text,
// shaped like `claude -p --output-format json`.
const fs = require('fs'), path = require('path')
const role = (path.basename(process.cwd()).match(/^run-\d+-([a-z_]+)$/) || [])[1]
const log = process.env.T57_LOG, list = JSON.parse(process.env.T57_PLAYS || '{}')[role] || ['']
const nf = `${log}.n-${role}`, n = (fs.existsSync(nf) ? +fs.readFileSync(nf, 'utf8') : 0) + 1
fs.writeFileSync(nf, String(n))
const p = list[Math.min(n, list.length) - 1], [file, st] = p.includes(':') ? p.split(':') : ['', p]
fs.appendFileSync(log, `${role} ${p}\n`)
const text = (file ? fs.readFileSync(`${process.env.TMPDIR || '/tmp'}/t0057-${file}.md`, 'utf8') : '') +
  `\nSTATUS: ${st}\nCONFIDENCE: high, stub\nESCALATIONS: none\n`
fs.writeFileSync('output.md', text)
process.stdout.write(JSON.stringify({ type: 'result', subtype: 'success', is_error: false, result: text,
  session_id: 'stub', total_cost_usd: 0, num_turns: 1, usage: {} }) + '\n')
EOF
chmod +x ${TMPDIR:-/tmp}/t0057-claude && mkdir -p ${TMPDIR:-/tmp}/t0057-bin && ln -sf ${TMPDIR:-/tmp}/t0057-claude ${TMPDIR:-/tmp}/t0057-bin/claude
cat > ${TMPDIR:-/tmp}/t0057-wf.mjs <<'EOF'
// node t0057-wf.mjs <workflow script> <ticket>, from the checkout under test: runs that Workflow-tool
// script on <ticket> of the store $FACTORY_STATE. Each clerk command runs for real (sh -c, from this
// checkout); each role call runs t0057-claude from the run's directory and returns its reply's result.
import { readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const [script, ticket] = process.argv.slice(2)
const src = readFileSync(script, 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  const run = prompt.match(/(\S+\/runs\/run-\d+-[a-z_]+)\/input\.md/)[1]
  const cp = spawnSync(`${process.env.TMPDIR || '/tmp'}/t0057-claude`, ['-p', prompt], { cwd: run, encoding: 'utf8' })
  return JSON.parse(cp.stdout).result
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket, repo: process.cwd(), state: process.env.FACTORY_STATE, inlineRoles: true }, agent,
  (m) => console.log(m), () => {}, async (fs) => Promise.all(fs.map(f => f())))
EOF
t57() { n=$1; shift; printf '%s\n' '=== proposal.md' '## Problem' 'A thing is missing.' '=== specs/thing/spec.md' \
  '## ADDED Requirements' '### Requirement: The thing works' 'The thing SHALL work.' "#### Scenario: $n" '- WHEN `true`' \
  '- THEN it exits 0' '=== verification.md' '## Acceptance' "$@"; }
t57 'the thing works' '- the thing works → NEW; fails today' > ${TMPDIR:-/tmp}/t0057-good.md
t57 'the thing works' '- the thing works' '  → NEW; fails today' > ${TMPDIR:-/tmp}/t0057-wrapped.md
t57 'the thing works' '- the thing works → REGRESSION in its new form.' > ${TMPDIR:-/tmp}/t0057-worded.md
t57 'the `echo hi` thing works' '- the `echo hi` thing works' '  → NEW; fails today' > ${TMPDIR:-/tmp}/t0057-ticked.md
cat > ${TMPDIR:-/tmp}/t0057-intake.sh <<'EOF'
# Sourced from the repo root with SIDE (script or drive) and P (plays, as for t0057-claude) set. Builds
# a throwaway store with current truth enabled (an `openspec/` tree, no capabilities yet) whose T-0001
# is ready for its spec writer, and takes it through intake: the intake Workflow script under node, or
# `factory drive T-0001 --phase intake`, each role played by t0057-claude. Leaves $S (the store) and
# prints `<state> spec=<round> versions=<n> writer=<runs> critic=<runs> reason=<park reason>`.
S=$(cd "$(mktemp -d)" && pwd -P)/store; export FACTORY_STATE=$S T57_LOG=$S.plays T57_PLAYS="$P"; : > $T57_LOG
mkdir -p $S/openspec/specs && printf '# Fixture\n\nThe bot should do the thing.\n' > $S.req.md
bin/factory ticket new --file $S.req.md >/dev/null && bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
if [ $SIDE = script ]; then node ${TMPDIR:-/tmp}/t0057-wf.mjs factory/workflows/intake.js T-0001 > $S.out 2> $S.err
else PATH=${TMPDIR:-/tmp}/t0057-bin:$PATH bin/factory drive T-0001 --phase intake > $S.out 2> $S.err; fi
.venv/bin/python -c 'import sys,yaml; t=yaml.safe_load(open(sys.argv[1])); print(t["status"], "spec=%s" % t["round"]["spec"], "versions=%s" % t["spec"]["version"], end=" ")' $S/tickets/T-0001.yaml
echo "writer=$(ls $S/runs | grep -c spec_writer) critic=$(ls $S/runs | grep -c critic) reason=$(.venv/bin/python -c 'import sys,yaml; print(((yaml.safe_load(open(sys.argv[1])).get("parked") or {}).get("reason") or "").strip())' $S/tickets/T-0001.yaml)"
EOF
```

- WHEN `(S=$(cd "$(mktemp -d)" && pwd -P)/store; export FACTORY_STATE=$S; mkdir -p $S/openspec/specs; printf '# F\n\nx\n' > $S.req.md; bin/factory ticket new --file $S.req.md >/dev/null; for f in wrapped worded good; do bin/factory spec add T-0001 --file ${TMPDIR:-/tmp}/t0057-$f.md >/dev/null 2>$S.err; echo "$f exit=$? versions=$(ls $S/specs/T-0001 2>/dev/null | grep -c '^v[0-9]*\.md$') added=$(cat $S/log/*.jsonl | grep -c '"spec.added"') err=$(head -1 $S.err)"; done)`
- THEN it prints exactly `wrapped exit=2 versions=0 added=0 err=spec not added: scenario 'the thing works' has no NEW/REGRESSION label in verification.md`, then `worded exit=2 versions=0 added=0 err=spec not added: scenario 'the thing works' has no NEW/REGRESSION label in verification.md`, then `good exit=0 versions=1 added=1 err=`, one per line

### Requirement: approve-spec keeps its own check
`approve-spec` SHALL still refuse a malformed spec, including one given with `--edit`, with its `spec not pinned: ` error.

#### Scenario: approve-spec still refuses a malformed spec
Needs the GIVEN block of "spec add refuses a spec whose label wraps or is followed by a word, and stores a well-formed one" run once.
- WHEN `(S=$(cd "$(mktemp -d)" && pwd -P)/store; export FACTORY_STATE=$S; mkdir -p $S/openspec/specs; printf '# F\n\nx\n' > $S.req.md; bin/factory ticket new --file $S.req.md >/dev/null; bin/factory approve-spec T-0001 --edit ${TMPDIR:-/tmp}/t0057-wrapped.md >/dev/null 2>$S.err; echo "exit=$? $(head -1 $S.err)")`
- THEN it prints exactly `exit=2 spec not pinned: scenario 'the thing works' has no NEW/REGRESSION label in verification.md`

### Requirement: spec add is unchanged where current truth is not enabled, and for a NEEDS-HUMAN draft
On a store with no `openspec/` tree, `spec add` SHALL store any spec as before, and `spec add --from-run` of a spec writer run that finished NEEDS-HUMAN MUST store its draft even when it is malformed.

#### Scenario: A store without current truth stores a malformed spec as before
Needs the GIVEN block of "spec add refuses a spec whose label wraps or is followed by a word, and stores a well-formed one" run once.
- WHEN `(S=$(cd "$(mktemp -d)" && pwd -P)/store; export FACTORY_STATE=$S; printf '# F\n\nx\n' > $S.req.md; bin/factory ticket new --file $S.req.md >/dev/null; bin/factory spec add T-0001 --file ${TMPDIR:-/tmp}/t0057-wrapped.md >/dev/null; echo "exit=$? versions=$(ls $S/specs/T-0001 | grep -c '^v[0-9]*\.md$')")`
- THEN it prints exactly `exit=0 versions=1`

#### Scenario: A spec writer's NEEDS-HUMAN draft is stored even when malformed
Needs the GIVEN block of "spec add refuses a spec whose label wraps or is followed by a word, and stores a well-formed one" run once.
- WHEN `(S=$(cd "$(mktemp -d)" && pwd -P)/store; export FACTORY_STATE=$S; mkdir -p $S/openspec/specs; printf '# F\n\nx\n' > $S.req.md; bin/factory ticket new --file $S.req.md >/dev/null; bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null; R=$(bin/factory run start --role spec_writer --ticket T-0001 | .venv/bin/python -c 'import json,sys; print(json.load(sys.stdin)["run_id"])'); { cat ${TMPDIR:-/tmp}/t0057-wrapped.md; printf 'STATUS: NEEDS-HUMAN\nCONFIDENCE: low, stub\nESCALATIONS: none\n'; } > $S/runs/$R/output.md; bin/factory run finish $R >/dev/null; bin/factory spec add T-0001 --from-run $R >/dev/null; echo "exit=$? versions=$(ls $S/specs/T-0001 | grep -c '^v[0-9]*\.md$')")`
- THEN it prints exactly `exit=0 versions=1`
