=== proposal.md
## Problem

The spec factory runs each ticket (a requested change) through AI agents, driven by two workflow scripts: the intake script (triage, then writing and critiquing a spec) and the build script (planning, building, checking and merging). A human signs off each spec at the spec gate before any code is written. Today both scripts can stop a ticket and leave no record of why. The operator then finds a ticket that has not moved and has to dig through store files to learn what happened. On the Nanobot port on 2026-10-04 this stalled six approved tickets at once.

Some terms used below. A role is one agent job, such as the planner or the verifier. A run is one call of a role; the store records each run and marks it "in flight" until it finishes. The planner splits an approved spec, the parent ticket, into sub-tickets that are built and merged one by one. To park a ticket is to stop it and put the reason in the human queue, the list a human works through.

Four defects, each seen on a real ticket:

1. **Intake plans without creating sub-tickets.** If the intake script is started on a ticket that has already passed the spec gate, it runs the planner and marks the parent "planned", but it never creates the sub-tickets. Only the build script has that step.
2. **The build then exits silently.** On a planned parent with no sub-tickets, the build script finds nothing to build. It asks the store whether the parent is finished, gets a refusal ("has no sub-tickets"), and returns after about 30 seconds. Nothing is parked and nothing is logged.
3. **A failed agent call leaves a run in flight forever.** If launching a role's agent fails with an error, for example because the agent type is not installed, the script stops. The run stays marked in flight and the ticket is not parked. Every later attempt on that ticket is refused because a run is still in flight.
4. **The verifier's test-suite result is misread when written as a heading.** The verifier reports the test-suite result on a line `Gate suite: PASS` or `Gate suite: FAIL`, and the harness records that line as the CI result. A verifier that wrote `## Gate suite: PASS` had its pass recorded as a failure. Each time this has cost a full revision round: another implementer run and another pair of checks.

The fix: intake stops at the spec gate and only the build script plans. A build that finds a planned parent with no sub-tickets creates them from the planner run already recorded for that parent, or parks the parent with the reason. A failed agent call records its run as killed and parks the ticket with the error. The harness reads the gate line in heading and bold forms, and the verifier's prompt states the exact form.

## Evidence

All reproductions below ran on `main` at `429d218` in this checkout. Each used a scratch store and a scratch target repository. The workflow scripts need Claude Code's Workflow runtime, so they were run under node with a small driver. The driver models that runtime's documented `agent()` and `parallel()` behaviour, runs every store command for real through `bin/factory`, and answers role calls from the repo's stub fixtures. It is given in full in the first scenario of `specs/workflow-dispatch/spec.md`.

