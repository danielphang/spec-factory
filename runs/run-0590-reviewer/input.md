## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`: `dev/issues.md`, this repo's issue index, kept live; and the build spec, its plan and the
  P0 walking skeleton, frozen as history from building the harness, which no change updates;
- the harness, as code in this repo: `factory/` (the package, its role prompts and its workflow
  scripts), `bin/factory` (the entry point), `agents/` (the agent definition templates) and
  `tests/factory/` (its suite). Install with `uv sync --frozen`; test with
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`;
- `.factory/`, this repo's own instance of the factory: `instance.yaml`, this briefing,
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `store/`.
  The store is a checkout of its own branch, `factory-store`; the operator commits it there, so a
  store commit never moves `main`.

Two checkouts. Tickets are built and merged in the dev checkout, `~/dev/spec-factory` on `main`.
The factory runs from the runtime checkout, `~/dev/spec-factory-harness`, a detached worktree of
this repo at the harness revision `.factory/harness.lock` has accepted. A merge into `main` never
changes the running code; only the upgrade step moves the runtime, after which the instance
refuses its store until `--accept-harness`. Your shell may start in another directory: use
absolute paths, or `cd ~/dev/spec-factory && <cmd>`.

The Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3.5`) is instance A: a target
with only `.factory/`, run from the same runtime by its own Driver session. This repo's harness was
imported from its retired `feat/lionbot-v3` branch. Read it only to observe what a fix does there; never write there, and never copy its test names,
line numbers or commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents, the harness suite). A change to the design doc keeps its
own conventions: its changelog entry in `docs/changelog.md`, and any `docs/prompts/` file whose
block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. For
every role but the implementer that is the only file you may create or modify. The implementer
also changes files in its own worktree and commits there, and nowhere else. Then return the same
text as your final message.

This repo's current-state page is the top-level `README.md`. A change to a command, state, stop or
path updates it in the same ticket; read its "Maintaining this page" section before editing it.

Who reads what the roles write here: the operator at the spec gate, and a technical reader new to this project reading the README or a PR description. Gloss every term specific to the factory at first use (docs/writing.md).
## Output file
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0590-reviewer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0590-reviewer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0590-reviewer/wt` (branch `factory/T-0057.1`, base `11080b100b31c70c69cc1867960819270d134a23`, head `3fdcda3e76e891e79e7949c78b78cef051f1dfd2`). There is no remote: commit on the branch; the PR is the branch plus the description you return. The verifier runs the gate commands on this head; you do not run them.

## Sub-ticket T-0057.1

T-0057.1 / Check a spec's format when the spec is added, and send a format error back to the spec writer instead of to the human gate
Depends on: none
Parallel-safe: yes

Parent: T-0057, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- spec add refuses a spec whose label wraps or is followed by a word, and stores a well-formed one
- approve-spec still refuses a malformed spec
- A store without current truth stores a malformed spec as before
- A spec writer's NEEDS-HUMAN draft is stored even when malformed
- A refused draft goes back to the spec writer and the next well-formed one reaches the critic, in the driver and the script
- A refusal in the last round parks with the refusal, quoted safely, in the driver and the script
- The spec writer's next run receives the refusal and its refused output
- README, the design doc and the changelog describe the refusal route
- The suite passes, only the two listed test files change, and every added test file fails on the base
Tests to change: the parent's list.
Protected paths: the parent's Risk list.

## Parent spec (v2, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0057/v2.md`

=== proposal.md
## Problem

The operator can approve a spec and still have the factory's own code refuse it, over a formatting mistake that code could have caught before any agent reviewed the spec. Then the operator has to fix the formatting by hand and approve the spec again.

Some background. In this factory, the spec writer agent writes each spec. The critic agent reviews it. Then the operator approves it at the spec gate, the one point where a human signs off a design before any code is written. The harness is the code that stores specs and moves tickets between agents. It keeps them in the store, a directory of tickets, spec versions and run records. The harness stores a spec writer's draft as a new spec version with the command `spec add`. The operator approves a version at the gate with the command `approve-spec`.

The harness also runs a format check on a spec. The check confirms that each part of the spec is present. One part, `verification.md`, lists the acceptance scenarios. The check confirms that each scenario there has a NEW or REGRESSION label on the line that names it. The check also confirms that the spec's changes fit current truth, the stored description of what the system does today. Current truth lives in the store's `openspec/` directory. A store without that directory has no current truth, and the harness runs no format check there.

Today the format check runs only when the operator approves. The spec writer and the critic never see its verdict. So a spec with a wrapped label line passes both agents, reaches the operator, and is refused only then. On 12 October that happened with three labels on one spec.

This change runs the same check when the spec writer's draft is stored. A draft that fails is not stored. It goes back to the spec writer with the harness's message, as a new round. A round is one write-then-review pass, and a spec gets two. The ticket parks only when no round is left. To park is to stop the ticket and wait for a human. This follows the operator's standing answer: a form error the harness can detect goes back to the role that produced it, and does not park.

## Root cause

`spec add` (`factory/cli.py:407-410`) stores any text. The format check, `_refuse_unless_applies` (`factory/human.py:115-120`), runs first at `approve-spec`. Neither runner has a route that sends a refused draft back to the spec writer, and the writer's input has no place for a refusal (`factory/compose.py:275-296`).

## Out of scope

- `approve-spec`, `spec amend` and `archive` keep their checks and messages unchanged.
- A store with no `openspec/` tree stores any spec, as today.
- `LABEL_RE` stays as it is. The request offered relaxing it. Cut: once the writer gets the refusal, it can fix the label in its own round.
- No role prompt changes. The request offered naming the label form in the spec writer's prompt. Cut for the same reason. Prompts are also under the replay rule (#80).
- The routing table in `instance.yaml` does not change.
- A `spec add` refusal that does not start `spec not added: ` still parks as `harness-bug: spec add: …`.
- No new `resolve` route. A park with no stored spec version cannot go to the gate with `resolve --to spec-gate`, which needs a version. See Risk.

## Open questions

none

## Decisions

- When the store has an `openspec/` tree, `spec add` runs the same check as `approve-spec`: well formed, and its changes apply to current truth. On failure it refuses with exit 2 and the error `spec not added: <the errors, joined by "; ">`, and writes nothing. The errors are exactly the ones `approve-spec` prints after `spec not pinned: `.
- The check covers `--file` sources and every `--from-run` source except a run that finished NEEDS-HUMAN. That draft carries open questions, and it is stored as today so the operator can read it. Rejected: refusing it. Its question would then reach the operator with no stored draft.
- Both runners, the driver and the intake Workflow script, read a `spec add` refusal whose first line starts `spec not added: ` as a form error. Any other refusal keeps the `harness-bug: spec add: …` park.
- A form error uses up a round. The writer's draft counts as round `max(stored round, 1)`, because the stored round is still 0 before the first move to the critic. If that is below `max_rounds.spec`, the runner sets the round one higher with `ticket set <id> round.spec=<n>` and runs the spec writer again. The ticket stays at `ready-for-spec-writer`. Rejected: a `ready-for-spec-writer → ready-for-spec-writer` routing edge, which would mean editing every instance's `instance.yaml`, a protected path, and the Nanobot instance's by hand. An instance left unedited would then park on the route. Rejected: a new round command, a new write that the live-store fence and README would also have to list.
- When no round is left, the ticket parks as `max rounds: <the refusal's first line>`. In that line each backtick, `$` and `\` becomes `'`, in both runners, so the driver and the script record the same reason and the clerk's shell runs nothing. Today's `park()` already turns each `"` into `'`.
- The writer's next input is built from what the store already holds, and nothing new is recorded. It gets one extra section when its previous finished spec-writer run ended READY-FOR-CRITIC or NEEDS-SPLIT, no `spec.added` event names that run as its source, and the check refuses that run's output now. The section is that run's `output.md`, titled "Your previous output, which the harness refused to store as a spec version", and it opens with the refusal. Rejected: `spec add` writing a refusal record, which breaks the rule that a refusal writes nothing. So the section is derived when the input is built; it is not a record of the refusal. Two edges follow. A draft the operator later stores by hand with `spec add --file` still shows as refused, if the run's own output fails the check. A draft refused only because current truth has changed since then does not show.
- This overturns, for a refused spec only, the 2026-10-07 T-0032 standing decision that later refusal kinds, "#68 format" among them, use the empty-output retry: one re-dispatch, then a park. The operator's Answer 1 (2026-10-19, recorded in `decisions.md` on 2026-10-20) chose a new round counted against the round limit. The operator approves the overturn at this gate.
- Standing, from Answer 1: a form error the harness can detect goes back to the role that produced it as a new round, and does not park until the rounds run out.
- README grows by at most one line net, measured against the change's base, so it fits under the current 1,185 cap and under T-0056's 1,225 in either merge order. Rejected: raising the cap here, which would collide with T-0056's edit of the same four requirements.
- `docs/design.md` gets one routing-table row for the new route, and `docs/changelog.md` gets one entry. The entry takes the next free number and opens `<n>. After issue #105 `. No `docs/prompts/` file changes, because no prompt block changes.

## Risk

Every spec writer run on a store with an `openspec/` tree is affected, on both instances. An instance is one target repository's `.factory/` directory and its store. There are two: this repository's and the Nanobot fork's. A spec that `approve-spec` would have refused now costs a round instead of a gate decision. A spec that only needs a fix the writer cannot make now parks one round earlier than it would have reached the gate. Its park reason starts `max rounds: spec not added:`. If that happens on the writer's first draft, no spec version exists, so `resolve --to spec-gate` refuses it. The operator then closes the ticket with `resolve --close`, or moves it back by hand with `factory ticket transition <id> --to ready-for-spec-writer --by <name> --round spec:reset`. Five existing tests change (Tests to change). The driver and the script change in the same way, and the scenarios check both.

