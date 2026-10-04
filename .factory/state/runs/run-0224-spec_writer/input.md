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
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `state/`.
  The store is tracked on `main` and the operator commits it between steps, so `main` moves even
  when no ticket merges.

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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0224-spec_writer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0224-spec_writer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Ticket (Triage output)

Type: bug

Title: Role runs can write the live instance store; a spec writer's test run initialised spec-factory's own store

Summary:
An agent working a ticket (a role run) can change the factory's live records for the repository it works in. It needs nothing more than a `factory` command run from inside that repository. These records are the instance store, `.factory/state/`: tickets, run records, the event log and, once created, the spec store. The cause is that `bin/factory` looks for its instance by walking up from the working directory, and a role's shell starts inside the target repository. The throwaway HOME that role runs already get (issue #36, the earlier live-state incident) does not help, because the store is not under HOME. The requester needs role runs kept out of the live store, so that only the dispatcher's own commands write it. The dispatcher is the harness process that starts role runs and records their results. The requester proposes three parts: (A) the store refuses writes that are neither the dispatcher's nor a human's; (B) the shared prompt preamble tells roles to use a throwaway store; (C) the tripwire watches the store root during role runs. The tripwire is the harness's check that a role run did not change listed live files. The operator also asks that the spec carry one decision as an Open question for the spec gate (the operator's sign-off on a spec before any code is written): keep or remove the spec store this incident created on instance B (this repository's own factory instance). The requester recommends keeping it.

Evidence:
- Request, issue #45 in `dev/issues.md:52` ("Roles can write the live instance store"), not yet in intake.
- The store log has the event, with no run attached: `.factory/state/log/2026-10.jsonl:995` records `"ts": "2026-10-04T13:35:44+00:00", "event": "store.initialised"`. Its files are `openspec/config.yaml`, `openspec/schemas/spec-factory/schema.yaml` and `decisions.md`. Its agents are six `.../spec-factory/.claude/agents/factory-*.md` paths: clerk, planner, spec-critic, spec-writer, stub and triage.
- The run in progress at that time was `runs/run-0196-spec_writer/meta.yaml`: started `13:16:09`, finished `13:47:49`, ticket T-0023 (the harness hygiene batch, issue #39).
- How it happened, per that run's own escalation (`log/2026-10.jsonl:997`, also in `run-0196-spec_writer/meta.yaml`): "I set `TMPDIR` inside my scratch directory, which is inside this repository. The suite's `test_init_refused_outside_a_git_work_tree` then ran `init` against this repo's instance on its own store." The run record does not show the role typing `factory init` itself. It shows the harness test suite doing it. I could not find the session transcript the request cites, so I could not check the request's wording ("its transcript shows the command"). Both routes reach the store the same way. The test calls `bin/factory init` as a subprocess, from a directory inside this repository (`tests/factory/test_instance.py:25-32` and `:132-137`). So the proposed refusal (part A) would cover both routes.
- A second spec-writer run repeated the same test the same way. That run found no new changes, because the files already existed (`log/2026-10.jsonl:1006`, run-0198). It suggested a guard in the suite and said that guard needed its own issue. I found no such issue in `dev/issues.md`.
- Instance B was not meant to have agent files. Its layout spec says "Agent files for instance B. This repo keeps dispatching with inline roles; no `.claude/agents/` is added here" (`.factory/state/specs/T-0012/v1.md:71`). `ls ~/dev/spec-factory/.claude` now prints "No such file or directory", which confirms the files were removed by hand.
- Effect on later tickets: the spec store is still active. `.factory/state/openspec/specs/` holds six capabilities: build-dispatch, harness-docs, harness-suite, human-resolution, store-setup and sub-ticket-planning. Commit `81294c8` records that T-0023 was "closed by archive into current truth … The spec store itself was created by a stray 'factory init' from intake run-0196". "Current truth" is the spec store's merged record of what the system does now. Before the incident, tickets on this instance closed as applied, because there was no spec store (`dev/issues.md:19`, T-0012 "no spec store on this instance").
- Part A does not exist yet. `grep -rn FACTORY_DISPATCH` over `factory/`, `bin/`, `docs/`, `dev/` and `.factory/instance.yaml` in this checkout found nothing. The same search over `~/dev/nanobot-upstream/factory` and `~/dev/nanobot-upstream/.factory` (the reference harness) found nothing either. The request names no Nanobot-side commit with an existing fix.
- The tripwire (issue #38) cannot watch the store root as it stands. `factory/tripwire.py:1-8` takes a SHA-256 of each listed file. It has no directory entries, and it compares once, when the run ends. This instance's `.factory/instance.yaml` has no `tripwire` key at all.

Assumptions:
- (Inference) The requirement is the outcome: no role run changes the live instance store unless it does so through a dispatcher (clerk) command. The command list, the `FACTORY_DISPATCH` variable name, exit code 2 and the error text in part A are the requester's suggestion. They are not requirements.
- (Inference) "Store-writing command" includes the command that created the agent files in `.claude/agents/`, because `init` writes them in the same step. So the refusal covers that write too.
- (Inference) Part C cannot be a configuration-only change. The tripwire watches file digests, not directories. Clerk commands also write the store legitimately while a role run is in flight. The spec writer has to say how a role's own write is told apart from a clerk's write, or drop part C and say why.
- (Inference) The guard in the suite that run-0198 suggested is outside this request unless the spec writer finds it is needed to meet the requirement. Issue #37 (an investigation into OS-level isolation for role runs) overlaps this request but does not duplicate it. It is a broader investigation and has not entered intake.
- Suggested priority: high. This is a suggestion, not a decision. It has already happened once on the live store, and the agent files it wrote would have changed every later session in this repository.
- The keep-or-remove decision is not decided here. As the operator directs, it goes into the spec as an Open question for the spec gate, with the requester's recommendation (keep) and reason (issue #21, the factory's own current-state spec, wanted current truth for instance B anyway).

Reason (ACCEPT):
The intent is clear and the evidence is checked against the store log and the run records. The one product decision has been sent by the operator to the spec gate. No duplicate exists. Issue #38 built the tripwire and is closed. Issue #36 gave role runs a throwaway HOME and is closed. Issue #37 is a separate investigation. Issue #30 (`init` on a throwaway store writing a half instance) is about what `init` writes, not about where it can write. The operator says the spec gate is not pre-approved.

STATUS: ACCEPT
CONFIDENCE: high. Each cited fact was read from the store log, the run records or the code. The only thing I could not check is the request's claim about the transcript, and the run record gives a mechanism that the same fix covers.
ESCALATIONS: none

## Request (raw)

---
title: "Roles can write the live instance store: a spec writer's 'factory init' initialised spec-factory's own store"
labels: "harness"
---
**Problem:** a role can run store-writing `factory` commands against the live instance it is working on. A role's shell starts inside the target repo, so `bin/factory` walks up to that repo's own `.factory/` and writes the live store. #36's throwaway HOME does not help, because the store is not under HOME.

**Evidence (spec-factory, 2026-10-04):** at 13:35:44Z, `factory init` ran against instance B's own store. The only role run active then was T-0023's spec writer (run-0196, 13:16–13:48), which was researching #30 (`init` on a throwaway store), and its transcript shows the command. It initialised the live store: `openspec/` and `decisions.md` were created, and six `factory-*.md` agent files were copied into `~/dev/spec-factory/.claude/agents/`. Instance B's spec (T-0012) gives it no agent files. The store log records it as `store.initialised` with no run attached. Effects:
- B silently gained a spec store, so later tickets archive into current truth instead of closing as applied.
- The agent files would have registered in the next session started in that repo. They were removed by hand.

**Proposed change:**
- A. **Only the dispatcher writes the instance's own store.** The clerk's commands carry `FACTORY_DISPATCH=1`. Any store-writing command (`ticket`, `run`, `results`, `subticket`, `merge`, `archive`, `init`, `resolve`, `approve-spec`, `decision`) on the instance's own store without it, and without a human's `--by`, is refused with exit 2: "role runs may not write the live store; use a throwaway FACTORY_STATE". Read commands (`show`, `paths`, `config`) stay open.
- B. **Preamble:** to try a `factory` command, use a throwaway store (`FACTORY_STATE=<your scratch>/store`) and a throwaway instance (`FACTORY_INSTANCE`). Never the live one.
- C. **The tripwire (#38) covers the instance's own store root** for a role run, as an escalate path. Any write there during a role run that is not a clerk command is reported.

**Decision for the operator (separate):** keep the spec store that run-0196 created on B (current truth now holds 6 capabilities from T-0023), or remove it and restore close-as-applied. Recommendation: keep it. #21 wanted current truth for B anyway, and this is a start.


---

Operator (2026-10-04): take this into intake so it is properly reviewed. The spec gate is NOT pre-approved: the spec comes to the operator. The keep-or-remove decision on instance B's accidentally created spec store belongs in the spec as an Open question for the gate, with the recommendation (keep).


## Answer 1

Operator, 2026-10-04: take the recommendations, and run the result through intake with a design-review critic.

1. Keep the spec store that run-0196 created on this instance. Tickets here close by archive into current truth; decisions.md stays and keeps reaching the spec writer, critic and planner. README's stale "never entered the spec store" line is corrected by the ticket that next touches README (or #21).
2. While a role run is in flight on the live store, the operator or a runner session writes it by prefixing that one command with `FACTORY_DISPATCH=1`. README documents this; the refusal message does not name it.

For the critic (Fable): beyond the rubric, review the design itself. Does the in-flight-only fence leave a gap, for example a write after a run dies or between runs? Is "every command except a read-only list" the right default? Is the marker's copyability acceptable as stated? Does the design interact with #46 (store on its own branch) and #38 (tripwire)? Raise design findings with severity, not only rubric findings.

## Current truth: build-dispatch

# build-dispatch

## Requirements

### Requirement: A park reason carries the failing command's error
When a store command fails and its relayed stderr is empty, the workflow scripts MUST put the refusal's JSON `error`, or else the exit code, after the reason's prefix, so that no park reason ends blank.

#### Scenario: A refused archive or sub-ticket add parks with the refusal text
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-parent-verify"}}, "ticket parent-check": {"out": {"ok": true, "state": "ready-for-parent-verify", "reuse": "run-0001-verifier"}}, "archive": {"out": {"ok": false, "error": "no spec store (factory init not run)"}, "exit": 2}}'; node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-planner"}}, "run finish": {"out": {"ok": true, "status": "PLANNED"}}, "subticket add": {"out": {"ok": false, "error": "ST-2: no Depends on line"}, "exit": 2}}')`
- THEN it prints exactly `park: archive: no spec store (factory init not run)`, then `start: planner`, then `park: harness-bug: subticket add: ST-2: no Depends on line`