- **Intake plans a gate-approved ticket without sub-tickets.** A ticket was taken through intake to the spec gate, approved with `bin/factory approve-spec T-0001`, then given to the intake script again. The driver printed `returned planned`, `ticket T-0001 planned` and `run run-0004-planner PLANNED`, and the store held only `T-0001.yaml`. So the planner ran and the parent is planned with no sub-tickets. The cause is `factory/workflows/intake.js` lines 172-189: the Plan phase runs `spec tasks` and `plan add`, then moves the ticket to `planned`, with no `subticket add`. `factory/workflows/build.js` line 190 is the only place that runs `subticket add`.
- **The build exits silently on that parent.** The build script on the same store printed `returned planned`. The last log line was still the `ready-for-planner → planned` transition, with no park and no `ticket.parked` event. So the build ended with no record of why. Cause: `build.js` lines 205-207 break out of the build loop when nothing is ready or remaining. Line 212 then calls `ticket parent-check`, which refuses with `T-0001 has no sub-tickets` (`factory/cli.py` line 594). Line 213 returns `{state: 'planned'}` without parking.
- **The Nanobot store shows the same thing at scale** (from triage, read only): six parents planned on 2026-10-04 with no sub-tickets (T-0001, T-0004, T-0007, T-0008, T-0011, T-0012). The Nanobot Driver session, which runs that port's builds, created them by hand with `subticket add <parent> --run <planner run>`, taking each run id from the parent's `plan.added` log event. `plan.added` is the event the store writes when a plan is recorded, and its `source` field names the planner run.
- **There is no way to create sub-tickets without naming the run.** `bin/factory subticket add T-0001` with neither `--run` nor `--file` printed `factory: TypeError: argument should be a str or an os.PathLike object ... not 'NoneType'` and exited 1. So the command crashes instead of using the plan the store already recorded.
- **A failed agent call orphans its run (intake).** The driver made the triage role's `agent()` call throw `agent type 'factory-triage' not found`. It printed `threw agent type 'factory-triage' not found`, `ticket T-0001 ready-for-triage in_flight=1` and `run run-0001-triage running`. So the script died, the run stayed in flight, and the ticket was not parked.
- **The same happens in the build.** With the implementer's call throwing, the driver printed `ticket T-0001.1 ready-for-implementer in_flight=1 reason=-` and `run run-0005-implementer running`. The build returned `planned` and logged "1 sub-ticket(s) parked or waiting on a human", which was false. This matches the issue #24 comment from 2026-10-04: "left the sub-ticket holding an orphan in-flight run and returned without parking", after "agent type 'factory-implementer' not found".
- **How `agent()` fails.** The Workflow reference says `agent()` returns null when the user skips it or after a terminal API error, and that a thunk which throws inside `parallel()` resolves to null. If the #24 call had returned null, `runRole` would have finished the run as KILLED (`build.js` lines 93-96). The run stayed `running`, so the call threw. `build.js` calls `buildOne` inside `parallel()` (line 210), so the throw was absorbed there and the build carried on. The reference does not say in so many words that an unknown agent type throws. That part is inferred from the #24 symptoms, which the reproduction above matches exactly.
- **Gate line read as a heading.** spec-factory `run-0073-verifier` (T-0012.5), `output.md` line 21, reads `## Gate suite: PASS`. The store logged `result.recorded ... role: ci, status: FAIL` for that run (log line 378), and `results/302f70bb…/ci.yaml` and `results/7090d9d2…/superseded-2/ci.yaml` both hold `detail: missing Gate suite line`. On a scratch store, `results record` gave ci `FAIL|missing Gate suite line` for each of `## Gate suite: PASS`, `**Gate suite:** PASS`, `### **Gate suite: PASS**` and `**Gate suite: FAIL** 2 failed`. Plain `Gate suite: PASS` gave `PASS|`. So any leading mark hides the verdict. The parser is `factory/cli.py` line 480, `re.search(r"^Gate suite:\s*(PASS|FAIL)\b(.*)$", text, re.M)`, which is anchored at the start of the line. The second occurrence was Nanobot v3.5 T-0012.1 (run-0052), as reported in the issue; I did not open that run.
- **The documents already expect this.** `README.md` lines 83-85 say intake's planning step "only runs when a ticket is already past the gate at launch; in practice the build script runs the planner". Line 276 says to start the build script after the gate, "never the intake script (#33)". `dev/build-harness.spec.md` lines 277-281 describe `intake.js` as triage and spec phases only. Removing the phase brings the code in line with the build spec.
- **Baseline gates.** `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `157 passed in 97.42s`. `git diff --check` printed nothing.

## Root cause

- `factory/workflows/intake.js` lines 172-189 (phase 3, Plan) is a second, incomplete planning path. It lacks `subticket add`, which `build.js` line 190 has.
- `factory/workflows/build.js` lines 197-215 have no case for a `planned` parent with no sub-tickets. They also drop a `parent-check` refusal on the floor at line 213: `if (!pc.ok || pc.state !== 'ready-for-parent-verify') return {...}`.
- `runRole` in both scripts (`intake.js` lines 74-104, `build.js` lines 64-101) handles a null or empty `agent()` result as KILLED, but nothing catches a thrown `agent()`. The run is never finished and the ticket is never parked. In `build.js` the throw is absorbed by `parallel()`, so the build goes on as if nothing happened.
- `factory/cli.py` `subticket_add` (lines 366-403) reads `Path(a.file)` when `--run` is absent, so a call with neither flag raises `TypeError`.
- `factory/cli.py` `results_record` line 480 anchors the gate-line regex at the start of the line, so heading (`#`) and emphasis (`*`) marks hide the verdict. The verifier prompt (`docs/design.md` line 644, `docs/prompts/07-verifier.md` line 37, `factory/prompts/verifier.md` line 38) says only `Gate suite: PASS/FAIL, with failing output` and does not forbid formatting.

## Out of scope

