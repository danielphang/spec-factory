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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0252-spec_writer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0252-spec_writer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Ticket (Triage output)

Type: feature

Title: Workflow view shows a short task title beside every ticket id, in narrator lines and agent labels

Summary:
The operator watches factory runs in the Claude Code workflow view, both in the terminal (`/workflows`) and in the mobile app. Every row there names a ticket by its bare id, such as `triage T-0012` or `clerk: run start triage`. The operator cannot remember which id is which task, so each glance means a lookup. The request asks the two workflow scripts, `factory/workflows/intake.js` and `factory/workflows/build.js`, to add a short title beside the id in three places:
- a narrator line at the start of a run giving the ticket, its short title and its state, plus the GitHub issue number when the request names one;
- a narrator line at each step that changes the ticket's state;
- every agent label, including those of the clerk agents that run the store commands.

A narrator line is a `log()` message that the Workflow tool prints above the progress tree. Routing, store calls and STATUS handling must not change. Only the label and log text changes.

Evidence:
- Request: the card reads `factory-intake`, agent rows read `triage T-0012` or `clerk: run start triage`. The operator "reviews on the phone and cannot remember which number is which task. Every glance means looking up `T-0018` or `#31`."
- Operator, 2026-10-04 (relayed by the harness as the user request for this run): "I would like some 1-liner snippet besides just identifiers like "T-0018" or "GH-#31" so i dont have to do the lookup … file it but just get to it."
- I confirmed the current labels on this checkout. The clerk label is built as `` `clerk: ${label}` `` at `factory/workflows/intake.js:54` and `factory/workflows/build.js:45`. The role labels are `` `${role} ${TICKET}` `` and `` `${role} (stub) ${TICKET}` `` (intake.js:97 and :91), and `` `${role} ${ticket}` `` (build.js:88 and :82). None of them carries a title.
- The title is already available to both scripts. intake.js:126 and build.js:198 call `ticket show <id> --json` for the parent ticket, and build.js:126 makes the same call for each sub-ticket. The JSON carries `"title"` (`factory/cli.py:88`).
- One claim in the request does not match the code. The request says "the scripts never call `log()`", but they do: intake.js:72, 112, 113 and 166, and build.js:63, 111, 112, 172, 176 and 232. Those lines name the ticket by bare id only (for example `` `${TICKET} parked: ${reason}` ``) or by run id (`` `${role} ${runId}: ${fin.status}` ``). So the problem stands, and part B of the request means extending these existing lines and adding lines for transitions that do not log yet.
- The card's name and description come from the fixed `meta` literal at the top of each script (intake.js:1-3, build.js:1-3). The request accepts that these cannot change at run time.
- No duplicate. No ticket title under `.factory/state/tickets/` and no row in `dev/issues.md` (issues 1-45) covers workflow labels or narrator lines. This request is ticket T-0026 itself.

Assumptions (my inferences, labelled as such):
- A1 (a gap in how the request can be accepted). The request's acceptance is "a stub-mode run of each workflow (the existing fixtures)". The workflow scripts cannot run under pytest. `tests/factory/test_shepherd.py` lines 9-11 say so and apply the same routing table in Python instead. No test in `tests/factory/` reads a workflow agent label. So a stub-mode run needs the Claude Code Workflow runtime, which is an operator step and not a shell command. The briefing requires acceptance commands that run as written from `~/dev/spec-factory`. I assume the spec writer will add shell checks, such as greps over the two scripts showing every `label:` and `log(` names the ticket's short title. The stub-mode run becomes an Operator step, together with the request's own confirmation that `log()` lines appear in the mobile view. Part D's "the stub-mode tests that read labels" has no such tests to keep passing on this checkout.
- A2 (calls made before the title is known). The first two clerk calls in each script run before the title is known: `config` and `ticket show` itself (intake.js:123 and :126). I assume those two keep their current labels.
- A3 (where the issue number comes from). The request says the GitHub issue number comes from a request header `issue:` or a `#NN` in the title. T-0026's own request has no `issue:` header (`.factory/state/requests/T-0026.md` lines 1-4). `ticket show --json` does not return the request's front matter. So the spec writer has to decide where the script reads the issue number. Any new CLI output field it adds is a store CLI change under `factory/`.
- A4 (a protected path, declared by the request). `factory/workflows/*.js` is a protected harness path. The request names those files as the change, so the spec's Risk section should declare them.
- A5 (no README change). The README does not quote label or log text. Line 487 points at the workflow scripts for "How a ticket moves", which this change leaves alone. So I assume the README needs no change.
- Priority (suggestion only): low risk and small. The operator has pre-approved it and asked for it to be done promptly.

Reason: ACCEPT. The intent is clear: show a short title beside every ticket id in the workflow view. The operator has already decided the product question by pre-approving it. A1-A3 are for the spec writer to settle and need no product call.

STATUS: ACCEPT
CONFIDENCE: high. The labels, the existing `log()` calls and the title source were all checked against this checkout's code. The one gap (A1, a stub-mode run cannot be a shell command) affects how the spec writer frames acceptance, not the intent.
ESCALATIONS: none

## Request (raw)

---
title: "Workflow view says what it is working on: a short title beside every ticket id, in narrator lines and agent labels"
labels: "harness"
---
**Problem:** the Claude Code workflow view (terminal `/workflows` and the mobile app) shows only bare ids. The card reads `factory-intake`, agent rows read `triage T-0012` or `clerk: run start triage`, and the scripts never call `log()`. The operator reviews on the phone and cannot remember which number is which task. Every glance means looking up `T-0018` or `#31`.

**What the Workflow tool allows:** the card's name and description come from a fixed `meta` literal and cannot change at run time. Each `agent()` call's `label` can be any string. `log(message)` prints narrator lines above the progress tree at any time.

**Proposed change** (`factory/workflows/intake.js`, `factory/workflows/build.js`):
- A. **At start, one `log()` line naming the work:** `<ticket> · <short title> · <state>`, and the GitHub issue when the request names one (for example, from a request header `issue:` or a `#NN` in its title). The title comes from the `ticket show --json` call the script already makes. Short title = the ticket title cut to about 60 characters at a word boundary.
- B. **A `log()` line at each step that changes state,** for example: `T-0024 · live-store fence: critic APPROVE (round 2) → awaiting spec gate`, `T-0024.1 · …: merged 4f8f1d5`, `T-0024 · …: parked — <reason>`.
- C. **Every agent label carries the ticket and its short title,** clerk labels included: `triage T-0025 · store on its own branch`, `clerk T-0025 · store on its own branch: transition → ready-for-critic`. Sub-tickets use their own title.
- D. **No behaviour change:** routing, store calls and STATUS handling are untouched; only label and log text change. The stub-mode tests that read labels keep passing or are updated in the same change.