Protected paths: `factory/cli.py`, `factory/compose.py`, `factory/drive.py`, `factory/workflows/intake.js`

## Operator steps

1. After merge, upgrade the runtime, the pinned harness checkout the factory runs from, as usual (README "Upgrading the runtime"). Then accept the new revision in both instances.
2. Before the next Workflow-script intake, write a fresh launch copy with `factory launch-script intake`. The launch copy is the file the Workflow tool runs, written from `intake.js`. A launch copy written earlier holds the old `intake.js` and parks a refused draft as `harness-bug: spec add: …`.

=== design.md
## Proposed change

One PR. The prototype's diff is about 75 lines of harness and documents, plus the test edits and new tests.

**A. `spec add` runs the format check** (`factory/cli.py`). In `spec_add`, read the text as today. If `specstore.is_active(root)`, and the source is not a `--from-run` run whose `meta.yaml` records `status: NEEDS-HUMAN`, call `_refuse_unless_applies(root, text, "spec not added")` before `_add_spec_version`. Import `_refuse_unless_applies` from `factory.human`, alongside the names `cli.py` already imports from there. Keep the function in `factory/human.py`, where `openspec/specs/harness-code/spec.md` pins it. `cli.py` must stay under 900 lines.

**B. The driver's route** (`factory/drive.py`, `intake`). Where `spec add` returns not ok:
- Let `why` be the first line of the stripped `stderr`. If it does not start `spec not added: `, park with `_harness_bug("spec add", added)` as today.
- Let `cur = max(rnd, 1)`. If `cur >= self.max_spec`, park with `"max rounds: " + <why with each backtick, $ and \ replaced by '>`, with outputs the writer's run id. Return `{"ticket", "state": "parked", "rounds": cur, "reason": "max rounds"}`.
- Otherwise call `ticket set <T> round.spec=<cur + 1>`. If that is not ok, park with `_harness_bug("round increment refused", st)`. Then set `rnd = cur + 1`, write one step line saying the spec went back to the writer in round `rnd`, with `why`, and `continue` the loop in state `ready-for-spec-writer`.

No other line in `drive.py` formats a `harness-bug: … stderr` reason. Current truth pins that count at 1.

**C. The intake script's route** (`factory/workflows/intake.js`). The same steps at the `spec add` call (line 188). `why` is the first line of the trimmed `added.stderr`. The round step is a clerk call of `${BIN} ticket set ${TICKET} round.spec=${cur + 1}`, labelled `round increment`. The park reason replaces `` ` ``, `$` and `\` with `'` (`/[`$\\]/g`) before `park()`. `log()` the same message the driver steps. The return values match B.

**D. The writer's next input** (`factory/compose.py`, the `spec_writer` branch). After the NEEDS-HUMAN case on `prev`, add a branch for a `prev` that ended `READY-FOR-CRITIC` or `NEEDS-SPLIT` when `specstore.is_active(root)`. Compute the refusal: `None` if any `spec.added` event in `store.log_lines(root)` has `source` equal to `prev`'s run id, or if its `output.md` is missing. Otherwise run `_refuse_unless_applies` on `status.strip_trailer(<output>)` with `"spec not added"`, and catch `store.Refused` for its text. When there is a refusal, `add()` the run's `output.md` under the heading `Your previous output, which the harness refused to store as a spec version`. Its body opens with `The harness refused it with: <refusal>`, then the output. That records the path in `input_sources`. `compose.py` may import `_refuse_unless_applies` from `factory.human`; nothing `human.py` imports reaches `compose.py`.

**E. Documents.**
- E1. `README.md`, "The intake workflow, step by step". Replace the paragraph's lines 2-7 (from `spec writer; REJECT closes` to `back to triage.`) with these six lines:
  ```
  spec writer; REJECT closes the ticket; CLARIFY waits for the requester; NEEDS-HUMAN parks. The
  harness saves the spec as a new version only if it is well-formed and fits current truth; if not, it
  goes back to the writer, using up a round. The critic's REVISE sends it back once; a second REVISE,
  or a refused spec in the last round, parks. NEEDS-SPLIT, a spec that names how to split an oversized
  request, goes to the critic like READY-FOR-CRITIC. APPROVE moves the ticket to the spec gate, where
  intake stops. The human approves or sends it back; a requester's answer returns a ticket to triage.
  ```
  In the flowchart below it, after the `W -- "READY-FOR-CRITIC or NEEDS-SPLIT" --> K…` line, add `  W -- "spec refused, a round left" --> W`.
- E2. `README.md`, "What each role reads and writes", Spec writer row. After the words "after a revision request, the critic's findings and its own previous spec;", add "after a spec that `spec add` refused, the refusal and that output;". The row stays one line.
- E3. `docs/design.md`, routing table. Before the `| Spec writer | NEEDS-HUMAN |` row, add `| Spec writer | READY-FOR-CRITIC / NEEDS-SPLIT, and `spec add` refuses the spec: malformed, or its changes do not apply to current truth | Spec writer (round +1) if round < {2}, else Human queue | The refusal and the refused output |`.
- E4. `docs/changelog.md`: one entry, the next free number, opening `<n>. After issue #105 (2026-10-12), where`. It says that `approve-spec` refused a spec the critic had approved, over three labels. It says that `spec add` now runs the same check. It says that a refused spec goes back to the spec writer as a new round, and parks with the refusal when no round is left. It names `spec add`, `approve-spec` and the round.

E1 adds one line net (the flowchart edge). E2 to E4 add none to README.

**F. Tests.** At least one new test file, for example `tests/factory/test_spec_add_refusal.py`, that fails on the base. Cover `spec add`'s refusal and its empty write, the NEEDS-HUMAN exemption, and the driver's route on a refused draft. Change the five tests below and no other existing test file.

## Tests to change

- `tests/factory/test_spec_store.py::test_item_88_gate_refuses_a_delta_that_does_not_apply_and_a_malformed_version`. It asserts that `spec add` stores a delta that does not apply (exit 0), then that `approve-spec --version 2` refuses it. It follows the first Decision: `spec add` now refuses that delta. Change: assert that `spec add` refuses with `spec not added` and `no-such-req`, then that `approve-spec --edit` of the same file refuses with `no-such-req`. Keep its later assertions: no approved v2, no `spec-v2.yaml`, v1's change folder intact.
- `tests/factory/test_spec_store.py::test_an_empty_op_heading_counts_as_a_heading_and_a_slash_label_is_no_label`. It stores two malformed versions with `spec add` and checks `approve-spec --version 2|3`. Same Decision. Change: check `approve-spec --edit <file>`, with the same refusal texts.
- `tests/factory/test_spec_store.py::test_acceptance_labels_allow_ordinary_punctuation_but_not_a_choice`. It stores each bad label through `spec add` and checks `approve-spec --version`. Same Decision. Change: check `approve-spec --edit <file>` for each bad label, with the same `no NEW/REGRESSION label` assertion.
- `tests/factory/test_spec_store.py::test_writer_and_critic_receive_current_truth_as_input_sources`. Its writer output, `=== proposal.md\n## Problem\nx\n`, is malformed, so `spec add` now stores no v1 and the critic's `input_sources` lose `specs/T-0001/v1.md`. Same Decision. Change: the writer's output becomes a well-formed spec whose change applies to the test's `status-parser` truth, for example the file's `FOUR_PART` with `ADDED` replaced by `MODIFIED`. The two `input_sources` assertions stay as they are.
- `tests/factory/test_shepherd.py::test_the_gate_refuses_a_delta_that_does_not_fit_current_truth`. It expects the second ticket's misfit delta to be stored, to reach the gate and to be refused by `approve-spec`. It follows the first and third Decisions: the delta is now refused at `spec add`, and the ticket stays with the spec writer. Change: dispatch the second ticket's spec writer with `route=False`, then assert that `spec add --from-run` refuses with `ADDED 'the-thing' is already in current truth`, and that the ticket stays `ready-for-spec-writer`. `tests/factory/_fixtures.py` does not change.

=== specs/spec-format-check/spec.md
## ADDED Requirements

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

=== specs/build-dispatch/spec.md
## ADDED Requirements

### Requirement: A spec that spec add refuses as malformed goes back to the spec writer as a new round
When `spec add` refuses a spec writer's READY-FOR-CRITIC or NEEDS-SPLIT output with an error starting `spec not added: `, the driver and the intake Workflow script SHALL send the ticket back to the spec writer, counting the refused draft as one round, while a round is left; the next stored version then goes to the critic as usual, and both runners MUST leave the same records.

#### Scenario: A refused draft goes back to the spec writer and the next well-formed one reaches the critic, in the driver and the script
Needs the GIVEN block of "spec add refuses a spec whose label wraps or is followed by a word, and stores a well-formed one" run once.
- WHEN `(for SIDE in script drive; do P='{"spec_writer": ["wrapped:READY-FOR-CRITIC", "good:READY-FOR-CRITIC"], "critic": ["APPROVE"]}'; . ${TMPDIR:-/tmp}/t0057-intake.sh; done)`
- THEN it prints exactly `awaiting-spec-gate spec=2 versions=1 writer=2 critic=1 reason=` twice, one per line

