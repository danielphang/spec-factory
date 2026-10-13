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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0501-verifier/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0501-verifier/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0501-verifier/wt` (branch `factory/T-0050.1`, base `2fbc170453cc3c549c487a6dd2c326b2b636e626`, head `b3b978dce1d5544c7f346695292b8ef37f64eaae`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

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

## PR description (the implementer's output)

Sub-ticket: T-0050.1 (parent T-0050, approved spec v1, `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0050/v1.md`)
Branch: `factory/T-0050.1`, worktree `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0050.1`
Commit: b3b978dce1d5544c7f346695292b8ef37f64eaae (base 2fbc170453cc3c549c487a6dd2c326b2b636e626)

## What changed

Before this change, a role could start, and be recorded, on a model the instance file never named. The model now comes only from the instance file, and `run start` refuses a different one. `run start` is the store command that opens a role run's record. The Workflow scripts already passed it a `--model` value that reached them through the clerk, the Haiku agent that runs store commands for them and can retype what it reports. `run start` used that value unchecked. Now it records the instance's `models[role]`. It refuses a `--model` naming another model with exit 2, and writes nothing. When the clerk misreports a model, the Workflow script parks the ticket at that role's run start, before any agent of that role is launched. A parked ticket is one stopped for a human.

A. `factory/cli.py` `run_start`
1. Directly after the unknown-role check, before the ticket is loaded, it reads `model = cfg["models"][a.role]`. When `a.model is not None and a.model != model`, it raises `Refused(f"model {a.model} refused for {a.role}: the instance names {model}")`. The existing `except Refused` handler (cli.py:871-874) prints that to stderr and exits 2. The check comes before `store.next_run_id`, so no run directory, `in_flight` entry or `run.started` event is written.
2. The line `model = a.model or cfg["models"][a.role]` is removed. `meta.yaml`, the `run.started` event and the printed JSON still carry `model`, now always the instance's.
3. `--model` has the help text "must match the instance's model for the role". `factory/cli.py` grows from 882 to 884 lines, so it stays under the 900-line limit.

I grepped the callers of `run start` (coding standard rule 2):
- `factory/drive.py:186` passes `self.models[role]`. That value comes from the driver's own Python `call("config")` (drive.py:657), so it is always the instance's value.
- `factory/workflows/intake.js:88` and `factory/workflows/build.js:79` pass `MODELS[role]`, the value the clerk relays. They park on a failed start (intake.js:89, build.js:84) with `harness-bug: run start <role>: <stderr>`. The new refusal therefore reaches the park reason unchanged. Neither script was changed, as the spec requires.
- `factory/human.py:223` already treats a `harness-bug: run start implementer:` park as resolvable by `resolve --ruling`.
- Test callers: the two listed fixtures, plus `test_p0_cli.py:72`, `test_instance.py:236` and `test_writing_standard.py:41`. Those three pass `--model opus` for triage, which the fixture instance also names, so they still pass.

The fix sits in `run_start` because every caller reaches that one function.

B. Tests
1. New file `tests/factory/test_run_start_model.py`, with 7 tests. Each uses a throwaway store and `FACTORY_INSTANCE` pointing at a copy of `factory/instance.template.yaml` whose triage model is `sonnet`, a model no other role uses. The tests cover:
   - a differing `--model`: exit 2 with the exact error, and no run directory, `run.started` event or `in_flight` entry;
   - the instance's own model: accepted and recorded;
   - no `--model`: the instance's model is recorded in `meta.yaml`, in the event and in the printed JSON;
   - reviewer, verifier and critic, each checked against its own entry, by refusal;
   - critic accepted on its own model (`fable`).
2. The two fixture edits from Tests to change: `"--model", "opus"` was dropped from the `run start` call in each fixture, and nothing else changed.

C. Docs
1. `dev/build-harness.spec.md`, the `run start` entry (line 203). The model text now reads "(`model:` the instance's `models[R]`, which `--model M` only cross-checks; …)". The first item of **Guards** is now the refusal, with its error `model <M> refused for <R>: the instance names <model>`.
2. `README.md`, the role-call paragraph under "The intake workflow, step by step". It now says that `run start` takes the role's model from `instance.yaml` and records it, and refuses a `--model` that names another model, so a model the clerk misreported parks the ticket before the agent starts. The status-header date was already 2026-10-12, today, so there was nothing to bump.
3. `docs/design.md` is unchanged, as the spec says. So there is no changelog entry and no `docs/prompts/` copy.

## Acceptance results

All commands ran from the worktree through the fresh-HOME wrapper, with `TMPDIR` set to this run's scratch directory. The GIVEN fixture blocks were run once beforehand: t0023 from human-resolution, t0032 from build-dispatch, and t0050 from this change. "Before" ran on the base 2fbc170. "After" ran on b3b978d.

- A run start given a model the instance does not name is refused and writes nothing, and one without --model records the instance's model (NEW).
  - Before: `refused: exit=0  runs=1 started=1` / `default: exit=2 returned= recorded=opus logged=opus`. This matches the "today" output in verification.md: the wrong model was accepted and a run was reserved.
  - After: `refused: exit=2 model opus refused for triage: the instance names sonnet runs=0 started=0` / `default: exit=0 returned=sonnet recorded=sonnet logged=sonnet`. This is exactly the THEN.
- A run start given the instance's own model is accepted and records it (REGRESSION). After: `exit=0 returned=sonnet recorded=sonnet`. This is exactly the THEN. It printed the same on the base.
- An intake run told the wrong triage model parks before triage starts, and one told the right model runs triage on it (NEW).
  - Before: `agent triage T-0001 model=opus` / `swap=none closed runs=triage=opus` / `agent triage T-0001 model=fable` / `swap=triage=fable closed runs=triage=fable`. Triage was launched on fable, recorded as fable, and the ticket closed.
  - After: `agent triage T-0001 model=opus` / `swap=none closed runs=triage=opus` / `park T-0001: harness-bug: run start triage: model fable refused for triage: the instance names opus` / `swap=triage=fable parked runs=`. This is exactly the THEN: no triage agent was launched and no run was recorded.
- A build told the wrong verifier model parks the sub-ticket before any verifier starts, and the reviewer still runs on its own model (NEW).
  - Before: `agent reviewer T-0001.1 model=fable` / `agent verifier T-0001 model=fable` / `agent verifier T-0001.1 model=fable` / `park T-0001: archive: no spec store (factory init not run)` / `merged runs=reviewer=fable verifier=fable verifier=fable`. Both verifiers ran on fable. That is the incident, and it matches verification.md.
  - After: `agent reviewer T-0001.1 model=fable` / `park T-0001.1: harness-bug: run start verifier: model fable refused for verifier: the instance names opus` / `parked runs=reviewer=fable`. This is exactly the THEN.
- The harness suite passes with only the two fixtures that passed a wrong model changed (REGRESSION). After: `583 passed in 388.87s (0:06:28)`, then `tests/factory/test_coding_standard.py` and `tests/factory/test_turn_economy.py`. The THEN holds: no failures or errors, and only the two listed files are modified under `tests/`. The new file is an addition, so `--diff-filter=DMR` does not list it.
- The build spec and the README describe the model check (NEW). Before: `old=1 guard=0 readme=0`. After: `old=0 guard=1 readme=1`, which matches the THEN with n=1.

These current-truth build-dispatch scenarios were re-run after the change, as verification.md asks. The GIVEN block of "The driver takes the intake fixtures through the same routes as the intake script" was run first. All three printed exactly their THEN:
- "The driver takes the build fixtures through the same routes as the build script": `parked script=4/4 drive=4/4 same`, `planned script=6/6 drive=6/6 same`, `planned script=4/4 drive=4/4 same`, `planned script=1/1 drive=1/1 same`. The driver and the build script still take the same routes.
- "Each role runs as one claude process with its prompt, model and tool limits": `critic ok`, `spec_writer ok`, `triage ok`, `implementer ok`, `reviewer ok`, `verifier ok`, `verifier ok`. Every role process was still launched with the run's model.
- "The Workflow scripts still take both fixtures to the end of their routes": `T-0001.1 merged T-0001 parked`, then `T-0001 awaiting-spec-gate`.

Gate commands were run from the worktree exactly as written:
- `git diff --check main...HEAD` exited 0 with no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `583 passed in 378.91s (0:06:18)` and exited 0.

New tests before the fix: `4 failed, 3 passed`. The failures were the differing-model refusal and the three per-role refusals. Before the fix, those three were refused only by the ready-state guard, with the wrong error. The 3 that passed check behaviour the base already had: no `--model` records the default, and a matching model is accepted. After the fix, all 7 pass inside the suite run above. `ruff check factory/cli.py tests/factory/test_run_start_model.py` printed `All checks passed!`.

## Tests added/changed
- Added `tests/factory/test_run_start_model.py` (part B.1).
- Changed `tests/factory/test_coding_standard.py`, fixture `system_prompts`. It is listed under Tests to change. Its reviewer start passed `--model opus` against the template's `reviewer: fable`, so the start would now be refused and both parametrised tests would error.
- Changed `tests/factory/test_turn_economy.py`, fixture `run_prompts`. It is listed under Tests to change, for the same reason: the reviewer start would be refused.

## Known gaps and uncertainties
- The refusal is checked before the ticket is loaded, so a run start that is wrong in two ways reports the model error first. For example, a wrong `--model` on a ticket in the wrong state reports the model refusal, not the state refusal. The spec orders it this way (design A.1).
- `cfg["models"][a.role]` is now read on every start. Before, when `--model` was given, it was not read. An instance with no `models` entry for a role would now fail that role's start with an unhandled KeyError, reported through the generic exception handler, even when `--model` is given. Without `--model`, the base already failed this way. The template and both instance files name every role. The spec's design A.2 asks for exactly this line.
- The residual risk the spec names under Risk is not covered, by design. A clerk that drops `--model` from the command would let the agent launch on a misrelayed model while the record shows the right one.
- factory: markers added: none.

## Out-of-scope observations
- Three other passages in `dev/build-harness.spec.md` still describe the old relay:
  - line 125 (decision D6): "`run start --model` records it in `meta.yaml`";
  - line 276 (`runRole`): "exit 2 from a guard → park `harness-bug: <stderr>`", where the scripts' actual reason is `harness-bug: run start <role>: <stderr>`;
  - line 534 (a round-4 response).

  Line 125 is still true for an accepted start, and the spec scoped the doc edit to line 203. None is contradicted outright, so I left all three unchanged.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every NEW scenario printed its "today" text on the base and exactly its THEN after the change, and the suite, both gates and the three driver and script parity scenarios pass.
ESCALATIONS: none

## Diff `2fbc170453cc3c549c487a6dd2c326b2b636e626...b3b978dce1d5544c7f346695292b8ef37f64eaae`

diff --git a/README.md b/README.md
index 0a7752a..a3cb1b6 100644
--- a/README.md
+++ b/README.md
@@ -253,7 +253,9 @@ in (`parked.from`).
 
 Every role call, in either workflow, is the same three store commands around one agent. `run start`
 creates the run directory and its prompt, and refuses unless the ticket is in that role's ready
-state. `run compose` writes `input.md`. The role agent runs. `run finish` reads the `STATUS:` line
+state. It takes the role's model from `instance.yaml` and records it. It refuses a `--model` that
+names another model, so a model the clerk misreported parks the ticket before the agent starts.
+`run compose` writes `input.md`. The role agent runs. `run finish` reads the `STATUS:` line
 and records it. Each command goes through the clerk.
 
 ```mermaid