**Acceptance:** a stub-mode run of each workflow (the existing fixtures) shows the start line, at least one transition line and labels carrying the short title. The operator confirms on the next real run, in the mobile view, that `log()` lines appear there; if they don't, labels alone still carry the title.

**Gate:** pre-approved by the operator (2026-10-04, "yes, let's do it pre-approved… just get to it").

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

### Requirement: The workflows' clerk commands carry the dispatcher marker
Every store command that `factory/workflows/intake.js` and `factory/workflows/build.js` send to the clerk MUST carry `FACTORY_DISPATCH=1` in its environment assignments, so that a dispatch SHALL still complete on a live store while its own role run is in flight.

#### Scenario: Every clerk command of both workflows carries the marker
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(echo "intake: $(node ${TMPDIR:-/tmp}/t0024-count.mjs factory/workflows/intake.js)"; echo "build: $(node ${TMPDIR:-/tmp}/t0024-count.mjs factory/workflows/build.js)")`
- THEN it prints exactly `intake: sent unmarked=0`, then `build: sent unmarked=0`

#### Scenario: An intake run against a real store reaches its end with its run in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once. The clerk commands run for real on a scratch instance's own store, from the checkout under test, and the triage run is in flight when the workflow records its result.
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && (cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null) && echo "returned=$(node ${TMPDIR:-/tmp}/t0024-e2e.mjs $T/tgt/.factory) stored=$(cd $T/tgt && $B ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints exactly `returned=closed stored=closed`

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

### Requirement: The documents record the live-store guard
`docs/changelog.md` SHALL gain one entry for this change as its last numbered entry, numbered without a gap; `docs/design.md` SHALL describe the dispatcher marker and the run-directory rule; README's "Where a human decides" SHALL open with the marker's exact command form and say that the refusal deliberately does not name it; README SHALL say the final verifier run is listed as in flight and SHALL no longer say the factory's capabilities never entered the spec store; no prompt copy under `docs/prompts/` or `factory/prompts/` SHALL change; and the change MUST add no whitespace errors.

#### Scenario: The changelog records the guard as its last entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e FACTORY_DISPATCH -e 'in flight' -e throwaway -e 'exit 2' -e 'worktrees/' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: The design doc names the marker and the run-directory rule, and no prompt copy changes
- WHEN `(echo "design=$(grep -c FACTORY_DISPATCH docs/design.md | awk '{print ($1 > 0)}') dirs=$(grep FACTORY_DISPATCH docs/design.md | grep -c 'worktrees/' | awk '{print ($1 > 0)}') prompts=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts | grep -c .)")`
- THEN it prints exactly `design=1 dirs=1 prompts=0`

#### Scenario: README tells the operator how to write during a run, first thing under Where a human decides
- WHEN `(H=$(sed -n '/^## Where a human decides/,/^## What is built/p' README.md); J=$(echo "$H" | tr '\n' ' ' | tr -s ' '); echo "first=$(echo "$H" | sed -n '3p' | grep -c 'FACTORY_DISPATCH=1') command=$(echo "$J" | grep -c 'FACTORY_DISPATCH=1 [^ ]*bin/factory ') unnamed=$(echo "$J" | grep -c 'deliberately does not name the marker') export=$(echo "$J" | grep -ci 'never export') rundirs=$(echo "$J" | grep -c 'worktrees/')")`
- THEN it prints exactly `first=1 command=1 unnamed=1 export=1 rundirs=1`

#### Scenario: README says the final verifier run is listed as in flight
- WHEN `(R=$(tr '\n' ' ' < README.md | tr -s ' '); echo "stale=$(echo "$R" | grep -o 'does not list it as in flight' | grep -c .) listed=$(echo "$R" | grep -o 'lists it as in flight' | grep -c .)")`
- THEN it prints exactly `stale=0 listed=1`

#### Scenario: README no longer says the factory's capabilities never entered the spec store
- WHEN `(echo "bullet=$(grep -c 'Current truth for the factory itself' README.md) stale=$(grep -c 'never entered it' README.md)")`
- THEN it prints exactly `bullet=1 stale=0`

#### Scenario: The guard change adds no whitespace errors
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

## Current truth: live-store-guard

# live-store-guard

## Requirements

### Requirement: Unmarked writes to a live store are refused while a role run is in flight there
While any run is in flight on an instance's own store, every `factory` command on that store except `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths` (and any command given `--accept-harness`) MUST be refused with exit 2, writing nothing to the store, the instance or the repository, unless its environment has `FACTORY_DISPATCH=1`; the refusal SHALL name a throwaway `FACTORY_STATE` and SHALL NOT name the marker.

#### Scenario: Unmarked writes from inside the target are refused while a run is in flight, init included
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0024-inflight.sh <<'EOF'
# Sourced from the repo root: a scratch target whose own store has one triage run in flight; the
# shell is left in a subdirectory of that target outside its store, as a role's shell may be.
# $S is the target's own store and $W the run's scratch directory inside it.
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory
git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1
S=$($B paths | tail -1 | sed -n 's/.*"state": "\([^"]*\)".*/\1/p')
printf '# F\n\nDo x.\n' > $T/req.md && printf '# G\n\nDo y.\n' > $T/req2.md && $B ticket new --file $T/req.md >/dev/null
R=$($B run start --role triage --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
W=$S/runs/$R/scratch
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

- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && rm -rf $T/tgt/.claude $S/openspec $S/decisions.md && S0=$(snap); $B init --repo-name x >/dev/null 2>&1; i=$?; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; $B ticket transition T-0001 --to closed --by t >/dev/null 2>&1; t=$?; $B decision add T-0001 x >/dev/null 2>&1; d=$?; echo "init=$i new=$n transition=$t decision=$d store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) agents=$([ -e $T/tgt/.claude ] && echo written || echo none)")`
- THEN it prints exactly `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`

#### Scenario: The refusal names the throwaway store and not the marker
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && E=$($B decision add T-0001 x 2>&1 >/dev/null); J=$($B decision add T-0001 x 2>/dev/null | tail -1); cd $W && E2=$(FACTORY_DISPATCH=1 $B decision add T-0001 x 2>&1 >/dev/null); echo "rule=$(echo "$E" | grep -c 'role runs may not write the live store') state=$(echo "$E" | grep -c FACTORY_STATE) marker=$(echo "$E$J$E2" | grep -c FACTORY_DISPATCH) json=$(echo "$J" | grep -c '"ok": false') inside=$(echo "$E2" | grep -c 'role runs may not write the live store')")`
- THEN it prints exactly `rule=1 state=1 marker=0 json=1 inside=1`

#### Scenario: A harness acceptance is refused while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && A=$(cat $T/tgt/.factory/harness.lock) && S0=$(snap); $B --accept-harness $A ticket show T-0001 >/dev/null 2>&1; echo "accept=$? store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `accept=2 store=unchanged`

### Requirement: Writes from inside a store's run directories or code checkouts are refused, marked or not
Every `factory` command on an instance's own store except the read-only list above MUST be refused with exit 2, writing nothing, when the caller's directory lies under that store's `runs/` or `worktrees/`, whether or not its environment has `FACTORY_DISPATCH=1` and whether or not any run is in flight.

#### Scenario: Marked writes from a run's scratch directory or a worktree directory are refused, init included
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && rm -rf $T/tgt/.claude $S/openspec $S/decisions.md && mkdir -p $S/worktrees/T-0001/sub && S0=$(snap); cd $W && FACTORY_DISPATCH=1 $B decision add T-0001 x >/dev/null 2>&1; d=$?; FACTORY_DISPATCH=1 $B init --repo-name x >/dev/null 2>&1; i=$?; cd $S/worktrees/T-0001/sub && FACTORY_DISPATCH=1 $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; echo "scratch_decision=$d scratch_init=$i worktree_new=$n store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) agents=$([ -e $T/tgt/.claude ] && echo written || echo none)")`
- THEN it prints exactly `scratch_decision=2 scratch_init=2 worktree_new=2 store=unchanged agents=none`