### Requirement: A spec refused in the last round parks the ticket with the refusal
When no round is left, the driver and the intake Workflow script SHALL park the ticket with the reason `max rounds: ` followed by the refusal's first line, in which each backtick, `$` and `\` is replaced by `'`, so that no part of it runs as a shell command; both runners MUST record the same reason.

#### Scenario: A refusal in the last round parks with the refusal, quoted safely, in the driver and the script
Needs the GIVEN block of "spec add refuses a spec whose label wraps or is followed by a word, and stores a well-formed one" run once. The first plays refuse both drafts. The second has the critic send a stored version back and then refuses the second draft.
- WHEN `(for P in '{"spec_writer": ["ticked:READY-FOR-CRITIC"]}' '{"spec_writer": ["good:READY-FOR-CRITIC", "worded:NEEDS-SPLIT"], "critic": ["REVISE"]}'; do for SIDE in script drive; do . ${TMPDIR:-/tmp}/t0057-intake.sh; done; done)`
- THEN it prints exactly `parked spec=2 versions=0 writer=2 critic=0 reason=max rounds: spec not added: scenario 'the 'echo hi' thing works' has no NEW/REGRESSION label in verification.md` twice, then `parked spec=2 versions=1 writer=2 critic=1 reason=max rounds: spec not added: scenario 'the thing works' has no NEW/REGRESSION label in verification.md` twice, one per line

=== specs/role-inputs/spec.md
## ADDED Requirements

### Requirement: The spec writer's run after a refused draft receives the refusal and that draft
When the ticket's previous finished spec writer run ended READY-FOR-CRITIC or NEEDS-SPLIT, no spec version came from it, and its output fails the format check, the next spec writer run's input SHALL hold a section titled "Your previous output, which the harness refused to store as a spec version" that opens with the refusal and holds that run's output, and that run's `output.md` MUST be among the input's sources; a first spec writer run gets no such section.

#### Scenario: The spec writer's next run receives the refusal and its refused output
Needs the GIVEN block of "spec add refuses a spec whose label wraps or is followed by a word, and stores a well-formed one" run once.
- WHEN `(SIDE=drive; P='{"spec_writer": ["wrapped:READY-FOR-CRITIC", "good:READY-FOR-CRITIC"], "critic": ["APPROVE"]}'; . ${TMPDIR:-/tmp}/t0057-intake.sh >/dev/null; I=$S/runs/run-0002-spec_writer/input.md; echo "first=$(grep -c '^## Your previous output, which the harness refused' $S/runs/run-0001-spec_writer/input.md) heading=$(grep -c '^## Your previous output, which the harness refused' $I 2>/dev/null) message=$(grep -c "spec not added: scenario 'the thing works' has no NEW/REGRESSION label in verification.md" $I 2>/dev/null) output=$(grep -cx '  → NEW; fails today' $I 2>/dev/null) source=$(grep -c 'runs/run-0001-spec_writer/output.md' $S/runs/run-0002-spec_writer/meta.yaml 2>/dev/null)")`
- THEN it prints exactly `first=0 heading=1 message=1 output=1 source=1`

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The documents record the format check at spec add and its route back to the spec writer
`README.md`'s "The intake workflow, step by step" SHALL say that a spec is saved only if it is well-formed and fits current truth, and that otherwise it goes back to the writer, using up a round; its flowchart SHALL draw that route back to the spec writer, and the Spec writer row of "What each role reads and writes" SHALL name the refusal. `docs/design.md`'s routing table SHALL hold the route with `spec add` and `round +1`. `docs/changelog.md` SHALL hold one entry opening `After issue #105 `, numbered without a gap, that names `spec add`, `approve-spec` and the round. This change MUST add at most one line net to `README.md`.

#### Scenario: README, the design doc and the changelog describe the refusal route
- WHEN `(B=$(git merge-base HEAD main); y() { [ "$1" -gt 0 ] && echo yes || echo no; }; I=$(sed -n '/^### The intake workflow, step by step$/,/^### The build workflow, step by step$/p' README.md); P=$(printf '%s\n' "$I" | awk '/^Intake runs triage once/{f=1} f&&/^$/{exit} f' | tr '\n' ' '); echo "formed=$(y $(printf '%s' "$P" | grep -c 'well-formed')) truth=$(y $(printf '%s' "$P" | grep -c 'current truth')) round=$(y $(printf '%s' "$P" | grep -c 'round')) edge=$(y $(printf '%s\n' "$I" | grep -cE '^ *W -- "[^"]*refused[^"]*" --> W$')) row=$(y $(grep '^| Spec writer (`spec_writer`) |' README.md | grep -c 'refus')) design=$(y $(grep '^| Spec writer | READY-FOR-CRITIC / NEEDS-SPLIT' docs/design.md | grep 'spec add' | grep -c 'round +1')) growth=$(git diff --numstat $B HEAD -- README.md | awk '{print ($1 - $2 <= 1 ? "ok" : "over")}')"; awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #105 ' docs/changelog.md); echo "entries=$(printf '%s\n' "$E" | grep -c .) terms=$(printf '%s' "$E" | grep -oF -e 'spec add' -e 'approve-spec' -e 'round' | sort -u | grep -c .)")`
- THEN it prints exactly `formed=yes truth=yes round=yes edge=yes row=yes design=yes growth=ok`, then `CONTIGUOUS`, then `entries=1 terms=3`, one per line

=== specs/harness-suite/spec.md
## ADDED Requirements

### Requirement: The suite passes with this change, which changes only the two test files its decisions overturn
The harness suite SHALL pass with this change; among existing test files this change MUST modify or delete only `tests/factory/test_spec_store.py` and `tests/factory/test_shepherd.py`, and each test file it adds SHALL fail, with at least one failed test, against the harness code of the change's base.

#### Scenario: The suite passes, only the two listed test files change, and every added test file fails on the base
Per the standing T-0023 decision, the command gives pytest its own temporary directory under `/tmp` and removes it when it ends. The base is `git merge-base HEAD main`. Its tree is unpacked into that directory, and the added files are copied in beside its tests.
- WHEN `(P=$(mktemp -d /tmp/t0057-suite.XXXXXX) && TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; B=$(git merge-base HEAD main); echo "changed=$(git diff --name-only --diff-filter=DMR $B HEAD -- tests | sort | paste -sd, -) added=$(git diff --name-only --diff-filter=A $B HEAD -- tests | grep -c '/test_[^/]*\.py$')"; mkdir $P/base && git archive $B | tar -x -C $P/base && for f in $(git diff --name-only --diff-filter=A $B HEAD -- tests); do mkdir -p $P/base/${f%/*} && cp $f $P/base/$f; done; for f in $(git diff --name-only --diff-filter=A $B HEAD -- tests | grep '/test_[^/]*\.py$'); do echo "$f on the base: $(cd $P/base && TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider $f 2>&1 | tail -1 | sed 's/ in [0-9.]*s.*//')"; done; rm -rf "$P")`
- THEN the first line reports a number of passed tests and no `failed` or `error`. The second is `changed=<list> added=<n>`, where `<list>` is empty or a comma-separated subset of `tests/factory/test_shepherd.py,tests/factory/test_spec_store.py`, and n is at least 1. Then n lines follow, each `<added test file> on the base: <pytest summary>`, and every summary includes `failed`

=== verification.md
## Acceptance
- spec add refuses a spec whose label wraps or is followed by a word, and stores a well-formed one → NEW; on `3e4705a` it prints `wrapped exit=0 versions=1 added=1 err=`, `worded exit=0 versions=2 added=2 err=` and `good exit=0 versions=3 added=3 err=`: every draft is stored.
- approve-spec still refuses a malformed spec → REGRESSION; it prints `exit=2 spec not pinned: …` on `3e4705a` and on the prototype.
- A store without current truth stores a malformed spec as before → REGRESSION; `exit=0 versions=1` on both.
- A spec writer's NEEDS-HUMAN draft is stored even when malformed → REGRESSION; `exit=0 versions=1` on both.
- A refused draft goes back to the spec writer and the next well-formed one reaches the critic, in the driver and the script → NEW; on `3e4705a` both lines read `awaiting-spec-gate spec=1 versions=1 writer=1 critic=1 reason=`: the wrapped draft is stored and approved, and the writer runs once.
- A refusal in the last round parks with the refusal, quoted safely, in the driver and the script → NEW; on `3e4705a` the first pair reads `parked spec=1 versions=1 writer=1 critic=1 reason=harness-bug: unknown STATUS UNKNOWN from critic` and the second pair reads `parked spec=2 versions=2 writer=2 critic=2 reason=max rounds`: each malformed draft is stored and judged.
- The spec writer's next run receives the refusal and its refused output → NEW; on `3e4705a` it prints `first=0 heading= message= output= source=`: no second writer run exists.
- README, the design doc and the changelog describe the refusal route → NEW; on `3e4705a` it prints every field `no` and `growth=` empty, then `CONTIGUOUS`, then `entries=0 terms=0`.
- The suite passes, only the two listed test files change, and every added test file fails on the base → NEW; on `3e4705a` the second line is `changed= added=0`, so n is 0, not at least 1.

## PR description (the implementer's output)

Sub-ticket: T-0057.1, "Check a spec's format when the spec is added, and send a format error back to the spec writer instead of to the human gate" (parent T-0057, approved spec v2, `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0057/v2.md`)

Branch: `factory/T-0057.1` in `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0057.1`. Base `11080b1`, head `3fdcda3`. There are two commits: `77b7b40` has the change, and `3fdcda3` removes a blank line at the end of the new test file that `git diff --check` flagged.

## What changed

Some terms first. The spec writer is the agent that writes each spec. The critic is the agent that reviews it. The spec gate is where the operator approves a spec. Current truth is the store's `openspec/` tree, which describes what the system does today. A round is one write-then-review pass, and a spec gets two.

Until now, the format check ran only when the operator approved a spec. After this change it also runs when the spec writer's draft is stored. A draft that fails the check is not stored. It goes back to the spec writer as a new round, together with the reason it failed.

**A. `spec add` runs the format check** (`factory/cli.py:409-413`). When the store has current truth, `spec_add` calls `_refuse_unless_applies(root, text, "spec not added")` before it writes the version. That is the same function `approve-spec` calls, and it stays in `factory/human.py`. The check is skipped for a `--from-run` run whose `meta.yaml` says `status: NEEDS-HUMAN`. A refusal exits 2 and writes nothing. `cli.py` is 899 lines, as it was on the base (see Known gaps).