#### Scenario: A refused run start during intake parks with the refusal text
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/intake.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}}}, "run start": {"out": {"ok": false, "error": "T-0001 is parked, not ready-for-triage"}, "exit": 2}}')`
- THEN it prints exactly `start: triage`, then `park: harness-bug: run start triage: T-0001 is parked, not ready-for-triage`

#### Scenario: A command that prints no JSON parks with its exit code
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-parent-verify"}}, "ticket parent-check": {"out": {"ok": true, "state": "ready-for-parent-verify", "reuse": "run-0001-verifier"}}, "archive": {"raw": "", "exit": 1}}')`
- THEN it prints exactly `park: archive: exit 1, no JSON on stdout`

### Requirement: The build runs only the checkers a commit still needs
When a sub-ticket reaches the checks without an implementer run in that pass, the build MUST run only the checkers that have no result row on its commit; after an implementer run it SHALL run both.

#### Scenario: A redispatched sub-ticket runs only the checker whose row was set aside
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": [], "resumable": ["T-0001.1"], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "checks-in-flight"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"verifier": "VERIFIED", "ci": "PASS"}, "missing": ["reviewer"]}}, "run finish": {"out": {"ok": true, "status": "APPROVE"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}')`
- THEN it prints exactly `start: reviewer`, then `park: stub stop`

#### Scenario: After an implementer run both checkers run
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": ["T-0001.1"], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "ready-for-implementer"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"reviewer": "REQUEST-CHANGES", "verifier": "VERIFIED", "ci": "PASS"}, "missing": []}}, "run finish": {"out": {"ok": true, "status": "READY-FOR-REVIEW"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}')`
- THEN it prints exactly `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop`, one per line

## Current truth: harness-docs

# harness-docs

## Requirements

### Requirement: The documents record the change
`docs/changelog.md` SHALL gain entry 51 covering every part, numbered without a gap, `README.md` SHALL describe the new `resolve` behaviour and relative environment paths, and the change MUST add no whitespace errors.