#### Scenario: Writes from a finished run's scratch directory are refused with no run in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && (cd $T/tgt && FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1) && S0=$(snap); cd $W && $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; FACTORY_DISPATCH=1 $B decision add T-0001 x >/dev/null 2>&1; d=$?; echo "idle=$($B ticket show T-0001 --json | tail -1 | grep -c '"in_flight": \[\]') new=$n decision=$d store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `idle=1 new=2 decision=2 store=unchanged`

### Requirement: Reads, marked commands from outside the store, throwaway stores and idle stores stay open
While a run is in flight on the live store, the read-only commands SHALL succeed from anywhere, a command with `FACTORY_DISPATCH=1` run from outside the store's `runs/` and `worktrees/` SHALL succeed as before, and a command on a throwaway store (`FACTORY_STATE` naming another store) SHALL NOT be fenced from any directory; with no run in flight, unmarked writes from outside those directories SHALL succeed as before.

#### Scenario: Read commands still answer while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && $B ticket show T-0001 >/dev/null 2>&1; s=$?; $B config >/dev/null 2>&1; c=$?; $B log tail >/dev/null 2>&1; l=$?; $B results show T-0001 >/dev/null 2>&1; r=$?; cd $W && $B ticket show T-0001 >/dev/null 2>&1; w=$?; echo "show=$s config=$c log=$l results=$r inside=$w")`
- THEN it prints exactly `show=0 config=0 log=0 results=0 inside=0`

#### Scenario: A marked write from the repository root still writes while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && cd $T/tgt && FACTORY_DISPATCH=1 $B decision add T-0001 "marked line" >/dev/null 2>&1; d=$?; FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1; f=$?; echo "decision=$d finish=$f cleared=$($B ticket show T-0001 --json | tail -1 | grep -c '"in_flight": \[\]')")`
- THEN it prints exactly `decision=0 finish=0 cleared=1`

#### Scenario: A throwaway store is not fenced, even from a run's scratch directory
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && (cd $T/tgt && FACTORY_STATE=$T/s $B init >/dev/null 2>&1); i=$?; cd $W && FACTORY_STATE=$T/s $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; echo "init=$i new=$n")`
- THEN it prints exactly `init=0 new=0`

#### Scenario: With no run in flight, unmarked commands write as before
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; $B decision add T-0001 "after the run" >/dev/null 2>&1; d=$?; echo "new=$n decision=$d")`
- THEN it prints exactly `new=0 decision=0`

### Requirement: The marker does not lift the harness lock
A command with `FACTORY_DISPATCH=1` on an instance's own store MUST still be refused by the harness lock's uncommitted-edit check, with exit 2 and nothing written, whether or not a run is in flight.