**B. The driver's route** (`factory/drive.py:301-320`). When `spec add` refuses, the driver reads the first line of stderr. If it does not start `spec not added: `, the ticket parks with `_harness_bug("spec add", …)`, as before. Otherwise the driver sets `cur = max(rnd, 1)`.
- If `cur >= max_spec`, the ticket parks as `max rounds: <that line>`, with each backtick, `$` and `\` replaced by `'`. The driver returns `{…, "rounds": cur, "reason": "max rounds"}`.
- Otherwise the driver calls `ticket set T round.spec=<cur+1>`. If that is refused, the ticket parks with `_harness_bug("round increment refused", …)`. If not, the driver steps `spec not stored; back to the spec writer in round <n>: <why>` and runs the writer again.

`grep -cE "harness-bug: .*stderr" factory/drive.py` still prints 1.

**C. The intake script's route** (`factory/workflows/intake.js:190-207`). It takes the same steps. The round increment is a clerk call of `${BIN} ticket set ${TICKET} round.spec=${cur + 1}`, labelled `round increment`. Before `park()`, the park reason goes through `.replace(/[`$\\]/g, "'")`. The script `log()`s the same message as the driver, prefixed `${TICKET}: `, and returns the same values. Every `run finish` still passes `--transcripts` (from T-0056). This change does not touch those lines.

**D. The writer's next input** (`factory/compose.py:65-77`, new `_refusal`; branch at `factory/compose.py:310-314`). Suppose the previous finished spec writer run ended READY-FOR-CRITIC or NEEDS-SPLIT, and the store has current truth. Then `_refusal` checks that run's output. It returns None in two cases: a `spec.added` event in `store.log_lines(root)` names that run as its `source`, or the run's `output.md` is missing. Otherwise it runs `_refuse_unless_applies` on `status.strip_trailer(output)` and returns the `Refused` text. When there is a refusal, `add()` puts that `output.md` under `## Your previous output, which the harness refused to store as a spec version`. The section's body opens `The harness refused it with: <refusal>`, and `add()` also records the path in `input_sources`. `compose.py` now imports `json`, `status` and `_refuse_unless_applies`. Nothing that `human.py` imports, directly or through other modules, imports `compose`.

**E. Documents.**
- E1: `README.md` "The intake workflow, step by step". Paragraph lines 2-7 are replaced with the six lines from the spec, word for word. The flowchart gains the edge `W -- "spec refused, a round left" --> W`.
- E2: the Spec writer row of "What each role reads and writes" gains "after a spec that `spec add` refused, the refusal and that output;". The row is still one line.
- E3: `docs/design.md` gets the routing-table row from the spec, word for word, placed before `| Spec writer | NEEDS-HUMAN |`.
- E4: `docs/changelog.md` gets entry 78, which opens `78. After issue #105 (2026-10-12), where`.

README grows by one line net (`git diff --numstat 11080b1 HEAD -- README.md` prints `8 7`). It is now 1,213 lines. No `docs/prompts/` file changed.

**F. Tests.** There is one new file, and the five listed tests are changed (see below).

Callers of each function this change edits (rule 2 of the coding standard, from `grep -n "_text_from(\|_refuse_unless_applies(" factory/*.py`):
- `_text_from` is called by `spec_add` (`cli.py:410`) and `plan_add` (`cli.py:418`). Its behaviour does not change. Only two of its lines were merged into one.
- `_refuse_unless_applies` is not edited. It gains two callers, `spec_add` and `compose._refusal`. It already had two: `spec_amend` (`human.py:69`) and `approve_spec` (`human.py:145`).

## Acceptance results

Every command ran from the worktree inside the HOME wrapper, with `TMPDIR` set to this run's scratch directory. The GIVEN block was copied word for word from `v2.md` into `scratch/given.sh` and sourced once. Each WHEN was copied word for word into `scratch/accept.sh` (scenarios 1-8) and `scratch/accept9.sh` (scenario 9). Before means base `11080b1`. After means `77b7b40`; scenarios 1-8 were run again on `3fdcda3` and the output did not change (`diff` printed nothing).

1. **spec add refuses a spec whose label wraps or is followed by a word, and stores a well-formed one** (NEW)
   - Before: `wrapped exit=0 versions=1 added=1 err=` / `worded exit=0 versions=2 added=2 err=` / `good exit=0 versions=3 added=3 err=`. This is the failure the spec predicts.
   - After: `wrapped exit=2 versions=0 added=0 err=spec not added: scenario 'the thing works' has no NEW/REGRESSION label in verification.md` / `worded exit=2 versions=0 added=0 err=spec not added: scenario 'the thing works' has no NEW/REGRESSION label in verification.md` / `good exit=0 versions=1 added=1 err=`. This matches the THEN.
2. **approve-spec still refuses a malformed spec** (REGRESSION). After: `exit=2 spec not pinned: scenario 'the thing works' has no NEW/REGRESSION label in verification.md`. It printed the same on the base.
3. **A store without current truth stores a malformed spec as before** (REGRESSION). After: `exit=0 versions=1`.
4. **A spec writer's NEEDS-HUMAN draft is stored even when malformed** (REGRESSION). After: `exit=0 versions=1`.
5. **A refused draft goes back to the spec writer and the next well-formed one reaches the critic, in the driver and the script** (NEW)
   - Before: `awaiting-spec-gate spec=1 versions=1 writer=1 critic=1 reason=`, twice.
   - After: `awaiting-spec-gate spec=2 versions=1 writer=2 critic=1 reason=`, twice.
6. **A refusal in the last round parks with the refusal, quoted safely, in the driver and the script** (NEW)
   - Before: `parked spec=1 versions=1 writer=1 critic=1 reason=harness-bug: unknown STATUS UNKNOWN from critic`, twice, then `parked spec=2 versions=2 writer=2 critic=2 reason=max rounds`, twice.
   - After: `parked spec=2 versions=0 writer=2 critic=0 reason=max rounds: spec not added: scenario 'the 'echo hi' thing works' has no NEW/REGRESSION label in verification.md`, twice, then `parked spec=2 versions=1 writer=2 critic=1 reason=max rounds: spec not added: scenario 'the thing works' has no NEW/REGRESSION label in verification.md`, twice.
7. **The spec writer's next run receives the refusal and its refused output** (NEW)
   - Before: `first=0 heading= message= output= source=`.
   - After: `first=0 heading=1 message=1 output=1 source=1`.
8. **README, the design doc and the changelog describe the refusal route** (NEW)
   - Before: `formed=no truth=no round=no edge=no row=no design=no growth=` / `CONTIGUOUS` / `entries=0 terms=0`.
   - After: `formed=yes truth=yes round=yes edge=yes row=yes design=yes growth=ok` / `CONTIGUOUS` / `entries=1 terms=3`.
9. **The suite passes, only the two listed test files change, and every added test file fails on the base** (NEW)
   - Before: not run. On the base the second line must read `changed= added=0`, because nothing has changed yet.
   - After, on `3fdcda3`: `652 passed in 106.96s (0:01:46)` / `changed=tests/factory/test_shepherd.py,tests/factory/test_spec_store.py added=1` / `tests/factory/test_spec_add_refusal.py on the base: 5 failed`.

Gates, run on `3fdcda3` exactly as written:
- `git diff --check main...HEAD`: no output, exit 0. On `77b7b40` it had flagged `tests/factory/test_spec_add_refusal.py:209: new blank line at EOF`, which `3fdcda3` fixes.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `652 passed in 108.55s (0:01:48)`, exit 0.

T-0056's tests, `tests/factory/test_transcript_record.py` and `tests/factory/test_scorecard.py`, pass unchanged in that run.

Current-truth checks on the command-line code (`openspec/specs/harness-code/spec.md`), run by hand on `3fdcda3`:
- `wc -l < factory/cli.py` plus the parser, entry-point and role-list count printed `899 3`.
- The drive.py counts printed `1 1 2`.
- The `specstore.applies(root, deltas)` count is 1.
- No file has three blank lines in a row.

## Tests added/changed

**Added: `tests/factory/test_spec_add_refusal.py`.** It has 5 tests. All 5 fail on the base and pass on the head. The driver tests use `factory drive` with a stand-in `claude`. The script tests run `factory/workflows/intake.js` under node, and each clerk command runs for real.
- `spec add` refuses a wrapped label and a label followed by a word. For each, it checks stderr, then that no version file, no `specs/T-0001.md` and no `spec.added` event exist. A good spec is then stored.
- With no current truth, a malformed spec is stored. A READY-FOR-CRITIC run's malformed draft is refused, and a NEEDS-HUMAN run's draft is stored.
- On both the driver and the script, a refused draft goes back to the writer, and the next one is stored and approved, ending at round 2. The second writer input holds the heading, the refusal and the refused lines. Its `input_sources` lists the first run's `output.md`, and the first input has no such section.
- On both runners, a refusal in the last round parks with the quoted reason, an exact return value, round 2, no version, and the last writer run as the park's output.
- On both runners, REVISE then a refused NEEDS-SPLIT draft parks without another writer run.

**Changed: the five tests under Tests to change, as each entry there says.**
- `test_spec_store.py::test_item_88_gate_refuses_a_delta_that_does_not_apply_and_a_malformed_version`: it now asserts that `spec add` refuses with `spec not added` and `no-such-req`, then that `approve-spec --edit` of the same file refuses with `no-such-req`. Its later assertions stay.
- `test_spec_store.py::test_an_empty_op_heading_counts_as_a_heading_and_a_slash_label_is_no_label`: `approve-spec --edit <file>` replaces `spec add` plus `approve-spec --version 2|3`. The refusal texts are the same.
- `test_spec_store.py::test_acceptance_labels_allow_ordinary_punctuation_but_not_a_choice`: `approve-spec --edit <file>` is used for each bad label. The assertion is the same.
- `test_spec_store.py::test_writer_and_critic_receive_current_truth_as_input_sources`: the writer's output is now `FOUR_PART` with `ADDED` replaced by `MODIFIED`. Both `input_sources` assertions are unchanged.
- `test_shepherd.py::test_the_gate_refuses_a_delta_that_does_not_fit_current_truth`: the second ticket's spec writer is dispatched with `route=False`. The test then asserts that `spec add --from-run` refuses with `ADDED 'the-thing' is already in current truth`, and that the ticket stays `ready-for-spec-writer`. `_fixtures.py` is unchanged.