#### Scenario: The changelog records the change in order
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print n, (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; sed -n '/^51\. /p' docs/changelog.md | grep -oF -e BLOCKED -e '--replan' -e 'next free' -e 'error text' -e redispatch -e '-whitespace' -e context.md -e relative -e uncommitted | sort -u | grep -c .)`
- THEN it prints `51 CONTIGUOUS`, then `9`

#### Scenario: The README describes the new resolve verbs
- WHEN `(echo "replan=$(grep -c -- '--replan' README.md | awk '{print ($1 > 0)}') gap=$(grep -c 'has no .resolve. verb' README.md)")`
- THEN it prints `replan=1 gap=0`

#### Scenario: The README says relative paths resolve from the caller's directory
- WHEN `(grep -c 'relative .FACTORY_' README.md | awk '{print ($1 > 0)}')`
- THEN it prints `1`

#### Scenario: The change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

## Current truth: harness-suite

# harness-suite

## Requirements

### Requirement: The harness suite runs mid-edit without loosening the lock
The harness's own test suite SHALL pass in a checkout that has an uncommitted edit under a harness path, and a store command on an instance's own store run from such a checkout MUST still be refused.

#### Scenario: The harness suite passes with an uncommitted harness edit
The command gives pytest its own temporary directory under `/tmp`, because four existing tests need one outside every repository and instance. Run it as written, whatever `TMPDIR` the caller has set; it removes that directory when it ends.
- WHEN `(T=$(mktemp -d) && P=$(mktemp -d /tmp/t0023-suite.XXXXXX) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && cd $T/c && TMPDIR=$P .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P")`
- THEN it prints one line reporting a number of passed tests and no `failed` or `error`

#### Scenario: The uncommitted-edit refusal still holds on an instance's own store
- WHEN `(T=$(mktemp -d) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $T/c/bin/factory init --repo-name demo >/dev/null 2>&1 && $T/c/bin/factory config >/dev/null 2>$T/err; echo "exit=$?"; head -1 $T/err | grep -o 'has uncommitted changes:$')`
- THEN it prints `exit=2`, then `has uncommitted changes:`

## Current truth: human-resolution

# human-resolution

## Requirements

### Requirement: A ruling returns a BLOCKED sub-ticket to its implementer
`factory resolve <id> --ruling F` on a park whose reason starts with `BLOCKED` MUST write F as the ticket's next ruling, return it to `ready-for-implementer` at the same round, and the next implementer input SHALL contain the ruling.

#### Scenario: A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0023-parent.sh <<'EOF'
# Sourced from the repo root: a scratch store whose T-0001 has passed the spec gate (no spec store).
T23=$(mktemp -d); export FACTORY_STATE=$T23/store
printf '# Fixture\n\nThe bot should do the thing.\n' > $T23/req.md && printf '## Problem\nx\n' > $T23/spec.md
bin/factory ticket new --file $T23/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T23/spec.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
bin/factory approve-spec T-0001 >/dev/null
git init -q -b main $T23/t && git -C $T23/t -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
export FACTORY_REPO=$T23/t FACTORY_INTEGRATION_BRANCH=main
EOF
cat > ${TMPDIR:-/tmp}/t0023-closed.sh <<'EOF'
# Sourced after t0023-parent.sh: T-0001 split into T-0001.1 and T-0001.2, both merged, then parked
# by a FAILED parent-close run.
printf 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: ST-1\nParallel-safe: yes\n' > $T23/plan1.md
bin/factory subticket add T-0001 --file $T23/plan1.md >/dev/null
bin/factory ticket set T-0001.1 status=merged >/dev/null && bin/factory ticket set T-0001.2 status=merged >/dev/null
bin/factory ticket transition T-0001 --to planned --by t >/dev/null
bin/factory ticket transition T-0001 --to ready-for-parent-verify --by t >/dev/null
bin/factory ticket park T-0001 --reason "FAILED from parent-close verifier" >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0023-wf.mjs <<'EOF'
// node t0023-wf.mjs <workflow.js> '<replies JSON>': runs one workflow script with a stub clerk that
// reports an empty stderr. A clerk command gets the reply of the longest key its `bin/factory`
// arguments start with: {"out": <object printed as JSON on stdout> | "raw": <stdout text>, "exit": n},
// or a list of such replies, used in turn (the last one repeats).
// Defaults: `config` and `run start` succeed; anything else prints {"ok": true}. Role agents return
// a bare trailer. Prints `park: <reason>` per ticket park and `start: <role>` per run start, in order.
import { readFileSync } from 'node:fs'
const [file, replies] = process.argv.slice(2)
const R = { 'config': { out: { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } },
  'run start': { out: { ok: true, run_id: 'run-0009-x', worktree: '/w' } }, ...JSON.parse(replies) }
const src = readFileSync(file, 'utf8').replace(/^export const meta/m, 'const meta')
const lines = []
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n'
  const cmd = m[1].replace(/^.*?bin\/factory /s, '')
  const p = cmd.match(/^ticket park \S+ --reason "([^"]*)"/)
  if (p) lines.push(`park: ${p[1]}`)
  const s = cmd.match(/^run start --role (\S+)/)
  if (s) lines.push(`start: ${s[1]}`)
  const key = Object.keys(R).filter(k => cmd.startsWith(k)).sort((a, b) => b.length - a.length)[0]
  let r = key ? R[key] : { out: { ok: true } }
  if (Array.isArray(r)) r = r.length > 1 ? r.shift() : r[0]
  return { stdout: 'raw' in r ? r.raw : JSON.stringify(r.out), exit: r.exit || 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r', state: '/tmp/s' }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(lines.join('\n'))
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && bin/factory ticket park T-0001.1 --reason "BLOCKED from implementer" >/dev/null && printf 'Ruling: take the second approach.\n' > $T23/r.md; bin/factory resolve T-0001.1 --ruling $T23/r.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') pr=$(bin/factory ticket show T-0001.1 | sed -n 's/^  pr: //p')"; cmp -s $T23/r.md $FACTORY_STATE/approvals/T-0001.1/ruling-1.md && echo ruling=kept || echo ruling=missing; R=$(bin/factory run start --role implementer --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; echo "in_input=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -c 'Ruling: take the second approach.')")`
- THEN it prints `exit=0 ready-for-implementer pr=0`, then `ruling=kept`, then `in_input=1`

### Requirement: Existing ruling routes are unchanged
A ruling on a critic ESCALATE park SHALL still return the ticket to `ready-for-critic`.

#### Scenario: A ruling on a critic ESCALATE still returns the ticket to the critic
- WHEN `(T=$(mktemp -d); export FACTORY_STATE=$T/store; printf '# F\n\nDo x.\n' > $T/req.md; bin/factory ticket new --file $T/req.md >/dev/null; bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null; bin/factory ticket transition T-0001 --to ready-for-critic --by t >/dev/null; bin/factory ticket park T-0001 --reason "ESCALATE from critic" >/dev/null; echo r > $T/r.md; bin/factory resolve T-0001 --ruling $T/r.md >/dev/null; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints `exit=0 ready-for-critic`

### Requirement: A re-plan returns a fully merged parent to its planner
`factory resolve <parent> --replan F` on a parked parent whose sub-tickets have all merged MUST move it to `ready-for-planner` with F as its next ruling, and the next planner input SHALL contain F and list each existing sub-ticket with its title and state; with any sub-ticket not merged it MUST refuse, naming that sub-ticket, and write nothing.

#### Scenario: A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'Re-plan: add one fix for the case-insensitive path.\n' > $T23/note.md; bin/factory resolve T-0001 --replan $T23/note.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')"; R=$(bin/factory run start --role planner --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; I=$FACTORY_STATE/runs/${R:-none}/input.md; echo "in_input=$(cat $I 2>/dev/null | grep -c 'Re-plan: add one fix') listed=$(cat $I 2>/dev/null | grep -cxF -e '- T-0001.1 / First: merged' -e '- T-0001.2 / Second: merged')")`
- THEN it prints `exit=0 ready-for-planner`, then `in_input=1 listed=2`

#### Scenario: A re-plan is refused while a sub-ticket is not merged
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && bin/factory ticket set T-0001.2 status=closed >/dev/null && echo n > $T23/note.md; echo "names=$(bin/factory resolve T-0001 --replan $T23/note.md 2>&1 >/dev/null | grep -c 'T-0001.2')"; echo "$(bin/factory ticket show T-0001 | sed -n 's/^status: //p') $(ls $FACTORY_STATE/approvals/T-0001 | tr '\n' ' ')")`
- THEN it prints `names=1`, then `parked spec-v1.yaml ` (still parked, and no ruling file written)

### Requirement: A redispatch sets aside only rows that did not pass
`factory resolve <id> --redispatch` MUST keep a reviewer row that is `APPROVE`, and the verifier and gate rows together when they are `VERIFIED` and `PASS`, and SHALL move every other row of that commit to `superseded-<n>/`.

#### Scenario: A redispatch after a killed reviewer keeps the verifier's passing rows
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && H=abababababababababababababababababababab && bin/factory ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/v.md && bin/factory results record T-0001.1 --head $H --role verifier --output $T23/v.md --run run-0002-verifier >/dev/null && bin/factory results record T-0001.1 --head $H --role reviewer --killed --run run-0003-reviewer >/dev/null && bin/factory ticket park T-0001.1 --reason "budget kill: reviewer" >/dev/null && bin/factory resolve T-0001.1 --redispatch >/dev/null && echo "kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')" && echo "set aside: $(ls $FACTORY_STATE/results/$H/superseded-1 | tr '\n' ' ')")`
- THEN it prints `kept: ci.yaml verifier.yaml `, then `set aside: reviewer.yaml `