#### Scenario: A marked write from a harness checkout with an uncommitted edit is still refused
- WHEN `(T=$(mktemp -d) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $T/c/bin/factory init --repo-name demo >/dev/null 2>&1 && printf '# F\n\nDo x.\n' > $T/req.md && $T/c/bin/factory ticket new --file $T/req.md >/dev/null && $T/c/bin/factory run start --role triage --ticket T-0001 >/dev/null && echo '# uncommitted edit' >> $T/c/factory/status.py && S0=$(find $T/tgt/.factory -type f -exec cksum {} + | sort | cksum) && FACTORY_DISPATCH=1 $T/c/bin/factory decision add T-0001 x >/dev/null 2>$T/err; echo "exit=$? lock=$(head -1 $T/err | grep -c 'has uncommitted changes:$') store=$([ "$(find $T/tgt/.factory -type f -exec cksum {} + | sort | cksum)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `exit=2 lock=1 store=unchanged`

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
2026-10-04 T-0024 Instance B keeps the spec store that run-0196 created. Its tickets close by archive into current truth, and `decisions.md` keeps reaching the spec writer, critic and planner. The operator decided this in the first answer to this ticket, and it is already recorded in `decisions.md`. This is a standing decision. This ticket touches README, so it also corrects README's stale "never entered it" line, as that answer directs.
2026-10-04 T-0024 While a role run is in flight on a live store, the operator or a runner session writes it by putting `FACTORY_DISPATCH=1` in front of that one command. README documents this. The refusal text never names the marker. The operator decided this in the same answer, and it is already recorded in `decisions.md`. This is a standing decision for every runner session, including the Driver session that runs the Nanobot fork's instance (instance A).
2026-10-04 T-0024 A write is refused, marker or not and run in flight or not, when the caller's directory lies under the own store's `runs/` or `worktrees/`. The operator's gate review asked for this rule. Rejected: applying it only while a run is in flight, because a process a role left running in its run directory would then write freely once the store went idle. Rejected: letting the marker lift it, because the rule exists so that a copied or exported marker does not help from there. This is a standing decision: the operator and runner sessions run store writes from outside the store.
2026-10-04 T-0024 The location rule is checked first, then the marker, then the in-flight list.
2026-10-04 T-0024 The in-flight rule acts only on an instance's own store, and only while at least one run is in flight on any ticket of that store. Rejected: refusing every unmarked write at all times, as the requester proposed. The operator would then need the marker on every command and would export it in the shell, and every role run started from that shell would inherit it. The operator's decision on the marker assumes unmarked writes when nothing is in flight.
2026-10-04 T-0024 The in-flight rule checks every ticket's in-flight list, not only the calling ticket's. The tool cannot tell which run, if any, is calling.
2026-10-04 T-0024 The marker is the environment variable `FACTORY_DISPATCH=1`. Both workflow scripts put it in front of every clerk command. Rejected: the requester's exemption for "a human's `--by`". Human commands have no `--by`, and `ticket transition` requires one from everyone.
2026-10-04 T-0024 A write is every command except a fixed read-only list: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths`. Any command given `--accept-harness` is a write, because it rewrites the lock and logs. A new command is fenced until someone adds it to the list. Rejected: the requester's list of ten write commands. It misses writes such as `ticket set`, `ticket park`, `ticket head`, `ticket ready-implementers`, `ticket parent-check`, `run compose` and `spec add`.
2026-10-04 T-0024 The refusal exits 2 and writes nothing. Its text is `role runs may not write the live store (<detail>); use a throwaway FACTORY_STATE`. The detail is `<store>; in flight: <run ids>` for the in-flight rule and `<store>; called from inside its runs/` (or `worktrees/`) for the location rule. The advice is meant for a role. The operator learns the marker from README.
2026-10-04 T-0024 A run left in flight by a dead workflow keeps the in-flight rule up. The operator clears it with a marked `run finish <run> --status-override KILLED`, run from the repository root, and README says so. Rejected: a timeout that drops the fence by itself. A long run that is still working would lose the fence.
2026-10-04 T-0024 The fence guards against accidents, not against a determined agent. It is not a security boundary. A role working from outside the store that copies the marker from the workflow scripts or README still gets through. That is recorded under Risk rather than designed around. Isolating role runs at the operating-system level is issue #37.
2026-10-04 T-0024 The fence is checked before the harness lock, the check that each instance runs only the harness revision it has accepted. A fenced command is refused before it reaches the lock, so a fenced `--accept-harness` rewrites nothing. A marked command still meets the lock and its uncommitted-edit refusal unchanged, so the marker cannot be used to get past the lock. Rejected: checking the fence after the lock, because `--accept-harness` rewrites the lock inside that check, so a fenced acceptance would write before it was refused.
2026-10-04 T-0024 Part B (a preamble line) is cut. The incident came from the test suite, not from a command the role typed, so a preamble line would not have stopped it. The refusal text gives the same advice at the moment it matters.
2026-10-04 T-0024 Part C (the tripwire on the store root) is cut. Role runs legitimately write their own run directory in the store (`output.md`, `scratch/`). Clerk commands for other tickets' runs also write the store during a run. A comparison of the store root therefore cannot tell whose write it saw. The fence refuses the write before it happens.
2026-10-04 T-0022 Removing clearly redundant work (a step, run or check that cannot change any outcome) is pre-approved, provided every refusal the pipeline gives today still fires (operator, 2026-10-04: 'slashing clearly redundant work is always going to be OK, if we trust our process')
2026-10-04 T-0022 Under a sub-ticket's Tests to change, the planner may list tests an earlier sibling of the same parent added, with a harness check that each first appeared in a sibling's merge; pre-existing tests still need the approved spec (operator, #40)

## Critic findings on your previous version

## Spec critic review: T-0026 workflow view, round 1

Spot checks (all run from `~/dev/spec-factory` on `main` at `0b1abad`, under a throwaway HOME, fixtures under this run's scratch directory via `TMPDIR`):

- Cited paths and lines: `factory/workflows/intake.js` lines 54, 72, 91, 97, 112, 113, 117, 126, 128, 166 and `factory/workflows/build.js` lines 45, 63, 82, 88, 111, 112, 116, 126-128, 172, 176, 198, 200, 232, 240, 243, 260 all hold what the spec says they hold (clerk label `clerk: ${label}`, role labels, every `log()` call, the two `ticket show --json` calls that keep only `state`). `factory/cli.py:88` returns `"title"` in `ticket show --json`. `tests/factory/test_shepherd.py:9-11` says the workflow script cannot run under pytest. `tests/factory/fixtures/stubs/accept-approve` exists. `grep -c '^issue:'` over the 28 request files found none.
- Acceptance: I ran the GIVEN block and all eight NEW scenarios plus the REGRESSION scenario on this checkout. Every NEW scenario printed exactly the "fails today" text verification.md states (`triage run-0009-x: ACCEPT`; `roles=0 clerk=0 untitled=18`; `start=0 roles=0 sub_clerk=0 parent_clerk=0 untitled=31`; `transitions=0 bare=4`; `changes=0 bare=6`; and so on). The REGRESSION scenario printed the five checksums as written (`intake 1072986007 1493` … `build 3636463416 2810`).
- Short-title rule: I applied the Decisions rule as design.md A states it (`lastIndexOf(' ', 60)`, strip `[\s,;:·—-]+`, append `…`) to the five fixture titles. It produces the exact strings the THEN clauses expect, including the dropped trailing comma in "park reasons…".
- Counts: the expected `clerk=13 untitled=2` (intake) and `sub_clerk=19 parent_clerk=6 untitled=3` (build) agree with a hand count of the clerk calls on each path given design.md C's rule for which calls stay bare.

The scenarios would fail against a stub or a wrong fix: they pin exact label text, exact narrator lines, the order of the start line, per-ticket attribution on the build path, and byte-identical commands. The spec makes no hidden product choice: the GitHub-issue cut and the uniform clerk label are stated under Decisions with the alternative rejected. The protected path is declared under Risk and matches the request. Nothing conflicts with the open-ticket decisions in the log.

### Findings

[BLOCKING] 6 proposal.md, Evidence first paragraph; Decisions last bullet; Operator steps step 1
Problem: Two terms specific to this system reach the operator unglossed in a first paragraph: "current-truth `build-dispatch` scenarios" (Evidence) and "stub mode" / "stub-mode run" (Decisions and Operator steps), and no human-facing section glosses either earlier.
Evidence: Read Problem, Evidence, Open questions, Decisions and Operator steps as the gate reader; "current truth" and "stub" appear nowhere in Problem. The rubric names this case as blocking even when a careful reader could work it out.
Suggested fix: In Evidence write "the acceptance scenarios already in force for the build script, which drive it the same way" in place of the bare term, and at the first "stub mode" (Decisions) add "a run in which each role returns a fixture file instead of calling a model".

[SHOULD-FIX] 6 proposal.md, Operator steps step 1
Problem: The step says "run the intake workflow in stub mode on a throwaway store" but gives no way to do it; README's "Running one ticket" shows the Workflow call with `{ticket, repo, instance}` only, and `stubs` does not appear anywhere in README.md.
Evidence: `grep -n stubs README.md` prints nothing; the arg is documented only in the comment at `factory/workflows/intake.js:16`.
Suggested fix: Give the call form, e.g. "call the Workflow tool with the intake script and args `{ticket, repo: <runtime>, instance: <.factory>, state: <throwaway store>, stubs: tests/factory/fixtures/stubs/accept-approve, inlineRoles: true}`".

[SHOULD-FIX] 4 design.md, part E against part D
Problem: E says "Add no `await`", but D requires `transition()` to await the clerk reply before printing, so the two parts contradict each other as written.
Evidence: `transition()` today returns the clerk promise without awaiting (intake.js:119, build.js:118); D's print-on-`res.ok` needs that await, which changes no command order.
Suggested fix: Reword E to "Add no new clerk call, branch or reordering of calls, so the command order stays the same".

[NIT] 1 proposal.md, Decisions second bullet
Problem: "the last space at or before character 60" reads as 1-based (index 59), while design.md A and the expected THEN strings use index 60 (the 61st character).
Evidence: The "Isolate the store…" fixture cuts to 60 characters plus `…`; with a 1-based reading of "character 60" the rule would still land on the same space here, but it would not in general.
Suggested fix: Write "at or before the 61st character (index 60)" or restate the rule as "the first 60 characters, then back to the last space".

### Out-of-scope observations

- The "Only the two workflow scripts change" scenario passes trivially on `main`; the spec says so. It is a fence for the PR, not evidence of the change, and that is acceptable here.
- Operator step 2 (mobile-app narrator lines) cannot be checked from a shell; its placement under Operator steps is right.

STATUS: REVISE
CONFIDENCE: high, every cited line, every "fails today" output and the five REGRESSION checksums reproduced on this checkout; the one blocking item is a gloss, not a design defect
ESCALATIONS: none

## Your previous spec (v1)

=== proposal.md
## Problem

The operator cannot tell, at a glance, what task a factory run is working on. Every row in the run's live progress display names the work by a bare ticket id, such as `T-0018`, and the operator does not remember which id is which task. Each glance at the display, often on a phone, means looking the id up.

Some background on the parts involved. The factory moves each request through a chain of AI agents. Each request is a ticket with an id (`T-0026`) and a one-line title. A large ticket is split into sub-tickets (`T-0025.1`), each with its own title. Two scripts drive the agents: one takes a ticket from request to an approved spec, and one builds an approved ticket. Both run inside Claude Code's Workflow tool, whose progress display (in the terminal and in the mobile app) shows two kinds of text:

- an agent label: one row per agent the script starts. Besides the role agents (triage, spec writer, implementer and so on), the scripts start a small "clerk" agent for every read or write of the ticket store, the database of ticket records. So most rows are clerk rows.
- a narrator line: a free-text message the script prints above the rows.

Today the role rows read `triage T-0012`, the clerk rows read `clerk: run start triage` with no ticket at all, and the narrator lines name the ticket by bare id or not at all. Nothing on the display says what the task is.

This change adds a short version of the ticket's title beside every ticket id in both scripts. The short title is the title cut to at most 60 characters at a word boundary. It appears in four places: a narrator line when a run starts, giving the ticket, its short title and its state; a narrator line each time the ticket's state changes; every role row; and every clerk row. A sub-ticket's rows and lines carry the sub-ticket's own title. Only display text changes: the store commands the scripts send and the way they route on each agent's result stay exactly as they are.

## Evidence

I ran each workflow script on this checkout under node with a stub clerk that records every agent label, every narrator line and every store command. The stub is the same technique as the current-truth `build-dispatch` scenarios. The full fixture is the GIVEN block of the first scenario.

An intake run of a ticket titled "Workflow view shows a short task title beside every ticket id, in narrator lines and agent labels" printed these labels and lines (excerpt):

```
label: clerk: run start triage
label: triage T-0001
log: triage run-0009-x: ACCEPT
label: clerk: transition -> ready-for-spec-writer
...
log: critic run-0009-x: APPROVE
label: clerk: transition -> awaiting-spec-gate
log: T-0001: spec approved by critic in round 1; awaiting the human gate (bin/factory approve-spec T-0001)
```

No label or line carries the title. Of 18 labels, none carries it: `roles=0 clerk=0 untitled=18`. Three state changes produced no narrator line of their own: `transitions=0`. The first narrator line appears only after the first agent has finished.

A build run of a parent ticket with one sub-ticket printed 31 labels, none with a title (`untitled=31`). Its narrator lines name the sub-ticket in brackets after a run id, for example `log: implementer run-0009-x (T-0001.1): READY-FOR-REVIEW`. The transitions to `checks-in-flight`, `ready-for-merge` and `closed` produced no narrator line (`changes=0`).

Where the code builds this text:

- `factory/workflows/intake.js:54` and `factory/workflows/build.js:45` build every clerk label as `` `clerk: ${label}` ``.
- Role labels are `` `${role} ${TICKET}` `` and `` `${role} (stub) ${TICKET}` `` (intake.js:97 and :91), and `` `${role} ${ticket}` `` and `` `${role} (stub) ${ticket}` `` (build.js:88 and :82).
- The narrator lines are the `log()` calls at intake.js:72, 112, 113 and 166, and at build.js:63, 111, 112, 172, 176, 232, 240, 243 and 260. None names a title. The request said "the scripts never call `log()`". That is not so; the existing calls name only an id, which is the problem.
- The title is already in hand. Both scripts call `ticket show <id> --json` for the parent (intake.js:126, build.js:198), and build.js:126 makes the same call for each sub-ticket. The JSON carries `"title"` (`factory/cli.py:88`).

The request's GitHub-issue part has no reliable source:

- None of the 26 requests under `.factory/state/requests/` has an `issue:` header (`grep -c '^issue:'` found 0 files).
- `ticket show --json` does not return a request's header.
- Two request titles carry a `#NN`, and only one of them names the ticket's own issue. `T-0015`'s title says "(rescoped #20)", and `dev/issues.md` row 20 is that ticket's issue. `T-0020`'s title says "(split from #36)", but its issue is #38 (`dev/issues.md` row 38).

I applied a prototype of the proposed change to copies of both scripts in my scratch directory and ran every scenario below against the copies and against this checkout. Every NEW scenario printed its THEN on the copies and the "fails today" output on this checkout. The REGRESSION checksums matched on both. The current-truth `build-dispatch` scenarios printed the same output on the copies as on this checkout: the park reasons, the role starts, and `intake: sent unmarked=0`, `build: sent unmarked=0`. The prototype changed 28 lines in intake.js and 77 in build.js.

## Root cause

The two scripts were written to route tickets, and their display text was never designed for a reader. The clerk helper (`clerk()` in both scripts) receives only an action name, so its label cannot name a ticket. In build.js the helper is called for both the parent and its sub-tickets, so it cannot even tell which ticket an action is for. The scripts keep only the `state` field from the parent's `ticket show --json` reply. intake.js:128 and build.js:200 keep the state and drop the title, and `buildOne` (build.js:126-128) does the same for each sub-ticket. `transition()` (intake.js:117, build.js:116) returns the store's reply without printing anything, so no state change is narrated unless the caller happens to log.

## Out of scope

- The GitHub issue number on the start line is cut. No request carries one in a header, and a `#NN` in a title is not reliable. A request header surfaced through `ticket show --json` would be a store CLI change and can be filed on its own.
- The workflow card's name and description. They come from the fixed `meta` literal (intake.js:1-8, build.js:1-9), which the Workflow tool reads before the script runs.
- Every store command the scripts send, its order, and the routing on each STATUS, join decision and refusal. The REGRESSION scenario fixes them byte for byte.
- The store CLI (`factory/cli.py`), the prompts, the agent definitions and the test suite.
- `README.md`, `docs/design.md` and `docs/changelog.md`. The design doc does not describe labels or narrator lines. The README describes a behaviour only after it has run on a real ticket ("Maintaining this page"), and it does not quote label text today.

## Open questions

none

## Decisions

- The GitHub issue part is cut. Its sources are missing or wrong: no request has an `issue:` header, and one of the two `#NN` titles names another issue. Rejected: parsing `#NN` from the title, which would show #36 for a ticket whose issue is #38. Also rejected: adding the request header to `ticket show --json`, a store CLI change the operator's ask ("a 1-liner snippet besides just identifiers") does not need.
- The short title is the ticket title with whitespace runs collapsed to one space. A title of 60 characters or fewer is shown whole. A longer one is cut at the last space at or before character 60. Trailing spaces and `,` `;` `:` `·` `—` `-` are then dropped, and `…` is added. A title with no space in its first 60 characters is cut at 60. Rejected: a fixed cut mid-word, which leaves fragments such as "ticke…".
- A ticket's tag is `<id> · <short title>`, joined by a middle dot (U+00B7). It is the bare id when the title is not known yet or is empty.
- Every clerk row reads `clerk <tag>: <action>`. That includes the two calls made before the title is known (`config` and the parent's `ticket show`) and each sub-ticket's first `ticket show`; their tag is the bare id. Rejected: the triage note's assumption that those calls keep their current labels. A uniform form still tells the operator which ticket the run is for.
- A state-change line is printed by the transition helper, and only when the store accepted the transition. A refused transition is followed by the park line the script already prints.
- The existing narrator lines keep their wording. Each now begins with the tag of the ticket it is about, followed by `: `. build.js's ` (<sub-ticket>)` after a run id is dropped, because the tag now names it.
- Acceptance runs the scripts under node with a stub clerk, as the `build-dispatch` scenarios do. A stub-mode run inside the Workflow tool, which the request named, needs the Claude Code runtime and cannot be a shell command, so it is an Operator step.

## Risk

Blast radius: display text only. Labels and narrator lines never reach a shell or the store. A title containing quotes or backticks therefore cannot change a command. A REGRESSION scenario checks that every store command is byte-identical on five paths, including a park.

Protected path touched: `factory/workflows/intake.js` and `factory/workflows/build.js`, under the harness path `factory/**`. The request names both files as the change. No other protected path is touched.

The change reaches running tickets only when the operator moves the runtime, the pinned checkout of the harness that runs tickets, and accepts it with `--accept-harness`. Merging into `main` does not change the running code.

The Workflow tool resumes a run by replaying the longest unchanged prefix of its agent calls. I could not confirm whether a label is part of that match. If it is, a run started on the old scripts and resumed on the new ones replays nothing and starts live from its first call. That is safe, because both scripts start from the state the store holds.

Long labels may be cut off on a phone screen. The tag puts the id first and caps the title at 61 characters, so the id and the start of the title stay visible.

## Operator steps

1. After the runtime moves to a revision that contains this change, run the intake workflow in stub mode on a throwaway store with one of the existing fixtures, for example `tests/factory/fixtures/stubs/accept-approve`. Confirm the start line, at least one `→` state-change line and role and clerk rows that carry the short title.
2. On the next real run, open the run in the Claude Code mobile app. Confirm that narrator lines appear there. If they do not, the rows alone still carry the title, and a follow-up ticket should say so.

=== design.md
## Proposed change

Both scripts get the same small helper. The Workflow tool runs a script as one function body with no imports, so the helper is copied into each script, as `clerk()` already is.

A. Title helper (both scripts). Add, next to `stubCount`:
- `TITLES`, an object mapping a ticket id to its short title;
- `shortTitle(t)`, the rule in proposal.md Decisions: collapse whitespace, keep ≤ 60 whole, else cut at the last space at or before index 60 (`lastIndexOf(' ', 60)`; at 60 when there is none), strip trailing `[\s,;:·—-]+`, append `…` (U+2026);
- `tag(id)`, which returns `` `${id} · ${TITLES[id]}` `` (U+00B7) when `TITLES[id]` is non-empty, else `id`.

Fill `TITLES[TICKET] = shortTitle(show.title)` right after the parent's `ticket show --json` (intake.js:128, build.js:200). In build.js `buildOne`, set `TITLES[st] = shortTitle(show.title)` right after `if (!show.ok) return`.

B. Start line (both scripts). Right after A's parent fill, print `log(TITLES[TICKET] ? `${TICKET} · ${TITLES[TICKET]} · ${state}` : `${TICKET} · ${state}`)`. It must come before any phase starts, so that it is the first narrator line.

C. Labels.
- Role rows: `` `${role} ${tag(TICKET)}` `` and `` `${role} (stub) ${tag(TICKET)}` `` in intake.js. Use `tag(ticket)` in build.js.
- Clerk rows: the label becomes `` `clerk ${tag(ticket)}: ${label}` ``. In intake.js the ticket is always `TICKET`. In build.js, give `clerk()` a fourth parameter `ticket = TICKET`. Pass the sub-ticket (`ticket` in `runRole`, `park` and `transition`; `st` in `buildOne`) on every call that acts on one, including the stub-script call at build.js:102. Calls on the parent (`config`, `ticket show`, `ready-implementers`, `spec tasks`, `plan add`, `subticket add`, `parent-check`, `archive`) keep the default.
- Action text: drop the ticket id now carried by the tag: `park ${ticket}` → `park`, `run start ${role} ${ticket}` → `run start ${role}`, `ticket show ${st}` → `ticket show`, `ticket head ${st}` → `ticket head`, `results show ${st}` → `results show`, `join ${st}…` → `join…`, `merge ${st}` → `merge`. build.js's transition label `${ticket} -> ${to}` → `transition -> ${to}`, as intake.js has it. Every other action text stays as it is.

D. Narrator lines.
- `transition()` (both scripts) awaits the clerk reply. When `res.ok`, it prints `` `${tag(ticket)}: → ${to}` `` (U+2192; `TICKET` in intake.js), then returns the reply unchanged. Callers are not edited.
- Each existing `log()` call that names a ticket starts with `` `${tag(<that ticket>)}: ` `` and keeps the rest of its text:
  - park: `<tag>: parked: <reason>`;
  - a tripwire park: `<tag>: parked: <fin.parked>`;
  - a role's result: `<tag>: <role> <runId>: <status>` plus intake's escalation count, with build.js's ` (<ticket>)` dropped;
  - join: `<tag>: join: <decision> (<reason>)`;
  - merge: `<tag>: merged: <main_after>`;
  - spec approved, sub-tickets created, sub-tickets parked or waiting, resuming, and reuse lines: tagged with the parent.

E. Nothing else. Add no `await`, clerk call or branch, so the command order stays the same; the REGRESSION scenario checks it. Make no change to the CLI, prompts, agents, tests, README, design doc or changelog.

## Tests to change

none. No test under `tests/factory/` runs the workflow scripts or reads their labels. `tests/factory/test_shepherd.py:9-11` says they cannot run under pytest.

=== specs/workflow-view/spec.md
## ADDED Requirements

### Requirement: A run opens by naming its ticket
Each workflow script MUST print, as its first narrator line, the ticket id, its short title and its stored state, as `<id> · <short title> · <state>`, or `<id> · <state>` when the ticket has no title.

#### Scenario: The intake run opens with the ticket, its short title and its state
Run every command in this change from the repository root of the checkout under test, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the six fixture files written by the block below, run once at column 0 as shown (every later scenario of this change reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0026-view.mjs <<'EOF'
// node t0026-view.mjs <workflow.js> '<replies JSON>': runs one workflow script with a stub clerk, as
// t0023-wf.mjs does (same reply keys, list replies used in turn, last one repeats), and prints, in order,
// `log: <message>` for every narrator line, `label: <label>` for every agent call and `cmd: <command>`
// for every clerk command, verbatim.
import { readFileSync } from 'node:fs'
const [file, replies] = process.argv.slice(2)
const R = { 'config': { out: { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } },
  'run start': { out: { ok: true, run_id: 'run-0009-x', worktree: '/w' } }, ...JSON.parse(replies) }
const src = readFileSync(file, 'utf8').replace(/^export const meta/m, 'const meta')
const lines = []
const agent = async (prompt, opts) => {
  lines.push(`label: ${opts && opts.label}`)
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n'
  const cmd = m[1].replace(/^.*?bin\/factory /s, '')
  lines.push(`cmd: ${m[1]}`)
  const key = Object.keys(R).filter(k => cmd.startsWith(k)).sort((a, b) => b.length - a.length)[0]
  let r = key ? R[key] : { out: { ok: true } }
  if (Array.isArray(r)) r = r.length > 1 ? r.shift() : r[0]
  return { stdout: 'raw' in r ? r.raw : JSON.stringify(r.out), exit: r.exit || 0, stderr: '' }
}
const log = (msg) => lines.push(`log: ${msg}`)
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r', state: '/tmp/s' }, agent, log, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(lines.join('\n'))
EOF
cat > ${TMPDIR:-/tmp}/t0026-intake.json <<'EOF'
{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}, "title": "Workflow view shows a short task title beside every ticket id, in narrator lines and agent labels"}}, "run finish": [{"out": {"ok": true, "status": "ACCEPT"}}, {"out": {"ok": true, "status": "READY-FOR-CRITIC"}}, {"out": {"ok": true, "status": "APPROVE"}}], "ticket transition": {"out": {"ok": true, "round": {"spec": 1}}}}
EOF
cat > ${TMPDIR:-/tmp}/t0026-park.json <<'EOF'
{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}, "title": "Harness hygiene: ruling on a BLOCKED park, park reasons, run-record whitespace and more"}}, "run finish": {"out": {"ok": true, "status": "NEEDS-HUMAN"}}}
EOF
cat > ${TMPDIR:-/tmp}/t0026-short.json <<'EOF'
{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}, "title": "Fix the label"}}, "run finish": {"out": {"ok": true, "status": "REJECT"}}, "ticket transition": {"out": {"ok": true}}}
EOF
cat > ${TMPDIR:-/tmp}/t0026-notitle.json <<'EOF'
{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}}}, "run finish": {"out": {"ok": true, "status": "REJECT"}}, "ticket transition": {"out": {"ok": true}}}
EOF
cat > ${TMPDIR:-/tmp}/t0026-build.json <<'EOF'
{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned", "title": "Isolate the store from the integration branch: store commits move main and force catch-up runs"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": ["T-0001.1"], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": [], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "ready-for-implementer", "title": "init puts a new store on its factory-store branch"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "run finish": [{"out": {"ok": true, "status": "READY-FOR-REVIEW"}}, {"out": {"ok": true, "status": "APPROVE"}}, {"out": {"ok": true, "status": "VERIFIED"}}], "ticket join": {"out": {"ok": true, "decision": "merge", "reason": "all green"}}, "merge": {"out": {"ok": true, "main_after": "4f8f1d5"}}, "ticket parent-check": {"out": {"ok": true, "state": "ready-for-parent-verify", "reuse": "run-0001-verifier"}}, "archive": {"out": {"ok": true, "archived_to": "x"}}}
EOF
```

- WHEN `(node ${TMPDIR:-/tmp}/t0026-view.mjs factory/workflows/intake.js "$(cat ${TMPDIR:-/tmp}/t0026-intake.json)" | sed -n 's/^log: //p' | head -1)`
- THEN it prints exactly `T-0001 · Workflow view shows a short task title beside every ticket… · ready-for-triage`

#### Scenario: A ticket with no title opens with its bare id and keeps bare-id labels
Needs the GIVEN block of "The intake run opens with the ticket, its short title and its state" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0026-view.mjs factory/workflows/intake.js "$(cat ${TMPDIR:-/tmp}/t0026-notitle.json)" | grep -e '^log: ' -e '^label: triage')`
- THEN it prints exactly `log: T-0001 · ready-for-triage`, `label: triage T-0001`, `log: T-0001: triage run-0009-x: REJECT`, `log: T-0001: → closed`, one per line

### Requirement: The short title is the title cut at a word boundary
The short title MUST be the whole title when it has 60 characters or fewer; a longer title SHALL be cut at the last space at or before character 60, with trailing punctuation dropped and `…` appended.

#### Scenario: A long title is cut at a word boundary and loses its trailing comma
Needs the GIVEN block of "The intake run opens with the ticket, its short title and its state" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0026-view.mjs factory/workflows/intake.js "$(cat ${TMPDIR:-/tmp}/t0026-park.json)" | sed -n 's/^log: //p')`
- THEN it prints exactly `T-0001 · Harness hygiene: ruling on a BLOCKED park, park reasons… · ready-for-triage`, then `T-0001 · Harness hygiene: ruling on a BLOCKED park, park reasons…: triage run-0009-x: NEEDS-HUMAN`, then `T-0001 · Harness hygiene: ruling on a BLOCKED park, park reasons…: parked: NEEDS-HUMAN from triage`

#### Scenario: A short title is shown whole
Needs the GIVEN block of "The intake run opens with the ticket, its short title and its state" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0026-view.mjs factory/workflows/intake.js "$(cat ${TMPDIR:-/tmp}/t0026-short.json)" | sed -n 's/^log: //p')`
- THEN it prints exactly `T-0001 · Fix the label · ready-for-triage`, then `T-0001 · Fix the label: triage run-0009-x: REJECT`, then `T-0001 · Fix the label: → closed`

