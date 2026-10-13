## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`, the working documents for building the factory itself: `dev/build-harness.spec.md` (the
  spec for building the harness), `dev/build-harness.plan.md` (the Planner's decomposition of it),
  `dev/P0-intake-skeleton.md` (the walking skeleton) and `dev/issues.md` (this repo's issue index);
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
own conventions: its changelog entry in `docs/changelog.md`, `dev/build-harness.spec.md`
consistent with the new text, and any `docs/prompts/` file whose block changed re-copied from it.

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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0499-implementer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0499-implementer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0050.1` (branch `factory/T-0050.1`, base `2fbc170453cc3c549c487a6dd2c326b2b636e626`, head `2fbc170453cc3c549c487a6dd2c326b2b636e626`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0050.1

T-0050.1 / `run start` takes each role's model from the instance and refuses a `--model` that differs, so a Workflow run cannot start on a model the instance never named
Depends on: none
Parallel-safe: yes

Parent: T-0050, approved spec v1. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- A run start given a model the instance does not name is refused and writes nothing, and one without --model records the instance's model
- A run start given the instance's own model is accepted and records it
- An intake run told the wrong triage model parks before triage starts, and one told the right model runs triage on it
- A build told the wrong verifier model parks the sub-ticket before any verifier starts, and the reviewer still runs on its own model
- The harness suite passes with only the two fixtures that passed a wrong model changed
- The build spec and the README describe the model check
Tests to change: the parent's list.
Protected paths: the parent's Risk list.

## Parent spec (v1, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0050/v1.md`

=== proposal.md
## Problem
A role can run on a model the operator never chose, and the factory's records show that model as if it had been chosen. This affects every run started by the Workflow scripts. In this repository it has already happened to 10 of 92 verifier runs.

Some background. Each agent role in the factory (triage, spec writer, critic, planner, implementer, code reviewer, verifier) runs on a model that the operator picks per role in the repository's instance file, `.factory/instance.yaml`. The factory can be run two ways. The first is the driver, `factory drive`, a Python process. The second is a pair of Workflow scripts, `factory/workflows/intake.js` and `build.js`, which run inside Claude Code's Workflow tool. That tool cannot run a shell command itself. So the scripts hand every store command to the clerk, a small Haiku agent that runs the command and reports what it printed. (The store is the factory's record of tickets and runs.)

The scripts learn each role's model by asking the clerk to run `factory config` and report its JSON. The clerk is a language model, and it sometimes retypes that JSON instead of copying it. On 2026-10-12 it reported the verifier's model as `fable` when the instance file says `opus`. Each role run then starts with `factory run start`, the command that opens the run's record, and the scripts pass it the relayed model as `--model`. `run start` uses any `--model` it is given in place of the instance's model, without a check. It records that model, and the script launches the role agent on it. Nothing ever compares the model with the instance file.

After this change the harness, not the clerk, decides each role's model. `run start` records the model the instance file names for the role. It refuses a `--model` that names a different one, with an error that names both. The Workflow scripts already pass `--model` and launch the agent on the same value. So a misrelayed model now stops the ticket at that role's run start, before any agent starts. The ticket is parked: stopped with a reason, for a human to look at. The driver already reads the model in Python and passes the instance's own value, so it is unaffected.

## Root cause
`factory/cli.py` `run_start` (line 220) takes the caller's `--model` over the instance's `models[role]`, and nothing compares the two. The Workflow scripts get `models` through the clerk, which can retype it (`build.js:218-219`, `intake.js:139-140`). A retyped value therefore reaches both the run record and the agent launch unchecked.

## Out of scope
- No change to `factory/workflows/build.js` or `intake.js`. They keep passing `--model` and launching on the same value (see Decisions).
- No change to `factory/drive.py`.
- No correction to past run records or to `factory stats`. The ten fable verifier runs stay as recorded, and their verdicts stand.
- Other values the clerk relays, which carry the same risk: `max_rounds`, `state_dir`, and the clerk's own model (`MODELS.clerk`). The request does not ask for these.
- The model table itself (`models:` in either instance file or the template).
- Making `--model` required, or removing it.

## Open questions
none

## Decisions
- The instance file is the only source of a role's model. `run start` records `models[role]` from the instance, and `--model` serves only as a cross-check. This is a standing decision: a later caller, including whatever replaces the Workflow scripts, gets its model from `run start` and never chooses one.
- A `--model` that differs from the instance's model is refused with exit 2, before a run id is reserved, so nothing is written. The error reads exactly `model <given> refused for <role>: the instance names <instance model>`. It contains no backtick, `$` or double quote, because the build script passes a park reason through a shell command. Leaving out `--model` is still accepted.
- The requester's part B is cut: the scripts do not switch to launching on the model `run start` returns. That value also reaches the script through the clerk's report, so launching on it would trust a second relay. Today the scripts launch on the same value they sent as `--model`. With part A, `run start` accepts that value only when it is the instance's model. Rejected: launching on the returned model, which adds a relay. Rejected: comparing the returned model with the sent one, which guards a failure the evidence does not show (the clerk changing the command it runs).
- When the clerk misrelays a model, the Workflow run parks the ticket at that role's run start, with reason `harness-bug: run start <role>: <the refusal>`. The run does not go ahead on the instance's model. Rejected: having the scripts stop sending `--model`. `run start` would then pick the right model, but the agent would still be launched on the misrelayed one.
- The requester's part C (a test) is kept as a new suite test file for `run start`. The two Workflow routes are checked by acceptance scenarios that run the scripts under node, as the standing T-0023 decision does for workflow fixes.

## Risk
- Blast radius: every `factory run start` call, so every role run of either Workflow script and of the driver.
  - The driver always passes the instance's own model, so it is unaffected. The suite's driver parity tests passed on the prototype.
  - A Workflow run whose config report was retyped now parks at the first run start of the affected role, where today it runs that role on the wrong model. The operator restarts the ticket the way any run-start park is restarted today: `resolve --redispatch` for a checker, `resolve --ruling` for an implementer, `ticket transition` for an intake ticket. Then the operator re-launches the workflow.
- Residual, not covered: a clerk that changes the command it is given (for example, by dropping `--model`) would still let the agent launch on a misrelayed model while the record is correct. The evidence shows no such case.
- `factory/cli.py` must stay under 900 lines (a current-truth requirement of harness-code). It is 882 today, and the change adds about 3.
- Protected paths: `factory/cli.py`

## Operator steps
1. After merge and the runtime upgrade (`--accept-harness`), watch the next Workflow build. A park reading `harness-bug: run start <role>: model … refused for <role>` means the clerk misrelayed the config. Restart the ticket as described under Risk.

=== design.md
## Proposed change
A. `factory/cli.py` `run_start`
   1. Directly after the unknown-role check, and before the ticket is loaded, refuse when `a.model is not None` and it differs from `cfg["models"][a.role]`. Raise `Refused(f"model {a.model} refused for {a.role}: the instance names {cfg['models'][a.role]}")`. Exit 2, and write nothing: no run directory, no `in_flight` entry, no event.
   2. Replace `model = a.model or cfg["models"][a.role]` with `model = cfg["models"][a.role]`. `meta.yaml`, the `run.started` event and the printed JSON keep carrying `model`, as today.
   3. Optionally, give `--model` (line 702) a help string saying it must match the instance's model for the role. Keep `factory/cli.py` under 900 lines.

B. Tests
   1. Add a new file, `tests/factory/test_run_start_model.py`. Use a throwaway store with `FACTORY_INSTANCE` pointing at a copy of `factory/instance.template.yaml` in which the triage model is changed to a value no other role uses (for example `sonnet`). Cover four cases.
      - A differing `--model` is refused with exit 2 and the exact error text. No run directory, `run.started` event or `in_flight` entry is written.
      - `--model` equal to the instance's model is accepted and recorded.
      - No `--model` records the instance's model, in `meta.yaml`, in the event and in the printed JSON.
      - A reviewer, verifier or other non-triage role is checked against its own entry, not triage's.
   2. Make the two fixture edits listed under Tests to change.

C. Docs
   1. `dev/build-harness.spec.md:203`, the `run start` entry. Replace "(`model: M`, default `config.yaml` `models[R]`; …)" with text saying the model is the instance's `models[R]`. Add the new guard to its **Guards** list with its error, `model <M> refused for <R>: the instance names <model>`.
   2. `README.md`, the role-call paragraph under "The intake workflow, step by step" (line 254). After "refuses unless the ticket is in that role's ready state", add that `run start` takes the role's model from `instance.yaml` and refuses a `--model` that names another. Bump the status-header date per "Maintaining this page".
   3. No change to `docs/design.md`. It already says the harness owns "choosing the model per role" (line 56). So no changelog entry is needed and no `docs/prompts/` copy changes.

## Tests to change
- `tests/factory/test_coding_standard.py`, fixture `system_prompts` (line 50). It starts an implementer run and a reviewer run with `--model opus`, but the instance template names `reviewer: fable`. Under the Decision that a differing `--model` is refused, the reviewer start fails and both parametrised tests error. Drop the `"--model", "opus"` arguments from that call and change nothing else. The tests read the system prompt, not the model.
- `tests/factory/test_turn_economy.py`, fixture `run_prompts` (line 105). The same call, for triage, planner, implementer, reviewer and verifier. The reviewer start is refused, so all five parametrised tests error. Drop the `"--model", "opus"` arguments from that call and change nothing else.

=== specs/build-dispatch/spec.md
## ADDED Requirements

### Requirement: Run start takes each role's model from the instance and refuses a --model that names another
`factory run start` MUST record, in the run's `meta.yaml`, its `run.started` event and its printed JSON, the model that the instance's `models` names for the role. When given a `--model` that differs from that model, it SHALL refuse with exit 2 and the error `model <given> refused for <role>: the instance names <instance model>`, reserving no run, writing no event and adding nothing to the ticket's in-flight list.

#### Scenario: A run start given a model the instance does not name is refused and writes nothing, and one without --model records the instance's model
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell. The instance here names `sonnet` for triage, so the check cannot pass by matching a default.
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); mkdir $T/inst && sed 's/^  triage: opus$/  triage: sonnet/' factory/instance.template.yaml > $T/inst/instance.yaml && export FACTORY_INSTANCE=$T/inst FACTORY_STATE=$T/store && printf '# F\n\nDo x.\n' > $T/req.md && bin/factory ticket new --file $T/req.md >/dev/null; bin/factory run start --role triage --ticket T-0001 --model opus >$T/o 2>$T/e; echo "refused: exit=$? $(cat $T/e) runs=$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c .) started=$(cat $FACTORY_STATE/log/*.jsonl | grep -c '"run.started"')"; bin/factory run start --role triage --ticket T-0001 >$T/o2 2>/dev/null; echo "default: exit=$? returned=$(tail -1 $T/o2 | sed -n 's/.*"model": "\([a-z]*\)".*/\1/p') recorded=$(sed -n 's/^model: //p' $FACTORY_STATE/runs/run-0001-triage/meta.yaml 2>/dev/null) logged=$(cat $FACTORY_STATE/log/*.jsonl | grep '"run.started"' | sed -n 's/.*"model": "\([a-z]*\)".*/\1/p' | paste -sd, -)")`
- THEN it prints exactly `refused: exit=2 model opus refused for triage: the instance names sonnet runs=0 started=0`, then `default: exit=0 returned=sonnet recorded=sonnet logged=sonnet`

#### Scenario: A run start given the instance's own model is accepted and records it
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); mkdir $T/inst && sed 's/^  triage: opus$/  triage: sonnet/' factory/instance.template.yaml > $T/inst/instance.yaml && export FACTORY_INSTANCE=$T/inst FACTORY_STATE=$T/store && printf '# F\n\nDo x.\n' > $T/req.md && bin/factory ticket new --file $T/req.md >/dev/null; bin/factory run start --role triage --ticket T-0001 --model sonnet >$T/o 2>/dev/null; echo "exit=$? returned=$(tail -1 $T/o | sed -n 's/.*"model": "\([a-z]*\)".*/\1/p') recorded=$(sed -n 's/^model: //p' $FACTORY_STATE/runs/run-0001-triage/meta.yaml)")`
- THEN it prints exactly `exit=0 returned=sonnet recorded=sonnet`

### Requirement: A Workflow run whose relayed configuration names the wrong model parks at that role's run start
When the configuration that the clerk relays to `factory/workflows/intake.js` or `factory/workflows/build.js` names, for a role, a model other than the instance's, the script SHALL park the ticket at that role's run start with the reason `harness-bug: run start <role>: model <relayed> refused for <role>: the instance names <instance model>`. It MUST launch no agent of that role and record no run of it. A role whose relayed model is the instance's SHALL be launched on that model.

#### Scenario: An intake run told the wrong triage model parks before triage starts, and one told the right model runs triage on it
- GIVEN the fixture file written by the block below, run once at column 0 as shown (the later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0050-wf.mjs <<'EOF'
// node t0050-wf.mjs <workflow script> <ticket>, from the checkout under test: runs that Workflow-tool
// script on <ticket> of the store $FACTORY_STATE. Each clerk command runs for real (sh -c, from this
// checkout), except that when T50_SWAP is `<role>=<model>`, the stdout of `factory config` names
// <model> for <role>, as a clerk that retyped it would. Each role call prints
// `agent <role> <ticket> model=<the model it was launched on>`, writes an output with the STATUS that
// T50_PLAYS ({"<role>": "<STATUS>"}) gives its role (with the run's head as its Commit: line and, for
// the verifier, "Gate suite: PASS"), and returns the same text. Each park prints `park <id>: <reason>`.
import { readFileSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const [script, ticket] = process.argv.slice(2)
const plays = JSON.parse(process.env.T50_PLAYS || '{}')
const [swapRole, swapModel] = (process.env.T50_SWAP || '=').split('=')
const src = readFileSync(script, 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt, opts) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    let stdout = cp.stdout
    if (swapRole && /bin\/factory config$/.test(m[1])) {
      const c = JSON.parse(stdout.trim().split('\n').pop()); c.models[swapRole] = swapModel; stdout = JSON.stringify(c) + '\n'
    }
    return { stdout, exit: cp.status, stderr: cp.stderr }
  }
  console.log(`agent ${opts.label} model=${opts.model}`)
  const r = prompt.match(/(\S+\/runs\/run-\d+-([a-z_]+))\/input\.md/)
  const head = (readFileSync(`${r[1]}/meta.yaml`, 'utf8').match(/^head: '?([0-9a-f]{40})/m) || [])[1]
  const text = (head ? `Commit: ${head}\n` : '') + (r[2] === 'verifier' ? 'Gate suite: PASS\n' : '') +
    `STATUS: ${plays[r[2]] || 'NONE'}\nCONFIDENCE: high, stub\nESCALATIONS: none\n`
  writeFileSync(`${r[1]}/output.md`, text)
  return text
}
const log = (s) => { const q = String(s).match(/^(\S+) parked: (.*)$/s); if (q) console.log(`park ${q[1]}: ${q[2]}`) }
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket, repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
  integration: process.env.FACTORY_INTEGRATION_BRANCH || 'main', inlineRoles: true }, agent, log, () => {},
  async (fs) => Promise.all(fs.map(f => f())))
EOF
```

- WHEN `(for swap in '' triage=fable; do (T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/store T50_SWAP=$swap T50_PLAYS='{"triage": "REJECT"}'; printf '# Fixture\n\nThe bot should do the thing.\n' > $T/req.md && bin/factory ticket new --file $T/req.md >/dev/null; node ${TMPDIR:-/tmp}/t0050-wf.mjs factory/workflows/intake.js T-0001 | grep .; echo "swap=${swap:-none} $(bin/factory ticket show T-0001 | sed -n 's/^status: //p') runs=$(for d in $(ls $FACTORY_STATE/runs 2>/dev/null); do echo "${d#run-????-}=$(sed -n 's/^model: //p' $FACTORY_STATE/runs/$d/meta.yaml)"; done | sort | paste -sd' ' -)"); done)`
- THEN it prints exactly `agent triage T-0001 model=opus`, `swap=none closed runs=triage=opus`, `park T-0001: harness-bug: run start triage: model fable refused for triage: the instance names opus`, `swap=triage=fable parked runs=`, one per line

#### Scenario: A build told the wrong verifier model parks the sub-ticket before any verifier starts, and the reviewer still runs on its own model
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution), "A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows" (current truth, build-dispatch) and "An intake run told the wrong triage model parks before triage starts, and one told the right model runs triage on it" run once. T-0001.1 waits at its checks, so the build starts its reviewer and verifier together. This is the incident's route.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && export T50_SWAP=verifier=fable T50_PLAYS='{"reviewer": "APPROVE", "verifier": "VERIFIED"}'; node ${TMPDIR:-/tmp}/t0050-wf.mjs factory/workflows/build.js T-0001 | grep . | sort; echo "$(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') runs=$(for d in $(ls $FACTORY_STATE/runs 2>/dev/null); do echo "${d#run-????-}=$(sed -n 's/^model: //p' $FACTORY_STATE/runs/$d/meta.yaml)"; done | sort | paste -sd' ' -)")`
- THEN it prints exactly `agent reviewer T-0001.1 model=fable`, `park T-0001.1: harness-bug: run start verifier: model fable refused for verifier: the instance names opus`, `parked runs=reviewer=fable`, one per line

### Requirement: Existing callers of run start keep working
The driver and the harness suite MUST still start every role run they start today; the only existing test files this change edits SHALL be the two fixtures that passed a model the instance does not name.

#### Scenario: The harness suite passes with only the two fixtures that passed a wrong model changed
Per the standing T-0023 decision, the command gives pytest its own temporary directory under `/tmp` and removes it when it ends.
- WHEN `(P=$(mktemp -d /tmp/t0050-suite.XXXXXX) && TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P"; git diff --name-only --diff-filter=DMR main...HEAD -- tests)`
- THEN the first line reports a number of passed tests and no `failed` or `error`, and every later line, if any, is `tests/factory/test_coding_standard.py` or `tests/factory/test_turn_economy.py`

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The documents record that run start owns each role's model
`dev/build-harness.spec.md`'s `run start` entry MUST say the model comes from the instance's `models[R]` and SHALL list the refusal of a differing `--model` among its guards, with its error; `README.md`'s role-call paragraph under "The intake workflow, step by step" SHALL say that `run start` refuses a `--model` the instance does not name.

#### Scenario: The build spec and the README describe the model check
- WHEN `echo "old=$(grep -c 'default .config.yaml. .models\[R\]' dev/build-harness.spec.md) guard=$(grep -c 'refused for <R>: the instance names' dev/build-harness.spec.md) readme=$(sed -n '/^### The intake workflow, step by step/,/sequenceDiagram/p' README.md | grep -c -- '--model')"`
- THEN it prints `old=0 guard=1 readme=<n>` with n of 1 or more

=== verification.md
## Acceptance
- A run start given a model the instance does not name is refused and writes nothing, and one without --model records the instance's model → NEW. Today it prints `refused: exit=0  runs=1 started=1`, because the wrong model is accepted and a run is reserved. It then prints `default: exit=2 returned= recorded=opus logged=opus`: the second start is refused because the first is in flight, and the run is recorded on opus, not on the instance's sonnet.
- A run start given the instance's own model is accepted and records it → REGRESSION
- An intake run told the wrong triage model parks before triage starts, and one told the right model runs triage on it → NEW. The first two lines already pass today. The swapped half prints `agent triage T-0001 model=fable`, then `swap=triage=fable closed runs=triage=fable`: triage is launched on fable, recorded as fable, and the ticket closes.
- A build told the wrong verifier model parks the sub-ticket before any verifier starts, and the reviewer still runs on its own model → NEW. Today it prints `agent reviewer T-0001.1 model=fable`, `agent verifier T-0001 model=fable`, `agent verifier T-0001.1 model=fable`, `park T-0001: archive: no spec store (factory init not run)`, `merged runs=reviewer=fable verifier=fable verifier=fable`. Both the sub-ticket's verifier and the parent's final verifier run on fable and are recorded as fable, which is the incident.
- The harness suite passes with only the two fixtures that passed a wrong model changed → REGRESSION. Without the two fixture edits, the change makes 7 tests error, all with `model opus refused for reviewer: the instance names fable`. With part A applied in a scratch clone, the suite reported `569 passed, 7 errors`.
- The build spec and the README describe the model check → NEW. Today it prints `old=1 guard=0 readme=0`.

Also re-run these current-truth scenarios from build-dispatch. They cover the driver, which passes `--model` with the instance's value, and the scripts' unchanged routes. All must still pass:
- "The driver takes the build fixtures through the same routes as the build script"
- "Each role runs as one claude process with its prompt, model and tool limits"
- "The Workflow scripts still take both fixtures to the end of their routes"