diff --git a/dev/build-harness.spec.md b/dev/build-harness.spec.md
index 45f634a..7e0bb54 100644
--- a/dev/build-harness.spec.md
+++ b/dev/build-harness.spec.md
@@ -200,7 +200,7 @@ CLI (the **store CLI** of doc §Harness table piece 1 — read, transition, reco
 - `factory intake [<dir>]` (default `knowledge_vault/specs`): `request new` for every `*.md` not yet imported (content hash in `requests/index.yaml`); prints `imported N, skipped M (already imported)` and the IDs. It does not run anything; the `/factory` skill then launches `intake.js` per ID.
 - `factory ticket new --type (retro|revert) --branch B [--reverts SHA] [--output FILE]` (harness or human): no-sub-ticket PR record (piece 5) with `head` from `git ls-remote`; `--reverts` required for `revert`, refused unless SHA is a `merged` ticket's `head`; `--type retro` also writes `retros/<date>.yaml` (proposals with their metrics, prior-proposal verdicts) from the retro run's output `FILE`. It then runs `factory gate-run ID --head <head>` (L) so the ticket has its ci row. Other types → exit 2 `use factory request new`.
 - `factory ticket show ID`; `factory ticket set ID key=value` (logged); `factory ticket transition ID --to STATE --by RUN [--round spec|pr:+1|reset|init]` (the clerk's one write for routing; `init` sets the counter to 1 if 0). **Guards (doc §Harness table piece 2: "put the round and routing guards in the CLI, not the clerk"):** exit 2, store unchanged, nothing logged, when `+1` would take the counter above `config.yaml` `max_rounds` (`round.spec 2 is at max_rounds 2`), or when `(current status, STATE)` is not an edge of the routing table stored in `config.yaml` `routing:` (the doc §Routing table rows plus the resolution rules; `no route ready-for-triage → merged`). `factory ticket park ID --reason R --outputs RUN,RUN [--question PATH]`.
-- `factory run start --role R --ticket ID|none --head SHA|none [--model M]` → prints `run_id`, writes `runs/<run_id>/{meta.yaml,system-prompt.txt}` and creates the empty `runs/<run_id>/scratch/` for the run's temporary files, which the store's `.gitignore` excludes (`model: M`, default `config.yaml` `models[R]`; `budget_usd` copied from the ticket), appends the id to `in_flight`. **Guards:** exit 2, nothing written, when the ticket is not in R's ready state (`T-0001 is ready-for-triage, not ready-for-critic`; ready states: triage `ready-for-triage`, spec_writer `ready-for-spec-writer`, critic `ready-for-critic`, planner `ready-for-planner`, implementer `ready-for-implementer`, reviewer/verifier `checks-in-flight` or `ready-for-checks`, verifier also `ready-for-parent-verify`; retro runs with `--ticket none`), or when the ticket's branch already has a run in `in_flight` (implementer, retro: any run; reviewer, verifier: a run of the same role) — `ticket/T-0001 already has run <id> in flight`; or, for an implementer run of a sub-ticket, when a `` `<file>` (added by <ID>) `` line in its "Tests to change" field names a file that existed at the parent's `parent_base` or whose first adding commit on the integration branch since then lies inside no merged sibling's recorded `merge` (doc §Harness, "Tests a sibling added") — `BLOCKED from harness: Tests to change lists <file> as added by a sibling, but no merged sibling of <parent> added it since <base>; …`. **Run id reservation:** after the guards pass and before anything else is written, `run start` reserves the run's directory by creating `runs/<run_id>/` create-exclusive (an mkdir that fails when the path already exists); on a collision it takes the next id and tries again. Two starts on one store at the same moment, whatever their tickets or roles, therefore never share a run directory, and the id is final before its `meta.yaml` is written. A refused start reserves nothing (item 70).
+- `factory run start --role R --ticket ID|none --head SHA|none [--model M]` → prints `run_id`, writes `runs/<run_id>/{meta.yaml,system-prompt.txt}` and creates the empty `runs/<run_id>/scratch/` for the run's temporary files, which the store's `.gitignore` excludes (`model:` the instance's `models[R]`, which `--model M` only cross-checks; `budget_usd` copied from the ticket), appends the id to `in_flight`. **Guards:** exit 2, nothing written, when `--model M` names a model other than the instance's `models[R]` (`model <M> refused for <R>: the instance names <model>`; checked before the ticket is read), or when the ticket is not in R's ready state (`T-0001 is ready-for-triage, not ready-for-critic`; ready states: triage `ready-for-triage`, spec_writer `ready-for-spec-writer`, critic `ready-for-critic`, planner `ready-for-planner`, implementer `ready-for-implementer`, reviewer/verifier `checks-in-flight` or `ready-for-checks`, verifier also `ready-for-parent-verify`; retro runs with `--ticket none`), or when the ticket's branch already has a run in `in_flight` (implementer, retro: any run; reviewer, verifier: a run of the same role) — `ticket/T-0001 already has run <id> in flight`; or, for an implementer run of a sub-ticket, when a `` `<file>` (added by <ID>) `` line in its "Tests to change" field names a file that existed at the parent's `parent_base` or whose first adding commit on the integration branch since then lies inside no merged sibling's recorded `merge` (doc §Harness, "Tests a sibling added") — `BLOCKED from harness: Tests to change lists <file> as added by a sibling, but no merged sibling of <parent> added it since <base>; …`. **Run id reservation:** after the guards pass and before anything else is written, `run start` reserves the run's directory by creating `runs/<run_id>/` create-exclusive (an mkdir that fails when the path already exists); on a collision it takes the next id and tries again. Two starts on one store at the same moment, whatever their tickets or roles, therefore never share a run directory, and the id is final before its `meta.yaml` is written. A refused start reserves nothing (item 70).
 - `factory run compose RUN` (**the one input mechanism**, critic S2) → writes `runs/<run_id>/input.md` from exactly the sources `factory/compose.py` declares for `(role, round, resolution)` — the "with input =" lists in H, read from the store and `~/factory/clone` — and records their paths as `input_sources:` and the pinned spec version it used as `spec_version:` in `meta.yaml` (a run keeps that version even if the spec is re-pinned while it is in flight, K). The file opens with the repo's role-context block (doc §Harness), ahead of those sources; it is not a store path, so it is not one of the `input_sources:` (its text is in `input.md`). The text `agent()` receives is only `Your entire input is ~/factory/state/runs/<run_id>/input.md; read it first.` No input text is composed anywhere else.
 - `factory run finish RUN --output-file F [--status-override KILLED]` → writes `output.md`, parses STATUS (H), removes the id from `in_flight`, prints `STATUS CONFIDENCE ESCALATIONS` as JSON, logs `escalation.queued` when the list is non-empty (H). A missing or blank `output.md` with no override is `EMPTY-OUTPUT` (error `empty output`, logged `run.finished`); `--status-override KILLED` still records `KILLED` and logs `run.killed`.
 - `factory run last-message RUN --text=T` → on a run whose `meta.yaml` status is `EMPTY-OUTPUT`, writes T plus one newline to `runs/<RUN>/last-message.md` and prints its path; on any other run, exit 2 and nothing written (I.5).
diff --git a/factory/cli.py b/factory/cli.py
index 728bfb4..3085c25 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -200,6 +200,9 @@ def _planner_run(root: Path, run: str, tid: str) -> Path:
 def run_start(a, root, cfg):
     if a.role not in ROLES:
         raise Refused(f"unknown role {a.role}; roles: {', '.join(ROLES)}")
+    model = cfg["models"][a.role]  # the instance is the only source of a role's model; --model only cross-checks it
+    if a.model is not None and a.model != model:
+        raise Refused(f"model {a.model} refused for {a.role}: the instance names {model}")
     t = store.load_ticket(root, a.ticket)
     parent_close = a.role == "verifier" and t["status"] == "ready-for-parent-verify"
     ready = cfg["ready_state"][a.role]
@@ -217,7 +220,6 @@ def run_start(a, root, cfg):
         compose.environment_sync(cfg)  # so does a malformed environment_sync
     baseline = tripwire.baseline(cfg)  # hashed before the run id is reserved: a refusal writes nothing
     rid = store.next_run_id(root, a.role)
-    model = a.model or cfg["models"][a.role]
     d = root / "runs" / rid
     meta = {"run_id": rid, "role": a.role, "ticket": t["id"], "model": model, "round": t["round"]["spec"],
             "spec_version": t["spec"]["version"], "started": store.now(), "finished": None,
@@ -699,7 +701,7 @@ def build_parser() -> argparse.ArgumentParser:
     p = rn.add_parser("start")
     p.add_argument("--role", required=True)
     p.add_argument("--ticket", required=True)
-    p.add_argument("--model")
+    p.add_argument("--model", help="must match the instance's model for the role")
     p.set_defaults(fn=run_start)
     p = rn.add_parser("compose")
     p.add_argument("run")
diff --git a/tests/factory/test_coding_standard.py b/tests/factory/test_coding_standard.py
index 2f5d693..a5a946a 100644
--- a/tests/factory/test_coding_standard.py
+++ b/tests/factory/test_coding_standard.py
@@ -47,7 +47,7 @@ def system_prompts(tmp_path_factory) -> dict[str, str]:
     for role, status in (("implementer", ["status=ready-for-implementer"]),
                          ("reviewer", ["status=checks-in-flight", "in_flight=[]", f"head={head}"])):
         cli(t, "ticket", "set", "T-0001", *status, **store)
-        cp = cli(t, "run", "start", "--role", role, "--ticket", "T-0001", "--model", "opus", **store)
+        cp = cli(t, "run", "start", "--role", role, "--ticket", "T-0001", **store)
         run_id = json.loads(cp.stdout.strip().splitlines()[-1])["run_id"]
         prompts[role] = (tmp / "s" / "runs" / run_id / "system-prompt.txt").read_text()
     return prompts
diff --git a/tests/factory/test_run_start_model.py b/tests/factory/test_run_start_model.py
new file mode 100644
index 0000000..5245154
--- /dev/null
+++ b/tests/factory/test_run_start_model.py
@@ -0,0 +1,90 @@
+"""`run start` takes each role's model from the instance and refuses a `--model` that names another.
+
+The instance here is a copy of the template with triage moved to `sonnet`, a model no other role
+uses, so a check that falls back to a default or to another role's entry cannot pass.
+"""
+from __future__ import annotations
+
+from pathlib import Path
+
+import pytest
+import yaml
+
+from ._cli import REPO, js, run_env, ticket
+
+
+@pytest.fixture
+def env(tmp_path: Path) -> dict:
+    inst = tmp_path / "inst"
+    inst.mkdir()
+    text = (REPO / "factory" / "instance.template.yaml").read_text()
+    assert "\n  triage: opus\n" in text
+    (inst / "instance.yaml").write_text(text.replace("\n  triage: opus\n", "\n  triage: sonnet\n"))
+    req = tmp_path / "req.md"
+    req.write_text("# F\n\nDo x.\n")
+    e = {"FACTORY_INSTANCE": str(inst), "FACTORY_STATE": str(tmp_path / "store")}
+    assert run_env(e, "ticket", "new", "--file", str(req)).returncode == 0
+    return e
+
+
+def _store(env: dict) -> Path:
+    return Path(env["FACTORY_STATE"])
+
+
+def _started_events(env: dict) -> list[str]:
+    return [ln for p in sorted((_store(env) / "log").glob("*.jsonl"))
+            for ln in p.read_text().splitlines() if '"run.started"' in ln]
+
+
+def _recorded(env: dict, cp) -> tuple[str, str, list[str]]:
+    rid = js(cp)["run_id"]
+    meta = yaml.safe_load((_store(env) / "runs" / rid / "meta.yaml").read_text())
+    return js(cp)["model"], meta["model"], _started_events(env)
+
+
+def test_a_differing_model_is_refused_and_writes_nothing(env):
+    cp = run_env(env, "run", "start", "--role", "triage", "--ticket", "T-0001", "--model", "opus")
+    assert cp.returncode == 2
+    assert cp.stderr.strip() == "model opus refused for triage: the instance names sonnet"
+    runs = _store(env) / "runs"
+    assert not runs.exists() or not any(runs.iterdir())
+    assert _started_events(env) == []
+    assert ticket(_store(env))["in_flight"] == []
+
+
+def test_the_instances_own_model_is_accepted_and_recorded(env):
+    cp = run_env(env, "run", "start", "--role", "triage", "--ticket", "T-0001", "--model", "sonnet")
+    assert cp.returncode == 0, cp.stderr
+    returned, recorded, events = _recorded(env, cp)
+    assert (returned, recorded) == ("sonnet", "sonnet")
+    assert len(events) == 1 and '"model": "sonnet"' in events[0]
+
+
+def test_no_model_records_the_instances_model(env):
+    cp = run_env(env, "run", "start", "--role", "triage", "--ticket", "T-0001")
+    assert cp.returncode == 0, cp.stderr
+    returned, recorded, events = _recorded(env, cp)
+    assert (returned, recorded) == ("sonnet", "sonnet")
+    assert len(events) == 1 and '"model": "sonnet"' in events[0]
+    assert ticket(_store(env))["in_flight"] == [js(cp)["run_id"]]
+
+
+@pytest.mark.parametrize("role, given, named", [
+    ("reviewer", "opus", "fable"),
+    ("verifier", "fable", "opus"),
+    ("critic", "sonnet", "fable"),
+])
+def test_each_role_is_checked_against_its_own_entry(env, role, given, named):
+    cp = run_env(env, "run", "start", "--role", role, "--ticket", "T-0001", "--model", given)
+    assert cp.returncode == 2
+    assert cp.stderr.strip() == f"model {given} refused for {role}: the instance names {named}"
+    assert _started_events(env) == []
+
+
+def test_a_non_triage_role_is_accepted_on_its_own_model(env):
+    for to in ("ready-for-spec-writer", "ready-for-critic"):
+        assert run_env(env, "ticket", "transition", "T-0001", "--to", to, "--by", "t").returncode == 0
+    cp = run_env(env, "run", "start", "--role", "critic", "--ticket", "T-0001", "--model", "fable")
+    assert cp.returncode == 0, cp.stderr
+    returned, recorded, _ = _recorded(env, cp)
+    assert (returned, recorded) == ("fable", "fable")
diff --git a/tests/factory/test_turn_economy.py b/tests/factory/test_turn_economy.py
index 54787df..3401619 100644
--- a/tests/factory/test_turn_economy.py
+++ b/tests/factory/test_turn_economy.py
@@ -102,7 +102,7 @@ def run_prompts(tmp_path_factory) -> dict[str, str]:
                          ("implementer", ["status=ready-for-implementer", "in_flight=[]"]),
                          ("reviewer", checks), ("verifier", checks)):
         _cli(t, "ticket", "set", "T-0001", *status, **store)
-        cp = _cli(t, "run", "start", "--role", role, "--ticket", "T-0001", "--model", "opus", **store)
+        cp = _cli(t, "run", "start", "--role", role, "--ticket", "T-0001", **store)
         run_id = json.loads(cp.stdout.strip().splitlines()[-1])["run_id"]
         prompts[role] = (tmp / "s" / "runs" / run_id / "system-prompt.txt").read_text()
     return prompts