#### Scenario: A redispatch after a verifier SPEC-DEFECT keeps the reviewer's approval
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && H=abababababababababababababababababababab && bin/factory ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && printf "Commit: $H\nGate suite: FAIL\nSTATUS: SPEC-DEFECT\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/v.md && printf "Commit: $H\nSTATUS: APPROVE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/r.md && bin/factory results record T-0001.1 --head $H --role verifier --output $T23/v.md --run run-0002-verifier >/dev/null && bin/factory results record T-0001.1 --head $H --role reviewer --output $T23/r.md --run run-0003-reviewer >/dev/null && bin/factory ticket park T-0001.1 --reason "SPEC-DEFECT from verifier" >/dev/null && bin/factory resolve T-0001.1 --redispatch >/dev/null && echo "kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')" && echo "set aside: $(ls $FACTORY_STATE/results/$H/superseded-1 | tr '\n' ' ')")`
- THEN it prints `kept: reviewer.yaml `, then `set aside: ci.yaml verifier.yaml `

## Current truth: store-setup

# store-setup

## Requirements

### Requirement: Run records are exempt from whitespace checks
A store that `init` or `run start` has touched MUST hold a `.gitattributes` with the line `runs/** -whitespace`, so that `git diff --check` SHALL NOT report run records while it still reports every other store file.

#### Scenario: Run records in a store pass whitespace checks and other store files do not
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(T=$(mktemp -d) && git init -q -b main $T/r && git -C $T/r -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && FACTORY_STATE=$T/r/store bin/factory init >/dev/null && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m store && mkdir -p $T/r/store/runs/run-0001-verifier && printf 'context \n x\n' > $T/r/store/runs/run-0001-verifier/diff.patch && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m record && git -C $T/r diff --check HEAD~1 HEAD >/dev/null; echo "runs=$?"; printf 'x \n' > $T/r/store/notes.md && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m notes && git -C $T/r diff --check HEAD~1 HEAD >/dev/null; echo "other=$?")`
- THEN it prints `runs=0`, then `other=2`

#### Scenario: A run start adds the whitespace rule to an existing store
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && bin/factory run start --role planner --ticket T-0001 >/dev/null && echo "rule=$(cat $FACTORY_STATE/.gitattributes 2>/dev/null | grep -cxF 'runs/** -whitespace')")`
- THEN it prints `rule=1`

### Requirement: No half instance, and a missing briefing refuses
`factory init` MUST refuse with exit 2, writing nothing, when it would create an instance while `FACTORY_STATE` names another store; `run compose` MUST refuse with exit 2, writing no input, when the instance has no `context.md`.

#### Scenario: init refuses to create an instance on a throwaway store and writes nothing
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && FACTORY_STATE=$T/s $B init --repo-name demo >/dev/null 2>$T/err; echo "exit=$? instance=$([ -e $T/tgt/.factory ] && echo written || echo none) store=$([ -e $T/s ] && echo written || echo none) names_state=$(grep -c FACTORY_STATE $T/err)")`
- THEN it prints `exit=2 instance=none store=none names_state=1`

#### Scenario: A missing briefing refuses the compose with exit 2
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && rm .factory/context.md && export FACTORY_STATE=$T/s && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null && $B run compose run-0001-triage >/dev/null 2>$T/err; echo "exit=$? input=$([ -e $T/s/runs/run-0001-triage/input.md ] && echo written || echo none) names_context=$(grep -c 'context.md' $T/err)")`
- THEN it prints `exit=2 input=none names_context=1`

### Requirement: Relative environment paths resolve from the caller's directory
A relative `FACTORY_STATE`, `FACTORY_INSTANCE` or `FACTORY_REPO` MUST resolve against the directory the command was run from; an absolute value SHALL be used as given.

#### Scenario: Relative FACTORY_STATE, FACTORY_INSTANCE and FACTORY_REPO resolve against the caller's directory
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; F=$(cd tests/factory/fixtures/instance && pwd -P); s=$(cd $T && FACTORY_INSTANCE=$F FACTORY_STATE=rel/store $B paths | tail -1); i=$(cd $F/.. && FACTORY_INSTANCE=instance $B paths | tail -1); r=$(cd $T && FACTORY_INSTANCE=$F FACTORY_REPO=rel $B paths | tail -1); echo "state=$(echo "$s" | grep -cF "\"state\": \"$T/rel/store\"") instance=$(echo "$i" | grep -cF "\"instance\": \"$F\"") repo=$(echo "$r" | grep -cF "\"state\": \"$T/rel/.factory/state\"")")`
- THEN it prints `state=1 instance=1 repo=1`

#### Scenario: An absolute FACTORY_STATE is used as given
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; F=$(cd tests/factory/fixtures/instance && pwd -P); cd / && echo "absolute=$(FACTORY_INSTANCE=$F FACTORY_STATE=$T/abs $B paths | tail -1 | grep -cF "\"state\": \"$T/abs\"")")`
- THEN it prints `absolute=1`

## Current truth: sub-ticket-planning

# sub-ticket-planning

## Requirements

### Requirement: A later plan's sub-tickets continue the parent's numbering
`factory subticket add` on a parent that already has sub-tickets MUST number the new ones from the next free index, SHALL accept a `Depends on:` line naming an existing sub-ticket, and MUST refuse a plan whose head line reuses an existing sub-ticket's id, writing nothing.

#### Scenario: A later plan's sub-tickets take the next free ids and may depend on a merged sibling
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'ST-1 / Fix the bypass\nDepends on: T-0001.2\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md 2>/dev/null | tail -1 | grep -o '"id": "[^"]*"\|"depends_on": \[[^]]*\]'; bin/factory ticket ready-implementers T-0001 | tail -1 | grep -o '"ready": \[[^]]*\]')`
- THEN it prints `"id": "T-0001.3"`, then `"depends_on": ["T-0001.2"]`, then `"ready": ["T-0001.3"]`

#### Scenario: A plan that reuses an existing sub-ticket id is refused and writes nothing
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'T-0001.1 / Again\nDepends on: none\nParallel-safe: yes\n' > $T23/plan3.md; bin/factory subticket add T-0001 --file $T23/plan3.md >/dev/null 2>&1; echo "exit=$? $(ls $FACTORY_STATE/tickets | tr '\n' ' ')")`
- THEN it prints `exit=2 T-0001.1.yaml T-0001.2.yaml T-0001.yaml `

## Decision log (decisions.md): standing decisions, read-only

2026-10-04 T-0023 `resolve --ruling F` also accepts a park whose reason starts with `BLOCKED`. It writes F as the next `approvals/<id>/ruling-<n>.md` and returns the sub-ticket to `ready-for-implementer` at the same round.
2026-10-04 T-0023 `resolve PARENT --replan F` moves a parked parent whose sub-tickets have all merged to `ready-for-planner`, with F as its next ruling. The planner receives F and plans the fix. Rejected: the requester's `--replan --file <plan>` straight to `planned`. It needs a new routing edge, which the queue policy does not count as small. It would also skip the planner. `dev/build-harness.spec.md` already sends a re-plan through the planner.
2026-10-04 T-0023 On a re-plan, the planner's input lists the parent's existing sub-tickets, each with its title and state. The human's note F therefore needs to say only what to fix. Rejected: asking the human to restate in F what has merged, which the store already knows.
2026-10-04 T-0023 Sub-tickets that a later plan adds take the next free ids under the parent, and their `Depends on:` lines may name the parent's existing sub-tickets. A plan head line that reuses an existing sub-ticket's id is refused. Rejected: honouring explicit non-colliding ids, a second numbering rule that the planner's free-form ids would make ambiguous.
2026-10-04 T-0023 A park reason is never blank. When the clerk relays an empty stderr, the workflows use the refusal's JSON `error`, and failing that `exit <n>, no JSON on stdout` or `exit <n>, no error text`. Rejected: editing each of the 26 reason sites.
2026-10-04 T-0023 A redispatch sets aside a checker's rows only when they did not pass. The reviewer's row is kept when it is `APPROVE`. The verifier and gate rows are kept together when they are `VERIFIED` and `PASS`, because one verifier run writes both. The build then runs only the checkers with no row on that commit. After an implementer run it still runs both. Rejected: a `--roles` flag on redispatch, which no reported case needs.
2026-10-04 T-0023 The store gets a `.gitattributes` holding `runs/** -whitespace`. `init` and every `run start` write it the way they already write `.gitignore`. Rejected: rewriting committed records, and excluding the store path inside each gate command.
2026-10-04 T-0023 `init` refuses, with exit 2 and nothing written, to create an instance while `FACTORY_STATE` names another store. A compose with no `context.md` refuses with exit 2. Rejected: writing every instance piece from a throwaway-store `init`. That contradicts the rule that such a run initialises only that store.
2026-10-04 T-0023 A relative `FACTORY_INSTANCE`, `FACTORY_STATE` or `FACTORY_REPO` resolves against the caller's directory: `FACTORY_CWD`, else the working directory.
2026-10-04 T-0023 The suite's own-store cases that are not about the uncommitted-edit refusal run the CLI through a test-only launcher that stubs that one check. The refusal itself keeps its tests on a clone's real `bin/factory`. Rejected: a switch the production CLI honours, which would loosen the check. Also rejected: running every case from a committed snapshot of the working tree, which changes every assertion that names this checkout's revision or paths.
2026-10-04 T-0023 The suite scenario gives pytest a fresh temporary directory under `/tmp` and removes it afterwards. Four existing tests need a temporary directory outside every repository, and an agent's scratch directory lies inside this one. The scenario states this in its command, so no role has to choose between its scratch rule and a valid run. Rejected: fixing those four tests in this ticket, which is beyond H8 and needs its own design (Out-of-scope observations).
2026-10-04 T-0023 The workflow-script fixes are checked by acceptance scenarios that run the scripts under node with a stub clerk. They get no suite test, because the suite does not need node today and adding that would change what the gate needs.
2026-10-04 T-0023 The change is built as four seams (design.md, "Size and seams"). They share one changelog entry, 51.
2026-10-04 T-0024 T-0024: instance B keeps the spec store created 2026-10-04 by run-0196; its tickets close by archive into current truth (operator)
2026-10-04 T-0024 While a role run is in flight on a live store, a human or runner writes it by prefixing that one command with FACTORY_DISPATCH=1; README documents it and the refusal text never names it (operator)

## Your previous output (the question you asked is answered in the request above)

=== proposal.md
## Problem
Any agent that the factory starts to work on a ticket can change the factory's live records for the repository it is working in. Such an agent is a role run. It can do this by running the harness's own command-line tool, `bin/factory`, from anywhere inside that repository.

The live records are the live store: the instance's own store under `.factory/state/`. It holds the tickets, the run records, the event log and the spec store, and it decides what the factory does next. Two parties are meant to write it. One is the dispatcher, the workflow script that starts role runs and records their results; it writes through a helper agent called the clerk, which runs one tool command at a time. The other is the human operator.

Nothing stops a role run from writing it as well. The tool finds its store by walking up from the directory it is run in. A role's shell starts inside the target repository, and so do its scratch directory and the temporary directories of the tests it runs. Role runs already get a throwaway home directory, but that does not help here, because the store is not under the home directory.

This has already happened on this repository. On 2026-10-04 a spec-writer role run ran the harness's test suite with its temporary directory set inside its scratch directory. One test runs the tool's `init` command and expects it to be refused outside a git repository. Instead, the command found this repository's live instance and initialised it. That created two things:
- a spec store, the record of what the system currently does, into which later tickets are archived;
- six agent definition files, which would have changed every later Claude Code session started in this repository.

The agent files were removed by hand. The spec store is still in use, and one later ticket has already closed into it.

Two parties are affected. The operator's store can be changed by an agent, and nothing records which run made the change. Every later ticket on that instance is also affected, because its routing depends on what the store holds.

The change makes the tool refuse every write to the live store while a role run is in flight there, meaning started and not yet finished. A command is let through if it carries a marker that only the dispatcher's commands set. Two questions go to the operator: whether to keep the spec store this incident created, and how the operator writes the live store while a run is in flight.

## Evidence
- **The event.** The store log records a `store.initialised` event with no run attached: `.factory/state/log/2026-10.jsonl:995`, `"ts": "2026-10-04T13:35:44+00:00"`. Its files are `openspec/config.yaml`, `openspec/schemas/spec-factory/schema.yaml` and `decisions.md`. Its `agents` are six `/Users/dphang/dev/spec-factory/.claude/agents/factory-*.md` paths.
- **The run.** Only run-0196 was in flight then (`runs/run-0196-spec_writer/meta.yaml`: started `13:16:09`, finished `13:47:49`, ticket T-0023). Its own escalation (`log/2026-10.jsonl:997`) gives the route: "I set `TMPDIR` inside my scratch directory, which is inside this repository. The suite's `test_init_refused_outside_a_git_work_tree` then ran `init` against this repo's instance on its own store." That test runs `bin/factory init` as a subprocess from its temporary directory (`tests/factory/test_instance.py:25-32`, `:132-137`). A second spec-writer run, run-0198, repeated the test the same way (`log/2026-10.jsonl:1006`). It wrote nothing new only because the files already existed.
- **The lasting effect.** `.factory/state/openspec/specs/` now holds six capabilities: build-dispatch, harness-docs, harness-suite, human-resolution, store-setup and sub-ticket-planning. Commit `81294c8` says that T-0023 "closed by archive into current truth" and that the spec store "was created by a stray 'factory init' from intake run-0196". Before the incident, this instance's tickets closed as applied because there was no spec store (`dev/issues.md:19`). This instance was never meant to have agent files (`.factory/state/specs/T-0012/v1.md:71`). `ls ~/dev/spec-factory/.claude` prints "No such file or directory", so they are gone now. A repeat of the suite route would write them again.
- **Reproduced on this checkout (base `3a3f58c`).** I set up a scratch target repository with one triage run in flight on its live store. I deleted its agent files and spec store, as on this repository today. From a subdirectory of the target, I ran the first scenario under "Unmarked writes from inside the target are refused while a run is in flight, init included". It printed `init=0 new=0 transition=0 decision=0 store=changed agents=written`. That means `init`, `ticket new`, `ticket transition` and `decision add` all succeeded while the run was in flight, and `init` wrote the agent files again.
- **The suite route, reproduced.** I set up the same kind of target and ran the one `init` test with `TMPDIR` inside it. Base printed `1 failed` and `agents=written`: the test fails because `init` succeeds, and the target's agent files reappear. With the prototype fence below, it printed `1 failed` and `agents=none`: the test still fails, because `init` is now refused with the new message, but nothing is written. The suite's other temporary-directory assumptions are outside this change; see Out of scope.
- **Prototype.** I built a prototype in a scratch clone: parts A and B below, 31 added and 2 changed lines. All eight runnable scenarios in specs/live-store-guard and specs/build-dispatch produce the THEN output on the prototype. The four NEW ones produce the "fails today" output on base. The harness suite gave `254 passed` on base. On the prototype it gave `1 failed, 253 passed`. The failure was `test_composed_input_opens_with_the_instance_context` (see Tests to change). After the one-line change listed there, the prototype gave `254 passed`. I ran both suites with `TMPDIR` under `/tmp`, as the current-truth suite scenario does.
- **Negative control for the dispatcher marker.** I took the marker out of `intake.js` on the prototype. The intake run against a real store then printed `returned=parked stored=ready-for-triage` instead of `closed`. That means the clerk's own `run finish` was refused. So the marker is what lets the dispatcher through, and the end-to-end scenario detects a missing marker.
- **The operator writes while runs are in flight.** Ticket T-0025 was filed at `17:50:05` (`log/2026-10.jsonl:1123`). This run, run-0220, had been in flight since `17:46:38` (`:1121`). Under this change, that `ticket new` would have needed the marker (Open question 2).
- **The requester's proposed exemption for humans does not match the code.** Human commands take no `--by`. `approve-spec`, `request-changes`, `resolve` and `decision add` record the operating-system user name (`factory/cli.py:638-639`, `_by()`). `ticket transition` requires `--by` on every call (`factory/cli.py:1063`), so a role would supply it too.
- **Part A does not exist yet.** `grep -rn FACTORY_DISPATCH` finds nothing in `factory/`, `bin/`, `docs/`, `dev/` or `.factory/instance.yaml`, and nothing in `~/dev/nanobot-upstream/factory` or `.factory`.

## Root cause
- `factory/instance.py:55` `find()`: when `FACTORY_INSTANCE` is unset, the instance is the nearest `.factory/instance.yaml` above the caller's directory. Any directory inside the repository resolves to the live instance. That includes a role's scratch directory, `runs/<id>/scratch/` inside the store, and any `tmp_path` under it.
- `factory/cli.py:1193-1203` `main()` and `factory/cli.py:845` `init_cmd()` check only the harness lock and the uncommitted-edit refusal (`instance.guard`, `factory/instance.py:141`) before writing the live store. Neither asks whether a role run is in flight or who is calling. `init_cmd` copies the agent files at `factory/cli.py:882`.
- The suite's `test_init_refused_outside_a_git_work_tree` (`tests/factory/test_instance.py:132`) assumes its temporary directory lies outside every repository. The scratch rule puts a role's temporary files inside the store, which is inside the repository. Together these turned a refusal test into a live `init`.

## Out of scope
- The test suite's assumption that its temporary directory lies outside every repository. run-0198 suggested a guard in the suite, and that needs its own issue. After this change, the test fails without writing the live store.
- Writes that bypass `bin/factory`, such as an editor or a shell redirect into `.factory/`. `.factory/**` is already a protected path in every role's rules. Isolating role runs at the operating-system level is issue #37.
- A role run of one instance writing a different instance whose live store has nothing in flight.
- Part B of the request (a preamble line telling roles to use a throwaway store) is cut. See Decisions.
- Part C of the request (the tripwire watching the store root) is cut. See Decisions.
- The clerk agent definition (`agents/factory-clerk.md`), the shared preamble and its copies (`factory/prompts/preamble.md`, `docs/prompts/00-preamble.md`), and `dev/build-harness.spec.md` do not change. The build spec describes neither of the comparable later guards: `grep -n -i "tripwire\|accept-harness\|uncommitted" dev/build-harness.spec.md` finds none.
- Logging refused attempts. A refusal writes nothing, as every other refusal does.

## Open questions
1. **Keep or remove the spec store that run-0196 created on this repository.**
   - Keep: this repository's tickets go on closing by archive into current truth. Current truth already holds six capabilities from T-0023, and this ticket's own approved spec would archive there too.
   - Remove: tickets go back to closing as applied, and the operator deletes `.factory/state/openspec/` and `.factory/state/decisions.md`. That also removes the decision log that later spec writers, critics and planners receive, which today holds T-0023's 13 standing decisions. Those decisions also exist in T-0023's spec, `.factory/state/specs/T-0023/v2.md`, but no role receives them from there.

   Recommendation (the requester's): keep it. Issue #21, the factory's own current-truth spec, wanted current truth for this instance anyway, and this is a start. This is a standing decision: it fixes how every later ticket on this instance closes.
2. **How the operator writes the live store while a role run is in flight there.** This happens in practice: T-0025 was filed while this run was in flight.
   - (a) The operator puts `FACTORY_DISPATCH=1` in front of that one command. README documents this. The refusal message does not mention it, so that a role reading the message is not shown the way past it.
   - (b) The operator waits until no run is in flight.
   - (c) A second variable just for the operator, which would only add attribution in the log.

   Recommendation: (a). This is a standing decision: it fixes what every runner session, including the Nanobot Driver, does when it files or resolves a ticket during a run.

## Decisions
- The fence applies only to the live store, and only while at least one role run is in flight there. Rejected: refusing every unmarked write at all times, as the requester proposed. The operator would then need the marker on every command and would export it in the shell, and every role run started from that shell would inherit it.
- The dispatcher marker is the environment variable `FACTORY_DISPATCH=1`. Both workflow scripts put it in front of every clerk command. Rejected: the requester's exemption for "a human's `--by`". Human commands have no `--by`, and `ticket transition` requires one from everyone.
- A write is every command except a fixed read-only list: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths`. Any command given `--accept-harness` is a write. Rejected: the requester's list of ten write commands. It misses writes such as `ticket set`, `ticket park`, `ticket head`, `run compose` and `spec add`, and a list of reads stays closed when a command is added.
- The refusal exits 2 and writes nothing. Its text is `role runs may not write the live store (<store>; in flight: <run ids>); use a throwaway FACTORY_STATE`, and it never names the marker.
- The fence guards against accidents, not against a determined agent. A role that reads the workflow scripts or README can copy the marker. That is recorded under Risk rather than designed around.
- Part B (a preamble line) is cut. The incident came from the test suite, not from a command the role typed, so a preamble line would not have stopped it. The refusal text gives the same advice at the moment it matters.
- Part C (the tripwire on the store root) is cut. Role runs legitimately write their own run directory in the store (`output.md`, `scratch/`). Clerk commands for other tickets' runs also write the store during a run. So a comparison of the store root cannot tell whose write it saw, and the fence refuses the write before it happens.

## Risk
- **Blast radius.** Every target that runs this harness: this repository (instance B) and the Nanobot fork (instance A) after it upgrades. Any runner command that writes the live store without the marker while a run is in flight there is refused with exit 2. That includes filing a ticket, `resolve`, `decision add`, `approve-spec`, `ticket set`, and `--accept-harness` on any command. The workflow scripts carry the marker, so intake and build are unaffected. A refused command writes nothing, so the failure is loud and safe.
- **Stale in-flight runs.** A workflow that dies leaves its run in flight. Unmarked operator writes are then refused until the run is cleared with a marked `ticket set`. README says so.
- **Not a security boundary.** See Decisions. Direct file writes are not stopped. That is issue #37.
- **Protected paths this change touches:**
  - harness: `factory/cli.py`, `factory/workflows/intake.js`, `factory/workflows/build.js`;
  - guardrail: one existing test, `tests/factory/test_instance.py` (Tests to change).
- **Not touched:** `.factory/**` (except by the operator step for Open question 1), `agents/**`, `bin/factory`, `docs/prompts/**`, `pyproject.toml`, `uv.lock`, `~/dev/nanobot-upstream/**`, `~/.nanobot/**`.

## Operator steps
1. Apply the answer to Open question 1. If keep: nothing to do. If remove: decide whether T-0023's 13 decision lines must still reach later roles, because removing the file stops that. Then `git rm -r .factory/state/openspec .factory/state/decisions.md` and commit.
2. After merge, between builds: move the runtime and accept the new revision in each target, as README "Upgrading the runtime" says.
3. Tell each runner session, including the Nanobot Driver, the answer to Open question 2 before its next intake or build.

## Out-of-scope observations
- README "Not built" says the factory's own capabilities "never entered" the spec store (`README.md:366`). Six of them are there now. That line is stale whatever the answer to Open question 1, and it is not changed here.

=== design.md
## Proposed change
**A. The fence, in `factory/cli.py`.**
1. Add the read-only set as `(command, subcommand)` pairs: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail`, `paths`. Each writes nothing; I checked that none calls `save_ticket`, `write_*` or `log_event`. `ticket head` saves the ticket, so it stays a write.
2. "Runs in flight" are the union of the `in_flight` lists over `tickets/*.yaml` in the store in use. Sub-tickets are ticket files too.
3. Add one fence function that raises `Refused` when all of these hold:
   - the store in use is the instance's own (`instance.is_own_store`);
   - the command is not in the read-only set, or `--accept-harness` was given;
   - at least one run is in flight;
   - `os.environ.get("FACTORY_DISPATCH") != "1"`.

   The message is exactly `role runs may not write the live store (<store>; in flight: <comma-separated run ids>); use a throwaway FACTORY_STATE`. `main()`'s existing `Refused` handler gives exit 2, stderr and `{"ok": false, "error": ...}`.
4. Call the fence in `main()` after `root = store.state_root(cfg)` and before `instance.guard(...)`, so that a fenced `--accept-harness` rewrites no lock.
5. Call the fence in `init_cmd` right after `cfg`/`root` are loaded for an existing instance, before any write: `context.md`, `harness.lock`, agent files, `.gitignore`, `.gitattributes`, the spec store. A brand-new instance has no tickets, so `init` on a new repository is never fenced.
6. Add the new behaviour's tests in a new file, such as `tests/factory/test_live_store_guard.py`.

**B. The dispatcher marker, in the workflow scripts.** In `factory/workflows/intake.js:26` and `factory/workflows/build.js:21`, start `ENV` with `'FACTORY_DISPATCH=1'` so that `BIN`, and with it every clerk command, carries it unconditionally. The clerk needs no change: runners already pass `instance` (README "Starting a run"), so clerk commands already begin with an environment assignment.

**C. Documents.**
- `docs/design.md`: a new paragraph after "**Tripwire on live files.**", titled "**Only the dispatcher writes a live store during a run.**". It states the rule from A (live store only, in flight only, read-only list, `--accept-harness`), the `FACTORY_DISPATCH=1` marker set by both workflow scripts, the refusal (exit 2, writes nothing, names a throwaway `FACTORY_STATE`, not the marker), and that this guards against accidents and is not isolation.
- `docs/changelog.md`: entry 52, one line, the next number after 51. It names `FACTORY_DISPATCH`, "in flight", the throwaway store and exit 2, and says that parts B and C of the request were declined, with their reasons.
- `README.md`:
  - a "Built" bullet for the fence, saying it is tested and has not yet fired on a real ticket;
  - in "Where a human decides", one paragraph saying that while a run is in flight on a store the operator puts `FACTORY_DISPATCH=1` in front of a write, a stale in-flight run included (subject to Open question 2);
  - bump the status date, per "Maintaining this page".
- `docs/prompts/` and `factory/prompts/` do not change.

## Tests to change
- `tests/factory/test_instance.py::test_composed_input_opens_with_the_instance_context` (line 274). Its `run compose` call is the dispatcher's own command. It runs on a scratch instance's live store while the triage run that `_start_triage` just started is in flight, so the fence refuses it. Change: pass `FACTORY_DISPATCH="1"` to that one `cli(...)` call. Verified on the prototype: `1 failed, 253 passed` without this change, `254 passed` with it. No other existing test changes.

=== specs/live-store-guard/spec.md
## ADDED Requirements
### Requirement: Unmarked writes to a live store are refused while a role run is in flight there
While any run is in flight on an instance's own store, every `factory` command on that store except `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths` (and any command given `--accept-harness`) MUST be refused with exit 2, writing nothing to the store, the instance or the repository, unless its environment has `FACTORY_DISPATCH=1`; the refusal SHALL name a throwaway `FACTORY_STATE` and SHALL NOT name the marker.

#### Scenario: Unmarked writes from inside the target are refused while a run is in flight, init included
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0024-inflight.sh <<'EOF'
# Sourced from the repo root: a scratch target whose own store has one triage run in flight; the
# shell is left in a subdirectory of that target, as a role's test or scratch directory would be.
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory
git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1
printf '# F\n\nDo x.\n' > $T/req.md && printf '# G\n\nDo y.\n' > $T/req2.md && $B ticket new --file $T/req.md >/dev/null
R=$($B run start --role triage --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
mkdir -p sub/scratch && cd sub/scratch
snap() { find $T/tgt/.factory $T/tgt/.claude -type f -exec cksum {} + 2>/dev/null | sort | cksum; }
EOF
cat > ${TMPDIR:-/tmp}/t0024-count.mjs <<'EOF'
// node t0024-count.mjs <workflow.js>: runs one workflow script with a stub clerk that answers every
// command {"ok": true}; prints whether any clerk command was sent and how many lack the marker.
import { readFileSync } from 'node:fs'
const src = readFileSync(process.argv[2], 'utf8').replace(/^export const meta/m, 'const meta')
let n = 0, unmarked = 0
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n'
  n++
  if (!/(^|\s)FACTORY_DISPATCH=1\s/.test(m[1].split('bin/factory')[0])) unmarked++
  const out = / config$/.test(m[1]) ? { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } : { ok: true, state: 'ready-for-triage' }
  return { stdout: JSON.stringify(out), exit: 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r' }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(`${n > 0 ? 'sent' : 'none-sent'} unmarked=${unmarked}`)
EOF
cat > ${TMPDIR:-/tmp}/t0024-e2e.mjs <<'EOF'
// node t0024-e2e.mjs <instance dir>, from the checkout under test: runs factory/workflows/intake.js
// on ticket T-0001 of that instance's own store. Each clerk command runs for real (sh -c, from this
// checkout, environment unchanged); each role writes the stub output "STATUS: REJECT". Prints the
// state the workflow returns.
import { readFileSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const src = readFileSync('factory/workflows/intake.js', 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  const o = prompt.match(/Write your complete output to (\S+) and return/)
  const text = 'STATUS: REJECT\nCONFIDENCE: high, stub\nESCALATIONS: none\n'
  writeFileSync(o[1], text)
  return text
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
const res = await fn({ ticket: 'T-0001', repo: process.cwd(), instance: process.argv[2], inlineRoles: true }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(res.state)
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && rm -rf $T/tgt/.claude $T/tgt/.factory/state/openspec $T/tgt/.factory/state/decisions.md && S0=$(snap); $B init --repo-name x >/dev/null 2>&1; i=$?; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; $B ticket transition T-0001 --to closed --by t >/dev/null 2>&1; t=$?; $B decision add T-0001 x >/dev/null 2>&1; d=$?; echo "init=$i new=$n transition=$t decision=$d store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) agents=$([ -e $T/tgt/.claude ] && echo written || echo none)")`
- THEN it prints exactly `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`

#### Scenario: The refusal names the throwaway store and not the marker
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && E=$($B decision add T-0001 x 2>&1 >/dev/null); J=$($B decision add T-0001 x 2>/dev/null | tail -1); echo "rule=$(echo "$E" | grep -c 'role runs may not write the live store') state=$(echo "$E" | grep -c FACTORY_STATE) marker=$(echo "$E$J" | grep -c FACTORY_DISPATCH) json=$(echo "$J" | grep -c '"ok": false')")`
- THEN it prints exactly `rule=1 state=1 marker=0 json=1`

### Requirement: Reads, marked commands, throwaway stores and idle stores stay open
While a run is in flight on the live store, the read-only commands and every command with `FACTORY_DISPATCH=1` SHALL succeed as before, and a command on a throwaway store (`FACTORY_STATE` naming another store) SHALL NOT be fenced; with no run in flight, unmarked writes SHALL succeed as before.

#### Scenario: Read commands still answer while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && $B ticket show T-0001 >/dev/null 2>&1; s=$?; $B config >/dev/null 2>&1; c=$?; $B log tail >/dev/null 2>&1; l=$?; $B results show T-0001 >/dev/null 2>&1; r=$?; echo "show=$s config=$c log=$l results=$r")`
- THEN it prints exactly `show=0 config=0 log=0 results=0`

#### Scenario: Marked commands still write while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && FACTORY_DISPATCH=1 $B decision add T-0001 "marked line" >/dev/null 2>&1; d=$?; FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1; f=$?; echo "decision=$d finish=$f cleared=$($B ticket show T-0001 --json | tail -1 | grep -c '"in_flight": \[\]')")`
- THEN it prints exactly `decision=0 finish=0 cleared=1`

#### Scenario: A throwaway store is not fenced while the live one has a run in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && FACTORY_STATE=$T/s $B init >/dev/null 2>&1; i=$?; FACTORY_STATE=$T/s $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; echo "init=$i new=$n")`
- THEN it prints exactly `init=0 new=0`

#### Scenario: With no run in flight, unmarked commands write as before
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; $B decision add T-0001 "after the run" >/dev/null 2>&1; d=$?; echo "new=$n decision=$d")`
- THEN it prints exactly `new=0 decision=0`

=== specs/build-dispatch/spec.md
## ADDED Requirements
### Requirement: The workflows' clerk commands carry the dispatcher marker
Every store command that `factory/workflows/intake.js` and `factory/workflows/build.js` send to the clerk MUST carry `FACTORY_DISPATCH=1` in its environment assignments, so that a dispatch SHALL still complete on a live store while its own role run is in flight.

#### Scenario: Every clerk command of both workflows carries the marker
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(echo "intake: $(node ${TMPDIR:-/tmp}/t0024-count.mjs factory/workflows/intake.js)"; echo "build: $(node ${TMPDIR:-/tmp}/t0024-count.mjs factory/workflows/build.js)")`
- THEN it prints exactly `intake: sent unmarked=0`, then `build: sent unmarked=0`

#### Scenario: An intake run against a real store reaches its end with its run in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once. The clerk commands run for real on a scratch instance's own store, and the triage run is in flight when the workflow records its result.
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && (cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null) && echo "returned=$(node ${TMPDIR:-/tmp}/t0024-e2e.mjs $T/tgt/.factory) stored=$(cd $T/tgt && $B ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints exactly `returned=closed stored=closed`

=== specs/harness-docs/spec.md
## ADDED Requirements
### Requirement: The documents record the live-store guard
`docs/changelog.md` SHALL gain entry 52 for this change, numbered without a gap; `docs/design.md` and `README.md` SHALL describe the dispatcher marker; no prompt copy under `docs/prompts/` or `factory/prompts/` SHALL change; and the change MUST add no whitespace errors.

#### Scenario: The changelog records the guard as entry 52
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print n, (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; sed -n '/^52\. /p' docs/changelog.md | grep -oF -e FACTORY_DISPATCH -e 'in flight' -e throwaway -e 'exit 2' | sort -u | grep -c .)`
- THEN it prints `52 CONTIGUOUS`, then `4`

#### Scenario: The design doc and README name the marker, and no prompt copy changes
- WHEN `(echo "design=$(grep -c FACTORY_DISPATCH docs/design.md | awk '{print ($1 > 0)}') readme=$(grep -c FACTORY_DISPATCH README.md | awk '{print ($1 > 0)}') prompts=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts | grep -c .)")`
- THEN it prints exactly `design=1 readme=1 prompts=0`

#### Scenario: The guard change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

=== verification.md
## Acceptance
- Unmarked writes from inside the target are refused while a run is in flight, init included → NEW. Today it prints `init=0 new=0 transition=0 decision=0 store=changed agents=written`: every write succeeds, and `init` writes the agent files again.
- The refusal names the throwaway store and not the marker → NEW. Today it prints `rule=0 state=0 marker=0 json=0`: the write succeeds, so there is no refusal text.
- Read commands still answer while a run is in flight → REGRESSION. Prints `show=0 config=0 log=0 results=0` on base and on the prototype.
- Marked commands still write while a run is in flight → REGRESSION. Prints `decision=0 finish=0 cleared=1` on base and on the prototype.
- A throwaway store is not fenced while the live one has a run in flight → REGRESSION. Prints `init=0 new=0` on base and on the prototype.
- With no run in flight, unmarked commands write as before → REGRESSION. Prints `new=0 decision=0` on base and on the prototype.
- Every clerk command of both workflows carries the marker → NEW. Today it prints `intake: sent unmarked=6`, then `build: sent unmarked=2`: no clerk command carries the marker.
- An intake run against a real store reaches its end with its run in flight → REGRESSION. Prints `returned=closed stored=closed` on base and on the prototype. With the fence but without the marker it prints `returned=parked stored=ready-for-triage`, so this scenario catches a missing or partial part B.
- The changelog records the guard as entry 52 → NEW. Today it prints `51 CONTIGUOUS`, then `0`.
- The design doc and README name the marker, and no prompt copy changes → NEW. Today it prints `design=0 readme=0 prompts=0`.
- The guard change adds no whitespace errors → REGRESSION. Prints `exit=0` on base.
- The gate suite (`uv run --frozen pytest -q -p no:cacheprovider tests/factory`) covers the one test listed under Tests to change. It is not a separate scenario.

STATUS: NEEDS-HUMAN
CONFIDENCE: medium. Every scenario was run on base `3a3f58c` and on a scratch prototype of parts A and B, and the suite passed on the prototype after the one listed test change. The design depends on two operator answers (keep the spec store; how the operator writes during a run), and a different answer to question 2 changes the README part and possibly the fence.
ESCALATIONS: none