### Requirement: Every agent row names its ticket and short title
Once a ticket's title has been read, every role label and every clerk label MUST carry `<id> · <short title>` of the ticket that agent works on, a sub-ticket's own title for a sub-ticket; clerk labels SHALL read `clerk <id>[ · <short title>]: <action>`.

#### Scenario: Every intake row after the ticket is read carries its short title
Needs the GIVEN block of "The intake run opens with the ticket, its short title and its state" run once.
- WHEN `(O=$(node ${TMPDIR:-/tmp}/t0026-view.mjs factory/workflows/intake.js "$(cat ${TMPDIR:-/tmp}/t0026-intake.json)"); T='T-0001 · Workflow view shows a short task title beside every ticket…'; echo "roles=$(echo "$O" | grep -cxF -e "label: triage $T" -e "label: spec_writer $T" -e "label: critic $T") clerk=$(echo "$O" | grep -cF "label: clerk $T: ") untitled=$(echo "$O" | grep '^label: ' | grep -vc ' · ')")`
- THEN it prints exactly `roles=3 clerk=13 untitled=2`

#### Scenario: Build rows carry the sub-ticket's own title, and the parent's rows the parent's
Needs the GIVEN block of "The intake run opens with the ticket, its short title and its state" run once.
- WHEN `(O=$(node ${TMPDIR:-/tmp}/t0026-view.mjs factory/workflows/build.js "$(cat ${TMPDIR:-/tmp}/t0026-build.json)"); P='T-0001 · Isolate the store from the integration branch: store commits…'; C='T-0001.1 · init puts a new store on its factory-store branch'; echo "start=$(echo "$O" | sed -n 's/^log: //p' | head -1 | grep -cxF "$P · planned") roles=$(echo "$O" | grep -cxF -e "label: implementer $C" -e "label: reviewer $C" -e "label: verifier $C") sub_clerk=$(echo "$O" | grep -cF "label: clerk $C: ") parent_clerk=$(echo "$O" | grep -cF "label: clerk $P: ") untitled=$(echo "$O" | grep '^label: ' | grep -vc ' · ')")`
- THEN it prints exactly `start=1 roles=3 sub_clerk=19 parent_clerk=6 untitled=3`