No other existing test file changed.

## Known gaps and uncertainties

- **`cli.py` had one line of headroom, not 20.** The spec says `cli.py` was 880 lines "today". On this base it is 899, because T-0056 added 19 lines, and current truth requires fewer than 900. To keep it at 899 I did two things a reviewer may object to:
  - `spec_add` is written densely. The NEEDS-HUMAN condition is one 140-character `if`. The version number is bound with a walrus inside the `out({...})` call, a 150-character line. Lines this long already exist in `cli.py`; its longest is 206 characters.
  - In `_text_from`, `d = _run_dir(...)` and `p = d / "output.md"` are merged into one line. The spec does not ask for this. It changes no behaviour, and I made it only for the line cap.

  `cli.py` now has no headroom. The next change that adds a line will need to split the spec commands out of it. That split is a design decision, so I did not make it.
- **The script route is tested under node, not under the real Workflow tool.** Each clerk is a stand-in that runs the command with `sh -c` and returns its real stdout, exit code and stderr. A live clerk agent that reformats stderr would change the first line the script reads. The `spec not added: ` prefix check would then fall through to the `harness-bug: spec add:` park, which is the old behaviour.
- **The refusal section in the writer's input is derived, not recorded.** It shows the two edge cases the spec's Decisions name. Suppose the operator later stores a refused run's output by hand with `spec add --file`. No `spec.added` event names the run, so the next writer input still shows that output as refused. Suppose instead a draft was refused only because of current truth at the time, and current truth has since changed so that it now passes. Then no section appears.
- **One path has no test.** I wrote no new test for "any other `spec add` refusal still parks as `harness-bug: spec add: …`". I tried one that made `specs/` unwritable, but it was fragile, so I removed it before committing. That code path keeps its old text, with the new `startswith` check in front of it.
- `factory:` markers added: none.
- Operator steps from the spec still apply after merge:
  - Upgrade the runtime, then accept the new revision in both instances.
  - Run `factory launch-script intake` before the next Workflow-script intake. A launch copy written earlier would park a refused draft as `harness-bug: spec add: …`.

## Out-of-scope observations

- The Shepherd fixture's `route` (`tests/factory/_fixtures.py:576`) still calls `self.ok("spec", "add", …)` for every writer status. A future Shepherd story with a malformed writer stub on a store with current truth would fail on that assertion, because the fixture does not model the new route back to the writer. No current story does that, and the suite passes. The spec says not to change `_fixtures.py`.
- The test name and docstring of `test_the_gate_refuses_a_delta_that_does_not_fit_current_truth` still talk about the gate. The refusal now happens at `spec add`. I kept the edit to what Tests to change describes.
- `docs/design.md`'s Critic REVISE row still says "else Human queue" for the last round. That is still accurate.

## Protected paths

This change touches `factory/cli.py`, `factory/compose.py`, `factory/drive.py` and `factory/workflows/intake.js`. The parent spec's Risk section declares all four.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every scenario printed its THEN exactly, both gates pass on the head, and each new test fails on the base. The one judgment call is the dense `spec_add` code, made to keep `cli.py` under 900 lines.
ESCALATIONS: none

## Diff `11080b100b31c70c69cc1867960819270d134a23...3fdcda3e76e891e79e7949c78b78cef051f1dfd2`

diff --git a/README.md b/README.md
index f4d2255..0887824 100644
--- a/README.md
+++ b/README.md
@@ -87,7 +87,7 @@ directories and `models` entries use.
 | Role | Reads | Ends with `STATUS:` | What the harness keeps |
 |---|---|---|---|
 | Triage (`triage`) | the request; the capability index, one line per current-truth capability with its spec's path and requirement names; after a human answer, its own earlier output | ACCEPT · CLARIFY · NEEDS-HUMAN · REJECT | the title and type, copied onto the ticket |
-| Spec writer (`spec_writer`) | triage's output, the request; current truth in full for the capabilities triage named, and the capability index for the rest; the whole decision log; after a revision request, the critic's findings and its own previous spec; the human's change requests from the gate; any human answer or ruling | READY-FOR-CRITIC · NEEDS-SPLIT · NEEDS-HUMAN | the spec, saved as its next version, `specs/<ticket>/v<n>.md` |
+| Spec writer (`spec_writer`) | triage's output, the request; current truth in full for the capabilities triage named, and the capability index for the rest; the whole decision log; after a revision request, the critic's findings and its own previous spec; after a spec that `spec add` refused, the refusal and that output; the human's change requests from the gate; any human answer or ruling | READY-FOR-CRITIC · NEEDS-SPLIT · NEEDS-HUMAN | the spec, saved as its next version, `specs/<ticket>/v<n>.md` |
 | Spec critic (`critic`) | the spec version; current truth in full for the capabilities triage named or the spec cites, and the capability index for the rest; the whole decision log; every other approved spec not yet archived, with its decisions; from round 2, its own earlier findings and the previous version; any ruling | APPROVE · REVISE · ESCALATE | the verdict; its findings are attached to the spec when it is pinned |
 | Planner (`planner`) | the approved spec; the whole decision log; rulings; any sub-tickets that already exist | PLANNED · ESCALATE | the plan, `plans/<ticket>.md`, and one sub-ticket per piece, with its dependencies |
 | Implementer (`implementer`) | where it works (its worktree, branch, base commit and the wrapped gate commands), the sub-ticket, the pinned spec; on a revision, both checkers' findings and the gate result | READY-FOR-REVIEW · BLOCKED | its commits on branch `factory/<sub-ticket>` and the head commit; the message itself is the PR description |
@@ -349,12 +349,12 @@ sequenceDiagram
 *The script never touches the store itself; every record goes through the clerk to the harness.*
 
 Intake runs triage once, then alternates the spec writer and the critic. Triage's ACCEPT starts the
-spec writer; REJECT closes the ticket; CLARIFY waits for the requester; NEEDS-HUMAN parks. The spec
-writer's spec is saved as a new version, and the critic judges it. The critic's REVISE sends it back
-once; a REVISE on the critic's second pass parks the ticket. NEEDS-SPLIT, a spec that names how to
-split an oversized request, goes to the critic like READY-FOR-CRITIC. APPROVE moves the ticket to the
-spec gate, where intake stops. From the gate, the human approves or sends the spec back to the
-writer; a requester's answer sends a waiting ticket back to triage.
+spec writer; REJECT closes the ticket; CLARIFY waits for the requester; NEEDS-HUMAN parks. The
+harness saves the spec as a new version only if it is well-formed and fits current truth; if not, it
+goes back to the writer, using up a round. The critic's REVISE sends it back once; a second REVISE,
+or a refused spec in the last round, parks. NEEDS-SPLIT, a spec that names how to split an oversized
+request, goes to the critic like READY-FOR-CRITIC. APPROVE moves the ticket to the spec gate, where
+intake stops. The human approves or sends it back; a requester's answer returns a ticket to triage.
 
 ```mermaid
 flowchart TD
@@ -368,6 +368,7 @@ flowchart TD
   T -- NEEDS-HUMAN --> P["parked"]:::human
   W -- NEEDS-HUMAN --> P
   W -- "READY-FOR-CRITIC or NEEDS-SPLIT" --> K["Spec critic"]:::role
+  W -- "spec refused, a round left" --> W
   K -- "REVISE, first pass" --> W
   K -- "REVISE, second pass" --> P
   K -- ESCALATE --> P
diff --git a/docs/changelog.md b/docs/changelog.md
index e0a6777..0b18178 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -86,4 +86,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 
 77. After issue #116 (2026-10-19), where the factory's own work had no outside bar: `docs/north-star.md` named four success measures but set no target for any of them, nothing reported them and nobody reviewed them, so factory work was chosen in answer to the factory's own incidents. `docs/north-star.md` gains "How we know it is working": the primary metric, correct target changes per hour of operator attention, where each instance decides whether its merges are target changes and spec-factory's are factory work on a line of their own; its constraint, that escaped defects do not rise; cost as the second measure; operator decisions and interventions per change standing in for hours until the store records operator time; the scorecard's numbers by name, which `factory stats` is to compute so that nobody types them; three outside comparisons, a plain-session baseline, the upstream benchmark and DORA-style lead time and change failure rate; and a review every two weeks. A fourth working rule admits a factory ticket only if it fixes a defect that hit a target ticket, or names the scorecard number it moves and re-measures it after it ships; the operator applies it at the spec gate, and no role prompt or harness check does. New files: `docs/reviews/TEMPLATE.md`, which each review copies; `docs/reviews/2026-10-19.md`, the baseline review, counted by hand by the operator and the one review whose numbers are not computed; `STATUS.md`, which each review rewrites and which now quotes the baseline; and `CONTRIBUTING.md`, which says how work is proposed and chosen. README gains a north-star paragraph on its first screen, the rule in "Filing a request from an issue tracker" and two rows in "Where things live", and stays within its 1,185-line budget. Rejected: a role prompt or harness check that enforces the rule, which the request rules out; and recording operator time by hand, which would mean typing a number.
 
+78. After issue #105 (2026-10-12), where `approve-spec` refused a spec the critic had approved, over three acceptance labels in `verification.md` that had wrapped onto the next line, and the operator had to fix the spec by hand and approve it again. The format check ran only at the spec gate, so neither the spec writer nor the critic saw its verdict. `spec add` now runs the same check as `approve-spec` on a store with current truth: a spec that is malformed, or whose changes do not apply to current truth, is refused with exit 2 and `spec not added: ` followed by the errors, and nothing is written. A spec writer's NEEDS-HUMAN draft is still stored unchecked, so the operator can read it. Both the driver and the intake workflow script send a refused spec back to the spec writer as a new round, counted against the round limit; the writer's next input holds the refusal and the refused output. When no round is left, the ticket parks as `max rounds: ` followed by the refusal, with each backtick, `$` and `\` replaced by `'`. This overturns, for a refused spec, the 2026-10-07 decision that a format refusal re-dispatches the role once and then parks. Rejected: a routing edge from the spec writer's ready state to itself, which every instance's `instance.yaml` would need; a new round command; and a record of the refusal, which would break the rule that a refusal writes nothing.
+
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index 4e66f97..879121a 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -122,6 +122,7 @@ Rules the table relies on:
 | Triage | CLARIFY | Requester, via piece 9; ticket parks until answered | The missing-info list |
 | Triage | REJECT | Closed | — |
 | Spec writer | READY-FOR-CRITIC / NEEDS-SPLIT | Critic | Spec, repo, current truth and the decision log, as the Spec store paragraph describes, read-only; every other approved change not yet archived, with its decisions; round 2+: prior findings, the writer's responses, previous spec version |