- The planner's output format (#13).
- A `resolve` verb that resumes a ticket parked by a failed agent call, or a parent parked for having no sub-tickets. A budget-killed implementer has the same gap today (README §"Where a human decides", "Gap, as of today").
- A clerk call whose own `agent()` throws. Parking needs the clerk, so there is nothing to park with.
- Which gate line counts when there are several. The parser keeps taking the first matching line, as today.
- The build's quiet `planned` return when every remaining sub-ticket is parked. Each of those sub-tickets is already in the queue with its own reason.
- Agent definitions for the build roles (#24 part A).
- Keeping the node driver as a permanent test. It is used here only as an inline acceptance fixture.
- `dev/issues.md` and #21's dead-code list. The operator maintains these.
- Describing the new park reasons in README's present-tense sections before they have run on a real ticket (README "Maintaining this page").

## Open questions

none

## Decisions

- Intake ends at the spec gate. The build script is the only path that runs the planner, so there is one planning path.
- `factory subticket add PARENT` with neither `--run` nor `--file` uses the planner run named by the parent's latest `plan.added` event. Rejected: picking the newest PLANNED planner run of the parent, because it could pick a run whose plan was never recorded.
- The build detects a parent with no sub-tickets from a new `subtickets` list in `ticket ready-implementers` output. Rejected: routing on the text of `parent-check`'s refusal, because refusal text is for humans and changes freely.
- When an `agent()` call throws, its run is recorded KILLED and the ticket parks with `agent call failed: <role>: <error>`. That reason is distinct from `budget kill`, so the operator can tell a missing agent from a budget overrun. A null or empty return keeps today's route.
- A `parent-check` refusal in the build parks the parent with the refusal text. It is not a silent return.
- The gate-line parser accepts leading whitespace, `#` and `*` before `Gate suite:`, and `*` and whitespace between the colon and the verdict. Emphasis marks are stripped from the detail. The verifier prompt pins the plain form. The two are kept together: the parser tolerates drift, and the prompt states the contract.

## Risk

Blast radius: every intake and build run on both instances after the runtime moves to this change. All changes can be undone by moving the runtime back. Behaviour changes, in brief:
- Intake on a `ready-for-planner` ticket now does nothing.
- A build on a planned parent with no sub-tickets now creates them or parks the parent.
- A thrown agent call now parks instead of orphaning its run.
- More verifier outputs now yield a ci row of PASS. The verdict is unchanged: PASS and FAIL are read from the same word, so no check is loosened. Only lines that start with `#`, `*` or whitespace before `Gate suite:` are newly read.

Protected paths touched, all declared:
- harness `factory/**`: `factory/workflows/intake.js`, `factory/workflows/build.js`, `factory/cli.py`, `factory/prompts/verifier.md`. The last is also a guardrail path, an agent prompt, and the ticket asks for this change to it.
- generated `docs/prompts/**`: `docs/prompts/07-verifier.md`, re-copied verbatim from the design doc's verifier block.

No `.factory/**`, `agents/**`, `bin/factory`, `pyproject.toml`, `uv.lock`, `~/dev/nanobot-upstream/**` or `~/.nanobot/**` path is touched. Existing tests are unchanged. New tests go in a new file.

The spec gate is pre-approved under `.factory/answers/queue-preapproval-policy.md`, which names #33. The same policy says a prompt change still gets the operator's acceptance test before the runtime moves. See Operator steps.

## Operator steps

1. Before the runtime moves to this change, run the acceptance test that the pre-approval policy requires for a prompt change. Take the next real verifier run on the new prompt and check two things: its output carries a plain `Gate suite: PASS` or `Gate suite: FAIL` line, and the ci row recorded for that head matches it (`bin/factory results show <sub-ticket>`).
2. After moving the runtime, accept the new harness revision on each instance with `--accept-harness <revision>`. Tell the Nanobot Driver session that intake no longer plans, and that a parent planned by an older runtime gets its sub-tickets from the build script.

=== design.md
## Proposed change

Size estimate: about 170 changed lines, including new tests.

**A. Intake ends at the spec gate** (`factory/workflows/intake.js`)
- Delete phase 3, Plan (lines 172-189).
- Remove the `Plan` entry from `meta.phases` (line 7). End `meta.description` at the human gate: drop "-> Planner".
- Drop `planner` from `AGENT_NAME` (line 35).
- A ticket in `ready-for-planner`, or in any state intake does not dispatch, falls through to the existing final `return { ticket, state, note: 'nothing to dispatch from this state' }` (line 191). No planner run starts.

**B. The build creates missing sub-tickets from the recorded plan**
- B1 (`factory/cli.py` `subticket_add` and its parser entry). With neither `--run` nor `--file`, take the run from the `source` of the parent's latest `plan.added` log event. Then proceed exactly as `--run <that run>` does today: the PLANNED-planner-run check, parsing, the `ticket.created` events, and the sub-ticket `source: plan:<run>`. Refuse with exit 2 and the store unchanged in two cases: when the parent has no `plan.added` event, or when its latest one names something that is not a run directory of this store (a plan added with `--file`). The refusal text names the parent and says no recorded planner run was found.
- B2 (`factory/cli.py` `ticket_ready_implementers`). Add `"subtickets"` to the output: every sub-ticket id of the parent, in id order. Existing keys are unchanged.
- B3 (`factory/workflows/build.js`, phase 2, before the loop's first `parallel`). If the first `ready-implementers` answer has an empty `subtickets` list, run clerk `subticket add PARENT` with no `--run`, at most once per build run. When that is refused, park the parent with a reason containing `no sub-tickets`, for example `no sub-tickets, and none could be created from the recorded plan: <stderr>`, and return `{ticket, state: 'parked'}`. When it succeeds, log how many sub-tickets were created and continue the loop.

**C. No silent exits**
- C1 (`build.js` lines 212-213). When `parent-check` is refused (`!pc.ok`), park the parent with `parent-check refused: <stderr>` and return `{ticket, state: 'parked'}`. When it succeeds with a state other than `ready-for-parent-verify`, return as today.
- C2 (`runRole` in both `intake.js` and `build.js`). Wrap the role's `agent()` call, in both the stub branch and the real branch, in `try`/`catch`. On a throw:
  - clerk `run finish RUN --status-override KILLED`;
  - in `build.js`, for a reviewer or verifier, clerk `run cleanup RUN` as today;
  - park the ticket with `agent call failed: <role>: <error message>` and the run id as outputs;
  - return `null`. Every caller already returns on `null`.

  A null or empty result keeps today's KILLED path. Pass the reason through the existing `park()`, which already replaces double quotes.

**D. Gate line**
- D1 (`factory/cli.py` `results_record`, line 480). Match the first line of the form `^[ \t#*]*Gate suite:[ \t*]*(PASS|FAIL)\b(.*)$` (`re.M`). The detail is group 2 with spaces and `*` stripped from both ends, or `None` when that leaves it empty. A line where `Gate suite:` follows anything other than spaces, tabs, `#` or `*` still does not match, so prose that mentions the gate suite is not read as a verdict. The no-match case is unchanged: `FAIL`, `missing Gate suite line`.
- D2 (the verifier prompt). In the `## 7. Verifier` block of `docs/design.md` (line 644), replace the line `Gate suite: PASS/FAIL, with failing output` with these two lines:
  ```
  Gate suite: PASS/FAIL, with failing output on the lines below it
    (a plain line starting "Gate suite:", never a heading or bold)
  ```
  Re-copy the block verbatim into `docs/prompts/07-verifier.md`. Make the same two-line replacement at `factory/prompts/verifier.md` line 38, whose step 4 differs from the design block on purpose and stays as it is.
- D3 (`docs/changelog.md`). Add entry `47. After issue #33 (2026-10-04), ...` after entry 46 and before "Declined:". It says three things: intake ends at the spec gate and the build owns planning; a failed agent call or a `parent-check` refusal parks with the reason; and the verifier writes `Gate suite:` as a plain line, which the harness also reads in heading or bold form.

**E. Documents that describe the changed behaviour**
- `README.md` lines 83-85: replace "The intake script also contains a planning step, … the build script runs the planner." with one sentence saying the intake script stops at the spec gate.
- `README.md` line 276: replace "never the intake script (#33)" with a reason that holds after this change, for example "the intake script stops at the gate". Bump the status-header date as "Maintaining this page" requires.
- `dev/build-harness.spec.md`:
  - line 275 (`runRole`): add that a thrown `agent()` is finished KILLED and parks `agent call failed: <role>: <error>`;
  - line 285 (build.js step 2): add the missing-sub-ticket repair (B3) and the `parent-check` refusal park (C1);
  - line 320 (L): say the `Gate suite:` line may carry leading heading or emphasis marks, and use the phrase "heading or emphasis marks".

**F. New tests** in a new file, `tests/factory/test_build_startup.py`, driven through `bin/factory` on a scratch store:
- `subticket add` with no source, in both the success case and the refusal case;
- the new `subtickets` key in `ready-implementers`;
- the gate-line forms in D1.

The workflow-script behaviour (A, B3, C) is covered by the acceptance driver only.

## Tests to change

none. No existing test asserts on intake's Plan phase. The `ready-implementers` tests read only `ready` and other existing keys (`tests/factory/test_subtickets.py` lines 119-152, `tests/factory/test_shepherd.py` lines 194, 299, 384, 466). The gate-line tests use plain `Gate suite:` lines, which still parse the same way.

=== specs/workflow-dispatch/spec.md
## ADDED Requirements

### Requirement: Intake stops at the spec gate
The intake workflow MUST NOT run the planner; a ticket that has passed the spec gate SHALL be left in `ready-for-planner` for the build workflow.

#### Scenario: Intake leaves an approved ticket for the build workflow
Run every command in this file from the repository root of the checkout under test, after `uv sync --frozen`, with node 18 or later on the PATH. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (later scenarios reuse them)

```sh
cat > ${TMPDIR:-/tmp}/t0018-drive.js <<'EOF'
// Acceptance driver for T-0018: runs a factory workflow script under node, with the Workflow API
// modelled as documented: agent() returns the agent's text (a schema'd call returns the object);
// a thunk that throws inside parallel() resolves to null. Clerk calls run their command for real.
// Role calls follow the script's stub prompt; the role named by the fifth argument throws instead.
// usage (repo root, FACTORY_STATE set): node DRV <workflow.js> <ticket> <stubs> <target repo> [throw role]
const fs = require('fs'), cp = require('child_process')
const [script, ticket, stubs, target, throwRole] = process.argv.slice(2)
const state = process.env.FACTORY_STATE
const body = fs.readFileSync(script, 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const c = /nothing else:\n\n([\s\S]*)\n\nReport its stdout/.exec(prompt)
  if (c) { const r = cp.spawnSync('sh', ['-c', c[1]], { encoding: 'utf8' }); return { stdout: r.stdout, exit: r.status, stderr: r.stderr } }
  const s = /Stub file: (\S+)\nOutput file: (\S+)/.exec(prompt)
  const role = s[1].split('/').pop().replace(/-\d+\.md$/, '')
  if (role === throwRole) throw new Error(`agent type 'factory-${role}' not found`)
  if (!fs.existsSync(s[1])) return ''
  const text = fs.readFileSync(s[1], 'utf8'); fs.writeFileSync(s[2], text); return text
}
const parallel = thunks => Promise.all(thunks.map(t => t().catch(() => null)))
const run = new (Object.getPrototypeOf(async function () {}).constructor)('args', 'agent', 'phase', 'log', 'parallel', body)
run({ ticket, repo: process.cwd(), state, stubs, target, integration: 'main', inlineRoles: true }, agent, () => {}, () => {}, parallel)
  .then(r => console.log(`returned ${r.state || r.error}`), e => console.log(`threw ${e.message}`))
  .then(() => {
    for (const f of fs.readdirSync(`${state}/tickets`).sort()) {
      const t = JSON.parse(cp.execSync(`bin/factory ticket show ${f.slice(0, -5)} --json`, { encoding: 'utf8' }).trim().split('\n').pop())
      console.log(`ticket ${t.id} ${t.state} in_flight=${t.in_flight.length} reason=${t.parked ? t.parked.reason : '-'}`)
    }
    for (const r of fs.readdirSync(`${state}/runs`).sort())
      console.log(`run ${r} ${/^status: (.*)$/m.exec(fs.readFileSync(`${state}/runs/${r}/meta.yaml`, 'utf8'))[1]}`)
  })
EOF
cat > ${TMPDIR:-/tmp}/t0018-approved.sh <<'EOF'
# Sourced from the repo root: a scratch store whose T-0001 has passed the spec gate, and a scratch target repo.
DRV=${TMPDIR:-/tmp}/t0018-drive.js; W=$(mktemp -d); export FACTORY_STATE=$W/store; mkdir $W/none
git init -q -b main $W/t && git -C $W/t -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
printf '# Fixture\n\nThe bot should do the thing.\n' > $W/req.md && bin/factory ticket new --file $W/req.md >/dev/null
node $DRV factory/workflows/intake.js T-0001 tests/factory/fixtures/stubs/accept-approve $W/t >/dev/null
bin/factory approve-spec T-0001 >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0018-handplan.sh <<'EOF'
# Sourced after t0018-approved.sh: plans T-0001 the way intake's Plan phase did (a planner run, plan add, planned), with no sub-tickets.
R=$(bin/factory run start --role planner --ticket T-0001 | tail -1 | sed 's/.*"run_id": "\([^"]*\)".*/\1/')
bin/factory run compose $R >/dev/null && cp tests/factory/fixtures/stubs/accept-approve/planner-1.md $FACTORY_STATE/runs/$R/output.md
bin/factory run finish $R >/dev/null && bin/factory plan add T-0001 --from-run $R >/dev/null
bin/factory ticket transition T-0001 --to planned --by workflow >/dev/null
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0018-approved.sh && node $DRV factory/workflows/intake.js T-0001 tests/factory/fixtures/stubs/accept-approve $W/t)`
- THEN the output contains `returned ready-for-planner` and `ticket T-0001 ready-for-planner in_flight=0 reason=-`, and no line starting `run run-0004-planner`

### Requirement: The build workflow plans and creates sub-tickets
The build workflow SHALL plan a parent in `ready-for-planner` and create its sub-tickets from that planner run.

#### Scenario: Build plans a gate-approved parent and creates its sub-tickets
- GIVEN the fixture files from "Intake leaves an approved ticket for the build workflow"
- WHEN `(. ${TMPDIR:-/tmp}/t0018-approved.sh && mkdir $W/p && cp tests/factory/fixtures/stubs/accept-approve/planner-1.md $W/p/ && node $DRV factory/workflows/build.js T-0001 $W/p $W/t; grep '^source:' $FACTORY_STATE/tickets/T-0001.1.yaml)`
- THEN the output contains `run run-0004-planner PLANNED`, `ticket T-0001.1 parked in_flight=0 reason=budget kill: implementer` (the stub directory has no implementer answer) and `source: plan:run-0004-planner`

### Requirement: A planned parent without sub-tickets is repaired or parked
A build that starts on a `planned` parent with no sub-tickets SHALL create them from the planner run named by the parent's recorded plan, or park the parent with a reason containing `no sub-tickets` when it cannot.

#### Scenario: Build creates the missing sub-tickets from the recorded planner run
- GIVEN the fixture files from "Intake leaves an approved ticket for the build workflow"
- WHEN `(. ${TMPDIR:-/tmp}/t0018-approved.sh && . ${TMPDIR:-/tmp}/t0018-handplan.sh && node $DRV factory/workflows/build.js T-0001 $W/none $W/t; grep '^source:' $FACTORY_STATE/tickets/T-0001.1.yaml)`
- THEN the output contains `ticket T-0001.1 parked in_flight=0 reason=budget kill: implementer`, `run run-0005-implementer KILLED` and `source: plan:run-0004-planner`

#### Scenario: Build parks a planned parent it cannot give sub-tickets
- GIVEN the fixture files from "Intake leaves an approved ticket for the build workflow"
- WHEN `(. ${TMPDIR:-/tmp}/t0018-approved.sh && bin/factory plan add T-0001 --file tests/factory/fixtures/stubs/accept-approve/planner-1.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by workflow >/dev/null && node $DRV factory/workflows/build.js T-0001 $W/none $W/t)`
- THEN the output contains `returned parked` and a line starting `ticket T-0001 parked in_flight=0 reason=` that contains `no sub-tickets`, and no line starting `ticket T-0001.1`

### Requirement: subticket add can use the recorded plan
`factory subticket add PARENT` with neither `--run` nor `--file` SHALL create the sub-tickets from the planner run named by the parent's latest `plan.added` event, and SHALL refuse with exit 2 and the store unchanged when no such run is recorded.

#### Scenario: subticket add without a source uses the recorded planner run
- GIVEN the fixture files from "Intake leaves an approved ticket for the build workflow"
- WHEN `(. ${TMPDIR:-/tmp}/t0018-approved.sh && . ${TMPDIR:-/tmp}/t0018-handplan.sh && bin/factory subticket add T-0001; echo "exit=$?"; grep '^source:' $FACTORY_STATE/tickets/T-0001.1.yaml)`
- THEN stdout's last JSON line has `"ok": true` and names `T-0001.1`, followed by `exit=0` and `source: plan:run-0004-planner`

#### Scenario: subticket add without a source refuses when the plan came from a file
- GIVEN the fixture files from "Intake leaves an approved ticket for the build workflow"
- WHEN `(. ${TMPDIR:-/tmp}/t0018-approved.sh && bin/factory plan add T-0001 --file tests/factory/fixtures/stubs/accept-approve/planner-1.md >/dev/null && bin/factory subticket add T-0001; echo "exit=$?"; ls $FACTORY_STATE/tickets)`
- THEN the output contains `exit=2` and no `TypeError`, and the listing is `T-0001.yaml` alone

### Requirement: A failed agent call is recorded and parked
When a role's `agent()` call throws, the workflow SHALL finish that run as KILLED and park the ticket with a reason that contains the error.

#### Scenario: A failed agent call in intake parks the ticket
- GIVEN the fixture files from "Intake leaves an approved ticket for the build workflow"
- WHEN `(DRV=${TMPDIR:-/tmp}/t0018-drive.js; W=$(mktemp -d); export FACTORY_STATE=$W/store; printf '# Fixture\n\nThe bot should do the thing.\n' > $W/req.md && bin/factory ticket new --file $W/req.md >/dev/null && node $DRV factory/workflows/intake.js T-0001 tests/factory/fixtures/stubs/accept-approve $W triage)`
- THEN the output contains `returned parked`, a line starting `ticket T-0001 parked in_flight=0 reason=` that contains `agent type 'factory-triage' not found`, and `run run-0001-triage KILLED`

#### Scenario: A failed agent call in the build parks the sub-ticket
- GIVEN the fixture files from "Intake leaves an approved ticket for the build workflow"
- WHEN `(. ${TMPDIR:-/tmp}/t0018-approved.sh && node $DRV factory/workflows/build.js T-0001 tests/factory/fixtures/stubs/accept-approve $W/t implementer)`
- THEN the output contains a line starting `ticket T-0001.1 parked in_flight=0 reason=` that contains `agent type 'factory-implementer' not found`, and `run run-0005-implementer KILLED`

### Requirement: The harness stays green
The harness suite SHALL pass and the change SHALL add no whitespace errors.

#### Scenario: The harness suite passes
- WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory`
- THEN it exits 0 with no failures

#### Scenario: The change adds no whitespace errors
- WHEN `git diff --check main...HEAD; echo "exit=$?"`
- THEN it prints only `exit=0`

=== specs/verifier-gate-line/spec.md
## ADDED Requirements

### Requirement: The gate line is read in heading and emphasis forms
`factory results record --role verifier` SHALL read the verdict from the first line that starts with optional spaces, tabs, `#` or `*` followed by `Gate suite:`, optional `*` or spaces, and `PASS` or `FAIL`; prose that mentions the gate suite mid-line MUST NOT count.

#### Scenario: Heading and emphasis gate lines are read
- WHEN `(W=$(mktemp -d); export FACTORY_STATE=$W/store; printf '# Fixture\n\nThe bot should do the thing.\n' > $W/req.md && bin/factory ticket new --file $W/req.md >/dev/null && H=$(printf 'a%.0s' $(seq 40)) && for form in '## Gate suite: PASS' '**Gate suite:** PASS' '### **Gate suite: PASS**' '**Gate suite: FAIL** 2 failed'; do printf 'Commit: %s\n%s\nSTATUS: VERIFIED\nCONFIDENCE: high\nESCALATIONS: none\n' $H "$form" > $W/v.md && bin/factory results record T-0001 --head $H --role verifier --output $W/v.md >/dev/null && echo "$form => $(sed -n 's/^status: //p' $FACTORY_STATE/results/$H/ci.yaml)|$(sed -n 's/^detail: //p' $FACTORY_STATE/results/$H/ci.yaml)"; done)`
- THEN it prints `## Gate suite: PASS => PASS|`, `**Gate suite:** PASS => PASS|`, `### **Gate suite: PASS** => PASS|` and `**Gate suite: FAIL** 2 failed => FAIL|2 failed`

#### Scenario: Plain gate lines and prose read as before
- WHEN `(W=$(mktemp -d); export FACTORY_STATE=$W/store; printf '# Fixture\n\nThe bot should do the thing.\n' > $W/req.md && bin/factory ticket new --file $W/req.md >/dev/null && H=$(printf 'a%.0s' $(seq 40)) && for form in 'Gate suite: PASS' 'Gate suite: FAIL 1 failed' 'The Gate suite: PASS line was missing'; do printf 'Commit: %s\n%s\nSTATUS: VERIFIED\nCONFIDENCE: high\nESCALATIONS: none\n' $H "$form" > $W/v.md && bin/factory results record T-0001 --head $H --role verifier --output $W/v.md >/dev/null && echo "$form => $(sed -n 's/^status: //p' $FACTORY_STATE/results/$H/ci.yaml)|$(sed -n 's/^detail: //p' $FACTORY_STATE/results/$H/ci.yaml)"; done)`
- THEN it prints `Gate suite: PASS => PASS|`, `Gate suite: FAIL 1 failed => FAIL|1 failed` and `The Gate suite: PASS line was missing => FAIL|missing Gate suite line`

### Requirement: The verifier prompt states the gate line format
The verifier prompt SHALL tell the verifier to write the gate result as a plain line starting `Gate suite:`, never a heading or bold, in the design doc's block, its generated copy and the harness's role prompt.

#### Scenario: The verifier prompt pins the gate line in all three copies
- WHEN `for f in docs/design.md docs/prompts/07-verifier.md factory/prompts/verifier.md; do echo "$f $(grep -cxF 'Gate suite: PASS/FAIL, with failing output on the lines below it' $f) $(grep -cxF '  (a plain line starting "Gate suite:", never a heading or bold)' $f) $(grep -cx 'Gate suite: PASS/FAIL, with failing output' $f)"; done`
- THEN it prints `docs/design.md 1 1 0`, `docs/prompts/07-verifier.md 1 1 0` and `factory/prompts/verifier.md 1 1 0`

#### Scenario: The design block and its prompt copy stay identical
- WHEN `awk 'BEGIN{q=sprintf("%c%c%c",96,96,96)} /^## 7\. Verifier/{f=1;next} f&&index($0,q"text")==1{p=1;next} p&&index($0,q)==1{exit} p' docs/design.md | diff - docs/prompts/07-verifier.md && echo SAME`
- THEN it prints `SAME`

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The documents describe the changed behaviour
The README SHALL no longer describe a planning step in the intake script, the changelog SHALL record the change as entry 47, and the build spec SHALL name the accepted gate line forms.

#### Scenario: The README no longer describes a planning step in intake
- WHEN `grep -c "planning step" README.md`
- THEN it prints `0`

#### Scenario: The changelog records the change
- WHEN `grep -c '^47\. After issue #33 (2026-10-04)' docs/changelog.md; grep '^47\. ' docs/changelog.md | grep -c 'Gate suite:'`
- THEN it prints `1` then `1`

#### Scenario: The build spec names the accepted gate line forms
- WHEN `grep -c "heading or emphasis marks" dev/build-harness.spec.md`
- THEN it prints a number of 1 or more

=== verification.md
## Acceptance

All workflow-dispatch scenarios need the GIVEN of the first one run once (it writes `${TMPDIR:-/tmp}/t0018-drive.js`, `t0018-approved.sh` and `t0018-handplan.sh`). Every command runs from the repository root of the checkout under test, after `uv sync --frozen`.

- Intake leaves an approved ticket for the build workflow → NEW. Today it prints `returned planned`, `ticket T-0001 planned in_flight=0 reason=-` and `run run-0004-planner PLANNED`: intake runs the planner.
- Build plans a gate-approved parent and creates its sub-tickets → REGRESSION. Today it prints `run run-0004-planner PLANNED`, `ticket T-0001.1 parked in_flight=0 reason=budget kill: implementer`, `run run-0005-implementer KILLED` and `source: plan:run-0004-planner`.
- Build creates the missing sub-tickets from the recorded planner run → NEW. Today it prints `returned planned` and `ticket T-0001 planned in_flight=0 reason=-`, with no `T-0001.1` line, and grep reports `T-0001.1.yaml: No such file or directory`.
- Build parks a planned parent it cannot give sub-tickets → NEW. Today it prints `returned planned` and `ticket T-0001 planned in_flight=0 reason=-`: no park.
- subticket add without a source uses the recorded planner run → NEW. Today it prints `factory: TypeError: argument should be a str or an os.PathLike object ... not 'NoneType'` and `exit=1`, and no `T-0001.1.yaml` exists.
- subticket add without a source refuses when the plan came from a file → NEW. Today it prints the same `TypeError` and `exit=1`, not a refusal with exit 2. The listing is already `T-0001.yaml` alone.
- A failed agent call in intake parks the ticket → NEW. Today it prints `threw agent type 'factory-triage' not found`, `ticket T-0001 ready-for-triage in_flight=1 reason=-` and `run run-0001-triage running`.
- A failed agent call in the build parks the sub-ticket → NEW. Today it prints `ticket T-0001.1 ready-for-implementer in_flight=1 reason=-` and `run run-0005-implementer running`.
- The harness suite passes → REGRESSION. Today: `157 passed in 97.42s`.
- The change adds no whitespace errors → REGRESSION.
- Heading and emphasis gate lines are read → NEW. Today all four lines end `=> FAIL|missing Gate suite line`.
- Plain gate lines and prose read as before → REGRESSION. Today it prints exactly the expected three lines.
- The verifier prompt pins the gate line in all three copies → NEW. Today each file prints `0 0 1`: the new lines are absent and the old line is present.
- The design block and its prompt copy stay identical → REGRESSION. Today it prints `SAME`.
- The README no longer describes a planning step in intake → NEW. Today it prints `1` (README line 83).
- The changelog records the change → NEW. Today it prints `0` then `0`: there is no entry 47.
- The build spec names the accepted gate line forms → NEW. Today it prints `0`.

STATUS: READY-FOR-CRITIC
CONFIDENCE: high. Every NEW scenario was run on `main` at `429d218` and failed as stated, and every REGRESSION scenario passed. The one inference is that an unknown agent type makes `agent()` throw rather than return null; it rests on the #24 symptoms, which the reproduction matches.
ESCALATIONS:
- This change edits protected and guardrail paths: the harness code under `factory/**`, including the verifier's role prompt, and the generated prompt copy `docs/prompts/07-verifier.md`. The Risk section declares all of them, and the spec gate is pre-approved for #33. Under the same pre-approval policy, the prompt change still needs the operator's acceptance test before the runtime moves. That test is listed under Operator steps, step 1.