### Requirement: Every narrator line names its ticket, and every state change is narrated
Every narrator line after the start line MUST begin with `<id>[ · <short title>]: ` for the ticket it is about, and each transition the store accepts SHALL print `<id>[ · <short title>]: → <state>`.

#### Scenario: Each intake state change gets a narrator line
Needs the GIVEN block of "The intake run opens with the ticket, its short title and its state" run once.
- WHEN `(O=$(node ${TMPDIR:-/tmp}/t0026-view.mjs factory/workflows/intake.js "$(cat ${TMPDIR:-/tmp}/t0026-intake.json)"); T='T-0001 · Workflow view shows a short task title beside every ticket…'; echo "transitions=$(echo "$O" | grep -cxF -e "log: $T: → ready-for-spec-writer" -e "log: $T: → ready-for-critic" -e "log: $T: → awaiting-spec-gate") bare=$(echo "$O" | grep '^log: ' | grep -vc "^log: $T")")`
- THEN it prints exactly `transitions=3 bare=0`

#### Scenario: Build state changes and the merge are narrated under the right ticket
Needs the GIVEN block of "The intake run opens with the ticket, its short title and its state" run once.
- WHEN `(O=$(node ${TMPDIR:-/tmp}/t0026-view.mjs factory/workflows/build.js "$(cat ${TMPDIR:-/tmp}/t0026-build.json)"); P='T-0001 · Isolate the store from the integration branch: store commits…'; C='T-0001.1 · init puts a new store on its factory-store branch'; echo "changes=$(echo "$O" | grep -cxF -e "log: $C: → checks-in-flight" -e "log: $C: → ready-for-merge" -e "log: $C: merged: 4f8f1d5" -e "log: $P: → closed") bare=$(echo "$O" | grep '^log: ' | grep -vc -e "^log: $P" -e "^log: $C")")`
- THEN it prints exactly `changes=4 bare=0`