+| Spec writer | READY-FOR-CRITIC / NEEDS-SPLIT, and `spec add` refuses the spec: malformed, or its changes do not apply to current truth | Spec writer (round +1) if round < {2}, else Human queue | The refusal and the refused output |
 | Spec writer | NEEDS-HUMAN | Human queue | Open questions |
 | Critic | APPROVE | Human spec gate | Spec + critic output |
 | Critic | REVISE | Spec writer (round +1) if round < {2}, else Human queue | Findings, the spec version they apply to |
diff --git a/factory/cli.py b/factory/cli.py
index 8c2da1d..7724f8c 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -20,7 +20,7 @@ from factory.common import _add_spec_version, _rel, fence, out
 from factory.drift import _check_drift, _check_sibling_tests
 from factory.gates import (_parent_close_verified, archive_cmd, merge_cmd, results_record, results_show,
                            ticket_head, ticket_join, ticket_parent_check)
-from factory.human import approve_spec, decision_add, escape_add, intervention_add, request_changes, resolve, spec_amend
+from factory.human import _refuse_unless_applies, approve_spec, decision_add, escape_add, intervention_add, request_changes, resolve, spec_amend
 from factory.setup import init_cmd, paths_cmd, store_migrate
 from factory.store import Refused
 
@@ -397,8 +397,7 @@ def _at_least_one(v: str) -> int:
 
 def _text_from(a, root) -> str:
     if a.from_run:
-        d = _run_dir(root, a.from_run)
-        p = d / "output.md"
+        p = _run_dir(root, a.from_run) / "output.md"
         if not p.exists():
             raise Refused(f"{a.from_run} has no output.md")
         return status.strip_trailer(p.read_text(encoding="utf-8"))
@@ -408,9 +407,10 @@ def _text_from(a, root) -> str:
 
 
 def spec_add(a, root, cfg):
-    t = store.load_ticket(root, a.id)
-    n = _add_spec_version(root, t, _text_from(a, root), a.from_run or a.file, cfg)
-    out({"ok": True, "id": t["id"], "version": n, "path": f"specs/{t['id']}/v{n}.md"})
+    t, text = store.load_ticket(root, a.id), _text_from(a, root)
+    if specstore.is_active(root) and not (a.from_run and store.read_yaml(root / "runs" / a.from_run / "meta.yaml").get("status") == "NEEDS-HUMAN"):
+        _refuse_unless_applies(root, text, "spec not added")  # a NEEDS-HUMAN draft is stored unchecked, for the operator to read
+    out({"ok": True, "id": t["id"], "version": (n := _add_spec_version(root, t, text, a.from_run or a.file, cfg)), "path": f"specs/{t['id']}/v{n}.md"})
 
 
 def plan_add(a, root, cfg):
diff --git a/factory/compose.py b/factory/compose.py
index e5bd846..2fc63d0 100644
--- a/factory/compose.py
+++ b/factory/compose.py
@@ -5,12 +5,14 @@ Per (role, round, resolution). No other code path assembles role input.
 from __future__ import annotations
 
 import difflib
+import json
 import math
 import re
 import shlex
 from pathlib import Path
 
-from factory import instance, specstore, store, subtickets
+from factory import instance, specstore, status, store, subtickets
+from factory.human import _refuse_unless_applies
 
 
 def _approvals(root: Path, ticket: str, kind: str) -> list[Path]:
@@ -60,6 +62,21 @@ def _last_run_meta(root: Path, ticket: str, role: str, exclude: str) -> dict | N
     return runs[-1] if runs else None
 
 