### Requirement: Store commands and routing are unchanged
The store commands both scripts send, and their order, MUST stay byte-identical; only label and narrator text SHALL change, and among harness and document paths only the two workflow scripts SHALL change.

#### Scenario: The clerk commands are byte-identical on five paths
Needs the GIVEN block of "The intake run opens with the ticket, its short title and its state" run once.
- WHEN `(for w in intake:intake intake:park intake:short intake:notitle build:build; do echo "${w#*:} $(node ${TMPDIR:-/tmp}/t0026-view.mjs factory/workflows/${w%%:*}.js "$(cat ${TMPDIR:-/tmp}/t0026-${w#*:}.json)" | grep '^cmd: ' | cksum)"; done)`
- THEN it prints exactly `intake 1072986007 1493`, `park 536447330 571`, `short 24042256 547`, `notitle 24042256 547`, `build 3636463416 2810`, one per line

#### Scenario: Only the two workflow scripts change
- WHEN `(git diff --name-only main...HEAD -- factory bin agents tests docs dev README.md pyproject.toml uv.lock)`
- THEN it prints exactly `factory/workflows/build.js`, then `factory/workflows/intake.js`

=== verification.md
## Acceptance

- The intake run opens with the ticket, its short title and its state → NEW; today it prints `triage run-0009-x: ACCEPT`, because the first narrator line comes after triage and carries no title.
- A ticket with no title opens with its bare id and keeps bare-id labels → NEW; today it prints `label: triage T-0001`, then `log: triage run-0009-x: REJECT`, with no start line and no `→ closed` line.
- A long title is cut at a word boundary and loses its trailing comma → NEW; today it prints `triage run-0009-x: NEEDS-HUMAN`, then `T-0001 parked: NEEDS-HUMAN from triage`.
- A short title is shown whole → NEW; today it prints only `triage run-0009-x: REJECT`.
- Every intake row after the ticket is read carries its short title → NEW; today it prints `roles=0 clerk=0 untitled=18`.
- Build rows carry the sub-ticket's own title, and the parent's rows the parent's → NEW; today it prints `start=0 roles=0 sub_clerk=0 parent_clerk=0 untitled=31`.
- Each intake state change gets a narrator line → NEW; today it prints `transitions=0 bare=4`.
- Build state changes and the merge are narrated under the right ticket → NEW; today it prints `changes=0 bare=6`.
- The clerk commands are byte-identical on five paths → REGRESSION; prints the same five lines on this checkout (verified 2026-10-04) and must after the change.
- Only the two workflow scripts change → NEW; today it prints nothing, because `main...HEAD` is empty on `main`. On the PR it fences the change to the two scripts: no CLI, test, prompt or document change.

Not restated here: the current-truth `build-dispatch` scenarios (park reasons, checker selection, the dispatcher marker) keep applying unchanged. I ran them against a prototype of this change, and they printed the same output as on this checkout.