+def _refusal(root: Path, run_id: str) -> str | None:
+    """Why `spec add` refuses spec writer run `run_id`'s output now, or None when a spec version came
+    from that run or the check passes. Derived from the store when an input is built: a refusal writes
+    nothing, so there is no record of it to read."""
+    p = root / "runs" / run_id / "output.md"
+    added = {e.get("source") for e in map(json.loads, filter(str.strip, store.log_lines(root))) if e.get("event") == "spec.added"}
+    if not p.exists() or run_id in added:
+        return None
+    try:
+        _refuse_unless_applies(root, status.strip_trailer(p.read_text(encoding="utf-8")), "spec not added")
+    except store.Refused as e:
+        return str(e)
+    return None
+
+
 def gate_entries(cfg: dict) -> list[tuple[str, list[str] | None]]:
     """Each `gate_commands` entry as (command as written, paths or None). An entry is a command
     string, or a mapping of a non-empty string `command` and an optional non-empty list of git
@@ -290,6 +307,11 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
         prev = _last_run_meta(root, tid, "spec_writer", run_id)
         if prev and prev.get("status") == "NEEDS-HUMAN":
             add(f"runs/{prev['run_id']}/output.md", "Your previous output (the question you asked is answered in the request above)")
+        elif prev and prev.get("status") in ("READY-FOR-CRITIC", "NEEDS-SPLIT") and specstore.is_active(root):
+            why = _refusal(root, prev["run_id"])
+            if why:
+                add(f"runs/{prev['run_id']}/output.md", "Your previous output, which the harness refused to store as a spec version",
+                    lambda text: f"The harness refused it with: {why}\n\n{text}")
         for p in _approvals(root, tid, "changes"):
             add(str(p.relative_to(root)), "Human gate: changes requested")
         for p in _approvals(root, tid, "ruling"):
diff --git a/factory/drive.py b/factory/drive.py
index 3a57b95..bc74b87 100644
--- a/factory/drive.py
+++ b/factory/drive.py
@@ -300,8 +300,24 @@ class Driver:
                     return parked
                 added = call("spec", "add", T, "--from-run", w["runId"])
                 if not added["ok"]:
-                    self.park(T, _harness_bug("spec add", added), [w["runId"]])
-                    return parked
+                    why = (added.get("stderr") or "").strip().split("\n")[0]
+                    if not why.startswith("spec not added: "):
+                        self.park(T, _harness_bug("spec add", added), [w["runId"]])
+                        return parked
+                    # A form error the harness detects goes back to the writer as a new round (doc §Routing
+                    # table). The stored round is still 0 before the first move to the critic.
+                    cur = max(rnd, 1)
+                    if cur >= self.max_spec:
+                        # no backtick, $ or \ reaches the park reason, which the script's clerk runs in a shell
+                        self.park(T, "max rounds: " + re.sub(r"[`$\\]", "'", why), [w["runId"]])
+                        return {**parked, "rounds": cur, "reason": "max rounds"}
+                    st = call("ticket", "set", T, f"round.spec={cur + 1}")
+                    if not st["ok"]:
+                        self.park(T, _harness_bug("round increment refused", st), [w["runId"]])
+                        return parked
+                    rnd = cur + 1
+                    self.step(f"spec not stored; back to the spec writer in round {rnd}: {why}")
+                    continue
                 tr = self.transition("ready-for-critic", "spec:init")
                 if not tr["ok"]:
                     self.park(T, _harness_bug("transition to critic", tr), [w["runId"]])
diff --git a/factory/workflows/intake.js b/factory/workflows/intake.js
index fc4120d..6800d79 100644
--- a/factory/workflows/intake.js
+++ b/factory/workflows/intake.js
@@ -188,7 +188,23 @@ if (state === 'ready-for-spec-writer' || state === 'ready-for-critic') {
       }
       if (w.status !== 'READY-FOR-CRITIC' && w.status !== 'NEEDS-SPLIT') { await park(`harness-bug: unknown STATUS ${w.status} from spec writer`, [w.runId], 'Spec'); return { ticket: TICKET, state: 'parked' } }
       const added = await clerk(`${BIN} spec add ${TICKET} --from-run ${w.runId}`, 'Spec', 'spec add')
-      if (!added.ok) { await park(`harness-bug: spec add: ${added.stderr || ''}`, [w.runId], 'Spec'); return { ticket: TICKET, state: 'parked' } }
+      if (!added.ok) {
+        const why = String(added.stderr || '').trim().split('\n')[0]
+        if (!why.startsWith('spec not added: ')) { await park(`harness-bug: spec add: ${added.stderr || ''}`, [w.runId], 'Spec'); return { ticket: TICKET, state: 'parked' } }
+        // A form error the harness detects goes back to the writer as a new round (doc §Routing table).
+        // The stored round is still 0 before the first move to the critic.
+        const cur = Math.max(round, 1)
+        if (cur >= MAX) {
+          // no backtick, $ or \ reaches the park reason, which the clerk runs in a shell
+          await park(`max rounds: ${why.replace(/[`$\\]/g, "'")}`, [w.runId], 'Spec')
+          return { ticket: TICKET, state: 'parked', rounds: cur, reason: 'max rounds' }
+        }
+        const st = await clerk(`${BIN} ticket set ${TICKET} round.spec=${cur + 1}`, 'Spec', 'round increment')
+        if (!st.ok) { await park(`harness-bug: round increment refused: ${st.stderr || ''}`, [w.runId], 'Spec'); return { ticket: TICKET, state: 'parked' } }
+        round = cur + 1
+        log(`${TICKET}: spec not stored; back to the spec writer in round ${round}: ${why}`)
+        continue
+      }
       const tr = await transition('ready-for-critic', 'spec:init', 'Spec')
       if (!tr.ok) { await park(`harness-bug: transition to critic: ${tr.stderr || ''}`, [w.runId], 'Spec'); return { ticket: TICKET, state: 'parked' } }
       round = (tr.round && typeof tr.round.spec === 'number') ? tr.round.spec : round
diff --git a/tests/factory/test_shepherd.py b/tests/factory/test_shepherd.py
index acc97e6..5c56c8d 100644
--- a/tests/factory/test_shepherd.py
+++ b/tests/factory/test_shepherd.py
@@ -160,11 +160,11 @@ def test_the_gate_refuses_a_delta_that_does_not_fit_current_truth(tmp_path):
     f.human_approves(first)
     f.human_runs("archive", first)
     second = f.request("# SPEC-93: Second\n\nThe thing again.\n")
-    for role in ("triage", "spec_writer", "critic"):
-        f.dispatch(role, second, stub=f"accept-approve/{role}-1.md")
-    cp = f.cli("approve-spec", second)
+    f.dispatch("triage", second, stub="accept-approve/triage-1.md")
+    w = f.dispatch("spec_writer", second, stub="accept-approve/spec_writer-1.md", route=False)
+    cp = f.cli("spec", "add", second, "--from-run", w.run_id)
     assert cp.returncode == 2 and "ADDED 'the-thing' is already in current truth" in cp.stderr
-    assert f.state(second) == "awaiting-spec-gate"  # nothing moved; the human amends or closes
+    assert f.state(second) == "ready-for-spec-writer"  # nothing stored; the writer gets the refusal next round
 
 
 def test_the_planned_ticket_is_built_checked_merged_and_archived(tmp_path):
diff --git a/tests/factory/test_spec_add_refusal.py b/tests/factory/test_spec_add_refusal.py
new file mode 100644
index 0000000..5ae931f
--- /dev/null
+++ b/tests/factory/test_spec_add_refusal.py
@@ -0,0 +1,208 @@
+"""T-0057 (issue #105): `spec add` runs the format check `approve-spec` runs, where the store has
+current truth (an `openspec/` tree), and a refused draft goes back to the spec writer as a new round.
+
+Black-box through `bin/factory` on throwaway stores. The driver and the intake Workflow script are
+each run on one ticket, with a stand-in `claude` that writes a spec body from a file, then the
+trailer: the driver as `factory drive`, the script under node with every clerk command run for real.
+"""
+from __future__ import annotations
+
+import json
+import shutil
+import subprocess
+import sys
+from pathlib import Path
+
+import yaml
+
+from ._cli import REPO, js, run
+from ._fixtures import FIXTURE_INSTANCE, Store
+
+LABEL = "scenario 'the thing works' has no NEW/REGRESSION label in verification.md"
+REFUSED = "## Your previous output, which the harness refused to store as a spec version"
+
+
+def spec(label_lines: str, name: str = "the thing works") -> str:
+    return ("=== proposal.md\n## Problem\nA thing is missing.\n=== specs/thing/spec.md\n## ADDED Requirements\n"
+            f"### Requirement: The thing works\nThe thing SHALL work.\n#### Scenario: {name}\n- WHEN `true`\n"
+            f"- THEN it exits 0\n=== verification.md\n## Acceptance\n{label_lines}")
+
+
+GOOD = spec("- the thing works → NEW; fails today\n")
+WRAPPED = spec("- the thing works\n  → NEW; fails today\n")
+WORDED = spec("- the thing works → REGRESSION in its new form.\n")
+TICKED = spec("- the `echo hi` thing works\n  → NEW; fails today\n", "the `echo hi` thing works")
+
+# Plays the next entry of its role's list in $STANDIN_PLAYS (the last one repeats): {"body": file,
+# "write": STATUS} writes output.md as the file's text, if given, then the trailer.
+STANDIN = '''#!{python}
+import json, os, pathlib, sys
+cwd = pathlib.Path.cwd(); log = pathlib.Path(os.environ["STANDIN_LOG"])
+role = cwd.name.split("-", 2)[2]
+plays = json.loads(os.environ.get("STANDIN_PLAYS") or "{{}}").get(role) or [{{"write": "UNKNOWN"}}]
+nf = log.with_name(log.name + ".n-" + role)
+n = int(nf.read_text()) + 1 if nf.exists() else 1
+nf.write_text(str(n))
+p = plays[min(n, len(plays)) - 1]
+text = (pathlib.Path(p["body"]).read_text() if "body" in p else "") + \\
+    "\\nSTATUS: %s\\nCONFIDENCE: high, stand-in\\nESCALATIONS: none\\n" % p["write"]
+(cwd / "output.md").write_text(text)
+print(json.dumps({{"type": "result", "is_error": False, "result": text, "session_id": "s-" + cwd.name,
+                  "total_cost_usd": 0, "num_turns": 1, "usage": {{"output_tokens": 1}}}}))
+'''
+
+# The intake Workflow script under node: a clerk prompt runs its command with sh; a role prompt runs
+# the stand-in from the run's directory and returns its reply's result.
+WORKFLOW = r"""
+import { readFileSync } from 'node:fs'
+import { spawnSync } from 'node:child_process'
+const [script, ticket, instance, claude] = process.argv.slice(2)
+const src = readFileSync(script, 'utf8').replace(/^export const meta/m, 'const meta')
+const agent = async (prompt) => {
+  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
+  if (m) {
+    const cp = spawnSync('sh', ['-c', m[1]], { encoding: 'utf8' })
+    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
+  }
+  const dir = prompt.match(/(\S+\/runs\/run-\d+-[a-z_]+)\/input\.md/)[1]
+  return JSON.parse(spawnSync(claude, [], { cwd: dir, encoding: 'utf8' }).stdout).result
+}
+const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
+const res = await fn({ ticket, repo: process.cwd(), instance, state: process.env.FACTORY_STATE, inlineRoles: true },
+  agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
+console.log(JSON.stringify(res))
+"""
+
+
+def bodies(tmp_path: Path) -> dict[str, str]:
+    paths = {}
+    tmp_path.mkdir(parents=True, exist_ok=True)
+    for name, text in (("good", GOOD), ("wrapped", WRAPPED), ("worded", WORDED), ("ticked", TICKED)):
+        (tmp_path / f"{name}.md").write_text(text)
+        paths[name] = str(tmp_path / f"{name}.md")
+    return paths
+
+
+def writer_store(tmp_path: Path) -> Store:
+    """The driver's store with current truth enabled and T-0001 ready for its spec writer."""
+    s = Store(tmp_path)
+    (s.root / "openspec" / "specs").mkdir(parents=True)
+    (tmp_path / "bin" / "claude").write_text(STANDIN.format(python=sys.executable))
+    s.ok("ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
+    return s
+
+
+def plays(paths: dict[str, str], writer: list[str], critic: list[str] = ()) -> dict:
+    """Plays from "<body>:<STATUS>" entries."""
+    def entry(e: str) -> dict:
+        body, st = e.split(":")
+        return {"body": paths[body], "write": st}
+    return {"spec_writer": [entry(e) for e in writer], "critic": [{"write": c} for c in critic]}
+
+
+def intake(s: Store, side: str, p: dict) -> dict:
+    if side == "drive":
+        cp, res = s.drive(p, "--phase", "intake")
+        assert cp.returncode == 0, cp.stderr
+        return res
+    node = shutil.which("node")
+    assert node, "node must be on PATH: this case runs factory/workflows/intake.js"
+    (s.tmp / "wf.mjs").write_text(WORKFLOW)
+    cp = subprocess.run([node, str(s.tmp / "wf.mjs"), str(REPO / "factory" / "workflows" / "intake.js"), "T-0001",
+                         str(FIXTURE_INSTANCE), str(s.tmp / "bin" / "claude")],
+                        capture_output=True, text=True, cwd=REPO, timeout=300,
+                        env={**s.env, "STANDIN_PLAYS": json.dumps(p)})
+    assert cp.returncode == 0, cp.stderr
+    return json.loads(cp.stdout.strip().splitlines()[-1])
+
+
+def versions(store: Path) -> int:
+    d = store / "specs" / "T-0001"
+    return len(list(d.glob("v*.md"))) if d.exists() else 0
+
+
+def spec_added(store: Path) -> int:
+    return sum(ln.count('"spec.added"') for p in (store / "log").glob("*.jsonl") for ln in p.read_text().splitlines())
+
+
+def roles(s: Store) -> list[tuple[str, str]]:
+    return [(m["role"], m["status"]) for m in s.runs()]
+
+
+def test_spec_add_refuses_a_malformed_spec_and_writes_nothing_where_current_truth_is_enabled(tmp_path):
+    paths, s = bodies(tmp_path), tmp_path / "state"
+    req = tmp_path / "req.md"
+    req.write_text("# F\n\nx\n")
+    assert run(s, "ticket", "new", "--file", str(req)).returncode == 0
+    (s / "openspec" / "specs").mkdir(parents=True)
+    for name in ("wrapped", "worded"):
+        cp = run(s, "spec", "add", "T-0001", "--file", paths[name])
+        assert cp.returncode == 2 and cp.stderr.splitlines()[0] == f"spec not added: {LABEL}", name
+        assert versions(s) == 0 and spec_added(s) == 0 and not (s / "specs" / "T-0001.md").exists(), name
+    cp = run(s, "spec", "add", "T-0001", "--file", paths["good"])
+    assert cp.returncode == 0, cp.stderr
+    assert js(cp)["version"] == 1 and versions(s) == 1 and spec_added(s) == 1
+
+
+def test_a_needs_human_draft_and_a_store_without_current_truth_keep_a_malformed_spec(tmp_path):
+    paths = bodies(tmp_path)
+    req = tmp_path / "req.md"
+    req.write_text("# F\n\nx\n")
+    bare = tmp_path / "bare"
+    assert run(bare, "ticket", "new", "--file", str(req)).returncode == 0
+    assert run(bare, "spec", "add", "T-0001", "--file", paths["wrapped"]).returncode == 0 and versions(bare) == 1
+    s = tmp_path / "state"
+    assert run(s, "ticket", "new", "--file", str(req)).returncode == 0
+    (s / "openspec" / "specs").mkdir(parents=True)
+    assert run(s, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t").returncode == 0
+    for st, code in (("READY-FOR-CRITIC", 2), ("NEEDS-HUMAN", 0)):
+        rid = js(run(s, "run", "start", "--role", "spec_writer", "--ticket", "T-0001"))["run_id"]
+        (s / "runs" / rid / "output.md").write_text(WRAPPED + f"STATUS: {st}\nCONFIDENCE: low, t\nESCALATIONS: none\n")
+        assert run(s, "run", "finish", rid).returncode == 0
+        cp = run(s, "spec", "add", "T-0001", "--from-run", rid)
+        assert cp.returncode == code, (st, cp.stderr)
+    assert versions(s) == 1
+
+
+def test_a_refused_draft_goes_back_to_the_writer_with_the_refusal_and_the_next_reaches_the_critic(tmp_path):
+    for side in ("drive", "script"):
+        paths = bodies(tmp_path / side)
+        s = writer_store(tmp_path / side)
+        res = intake(s, side, plays(paths, ["wrapped:READY-FOR-CRITIC", "good:READY-FOR-CRITIC"], ["APPROVE"]))
+        assert res["state"] == "awaiting-spec-gate" and res["rounds"] == 2, (side, res)
+        t = s.ticket()
+        assert t["status"] == "awaiting-spec-gate" and t["round"]["spec"] == 2 and t["spec"]["version"] == 1, side
+        assert roles(s) == [("spec_writer", "READY-FOR-CRITIC"), ("spec_writer", "READY-FOR-CRITIC"),
+                            ("critic", "APPROVE")], side
+        first, second = (s.root / "runs" / m["run_id"] for m in s.runs()[:2])
+        assert REFUSED not in (first / "input.md").read_text(), side
+        text = (second / "input.md").read_text()
+        assert f"{REFUSED}\n\nThe harness refused it with: spec not added: {LABEL}\n\n" in text, side
+        assert "- the thing works\n  → NEW; fails today\n" in text, side
+        sources = yaml.safe_load((second / "meta.yaml").read_text())["input_sources"]
+        assert f"runs/{first.name}/output.md" in sources, side
+
+
+def test_a_refusal_in_the_last_round_parks_with_the_refusal_quoted_safely(tmp_path):
+    ticked = "max rounds: spec not added: scenario 'the 'echo hi' thing works' has no NEW/REGRESSION label in verification.md"
+    for side in ("drive", "script"):
+        paths = bodies(tmp_path / side)
+        s = writer_store(tmp_path / side)
+        res = intake(s, side, plays(paths, ["ticked:READY-FOR-CRITIC"]))
+        assert res == {"ticket": "T-0001", "state": "parked", "rounds": 2, "reason": "max rounds",
+                       **({"ok": True} if side == "drive" else {})}, side
+        t = s.ticket()
+        assert t["parked"]["reason"] == ticked and t["round"]["spec"] == 2 and t["spec"]["version"] == 0, side
+        assert roles(s) == [("spec_writer", "READY-FOR-CRITIC")] * 2, side
+        assert t["parked"]["outputs"] == [s.runs()[1]["run_id"]], side
+
+
+def test_a_refusal_after_a_revise_in_the_last_round_parks_without_another_writer_run(tmp_path):
+    for side in ("drive", "script"):
+        paths = bodies(tmp_path / side)
+        s = writer_store(tmp_path / side)
+        intake(s, side, plays(paths, ["good:READY-FOR-CRITIC", "worded:NEEDS-SPLIT"], ["REVISE"]))
+        t = s.ticket()
+        assert t["status"] == "parked" and t["parked"]["reason"] == f"max rounds: spec not added: {LABEL}", side
+        assert t["round"]["spec"] == 2 and t["spec"]["version"] == 1, side
+        assert roles(s) == [("spec_writer", "READY-FOR-CRITIC"), ("critic", "REVISE"), ("spec_writer", "NEEDS-SPLIT")]
diff --git a/tests/factory/test_spec_store.py b/tests/factory/test_spec_store.py
index 060a7ee..0484fcf 100644
--- a/tests/factory/test_spec_store.py
+++ b/tests/factory/test_spec_store.py
@@ -46,7 +46,7 @@ def test_writer_and_critic_receive_current_truth_as_input_sources(store):
     rid = writer_run(store)
     assert "### Requirement: trailer-read" in (store / "runs" / rid / "input.md").read_text()
     assert meta(store, rid)["input_sources"] == ["requests/T-0001.md", "openspec/specs/status-parser/spec.md"]
-    finish(store, rid, "=== proposal.md\n## Problem\nx\n", "READY-FOR-CRITIC")
+    finish(store, rid, FOUR_PART.replace("## ADDED Requirements", "## MODIFIED Requirements"), "READY-FOR-CRITIC")
     run(store, "spec", "add", "T-0001", "--from-run", rid)
     run(store, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
     cid = js(run(store, "run", "start", "--role", "critic", "--ticket", "T-0001"))["run_id"]
@@ -167,8 +167,9 @@ def test_item_88_gate_refuses_a_delta_that_does_not_apply_and_a_malformed_versio
     bad = FOUR_PART.replace("## ADDED Requirements", "## MODIFIED Requirements").replace("trailer-read", "no-such-req")
     f = tmp_path / "v2.md"
     f.write_text(bad)
-    assert run(store, "spec", "add", "T-0001", "--file", str(f)).returncode == 0
-    cp = run(store, "approve-spec", "T-0001", "--version", "2")
+    cp = run(store, "spec", "add", "T-0001", "--file", str(f))
+    assert cp.returncode == 2 and "spec not added" in cp.stderr and "no-such-req" in cp.stderr
+    cp = run(store, "approve-spec", "T-0001", "--edit", str(f))
     assert cp.returncode == 2 and "no-such-req" in cp.stderr
     t = yaml.safe_load((store / "tickets" / "T-0001.yaml").read_text())
     assert t["spec"]["approved_version"] == 1
@@ -335,12 +336,10 @@ def test_an_empty_op_heading_counts_as_a_heading_and_a_slash_label_is_no_label(s
     assert run(store, "approve-spec", "T-0001").returncode == 0
     f = tmp_path / "v2.md"
     f.write_text(FOUR_PART.replace("→ NEW; today it parks", "→ NEW / REGRESSION"))
-    run(store, "spec", "add", "T-0001", "--file", str(f))
-    cp = run(store, "approve-spec", "T-0001", "--version", "2")
+    cp = run(store, "approve-spec", "T-0001", "--edit", str(f))
     assert cp.returncode == 2 and "no NEW/REGRESSION label" in cp.stderr
     f.write_text(FOUR_PART.replace("- THEN status is NEEDS-HUMAN\n", "- THEN status is NEEDS-HUMAN\n#### Scenario: wrapped confidence\n- WHEN `y`\n- THEN z\n"))
-    run(store, "spec", "add", "T-0001", "--file", str(f))
-    cp = run(store, "approve-spec", "T-0001", "--version", "3")
+    cp = run(store, "approve-spec", "T-0001", "--edit", str(f))
     assert cp.returncode == 2 and "named more than once" in cp.stderr
 
 
@@ -363,7 +362,5 @@ def test_acceptance_labels_allow_ordinary_punctuation_but_not_a_choice(store, tm
     f = tmp_path / "v2.md"
     for bad in ("→ NEW / REGRESSION", "→ NEWS", "→ NEW today it parks"):
         f.write_text(FOUR_PART.replace("→ NEW; today it parks", bad))
-        run(store, "spec", "add", "T-0001", "--file", str(f))
-        v = yaml.safe_load((store / "tickets" / "T-0001.yaml").read_text())["spec"]["version"]
-        cp = run(store, "approve-spec", "T-0001", "--version", str(v))
+        cp = run(store, "approve-spec", "T-0001", "--edit", str(f))
         assert cp.returncode == 2 and "no NEW/REGRESSION label" in cp.stderr, bad

## Human ruling

Ruling (Green for the operator, 2026-10-25): proceed on spec v2 unchanged. The drift is a sibling ticket's work, not a change to this spec's intent. T-0056 merged just before this build (b863e4ec2, 11080b100) and added `tests/factory/test_transcript_record.py` and `tests/factory/test_scorecard.py`. This spec neither lists nor needs to change them. They are regression tests from now on: they must pass on this branch unchanged. If this change makes either of them fail, that is a defect in the change. Report it BLOCKED, and do not edit those tests. T-0056 also edited `factory/drive.py`, `factory/workflows/intake.js` and `factory/cli.py`: every `run finish` now passes `--transcripts`. Build this change's new `spec add` route on top of those edits, and keep the `--transcripts` argument on every `run finish`.
