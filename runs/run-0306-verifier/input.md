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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0306-verifier/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0306-verifier/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0306-verifier/wt` (branch `factory/T-0032.1`, base `97becfdf573248116c7933347224765c8a2ede83`, head `c01e7c2cf8bdef4f73fd8443744906b9ea89db74`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0032.1

T-0032.1 / A role that ends its turn while its own background commands are still running returns no output, and the harness records it as a budget kill and parks the ticket
Depends on: none
Parallel-safe: yes

Parent: T-0032, approved spec v1. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows
- One empty reviewer run followed by a real one routes on the real one
- An implementer that returns nothing twice parks as EMPTY-OUTPUT
- An intake role's second empty output in a row parks as EMPTY-OUTPUT
- A reviewer that writes its output runs once
- Every preamble copy carries the wait rule and the copies stay identical
- Implementer, reviewer and verifier run prompts carry the wait rule, and only the reviewer's carries the judge-the-diff rule
- Every reviewer copy carries the rule, keeps every existing line, and the verifier prompt is unchanged
- The reviewer's input no longer hands it the gate commands, and the implementer's and verifier's still do
- The design doc states the EMPTY-OUTPUT rule, its rows and its park
- The build spec describes EMPTY-OUTPUT and no longer a KILLED condition
- README drops the budget park and describes the empty-output retry
- The changelog records issue 41 without a numbering gap
- The empty-output change adds no whitespace errors
Tests to change: the parent's list.
Protected paths: the parent's Risk list.

## Parent spec (v1, pinned)

=== proposal.md
## Problem

A finished change can be parked for a human because its code reviewer stopped early, and the record wrongly says the reviewer ran out of budget. The operator is the one affected: each time, they have to re-run a review by hand on a commit that the other checker has already passed.

Some background. The factory runs each role as an AI agent in a workflow script. A role here is one step of the pipeline: triage, spec writer, implementer, code reviewer, verifier and so on. The harness is the code that starts the runs and routes their results. A role's final message ends its run. The harness then reads the output file the role was told to write. The code reviewer judges a change's diff. The verifier, which runs at the same time on the same commit, runs the acceptance checks and the gate, meaning the test suite and the other checks a change must pass before it merges.

Three times on 2026-10-04, a code reviewer started the full test suite in the background and then ended its turn, saying it would write the review when the suite finished. Ending the turn ended the run, so no review was ever written. The harness has one rule for a run that leaves no output: it records the run as `KILLED` and parks the ticket as a "budget kill", a run stopped for going over its time or token budget. Parking stops the ticket until a human acts. That label is false. The harness enforces no budget, and the agent call does not report why a run stopped. Each time, the verifier had already passed the same commit.

The operator chose a three-part fix and made it standing policy:
- every role is told to run its commands in the foreground and never to end its turn while one is still running;
- the code reviewer reads the diff and leaves the suite and the gate to the verifier;
- a run that leaves no output is recorded as `EMPTY-OUTPUT`, together with the agent's last message, and never as a budget kill. The same role runs once more on its own; a second empty output in a row parks the ticket as before.

## Evidence

**The incidents.** The table lists every reviewer run in this repo's store that left no output file. The last message is what the workflow's agent call returned, as kept in the workflow journals under `~/.claude/projects/-Users-dphang-dev-nanobot/c69bfd1d-97a6-43e3-9d5a-a517c28d382c/subagents/workflows/`.

| Run | Sub-ticket | Wall time | Last message returned | Verifier on the same commit |
|---|---|---|---|---|
| run-0209-reviewer | T-0023.3 | 288 s | "Both suite runs are still in progress; I'll write the review once the monitor reports their final lines." (`wf_f15c105e-ca0/journal.jsonl:146`) | VERIFIED |
| run-0288-reviewer | T-0029.1 | 122 s | "Nothing else is outstanding; waiting on the gate result before writing the review." (`wf_06e3790e-c18/journal.jsonl:50`) | run-0287, VERIFIED |
| run-0290-reviewer | T-0029.1 (the hand re-dispatch of run-0288) | 119 s | "The suite run takes about six minutes. While it finishes, the only remaining input is its result; everything else for the review is in hand." (`wf_686fdf22-2f3/journal.jsonl`) | run-0287, VERIFIED |
| run-0074-reviewer, run-0076-reviewer | T-0012.5, T-0012.4 (2026-10-03) | 116 s, 19 s | none kept: the workflow took its empty-return path (clerk label `run finish reviewer (killed)` in `wf_528ea336-e9a/journal.jsonl`) | not checked |

Each run's `meta.yaml` says `status: KILLED`, and each has no `output.md`. The store log records `run.killed`, then `result.recorded … "status": "KILLED"` (for example `log/2026-10.jsonl:1059-1060` for run-0209). What the third row shows: run-0290 was a hand re-dispatch of run-0288 on the same inputs, and it ended the same way. A retry alone would not have saved that ticket. The two prompt changes address the cause.

**Which code path labelled them.** The triage pointed at `factory/workflows/build.js:109`. That line marks a run killed only when the agent call returns nothing. The three 2026-10-04 runs returned text, so the workflow called a plain `run finish` (journal label `clerk: run finish reviewer`, with no "(killed)"). Then `factory/cli.py:329-330` turned the missing `output.md` into `KILLED`. `build.js:169` recorded a `KILLED` result row, and `factory/cli.py:634-636` parked the sub-ticket as `budget kill: reviewer`. The two 2026-10-03 runs went through `build.js:109-111` instead. Both paths produce the same label. `build.js:137` parks an implementer `KILLED` as `budget kill: implementer`. In `factory/workflows/intake.js:106-109`, a `KILLED` triage, spec writer or critic run falls through to `harness-bug: unknown STATUS KILLED`.

**What the agent call can report.** Per the Workflow script reference (the `workflow-authoring` skill), `agent()` returns the agent's final text. It returns `null` when the user skips the agent or the agent dies on a terminal API error. It throws once the turn's token ceiling is spent. Nothing else says why a run stopped. A thrown call already parks the ticket as `agent call failed: <role>: <error>` (`build.js:95-102`). The harness enforces no time or token budget of its own: `grep -rn "time_budget\|budget_usd" factory/*.py` prints nothing. So every empty output that reaches `run finish` gets the `EMPTY-OUTPUT` label, as the operator's answer requires for this case.

**Today's behaviour, reproduced.** The fixture in the first scenario of this change runs `build.js` on a scratch store, with real store commands. The reviewer returns run-0209's last message and writes no file, and the verifier writes VERIFIED. On this checkout it prints:
```
park T-0001.1: budget kill: reviewer
reviewer: KILLED
verifier: VERIFIED
kept=0 "rows": {"ci": "PASS", "verifier": "VERIFIED", "reviewer": "KILLED"}
```
This is the incident: one reviewer run, a `KILLED` row beside the verifier's passing rows, a budget-kill park, and no last message kept (`kept=0`). An implementer whose agent call returns empty text parks as `budget kill: implementer` after one run (the third scenario prints `implementer: KILLED`).

**The reviewer is told to run the gate.** `factory/compose.py:175-179` gives the implementer, the reviewer and the verifier the same "Where you work" paragraph: "Gate commands (run each from your worktree, exactly as written; each is already wrapped): …". The design's routing table gives `{gate commands}` to the verifier only (`docs/design.md:126`, Implementer READY-FOR-REVIEW row). The reviewer prompt says nothing about what to run. Of the 38 reviewer outputs in this store, 36 mention `pytest` or `tests/factory`. (`ls -d .factory/store/runs/*-reviewer` lists 43 runs, and 5 have no output.)

**What the design says now.** `docs/design.md:99` lists "a budget kill (piece 3)" among the reasons a ticket parks. `docs/design.md:106` says "A budget-killed run re-dispatches the same role on the same inputs, same round … or the ticket closes". The routing table has no row for an empty output.

**A prototype of this change works.** A prototype in this run's scratch directory (`scratch/proto`, branch `proto`: 9 files, 91 lines added and 13 removed, before the document edits) passes every NEW scenario below and fails none of the existing ones. The full harness suite passed on it: `310 passed in 153.04s`. These existing current-truth scenarios also still print what they say on it: "A redispatched sub-ticket runs only the checker whose row was set aside", "The build parks the blocked sub-ticket with the harness's reason, and a ruling sends it back", and "All three run prompts keep the undeclared-path rule and the reviewer keeps check 6".

## Root cause

- `factory/cli.py:329-330` (`run_finish`): a run with no output, or an empty one, and no `--status-override` is given status `KILLED`.
- `factory/workflows/build.js:109-111` and `factory/workflows/intake.js:106-109` (`runRole`): an agent call that returns `null` or blank text is finished with `--status-override KILLED`.
- `factory/cli.py:634-636` (`ticket_join`): any `KILLED` checker row parks the sub-ticket as `budget kill: <role>`. `build.js:137` does the same for an implementer.
- The `runRole` function in both workflows has no retry. Neither workflow keeps the agent's last message anywhere.
- `factory/prompts/preamble.md` (the shared rules every role reads first) says nothing about background commands or ending the turn.
- `factory/compose.py:175-179` gives the reviewer the gate commands. `factory/prompts/reviewer.md` does not say that the verifier runs them.

## Out of scope

- The join's `budget kill: <role>` reason for a `KILLED` row, and `results record --killed`. They stay for a row a human records by hand. After this change the workflows no longer write one.
- `run finish --status-override KILLED` stays unchanged. README tells the operator to use it to clear a run left in flight.
- A thrown agent call keeps its `KILLED` record and its `agent call failed: <role>: <error>` park, with no re-dispatch.
- Treating the agent's returned text as the output when the role wrote no output file.
- A `resolve` verb for an `EMPTY-OUTPUT` park outside the checks: the implementer, triage, spec writer, critic, planner and parent-close verifier. Each is recovered by hand, as its `KILLED` park is today.
- Enforcing a time or token budget.
- The verifier prompt and the verifier's gate step stay unchanged. So do the implementer's gate commands.
- `agents/` templates. There is no reviewer template, and the preamble is not copied into any template (`grep -c "RUNNING CODE" agents/*.md` prints 0 for each).
- Observed, not changed:
  - The suite's Python stand-in for the build loop (`tests/factory/test_shepherd.py`, which `tests/factory/test_killed_checker.py` uses) still models the old killed path. Those tests still pass, because the CLI behaviour they drive is unchanged.
  - The comment in the current-truth fixture `t0022-build.mjs` (capability build-dispatch) says an empty role output "the workflow records as a killed run". After this change, that run is recorded as `EMPTY-OUTPUT`.

## Open questions

none

## Decisions

- An empty output is `EMPTY-OUTPUT`, never a budget kill. That covers a missing or empty output file, an agent call that returns blank text, and one that returns `null` (a user skip or a terminal API error). Rejected: keeping a budget-kill path for some of these. The harness enforces no budget, and the agent call reports no reason (Evidence).
- Standing, from the operator's answer, already in `decisions.md` as the 2026-10-04 T-0032 line, for both parts: the empty-output route, and the reviewer leaving the suite and the gate to the verifier. Later changes follow both.
- `EMPTY-OUTPUT` is decided in one place, `run finish`. The workflows no longer send `--status-override KILLED` for an empty return, so `run finish` reads the output file for every run. Rejected: a second override value in the scripts. It would label a run empty even when its output file was written.
- The retry is counted inside one workflow run: one re-dispatch, then a park. Rejected: a counter in the store. It would add a ticket field for a case that a human already watches, because a workflow that stops is restarted by hand.
- A thrown agent call is not re-dispatched. It carries its own error text, including the error thrown when the turn's token ceiling is spent, so it is the one stop the harness can name.
- The last message is kept by a new command, `factory run last-message RUN --text=…`, called only after `run finish` has returned `EMPTY-OUTPUT`. The text is the last 4000 characters, as one shell single-quoted word. Rejected: passing it on every `run finish`, which would put each role's whole output through every clerk command.
- A second empty output parks as `EMPTY-OUTPUT from <role>`, in the same form as the other role parks, and lists both runs. The last messages stay in the run directories, not in the reason.
- A checker's second empty output parks before any result row is recorded for it. `resolve --redispatch` then re-runs only that checker, because the other checker's passing rows stand. Rejected: an `EMPTY-OUTPUT` result row and a join rule for it, a new row status for the same outcome.
- The reviewer's input no longer lists the gate commands. It says that the verifier runs them, as the design's routing table already declares (`docs/design.md:126`).
- The `budget kill` join reason is kept for hand-recorded `KILLED` rows. Rejected: renaming it, which would change three existing tests for a case no one reported.
- `build.js:137` (the implementer's `budget kill` park) is removed. `run finish` can no longer return `KILLED` to the workflow, so the line would never run.

## Risk

The change touches every role run, in three ways. Every system prompt gains one preamble bullet. Every run that leaves no output takes a new route in both workflows. The reviewer's prompt and input change. A wrong retry could run a role twice when once was meant, or park a run that did produce output. The scenarios check both cases. Nothing changes in a running instance until its operator upgrades the runtime and accepts the new harness revision.

Protected paths this change touches:
- harness: `factory/cli.py`, `factory/compose.py`, `factory/workflows/build.js`, `factory/workflows/intake.js`, `factory/prompts/preamble.md`, `factory/prompts/reviewer.md`;
- generated: `docs/prompts/00-preamble.md` and `docs/prompts/06-code-reviewer.md`, each re-copied from its `docs/design.md` block.

New test file: `tests/factory/test_empty_output.py`. It is not a protected path.

Overlap: T-0030 (approved, waiting for its planner) changes per-role agent definitions and role inputs, the reviewer's included. Both changes may edit `factory/prompts/reviewer.md`, the `docs/design.md` §6 block and `factory/compose.py`. The planner should order the two or note the overlap.

## Operator steps

- After merge, upgrade the runtime and accept the new harness revision in each instance. On the next build, check that the reviewer runs no full suite, and that any empty output appears as `EMPTY-OUTPUT` with a `last-message.md` in its run directory.

=== design.md
## Proposed change

**A. Preamble: wait for your own commands.** Insert this bullet in the RUNNING CODE section, right after the bullet that ends "check command your briefing, ticket or spec gives you.". Make the same edit in all three copies: the `docs/design.md` §Shared preamble block (line 218), `docs/prompts/00-preamble.md` (line 44) and `factory/prompts/preamble.md` (line 44). All three stay byte-identical.
```
- Run every command in the foreground and wait for it to finish.
  Never end your turn while a command you started is still running:
  your final message ends your run, and an output you have not yet
  written is lost.
```

**B. Code reviewer: judge the diff.**
1. Insert this section between "beyond the PR description." and "CHECK, IN THIS ORDER", with one blank line before and after. Make the edit in the `docs/design.md` §6 block (line 611), `docs/prompts/06-code-reviewer.md` (line 4) and `factory/prompts/reviewer.md` (line 4). Change no existing line. The run copy keeps its one fill, "After round 2".
```
WHAT YOU RUN
- Judge the diff by reading it. Do not run the test suite or the gate
  commands: the verifier runs them on the same head.
- You may run a narrow command to confirm a specific finding, such as
  one test or a grep, and cite its output with that finding.
```
2. In `factory/compose.py` (`compose`, the "Where you work" paragraph, lines 175-179), the reviewer's paragraph keeps the worktree, branch, base and head sentence and the no-remote sentence. Its gate-commands sentence is replaced with `The verifier runs the gate commands on this head; you do not run them.` The implementer's and the verifier's paragraphs stay unchanged.

**C. Harness: empty output.**
1. `factory/cli.py` `run_finish`: a run with no `output.md`, or a blank one, and no `--status-override` gets status `EMPTY-OUTPUT` (today `KILLED`), with the error "empty output". It is logged as `run.finished`. An override is unchanged: `--status-override KILLED` still records `KILLED` and logs `run.killed`.
2. New command `factory run last-message RUN --text=TEXT`. When the run's `meta.yaml` status is `EMPTY-OUTPUT`, it writes `runs/<RUN>/last-message.md` (TEXT plus one newline) and prints `{"ok": true, "run_id": …, "last_message": "runs/<RUN>/last-message.md"}`. Otherwise it refuses with exit 2 and writes nothing. It is not on the read-only list, so the live-store guard treats it as a write.
3. Make the same change to `runRole` in `factory/workflows/build.js` and in `factory/workflows/intake.js`:
   - Rename today's body to `runOnce`, with the same arguments and the same returns.
   - In `runOnce`, delete the `killed` condition and always call `run finish <run>` with no override. Keep `run cleanup` for a reviewer or verifier.
   - When `run finish` succeeds with status `EMPTY-OUTPUT` and the agent returned non-blank text, the clerk runs `run last-message <run> '--text=<text>'`. The text is the last 4000 characters of the trimmed returned text. It is shell single-quoted, with each `'` written as `'\''`. A failure of this call is ignored: it never parks and never changes the route.
   - The new `runRole` calls `runOnce`. If the result is `EMPTY-OUTPUT`, it logs the fact and calls `runOnce` once more, on the same role and ticket. If that result is also `EMPTY-OUTPUT`, it parks the ticket with the reason `EMPTY-OUTPUT from <role>` and both run ids as outputs, and returns `null`. Every other result is returned as today.
   - The thrown-call path (`catch`) stays as it is.
   - In `build.js`, delete line 137, the `budget kill: implementer` park.
4. New suite test file `tests/factory/test_empty_output.py`. It checks the CLI half on a throwaway store:
   - `run finish` with no output gives `EMPTY-OUTPUT` in its JSON and in `meta.yaml`;
   - `--status-override KILLED` still gives `KILLED`;
   - `run last-message` writes the file for an `EMPTY-OUTPUT` run;
   - `run last-message` refuses with exit 2, and writes nothing, for a run that finished with an output.

   The workflow halves are checked by the node scenarios, as decided for T-0023: the suite does not need node.

**D. Documents.**
1. `docs/design.md`, §Routing table, "Rules the table relies on":
   - In the bullet that starts "A non-empty ESCALATIONS line" (line 99), add "a second EMPTY-OUTPUT in a row" after "a budget kill (piece 3)" in the list of park reasons.
   - Add a new bullet right after that one: `- A role run that ends without writing its output is EMPTY-OUTPUT, whatever stopped it. The agent call reports no reason, so an empty output is never recorded as a budget kill; the harness keeps the agent's last message with the run. The same role is re-dispatched once, on the same inputs and in the same round. A second EMPTY-OUTPUT in a row parks the ticket with both runs.`
   - In the resolution bullet at line 106, change "A budget-killed run re-dispatches" to "A budget-killed run, or a ticket parked on a second EMPTY-OUTPUT, re-dispatches".
   - Add two table rows after the `| Verifier | SPEC-DEFECT |` row (line 132): `| Any role | EMPTY-OUTPUT, the first in a row | The same role again, same round | The same inputs |` and `| Any role | EMPTY-OUTPUT, the second in a row | Human queue | Both runs' last messages |`.

   The preamble (A) and reviewer (B.1) blocks change as given above.
2. `dev/build-harness.spec.md`:
   - In "Common step `runRole`" (line 275), replace the KILLED condition with: one `run finish RUN`; `EMPTY-OUTPUT` → `run last-message` with the returned text, then one re-dispatch; a second `EMPTY-OUTPUT` → park `EMPTY-OUTPUT from <role>`. Change "the KILLED seam" to "the EMPTY-OUTPUT seam".
   - Rewrite I.5 (line 300) to say the same, and to say that no budget is enforced or reported, so no empty output is a budget kill.
   - Rewrite item 49 (line 410) as the case where the reviewer is empty twice → `EMPTY-OUTPUT from reviewer`, followed by `--redispatch`.
   - Add `factory run last-message RUN --text=T` beside `run finish` (line 205), and say that an empty or missing output is `EMPTY-OUTPUT` there.
   - After this, no line may contain "KILLED condition" or "KILLED seam".
3. `README.md`:
   - Line 107: replace "or a run exceeding its budget" with "or a role that ended without output twice in a row (the first time, the harness runs it once more on the same inputs and keeps its last message)".
   - Line 149, the diagram edge label: change "over budget" to "no output twice".
   - Unstick row (line 437): extend the `--redispatch` gloss to "re-run the checks on the same commit after an outside fix, or after a checker ended without output twice".
   - Add a Built bullet after "Sibling tests check" (line 477). It starts `- **Empty output.**` and says three things in plain words: a run that ends without its output file is re-run once and then parks; the reviewer leaves the suite to the verifier; every role is told to wait for its commands. It ends "It is tested, and has not yet fired on a real ticket."
   - Bump the status date.
4. `docs/changelog.md`: one new last entry, numbered without a gap, starting `After issue #41 (2026-10-04),`. It names `EMPTY-OUTPUT`, the foreground rule, the kept last message, "re-dispatched once", and the reviewer leaving the gate commands to the verifier.

Size: the prototype's code and prompt edits are 104 changed lines. With D and the new test file, the total is about 200.

## Tests to change

none. The full suite passed on the prototype (`310 passed`). The existing tests that pin `KILLED` either use `--status-override KILLED` or record a `KILLED` row by hand, and both stay unchanged.

=== specs/build-dispatch/spec.md
## ADDED Requirements

### Requirement: A role run that leaves no output is re-dispatched once, then parks as EMPTY-OUTPUT
When a role run ends without an output file, or with a blank one, whatever the agent call returned, `run finish` MUST record it as `EMPTY-OUTPUT` and never as `KILLED`. The workflow MUST keep the agent's non-blank last message as that run's `last-message.md` and re-dispatch the same role once. A second `EMPTY-OUTPUT` in a row SHALL park the ticket as `EMPTY-OUTPUT from <role>`, with no result row for that run.

#### Scenario: A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell. This scenario needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- GIVEN the two fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0032-checks.sh <<'EOF'
# Sourced from the repo root after t0023-parent.sh: T-0001 is planned as one sub-ticket, T-0001.1,
# whose branch factory/T-0001.1 holds one commit; T-0001.1 is at checks-in-flight on that head $H,
# with no result rows, so the build runs both checkers on it.
printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md
bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null
bin/factory ticket transition T-0001 --to planned --by t >/dev/null
git -C $T23/t checkout -qb factory/T-0001.1 && echo x > $T23/t/x.txt && git -C $T23/t add x.txt
git -C $T23/t -c user.email=f@x -c user.name=f commit -qm work && git -C $T23/t checkout -q main
H=$(git -C $T23/t rev-parse factory/T-0001.1)
bin/factory ticket set T-0001.1 status=checks-in-flight branch=factory/T-0001.1 head=$H >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0032-build.mjs <<'EOF'
// node t0032-build.mjs '<plays JSON>', from the checkout under test after sourcing t0023-parent.sh
// and t0032-checks.sh: runs factory/workflows/build.js on parent T-0001 of the store $FACTORY_STATE.
// Each clerk command runs for real (sh -c, from this checkout, environment unchanged). Each role
// run plays the next entry of its role's list in <plays> (the last one repeats):
//   {"say": "<text>"}     returns <text> (or null) as its final message and writes no output file;
//   {"write": "<STATUS>"} writes an output with the run's head as its Commit: line (and, for the
//                         verifier, "Gate suite: PASS") and that STATUS, and returns the same text.
// Prints each park, as `park <id>: <reason>`.
import { readFileSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const plays = JSON.parse(process.argv[2]), n = {}
const src = readFileSync('factory/workflows/build.js', 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  const r = prompt.match(/(\S+\/runs\/run-\d+-([a-z_]+))\/input\.md/)
  const list = plays[r[2]] || [{ say: '' }]
  n[r[2]] = (n[r[2]] || 0) + 1
  const p = list[Math.min(n[r[2]], list.length) - 1]
  if ('say' in p) return p.say
  const head = (readFileSync(`${r[1]}/meta.yaml`, 'utf8').match(/^head: '?([0-9a-f]{40})/m) || [])[1]
  const text = `Commit: ${head}\n` + (r[2] === 'verifier' ? 'Gate suite: PASS\n' : '') + `STATUS: ${p.write}\nCONFIDENCE: high, stub\nESCALATIONS: none\n`
  writeFileSync(`${r[1]}/output.md`, text)
  return text
}
const log = (s) => { const q = String(s).match(/^(\S+) parked: (.*)$/s); if (q) console.log(`park ${q[1]}: ${q[2]}`) }
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
  integration: 'main', inlineRoles: true }, agent, log, () => {}, async (fs) => Promise.all(fs.map(f => f())))
EOF
```

- WHEN `(M="Both suite runs are still in progress; I'll write the review once the monitor reports their final lines."; . ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && node ${TMPDIR:-/tmp}/t0032-build.mjs "{\"reviewer\": [{\"say\": \"$M\"}], \"verifier\": [{\"write\": \"VERIFIED\"}]}"; for r in reviewer verifier; do echo "$r: $(for d in $(ls -d $FACTORY_STATE/runs/*-$r); do sed -n 's/^status: //p' $d/meta.yaml; done | tr '\n' ' ')"; done; echo "kept=$(find $FACTORY_STATE/runs -path '*-reviewer/last-message.md' -exec grep -lxF "$M" {} + | grep -c .) $(bin/factory results show T-0001.1 | tail -1 | grep -o '"rows": {[^}]*}')")`
- THEN it prints exactly `park T-0001.1: EMPTY-OUTPUT from reviewer`, then `reviewer: EMPTY-OUTPUT EMPTY-OUTPUT ` (two reviewer runs, both empty), then `verifier: VERIFIED `, then `kept=2 "rows": {"ci": "PASS", "verifier": "VERIFIED"}` (both last messages kept verbatim, apostrophe included; no reviewer row, so a `--redispatch` re-runs only the reviewer)

#### Scenario: One empty reviewer run followed by a real one routes on the real one
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows" run once. The first reviewer call returns `null`; the verifier's SPEC-DEFECT gives the join a fixed stop.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && node ${TMPDIR:-/tmp}/t0032-build.mjs '{"reviewer": [{"say": null}, {"write": "APPROVE"}], "verifier": [{"write": "SPEC-DEFECT"}]}'; echo "reviewer: $(for d in $(ls -d $FACTORY_STATE/runs/*-reviewer); do sed -n 's/^status: //p' $d/meta.yaml; done | tr '\n' ' ')")`
- THEN it prints exactly `park T-0001.1: SPEC-DEFECT from verifier`, then `reviewer: EMPTY-OUTPUT APPROVE `

#### Scenario: An implementer that returns nothing twice parks as EMPTY-OUTPUT
Needs the GIVEN block of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" run once. In that fixture every role run returns an empty string.
- WHEN `(E=tests/test_interim.py; . ${TMPDIR:-/tmp}/t0022-sib.sh && node ${TMPDIR:-/tmp}/t0022-build.mjs; echo "implementer: $(for d in $(ls -d $FACTORY_STATE/runs/*-implementer); do sed -n 's/^status: //p' $d/meta.yaml; done | tr '\n' ' ')")`
- THEN it prints exactly `park T-0001.2: EMPTY-OUTPUT from implementer`, then `implementer: EMPTY-OUTPUT EMPTY-OUTPUT `

#### Scenario: An intake role's second empty output in a row parks as EMPTY-OUTPUT
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once. The stub store answers every `run finish` with `EMPTY-OUTPUT`.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/intake.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}}}, "run finish": {"out": {"ok": true, "run_id": "run-0009-x", "status": "EMPTY-OUTPUT", "escalations": []}}}')`
- THEN it prints exactly `start: triage`, then `start: triage`, then `park: EMPTY-OUTPUT from triage`

### Requirement: A role run that writes its output runs once and routes on its STATUS
A role run whose output file holds a STATUS MUST NOT be re-dispatched, and the build SHALL route on that STATUS as before.

#### Scenario: A reviewer that writes its output runs once
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && node ${TMPDIR:-/tmp}/t0032-build.mjs '{"reviewer": [{"write": "APPROVE"}], "verifier": [{"write": "SPEC-DEFECT"}]}'; echo "reviewer: $(for d in $(ls -d $FACTORY_STATE/runs/*-reviewer); do sed -n 's/^status: //p' $d/meta.yaml; done | tr '\n' ' ')")`
- THEN it prints exactly `park T-0001.1: SPEC-DEFECT from verifier`, then `reviewer: APPROVE `

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: Every role is told to wait for its own commands
Every copy of the shared preamble SHALL carry the bullet that starts `- Run every command in the foreground and wait for it to finish.` and says `Never end your turn while a command you started is still running`. The design block and both files MUST stay byte-identical, and every role run's system prompt SHALL carry the bullet.

#### Scenario: Every preamble copy carries the wait rule and the copies stay identical
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0032-pre.txt; sed -n '/^## Shared preamble/,/^## [0-9]/p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/00-preamble.md factory/prompts/preamble.md; do echo "fg=$(grep -c '^- Run every command in the foreground and wait for it to finish\.$' $f) end=$(tr '\n' ' ' < $f | tr -s ' ' | grep -c 'Never end your turn while a command you started is still running')"; done; cmp -s $X docs/prompts/00-preamble.md && cmp -s docs/prompts/00-preamble.md factory/prompts/preamble.md && echo verbatim || echo differs)`
- THEN it prints three lines, each exactly `fg=1 end=1`, then `verbatim`

#### Scenario: Implementer, reviewer and verifier run prompts carry the wait rule, and only the reviewer's carries the judge-the-diff rule
Needs the GIVEN block of "Implementer and verifier run prompts carry the declared-path rule" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && for r in implementer reviewer verifier; do P=$(prompt $r); echo "$r fg=$(echo "$P" | grep -c 'Never end your turn while a command you started is still running') judge=$(echo "$P" | grep -c 'Do not run the test suite or the gate commands')"; done)`
- THEN it prints exactly `implementer fg=1 judge=0`, `reviewer fg=1 judge=1`, `verifier fg=1 judge=0`, one per line

### Requirement: The code reviewer judges the diff and leaves the suite and the gate to the verifier
Every copy of the code reviewer prompt SHALL say `Do not run the test suite or the gate commands: the verifier runs them on the same head`, and SHALL allow a narrow command that confirms a specific finding. No existing line of that prompt MAY be removed, and the verifier prompt MUST NOT change. The reviewer's composed input MUST NOT list the gate commands, while the implementer's and the verifier's inputs still SHALL.

#### Scenario: Every reviewer copy carries the rule, keeps every existing line, and the verifier prompt is unchanged
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0032-rev.txt; T=$(mktemp -d); sed -n '/^## 6\. Code reviewer/,/^## 7\. /p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/06-code-reviewer.md factory/prompts/reviewer.md; do J=$(tr '\n' ' ' < $f | tr -s ' '); echo "judge=$(echo "$J" | grep -c 'Do not run the test suite or the gate commands: the verifier runs them on the same head') narrow=$(echo "$J" | grep -c 'You may run a narrow command to confirm a specific finding')"; done; git show main:factory/prompts/reviewer.md > $T/a; git show main:docs/prompts/06-code-reviewer.md > $T/b; echo "copy=$(cmp -s $X docs/prompts/06-code-reviewer.md && echo SAME || echo DIFF) fill=$([ "$(diff factory/prompts/reviewer.md docs/prompts/06-code-reviewer.md | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed) removed=$(git diff main...HEAD -- docs/prompts/06-code-reviewer.md factory/prompts/reviewer.md | grep -v '^---' | grep -c '^-') verifier_changed=$(git diff --name-only main...HEAD -- docs/prompts/07-verifier.md factory/prompts/verifier.md | grep -c .)")`
- THEN it prints three lines, each exactly `judge=1 narrow=1`, then `copy=SAME fill=unchanged removed=0 verifier_changed=0`

#### Scenario: The reviewer's input no longer hands it the gate commands, and the implementer's and verifier's still do
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && for r in reviewer verifier implementer; do [ $r = implementer ] && bin/factory ticket set T-0001.1 status=ready-for-implementer 'in_flight=[]' >/dev/null; R=$(bin/factory run start --role $r --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); bin/factory run compose ${R:-none} >/dev/null 2>&1; I=$FACTORY_STATE/runs/${R:-none}/input.md; echo "$r gates=$(grep -c 'Gate commands (run each from your worktree' $I 2>/dev/null) told=$(grep -c 'The verifier runs the gate commands on this head; you do not run them' $I 2>/dev/null)"; done)`
- THEN it prints exactly `reviewer gates=0 told=1`, `verifier gates=1 told=0`, `implementer gates=1 told=0`, one per line

### Requirement: The documents record the empty-output route
`docs/design.md` SHALL state the EMPTY-OUTPUT rule and its two routing-table rows, and SHALL list a second EMPTY-OUTPUT among the park reasons. `dev/build-harness.spec.md` SHALL describe EMPTY-OUTPUT and `run last-message`, and SHALL no longer describe a KILLED condition or seam. `README.md` SHALL no longer say that a run is parked for exceeding a budget, and SHALL describe the empty-output retry. `docs/changelog.md` SHALL gain an entry for issue #41, numbered without a gap. The change MUST add no whitespace errors.

#### Scenario: The design doc states the EMPTY-OUTPUT rule, its rows and its park
- WHEN `(echo "rule=$(grep -c '^- A role run that ends without writing its output is EMPTY-OUTPUT' docs/design.md) rows=$(grep -c '^| Any role | EMPTY-OUTPUT' docs/design.md) parks=$(grep '^- A non-empty ESCALATIONS line' docs/design.md | grep -c 'a second EMPTY-OUTPUT in a row') kill=$(grep -c 'never recorded as a budget kill' docs/design.md)")`
- THEN it prints exactly `rule=1 rows=2 parks=1 kill=1`

#### Scenario: The build spec describes EMPTY-OUTPUT and no longer a KILLED condition
- WHEN `(echo "stale=$(grep -c 'KILLED condition\|KILLED seam' dev/build-harness.spec.md) empty=$(grep -c 'EMPTY-OUTPUT' dev/build-harness.spec.md | awk '{print ($1 > 0)}') note=$(grep -c 'run last-message' dev/build-harness.spec.md | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `stale=0 empty=1 note=1`

#### Scenario: README drops the budget park and describes the empty-output retry
- WHEN `(echo "budget=$(grep -c 'exceeding its budget\|over budget' README.md) built=$(grep -c '^- \*\*Empty output\.\*\*' README.md) unstick=$(grep '^| \*\*Unstick\*\*' README.md | grep -c 'ended without output twice')")`
- THEN it prints exactly `budget=0 built=1 unstick=1`

#### Scenario: The changelog records issue 41 without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. After issue #41 ' docs/changelog.md | grep -oF -e EMPTY-OUTPUT -e foreground -e 'last message' -e 're-dispatched once' -e 'gate commands' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: The empty-output change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

=== verification.md
## Acceptance

Every scenario below was run on this checkout (`a69aaf4`) and on the scratch prototype, with a throwaway HOME and `TMPDIR` set to this run's scratch directory. The "fails today" text is the actual output on `a69aaf4`.

- A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows → NEW. It fails today with `park T-0001.1: budget kill: reviewer`, `reviewer: KILLED `, `verifier: VERIFIED `, `kept=0 "rows": {"ci": "PASS", "verifier": "VERIFIED", "reviewer": "KILLED"}`: one reviewer run, labelled a budget kill, with no last message kept. This is the incident.
- One empty reviewer run followed by a real one routes on the real one → NEW. It fails today with `park T-0001.1: budget kill: reviewer`, `reviewer: KILLED `: the `null` return is never retried.
- An implementer that returns nothing twice parks as EMPTY-OUTPUT → NEW. It fails today with `park T-0001.2: budget kill: implementer`, `implementer: KILLED `.
- An intake role's second empty output in a row parks as EMPTY-OUTPUT → NEW. It fails today with `start: triage`, `park: harness-bug: unknown STATUS EMPTY-OUTPUT from triage`: no retry, and the status is unknown to the intake script.
- A reviewer that writes its output runs once → REGRESSION. It prints `park T-0001.1: SPEC-DEFECT from verifier`, `reviewer: APPROVE ` both today and on the prototype.
- Every preamble copy carries the wait rule and the copies stay identical → NEW. It fails today with three lines `fg=0 end=0`, then `verbatim`.
- Implementer, reviewer and verifier run prompts carry the wait rule, and only the reviewer's carries the judge-the-diff rule → NEW. It fails today with `implementer fg=0 judge=0`, `reviewer fg=0 judge=0`, `verifier fg=0 judge=0`.
- Every reviewer copy carries the rule, keeps every existing line, and the verifier prompt is unchanged → NEW. It fails today with three lines `judge=0 narrow=0`; its last line already prints `copy=SAME fill=unchanged removed=0 verifier_changed=0`.
- The reviewer's input no longer hands it the gate commands, and the implementer's and verifier's still do → NEW. It fails today with `reviewer gates=1 told=0`; the verifier and implementer lines already print as expected.
- The design doc states the EMPTY-OUTPUT rule, its rows and its park → NEW. It fails today with `rule=0 rows=0 parks=0 kill=0`.
- The build spec describes EMPTY-OUTPUT and no longer a KILLED condition → NEW. It fails today with `stale=3 empty=0 note=0`.
- README drops the budget park and describes the empty-output retry → NEW. It fails today with `budget=2 built=0 unstick=0`.
- The changelog records issue 41 without a numbering gap → NEW. It fails today with `CONTIGUOUS`, then `0`.
- The empty-output change adds no whitespace errors → REGRESSION.

## PR description (the implementer's output)

Sub-ticket: T-0032.1 (branch `factory/T-0032.1`, head `c01e7c2`, base `97becfd`; worktree `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0032.1`)

This round applies the operator's ruling of 2026-10-06 on the BLOCKED round (run-0304). The branch now passes every acceptance scenario and both gate commands: `360 passed`.

## What changed

The first commit, `679dccc`, holds the whole change as the spec describes it. The second commit, `c01e7c2`, applies the ruling and changes 2 files.

**A. Every role is told to wait for its own commands.** The shared preamble is the rule text every role reads first. It gains one bullet in its RUNNING CODE section: run every command in the foreground, and never end the turn while one is still running, because the final message ends the run. The bullet follows the one ending "check command your briefing, ticket or spec gives you.". All three copies stay byte-identical: the `docs/design.md` block, `docs/prompts/00-preamble.md` and `factory/prompts/preamble.md`.

**B. The code reviewer judges the diff.**
- B.1: the reviewer prompt gains a WHAT YOU RUN section before CHECK, IN THIS ORDER, in all three copies. The reviewer reads the diff. It does not run the test suite or the gate commands, because the verifier runs them on the same head. A narrow command that confirms one finding is allowed. No existing line changed, and the run copy keeps its "After round 2" fill.
- B.2: `factory/compose.py` builds each run's input. The reviewer's "Where you work" paragraph keeps the worktree and branch sentence and the no-remote sentence. Its gate-commands sentence is replaced with "The verifier runs the gate commands on this head; you do not run them." The implementer's and the verifier's paragraphs are unchanged. As the ruling directs (item 3), the reviewer's input still lists the "SKIPPED by the harness for this diff, do not run: `<cmd>`: <reason>" lines. T-0028 added these lines, one for each gate command whose paths the diff does not touch. They come after the new sentence and are worded exactly as before (`c01e7c2`).

**C. A run with no output is EMPTY-OUTPUT.**
- C.1: `run finish` records a run with a missing or blank `output.md`, and no override, as `EMPTY-OUTPUT`, logged as `run.finished`. Before this change, it recorded `KILLED`. `--status-override KILLED` is unchanged: it still records `KILLED` and logs `run.killed`.
- C.2: the new command `factory run last-message RUN --text=T` writes `runs/<RUN>/last-message.md`, which holds T plus a newline. It does this only when the run's status is `EMPTY-OUTPUT`. Otherwise it exits 2 and writes nothing. The command is not on the read-only list, so the live-store fence treats it as a write. The fence is the guard that refuses unmarked writes to a store while a run is in flight.
- C.3: the change is the same in both workflow scripts, `build.js` and `intake.js`. Today's `runRole` body is now `runOnce`. `runOnce` always calls a plain `run finish`, and the scripts no longer send a KILLED override for an empty return. The clerk is the low-effort agent that runs one store command for the script. When `run finish` returns `EMPTY-OUTPUT` and the agent returned non-blank text, the clerk keeps that text with `run last-message`. It keeps the last 4000 characters, shell single-quoted. A failure of this call is ignored. The new `runRole` runs `runOnce` and, on `EMPTY-OUTPUT`, runs it once more. A second `EMPTY-OUTPUT` parks the ticket as `EMPTY-OUTPUT from <role>`, with both run ids as outputs. The path for a thrown agent call is unchanged. In `build.js`, the `budget kill: implementer` park is deleted.
- C.4: new test file `tests/factory/test_empty_output.py`, with 6 tests.

**D. Documents.**
- `docs/design.md`: "a second EMPTY-OUTPUT in a row" joins the park reasons, and a new rule bullet follows them. The resolution bullet now covers a ticket parked on a second EMPTY-OUTPUT. The routing table gains two `Any role | EMPTY-OUTPUT` rows.
- `dev/build-harness.spec.md`: `run finish` now names `EMPTY-OUTPUT`, and `run last-message` is listed. The `runRole` step, I.5 and item 49 describe the EMPTY-OUTPUT route. No line says "KILLED condition" or "KILLED seam".
- `README.md`: the budget park becomes the empty-output park, in the text and in the diagram edge. The Unstick row's `--redispatch` gloss is extended. A new Built bullet, **Empty output.**, is added. The status date is now 2026-10-06.
- `docs/changelog.md`: new entry 57, "After issue #41 (2026-10-04), …".

None of these documents says the reviewer loses its SKIPPED lines. A grep of the branch's diff for "skip" finds only the changed I.5 text, which is about the user skipping an agent. So the restored lines need no document change. The current-truth `gate-commands` requirement says a reviewer or verifier run "MUST list that command apart from the commands to run". It holds again, so the pinned spec needs no MODIFIED delta.

Callers of the changed functions, found by grep in the first round, are unchanged by this round. `runRole` is called in `build.js` (planner, implementer, both checkers, parent-close verifier) and in `intake.js` (triage, spec writer, critic). `compose.compose` has one caller, `run_compose` in `factory/cli.py`.

## Acceptance results

I ran every command from the worktree, with a throwaway HOME and with `TMPDIR` set to this run's scratch directory. The GIVEN fixtures were extracted verbatim from current truth and from the pinned spec: `t0023-parent.sh`, `t0023-wf.mjs`, `t0022-sib.sh`, `t0022-build.mjs`, `t0029-prompt.sh`, `t0032-checks.sh` and `t0032-build.mjs`. The WHEN commands were extracted verbatim from `specs/T-0032/v1.md`, all 14 of them. The "Before" column is run-0304's output on base `97becfd`. Each value there matches the "fails today" text in verification.md. The "After" column is this round's output on the committed head `c01e7c2`, and each value matches its THEN exactly.

| # | Scenario | Label | Before (`97becfd`) | After (`c01e7c2`) |
|---|---|---|---|---|
| 1 | Reviewer ends its turn waiting: re-dispatched once, then parks | NEW | `park T-0001.1: budget kill: reviewer` / `reviewer: KILLED ` / `verifier: VERIFIED ` / `kept=0 "rows": {"ci": "PASS", "verifier": "VERIFIED", "reviewer": "KILLED"}` | `park T-0001.1: EMPTY-OUTPUT from reviewer` / `reviewer: EMPTY-OUTPUT EMPTY-OUTPUT ` / `verifier: VERIFIED ` / `kept=2 "rows": {"ci": "PASS", "verifier": "VERIFIED"}` |
| 2 | One empty reviewer run, then a real one | NEW | `park T-0001.1: budget kill: reviewer` / `reviewer: KILLED ` | `park T-0001.1: SPEC-DEFECT from verifier` / `reviewer: EMPTY-OUTPUT APPROVE ` |
| 3 | Implementer returns nothing twice | NEW | `park T-0001.2: budget kill: implementer` / `implementer: KILLED ` | `park T-0001.2: EMPTY-OUTPUT from implementer` / `implementer: EMPTY-OUTPUT EMPTY-OUTPUT ` |
| 4 | Intake role empty twice | NEW | `start: triage` / `park: harness-bug: unknown STATUS EMPTY-OUTPUT from triage` | `start: triage` / `start: triage` / `park: EMPTY-OUTPUT from triage` |
| 5 | Reviewer that writes its output runs once | REGRESSION | n/a | `park T-0001.1: SPEC-DEFECT from verifier` / `reviewer: APPROVE ` |
| 6 | Preamble copies carry the wait rule, identical | NEW | `fg=0 end=0` ×3 / `verbatim` | `fg=1 end=1` ×3 / `verbatim` |
| 7 | Run prompts: wait rule for all three, judge rule for the reviewer only | NEW | `implementer fg=0 judge=0` / `reviewer fg=0 judge=0` / `verifier fg=0 judge=0` | `implementer fg=1 judge=0` / `reviewer fg=1 judge=1` / `verifier fg=1 judge=0` |
| 8 | Reviewer copies carry the rule, no line removed, verifier unchanged | NEW | `judge=0 narrow=0` ×3 / `copy=SAME fill=unchanged removed=0 verifier_changed=0` | `judge=1 narrow=1` ×3 / `copy=SAME fill=unchanged removed=0 verifier_changed=0` |
| 9 | Reviewer input no longer lists the gate commands | NEW | `reviewer gates=1 told=0` / `verifier gates=1 told=0` / `implementer gates=1 told=0` | `reviewer gates=0 told=1` / `verifier gates=1 told=0` / `implementer gates=1 told=0` |
| 10 | Design doc states the rule, rows and park | NEW | `rule=0 rows=0 parks=0 kill=0` | `rule=1 rows=2 parks=1 kill=1` |
| 11 | Build spec: EMPTY-OUTPUT, no KILLED condition | NEW | `stale=3 empty=0 note=0` | `stale=0 empty=1 note=1` |
| 12 | README drops the budget park | NEW | `budget=2 built=0 unstick=0` | `budget=0 built=1 unstick=1` |
| 13 | Changelog records issue 41, no gap | NEW | `CONTIGUOUS` / `0` | `CONTIGUOUS` / `5` |
| 14 | No whitespace errors | REGRESSION | n/a | `exit=0` |

I ran each gate command exactly as written, from the worktree, on `c01e7c2`:
- `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`: exit 0.
- `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`: `360 passed in 218.78s (0:03:38)`. The one failure from run-0304, `test_gate_paths.py::test_a_diff_that_touches_a_scoped_command_s_paths_runs_it`, now passes.

I also checked the restored SKIPPED lines directly, outside the gates. A scratch script (`scratch/check_reviewer_skipped.py`) used the suite's own `Target` helper from `test_gate_paths.py` to compose a reviewer input and a verifier input for a diff that skips the scoped command. Both inputs printed the same single line, `SKIPPED by the harness for this diff, do not run: `sh -c 'exit 7'`: the diff <base>...<head> touches none of its paths: src/`, and the same `gate_skipped` entry in `meta.yaml`. The reviewer's paragraph ends "The verifier runs the gate commands on this head; you do not run them." The verifier's paragraph still lists the commands to run.

## Tests added/changed

- Added `tests/factory/test_empty_output.py`, a new file in `679dccc`, unchanged this round. It has 6 tests covering 4 cases:
  - `run finish` with no output, an empty output or a whitespace-only output gives `EMPTY-OUTPUT` in its JSON and in `meta.yaml`, and logs `run.finished`, never `run.killed`.
  - `--status-override KILLED` still gives `KILLED` and logs `run.killed`.
  - `run last-message` writes the file for an `EMPTY-OUTPUT` run and prints the spec's JSON.
  - `run last-message` exits 2 and writes nothing for a run that finished with an output.

  Before the change, 5 of the 6 failed. The override test already passed, because that behaviour does not change.
- Changed `tests/factory/test_gate_paths.py::test_a_diff_that_touches_a_scoped_command_s_paths_runs_it`, under ruling item 1. Its `t.checker("reviewer")` is now `t.checker()`, which composes a verifier input. Nothing else in the file changed (`git diff 679dccc c01e7c2 -- tests/factory/test_gate_paths.py` is one line). The change was needed because B.2 removes the gate commands from the reviewer's input. The test checks that a scoped command whose paths the diff touches is listed to run. It now checks that on the verifier, the role that still receives the gate commands. Its assertions are unchanged.

## Known gaps and uncertainties

- No suite test asserts that the reviewer's input carries the SKIPPED lines. The only test for that case, `test_a_scoped_command_is_skipped_for_a_diff_that_touches_none_of_its_paths`, composes a verifier input. I checked the reviewer case once by hand (above). The ruling said "Nothing else changes", so I added no test. If a later change drops the lines for the reviewer again, the suite will not notice.
- The `results record … --killed` suffix in `build.js` can no longer be reached from the workflow, because `run finish` without an override can no longer return `KILLED`. The spec keeps `--killed` for rows a human records by hand and does not ask to remove the suffix, so it stays.
- `factory:` markers added: none.
- The clerk receives the last message inside its prompt as one shell single-quoted word of up to 4000 characters, possibly with newlines. The scenarios pass this through a real `sh -c`. No real clerk agent has yet relayed a long multi-line argument. If a clerk mangles one, the call fails and is ignored, as specified, and only the kept message is lost.
- Changelog entry 57 is one long line, like entries 54 to 56. Its wording is mine, written to the five terms scenario 13 checks.

## Out-of-scope observations

- `dev/build-harness.spec.md` item 59 ("Wall-clock kill … `time_budget_s: 1800` → `status: KILLED`") and item 83 (`--redispatch --budget`) describe a budget mechanism that does not exist: the spec's evidence shows `grep -rn "time_budget\|budget_usd" factory/*.py` prints nothing. I rewrote I.5 as the spec asks, so it no longer claims a wall-clock kill. I left items 59 and 83 alone.
- `tests/factory/test_shepherd.py` and `test_killed_checker.py` still model the old killed path through the CLI, and they pass, as the spec predicted. The comment in the current-truth fixture `t0022-build.mjs` still says "the workflow records as a killed run". The spec lists both as observed, not changed.
- T-0030 overlaps this change: it also edits `factory/prompts/reviewer.md`, the design doc's §6 block and `factory/compose.py`. Whichever merges second will hit a text conflict in the reviewer's "Where you work" paragraph.

Protected paths this change touches, all declared in the parent's Risk list:
- harness: `factory/cli.py`, `factory/compose.py`, `factory/workflows/build.js`, `factory/workflows/intake.js`, `factory/prompts/preamble.md`, `factory/prompts/reviewer.md`;
- generated: `docs/prompts/00-preamble.md`, `docs/prompts/06-code-reviewer.md`.

## Responses to the ruling (2026-10-06, on run-0304's BLOCKED)

1. Retarget the test: DONE in `c01e7c2`. `t.checker("reviewer")` became `t.checker()`, and nothing else in `tests/factory/test_gate_paths.py` changed.
2. Keep B.2's gate-commands sentence: DONE. It is unchanged from `679dccc`, and scenario 9 prints `reviewer gates=0 told=1`.
3. Restore the reviewer's SKIPPED lines: DONE in `c01e7c2`. They are added after the gate sentence for every role, worded exactly as before. Checked by hand as described in Acceptance results.
4. Re-run the gate commands: DONE. `git diff --check` exited 0, and the suite printed `360 passed`.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. All 14 scenarios print their THEN on `c01e7c2`, both gates pass (360 tests), and this round's change is the two edits the ruling names.
ESCALATIONS: none

## Diff `97becfdf573248116c7933347224765c8a2ede83...c01e7c2cf8bdef4f73fd8443744906b9ea89db74`

diff --git a/README.md b/README.md
index 8ec155d..2215c6b 100644
--- a/README.md
+++ b/README.md
@@ -6,7 +6,7 @@ table, and human gates. This page is the system as it runs today; install and us
 
 | | |
 |---|---|
-| **Status** | Current state as of 2026-10-04. Intake works end to end. Build works, in local-only mode. |
+| **Status** | Current state as of 2026-10-06. Intake works end to end. Build works, in local-only mode. |
 | **Reader** | Technical, seeing this project for the first time. Terms specific to this system are defined in "Terms used on this page" or at first use. |
 | **Scope** | What runs now. The intended design and its reasoning are in `docs/design.md`; where the two disagree, this page is right about what runs and the design is amended. |
 | **Internal references** | Ticket ids, issue numbers and who did what are in "Related work and history" near the end. |
@@ -170,8 +170,10 @@ not updated. While that final run is in progress, the ticket's record lists it a
 any other run.
 
 At any step a role can say it needs a human: a question, an escalation, a blocked build. The
-harness parks the ticket. So does running out of rounds, or a run exceeding its budget. A human
-unsticks it with `factory resolve`, and the ticket re-enters at the step the rules name.
+harness parks the ticket. So does running out of rounds, or a role that ended without output
+twice in a row (the first time, the harness runs it once more on the same inputs and keeps its
+last message). A human unsticks it with `factory resolve`, and the ticket re-enters at the step
+the rules name.
 
 ```mermaid
 flowchart LR
@@ -212,7 +214,7 @@ flowchart LR
   CL --> ST[("the store<br/>tickets · runs · specs · verdicts · log · current truth")]:::store
 
   PK{"parked ticket<br/>a human runs factory resolve"}:::human
-  TR & SW & SC & PL & IM & J & PC -. "needs a human · out of rounds · over budget" .-> PK
+  TR & SW & SC & PL & IM & J & PC -. "needs a human · out of rounds · no output twice" .-> PK
 ```
 
 *One ticket from request file to closed record. Orange is the human; grey is the agents; teal is
@@ -789,7 +791,7 @@ FACTORY_DISPATCH=1 $RUNTIME/bin/factory run finish <run> --status-override KILLE
 |---|---|---|
 | **File** | `factory ticket new --file <abs path>` | that this request is worth a ticket |
 | **Gate** | `factory approve-spec T-n [--edit F]` · `factory request-changes T-n F` · close | the spec's intent, risk declarations, operator steps, "tests to change"; a gate edit becomes a new spec version and is what gets pinned |
-| **Unstick** | `factory resolve T-n --answer F` (a role asked a question) · `--ruling F` (a role escalated, an implementer reported itself blocked, or the harness blocked an implementer whose sub-ticket lists a test no merged sibling added) · `--redispatch` (re-run the checks on the same commit after an outside fix) · `--replan F` (the final check failed after every sub-ticket merged: back to the planner with a note; new sub-tickets take the next free ids) · `--to spec-gate` · `--close`; with `--answer` or `--close`, add `--decision "<line>"` to also record the answer as a standing decision | an answer, a ruling, a re-check, a re-plan, a re-scope, or closing |
+| **Unstick** | `factory resolve T-n --answer F` (a role asked a question) · `--ruling F` (a role escalated, an implementer reported itself blocked, or the harness blocked an implementer whose sub-ticket lists a test no merged sibling added) · `--redispatch` (re-run the checks on the same commit after an outside fix, or after a checker ended without output twice) · `--replan F` (the final check failed after every sub-ticket merged: back to the planner with a note; new sub-tickets take the next free ids) · `--to spec-gate` · `--close`; with `--answer` or `--close`, add `--decision "<line>"` to also record the answer as a standing decision | an answer, a ruling, a re-check, a re-plan, a re-scope, or closing |
 | **Record** | `factory decision add T-n "<line>"`, at any ticket state, closed included. It appends one dated line to the target's decision log, `decisions.md`, which the spec writer, critic and planner receive with their input | that a decision binds later tickets |
 | **Upgrade** | `factory --accept-harness <sha> <command>` | that this target adopts a new harness revision |
 
@@ -855,6 +857,13 @@ path above is relative to the store.
   sub-ticket added the file. If none did, the sub-ticket parks as blocked, and the human rules on it
   as on any blocked build ("Where a human decides"). Any other existing test still changes only if
   the approved spec lists it. It is tested, and has not yet fired on a real ticket.
+- **Empty output.** A role run that ends without writing its output file is run once more on the
+  same inputs, and the harness keeps the agent's last message with the run. A second run in a row
+  that ends the same way parks the ticket. The harness enforces no time or token budget and cannot
+  tell why a run stopped, so it never labels such a run a budget kill. The code reviewer judges the
+  diff and leaves the test suite and the gate commands to the verifier. Every role is told to wait
+  for the commands it starts before it ends its turn. It is tested, and has not yet fired on a real
+  ticket.
 
 **Not built**
 
diff --git a/dev/build-harness.spec.md b/dev/build-harness.spec.md
index 1991982..c7fc35d 100644
--- a/dev/build-harness.spec.md
+++ b/dev/build-harness.spec.md
@@ -202,7 +202,8 @@ CLI (the **store CLI** of doc §Harness table piece 1 — read, transition, reco
 - `factory ticket show ID`; `factory ticket set ID key=value` (logged); `factory ticket transition ID --to STATE --by RUN [--round spec|pr:+1|reset|init]` (the clerk's one write for routing; `init` sets the counter to 1 if 0). **Guards (doc §Harness table piece 2: "put the round and routing guards in the CLI, not the clerk"):** exit 2, store unchanged, nothing logged, when `+1` would take the counter above `config.yaml` `max_rounds` (`round.spec 2 is at max_rounds 2`), or when `(current status, STATE)` is not an edge of the routing table stored in `config.yaml` `routing:` (the doc §Routing table rows plus the resolution rules; `no route ready-for-triage → merged`). `factory ticket park ID --reason R --outputs RUN,RUN [--question PATH]`.
 - `factory run start --role R --ticket ID|none --head SHA|none [--model M]` → prints `run_id`, writes `runs/<run_id>/{meta.yaml,system-prompt.txt}` and creates the empty `runs/<run_id>/scratch/` for the run's temporary files, which the store's `.gitignore` excludes (`model: M`, default `config.yaml` `models[R]`; `budget_usd` copied from the ticket), appends the id to `in_flight`. **Guards:** exit 2, nothing written, when the ticket is not in R's ready state (`T-0001 is ready-for-triage, not ready-for-critic`; ready states: triage `ready-for-triage`, spec_writer `ready-for-spec-writer`, critic `ready-for-critic`, planner `ready-for-planner`, implementer `ready-for-implementer`, reviewer/verifier `checks-in-flight` or `ready-for-checks`, verifier also `ready-for-parent-verify`; retro runs with `--ticket none`), or when the ticket's branch already has a run in `in_flight` (implementer, retro: any run; reviewer, verifier: a run of the same role) — `ticket/T-0001 already has run <id> in flight`; or, for an implementer run of a sub-ticket, when a `` `<file>` (added by <ID>) `` line in its "Tests to change" field names a file that existed at the parent's `parent_base` or whose first adding commit on the integration branch since then lies inside no merged sibling's recorded `merge` (doc §Harness, "Tests a sibling added") — `BLOCKED from harness: Tests to change lists <file> as added by a sibling, but no merged sibling of <parent> added it since <base>; …`. **Run id reservation:** after the guards pass and before anything else is written, `run start` reserves the run's directory by creating `runs/<run_id>/` create-exclusive (an mkdir that fails when the path already exists); on a collision it takes the next id and tries again. Two starts on one store at the same moment, whatever their tickets or roles, therefore never share a run directory, and the id is final before its `meta.yaml` is written. A refused start reserves nothing (item 70).
 - `factory run compose RUN` (**the one input mechanism**, critic S2) → writes `runs/<run_id>/input.md` from exactly the sources `factory/compose.py` declares for `(role, round, resolution)` — the "with input =" lists in H, read from the store and `~/factory/clone` — and records their paths as `input_sources:` and the pinned spec version it used as `spec_version:` in `meta.yaml` (a run keeps that version even if the spec is re-pinned while it is in flight, K). The file opens with the repo's role-context block (doc §Harness), ahead of those sources; it is not a store path, so it is not one of the `input_sources:` (its text is in `input.md`). The text `agent()` receives is only `Your entire input is ~/factory/state/runs/<run_id>/input.md; read it first.` No input text is composed anywhere else.
-- `factory run finish RUN --output-file F [--status-override KILLED]` → writes `output.md`, parses STATUS (H), removes the id from `in_flight`, prints `STATUS CONFIDENCE ESCALATIONS` as JSON, logs `escalation.queued` when the list is non-empty (H).
+- `factory run finish RUN --output-file F [--status-override KILLED]` → writes `output.md`, parses STATUS (H), removes the id from `in_flight`, prints `STATUS CONFIDENCE ESCALATIONS` as JSON, logs `escalation.queued` when the list is non-empty (H). A missing or blank `output.md` with no override is `EMPTY-OUTPUT` (error `empty output`, logged `run.finished`); `--status-override KILLED` still records `KILLED` and logs `run.killed`.
+- `factory run last-message RUN --text=T` → on a run whose `meta.yaml` status is `EMPTY-OUTPUT`, writes T plus one newline to `runs/<RUN>/last-message.md` and prints its path; on any other run, exit 2 and nothing written (I.5).
 - `factory spec add ID --file F` → `spec.version += 1`, `specs/ID/v<N>.md`; `factory spec tasks PARENT --run RUN` → writes that planner run's `output.md`, trailer removed as for spec text (above), to `openspec/changes/<PARENT>/tasks.md` (exit 2 unless RUN is a `PLANNED` planner run of PARENT); `factory subticket add PARENT --file F --depends-on IDS --parallel-safe yes|no` → sub-ticket in `ready-for-implementer` or `waiting-dependencies`; `factory plan whole-spec PARENT` → when the approved spec needs one sub-ticket (the parent has no sub-ticket and no earlier planner run, its latest spec-writer run did not end `NEEDS-SPLIT`, and the approved spec has no `##` or `###` heading, other than a `### Requirement:` line, naming seams), creates `<PARENT>.1` from the whole spec in `ready-for-implementer`, its text naming every scenario, writes the same text to `plans/<PARENT>.md` and, with a spec store, `openspec/changes/<PARENT>/tasks.md`, logs `plan.skipped`, and prints `"planner": "skipped"`; otherwise prints `"planner": "needed"` with the reason and writes nothing (exit 2 when PARENT is not `ready-for-planner`, has a run in flight, has no approved spec, or has no change folder under an active spec store).
 - **Operator commands** (`approve-spec`, `approve-pr`, `approve-guardrail`, `request-changes`, `resolve`, `queue apply`, `merge`, `ticket new`, `results record`) refuse with exit 2, stderr `set FACTORY_KEY`, nothing written or logged, when `FACTORY_KEY` is unset (item 78); reads (`ticket show`, `results show`, `queue`, `log tail`) never need it. `gate-run` always uses the harness key.
 
@@ -272,7 +273,7 @@ Both scripts are plain JS per E7; they hold the routing, the join and the round
 
 **STATUS parser** (`factory/status.py`, used by `run finish` and `results record`; doc §Routing rules): the **last** line matching `^STATUS:\s*(\S+)` gives the STATUS. CONFIDENCE is the first line after it matching `^CONFIDENCE:`, and ESCALATIONS the first line after that matching `^ESCALATIONS:`; lines between labelled lines are continuation (a wrapped CONFIDENCE reason, commentary between STATUS and CONFIDENCE), never a parse failure. No `CONFIDENCE:` line after the last STATUS, or no `ESCALATIONS:` line after that CONFIDENCE → parse failure → unknown STATUS. The **head** is the rest of the `ESCALATIONS:` line, trimmed; the list is the head plus every non-blank line after it to EOF, each item as written (a leading `- ` or `* ` marker stripped, item 8). A **`none` head** matches `(?i)^none\s*($|[.,;:—–-])`: `none` in any case, then end of line or punctuation, never a space and a word, so `none`, `none.` and `none. The boundary was observed` are `none` heads and `Nonetheless …`, `None of …` are not. The list is empty iff nothing non-blank follows the head and the head is empty or a `none` head; a `none` head with prose after it on its line therefore routes as no escalation, and `run finish` writes that head verbatim to the run's `meta.yaml` as `escalations_note:` (written only when the list is empty and prose follows the `none` head; every other shape, including bare `none` and a `none` head with lines below it, writes `null`) so an auditor reads it with the run. A `none` head followed by any further non-blank line is a real list, every line from the head on an item, verbatim (a wrapped `none` prose line is such a line: when the parser is unsure, the text goes to the human queue). The parser reads no severities: doc §Human gates' rule that REVISE and REQUEST-CHANGES carry at least one BLOCKING finding is the checker's to keep, and every stub that models them (items 38, 44, 46) includes a BLOCKING line.
 
-Common step `runRole(role, ticket, head)` in both scripts: clerk `factory run start … --model MODELS[role]` (prints `run_id`; exit 2 from a guard → park `harness-bug: <stderr>` and return; in `build.js`, a refusal whose JSON `error` starts `BLOCKED ` parks with that error verbatim instead, so `resolve --ruling` applies); clerk `factory run compose RUN_ID` (writes `input.md`, I.2); `const out = await agent('Your entire input is ~/factory/state/runs/' + runId + '/input.md; read it first.', {agentType: args.stubs ? 'factory-stub' : 'factory-' + role, model: MODELS[role], label: role + ' ' + ticket, isolation: role in {implementer, retro} ? 'worktree' : undefined})`; **KILLED condition** `out === null || out.trim() === ''` (I.5) → clerk `factory run finish RUN --status-override KILLED`; else clerk `factory run finish RUN --output-file -` with `out`. **A thrown `agent()`** (stub or real call) is finished the same way, clerk `factory run finish RUN --status-override KILLED` (in `build.js`, then clerk `factory run cleanup RUN` for a reviewer or verifier), and parks the ticket `agent call failed: <role>: <error>` with the run id as outputs; `runRole` returns `null`, on which every caller returns. The clerk returns only `{stdout, exit, stderr}`; the script parses `run_id` from `run start`'s JSON and `{status, escalations}` from `run finish`'s. The stub agent definition reads `args.stubs/<role>-<n>.md` (n = how many times that role has run in this workflow, counted in the script) and returns it verbatim, or **returns an empty string when the file is absent** (the KILLED seam): the only test seam. The CLI guards (B) are authoritative over the script's `round < MAX` checks: a `transition` the routing table or `max_rounds` forbids exits 2 with the store unchanged, and the script treats that as `park --reason 'harness-bug: <stderr>'`.
+Common step `runRole(role, ticket, head)` in both scripts: clerk `factory run start … --model MODELS[role]` (prints `run_id`; exit 2 from a guard → park `harness-bug: <stderr>` and return; in `build.js`, a refusal whose JSON `error` starts `BLOCKED ` parks with that error verbatim instead, so `resolve --ruling` applies); clerk `factory run compose RUN_ID` (writes `input.md`, I.2); `const out = await agent('Your entire input is ~/factory/state/runs/' + runId + '/input.md; read it first.', {agentType: args.stubs ? 'factory-stub' : 'factory-' + role, model: MODELS[role], label: role + ' ' + ticket, isolation: role in {implementer, retro} ? 'worktree' : undefined})`; one clerk `factory run finish RUN`, which reads the run's output file; on `EMPTY-OUTPUT` with non-blank returned text, clerk `factory run last-message RUN '--text=<last 4000 characters>'`, a failure of which is ignored, then one re-dispatch of the same role; a second `EMPTY-OUTPUT` in a row parks `EMPTY-OUTPUT from <role>` with both run ids as outputs (I.5). **A thrown `agent()`** (stub or real call) is finished the same way, clerk `factory run finish RUN --status-override KILLED` (in `build.js`, then clerk `factory run cleanup RUN` for a reviewer or verifier), and parks the ticket `agent call failed: <role>: <error>` with the run id as outputs; `runRole` returns `null`, on which every caller returns. The clerk returns only `{stdout, exit, stderr}`; the script parses `run_id` from `run start`'s JSON and `{status, escalations}` from `run finish`'s. The stub agent definition reads `args.stubs/<role>-<n>.md` (n = how many times that role has run in this workflow, counted in the script) and returns it verbatim, or **returns an empty string when the file is absent** (the EMPTY-OUTPUT seam): the only test seam. The CLI guards (B) are authoritative over the script's `round < MAX` checks: a `transition` the routing table or `max_rounds` forbids exits 2 with the store unchanged, and the script treats that as `park --reason 'harness-bug: <stderr>'`.
 
 `intake.js` (`args: {ticket, stubs?}`):
 1. `phase('Triage')`: `runRole('triage', …)` with input = request, answers appended (+ after an `--answer`: Triage's previous output, K); `ACCEPT` → clerk `transition --to ready-for-spec-writer` (title/type from the output); `REJECT` → `closed`; `NEEDS-HUMAN` → `park --question`; `CLARIFY` → `transition --to waiting-requester` + clerk `factory reply ID --file -` (piece 9: writes `<source dir>/<file>.reply.md` next to the request, appends to `queue.md`, event `reply.sent`); then **return**. Unknown STATUS → `park --reason 'harness-bug: unknown STATUS <s>'` + `harness-bug` event; always return.
@@ -297,7 +298,7 @@ Resumption after a human decision: the `/factory` skill re-runs `build.js` for t
 2. Input composed by `factory run compose RUN` (B): the role-context block (doc §Harness), then exactly the declared sources (H), written as `runs/<run_id>/input.md` with `input_sources:` in `meta.yaml` **before** the role runs; the role's prompt is a pointer to that file, so what the role saw is auditable and no second composition path exists.
 3. Mutating roles get `isolation: 'worktree'` (E7), which the Workflow tool creates and removes; the implementer's `git push` uses the implementer key via `GIT_SSH_COMMAND` set in its agent definition's `env:` (not verified: whether agent-definition frontmatter supports `env:`; fallback: a `factory git-push ticket/<ID>` wrapper the implementer is allowed to run, which supplies the key). Checkers run read+shell in a checkout the clerk made; they have no key, so a push fails at authentication.
 4. Tool restriction is the agent definition's `tools:` (R6); no `bypassPermissions` anywhere; `--restricted` applies to `claude -p` test drivers (E6).
-5. Budget (piece 3): the KILLED condition is `out === null || out.trim() === ''` (`agent()` returned `null` on a terminal error or after the user skipped the agent, or returned nothing) → `run finish --status-override KILLED` → `KILLED` results row, `parked` (`budget kill: <role>`), round unchanged. The one manual kill path the Workflow reference provides: the user skips the agent in the session, `agent()` returns `null`, KILLED. Until then a hung agent blocks `parallel()` and every sibling in that join; the doc's "recorded … so no join waits on it" is post-hoc in v0, not pre-emptive. Wall-clock: the clerk stamps `started`/`finished` in `meta.yaml`; `run finish` sets `status: KILLED` when `wall_s > time_budget_s` even if output arrived. There is no pre-emptive kill in v0 (E7; Open question 4).
+5. Empty output (doc §Routing rules): no time or token budget is enforced, and `agent()` reports no reason a run stopped, so no empty output is a budget kill. A run that ends without its output file, or with a blank one, is `EMPTY-OUTPUT` in `run finish`, whether `agent()` returned text, blank text or `null` (a user skip or a terminal error). When the returned text is non-blank, the script keeps its last 4000 characters with `run last-message`. The same role is re-dispatched once, on the same inputs and in the same round; a second `EMPTY-OUTPUT` in a row parks `EMPTY-OUTPUT from <role>` with both runs as outputs and records no result row for it, so `resolve --redispatch` re-runs only that role. A thrown `agent()` stays `KILLED`, parked `agent call failed: <role>: <error>`, with no re-dispatch. Until a run returns, a hung agent blocks `parallel()` and every sibling in that join; the user skipping the agent is the one manual stop (E7; Open question 4).
 6. After each run: `meta.yaml` complete, the checker worktree removed by the clerk (`factory run cleanup RUN`). The run's `runs/<run_id>/scratch/` stays until its ticket's next state change other than `parked`, which removes it (`store.save_ticket`).
 
 ### J. Secrets (piece 12)
@@ -407,7 +408,7 @@ Driver: `claude -p … "/factory run build T-0001 --stubs tests/factory/fixtures
 46. Case `parking-wins` (reviewer REQUEST-CHANGES with a `[BLOCKING]` finding, verifier SPEC-DEFECT) → `parked`, `parked.outputs` lists both run ids; `queue.md` shows both output paths [NEW]
 47. Case `gate-fail` (verifier FAILED + `Gate suite: FAIL`, reviewer APPROVE, twice) → after round 1: `results/<head>/ci.yaml` `FAIL`, `round.pr: 2`; after round 2: `parked`, `max-round cutoff`. Variant: verifier output without a `Gate suite:` line → ci `FAIL`, `detail: missing Gate suite line`, and the join still proceeded (round incremented) [NEW]
 48. After 47: `AS daniel factory resolve T-0001.1 --ruling notes.md --to implementer --amend-subticket sub2.md --amend-spec spec2.md` → `ready-for-implementer`, `round.pr: 0`, `specs/T-0001/subticket.md` = `sub2.md`, `specs/T-0001/v<N+1>.md` = `spec2.md`, `approved_version: N+1`, `approvals/T-0001/spec-v<N+1>.yaml` exists, `knowledge_vault/sanitized_specs/T-0001.md` = `spec2.md`; re-running `build` → `runs/<implementer run>/input.md` contains the notes, `sub2.md` and `spec2.md` text [NEW]
-49. **Checker KILLED (S6, S4):** case `reviewer-killed` (stub file `reviewer-1.md` absent → the stub agent returns an empty string → the script's KILLED condition `out === null || out.trim() === ''` (I.5) holds; verifier VERIFIED) → `results/<head>/reviewer.yaml` `KILLED`, `parked`, `parked.reason: budget kill: reviewer`, `round.pr: 1`; `AS daniel factory resolve T-0001.1 --redispatch` → `ready-for-checks`; re-running `build` with `reviewer-1.md` present → exactly one new `run.started` (reviewer, same head), none for verifier; `round.pr` still 1; ticket proceeds to `merged` [NEW]
+49. **Checker empty twice (S6, S4):** case `reviewer-empty` (stub files `reviewer-1.md` and `reviewer-2.md` absent → the stub agent returns an empty string and writes no output, twice → `run finish` gives `EMPTY-OUTPUT` both times (I.5); verifier VERIFIED) → no `results/<head>/reviewer.yaml`, `parked`, `parked.reason: EMPTY-OUTPUT from reviewer`, both reviewer runs as outputs, `round.pr: 1`; `AS daniel factory resolve T-0001.1 --redispatch` → `ready-for-checks`; re-running `build` with `reviewer-1.md` present (each workflow run counts stubs from 1) → exactly one new `run.started` (reviewer, same head), none for verifier; `round.pr` still 1; ticket proceeds to `merged` [NEW]
 50. `AS daniel factory resolve T-0001 --to spec-gate` on a parked spec loop → `ready-for-spec-gate`; `AS daniel factory resolve T-0001 --close` → `closed`, `approvals/T-0001/resolve-1.yaml` `by: daniel` [NEW]
 51. No second implementer: with `T-0001.1` `in_flight` set to an implementer run, running `build` → `factory ticket ready-implementers T-0001` → `[]`, no new `run.started` for `.1`; `git -C ~/factory/clone worktree list | grep -c ticket/T-0001.1` ≤ 1 [NEW]
 52. Head-does-not-contain-main inside the loop: case `review-fix` with `main` advanced by `M` between the push and the join → history shows `ready-for-merge → ready-for-implementer` with `round.pr` unchanged and findings `does not contain main M`; the next implementer input contains that line [NEW]
diff --git a/docs/changelog.md b/docs/changelog.md
index 2635d2e..da2cefe 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -58,5 +58,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 54. After issue #40 (2026-10-04), where sub-tickets parked for three causes that were visible when the work was planned or specified: a NEW check copied from the whole spec already passed at the sub-ticket's own start; an implementer could not change a test an earlier sibling sub-ticket had added to pin its interim behaviour, because only the spec gate's "Tests to change" list authorized a test edit and that test did not exist at the gate; and a spec's Decision overturned an existing test that nobody listed. The planner labels each check NEW or REGRESSION against the sub-ticket's own base, the integration branch with its dependencies merged, not by the parent's label. An earlier sibling names the new test files a later sibling will break under "Interim tests", which the harness does not read. A sub-ticket's "Tests to change" may list a test file an earlier sibling added, as `` `<file>[::<test>]` (added by <sibling ID>): <reason> ``. Before each implementer run, `run start` checks in git that the file was absent at the parent's base and was first added inside a merged sibling's recorded merge; otherwise it refuses with exit 2, writing nothing, with an error that starts `BLOCKED from harness:`, and the build parks the sub-ticket with that error so `resolve --ruling` returns it to its implementer. The preamble and the code reviewer accept such a checked entry. The spec writer lists the tests each behaviour-changing Decision overturns, and critic rubric 1 makes a missing one a finding. A test that existed before the parent's first merge still needs the pinned spec's list. Rejected: letting the implementer edit a test on its own judgement.
 55. After issue #49 (2026-10-04), where the implementer and verifier queued the same declared-path list as the code reviewer: in the store's log, 10 implementer and verifier runs did this, and their lists made up 30 of the 205 items queued so far. The implementer and verifier prompts gain one RULES bullet: a protected path the sub-ticket declares is not an escalation. The code reviewer lists declared paths once for each head it reviews, through its check 6, unchanged. The other two roles may name them in their output, but not under ESCALATIONS. An undeclared protected path, or a change to a declared one that the spec does not describe, still goes under ESCALATIONS from every role. Rejected: the retro's figure of 26 of 139 items, which its own table contradicts with 38.
 56. After issue #48 (2026-10-04), where every approved spec paid for a planner run and every sub-ticket for every gate command, though nine of the thirteen specs planned so far got exactly one sub-ticket, each after a 72 to 302 second planner run that restated it: the small-change lane. A spec that needs one sub-ticket skips the planner. At `ready-for-planner` the build first runs `factory plan whole-spec`, which creates `<parent>.1` from the whole spec, ready for its implementer, naming every scenario of the spec, and logs `plan.skipped`, when the parent has no sub-ticket and no earlier planner run, its latest spec-writer run did not end NEEDS-SPLIT, and its approved spec has no `##` or `###` heading, other than a `### Requirement:` line, that names seams. Otherwise it reports that the planner is needed, writes nothing, and the planner runs as before; it refuses a parent that is not ready for its planner, has a run in flight or has no approved spec, and the build parks that refusal as a harness bug. To force the planner on such a spec, the operator adds a `### Size and seams` heading at the gate. A gate command may also declare `paths`, as git pathspecs. When a reviewer or verifier run starts on a sub-ticket, the harness marks SKIPPED, with the reason, each command whose paths the sub-ticket's diff touches none of, lists it apart from the commands to run, and records it in the run's `meta.yaml` and on the `ci` row, whose PASS or FAIL still comes from the commands that ran. The implementer and the parent-close verifier still get every command, and a malformed entry refuses every build role's run start. This overturns the cut of the path-scoped skip in T-0016's spec; no repository's gate configuration changes. Rejected: the request's trigger of exactly one lettered part, which would have skipped none of the nine.
+57. After issue #41 (2026-10-04), where a code reviewer started the full test suite in the background, ended its turn to wait for it, and so wrote no review, three times in one day, each time on a commit the verifier had already passed; the harness recorded each run as KILLED and parked the ticket as a budget kill, though it enforces no budget and the agent call reports no reason a run stopped. A role run that ends without writing its output is now EMPTY-OUTPUT in `run finish`, never a budget kill, and the workflow keeps the agent's last message with the run (`factory run last-message`). The same role is re-dispatched once, on the same inputs and in the same round; a second EMPTY-OUTPUT in a row parks the ticket as `EMPTY-OUTPUT from <role>` with both runs, and records no result row for that run, so `resolve --redispatch` re-runs only that checker. A thrown agent call keeps its KILLED record and its `agent call failed` park. The shared preamble gains one RUNNING CODE bullet: run every command in the foreground and never end the turn while one is still running. The code reviewer prompt gains a WHAT YOU RUN section: judge the diff by reading it and leave the test suite and the gate commands to the verifier, which runs them on the same head; a narrow command that confirms one finding is allowed. The reviewer's input no longer lists the gate commands; it says the verifier runs them. The routing table gains two EMPTY-OUTPUT rows. Rejected: keeping a budget-kill label for some empty outputs, and a retry counter in the store.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index 7375500..7a4ed2b 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -98,14 +98,15 @@ Rules the table relies on:
 - A round is one checker pass; the first check is round 1. Two loops carry a counter: the spec loop (writer ↔ critic) and the PR loop (implementer ↔ reviewer + verifier). The counter increments when the author re-enters after REVISE, REQUEST-CHANGES, or FAILED. A gate failure, whether CI reports it or the verifier's gate step does, counts: the implementer ran the gates locally before pushing. Rebases and merge-main rounds do not count.
 - The PR loop routes only after CI and both checker results for the current head are recorded. One implementer run then receives all three outputs. Never launch a second implementer run on a branch that already has one in flight.
 - The dispatcher reads a role's trailer by its labels, not by line position. The last `STATUS:` line wins; CONFIDENCE is the next line labelled `CONFIDENCE:` after it, and ESCALATIONS the next line labelled `ESCALATIONS:` after that. Lines between labelled lines are continuation (a wrapped reason, a remark), so a verbose but well-formed verdict routes on its STATUS. A trailer with no CONFIDENCE or no ESCALATIONS line after its last STATUS is a parse failure, which routes as a STATUS not in this table.
-- A non-empty ESCALATIONS line is copied to the human queue without blocking the STATUS route. An ESCALATIONS line that starts with the word `none` followed by end of line or punctuation (so not `None of …`), with prose after it on that line and nothing below it, is empty for routing, and the prose is kept with the run for audit. A `none` line with further lines below it is a real list, copied verbatim from that line on. Only NEEDS-HUMAN, CLARIFY, BLOCKED, ESCALATE, SPEC-DEFECT, a max-round cutoff, a budget kill (piece 3), a parent-close FAILED, and an archive refusal (Spec store: a delta that does not apply, no change folder, or no spec store) park the ticket. A parking STATUS from one checker wins over the other's REQUEST-CHANGES or FAILED; both outputs go to the queue.
+- A non-empty ESCALATIONS line is copied to the human queue without blocking the STATUS route. An ESCALATIONS line that starts with the word `none` followed by end of line or punctuation (so not `None of …`), with prose after it on that line and nothing below it, is empty for routing, and the prose is kept with the run for audit. A `none` line with further lines below it is a real list, copied verbatim from that line on. Only NEEDS-HUMAN, CLARIFY, BLOCKED, ESCALATE, SPEC-DEFECT, a max-round cutoff, a budget kill (piece 3), a second EMPTY-OUTPUT in a row, a parent-close FAILED, and an archive refusal (Spec store: a delta that does not apply, no change folder, or no spec store) park the ticket. A parking STATUS from one checker wins over the other's REQUEST-CHANGES or FAILED; both outputs go to the queue.
+- A role run that ends without writing its output is EMPTY-OUTPUT, whatever stopped it. The agent call reports no reason, so an empty output is never recorded as a budget kill; the harness keeps the agent's last message with the run. The same role is re-dispatched once, on the same inputs and in the same round. A second EMPTY-OUTPUT in a row parks the ticket with both runs.
 - When a human resolves a parked ticket:
   - A question returns to the role that asked, with the answer and that role's previous output (the output that asked it); a requester's CLARIFY answer returns to Triage the same way. When the answer is a standing decision, the human passes `--decision "<line>"` with the answer, or with the close, so that it lands in `decisions.md`.
   - BLOCKED, a critic ESCALATE, and a planner ESCALATE return to the role that emitted them with the ruling, same round, or the human re-scopes (spec gate or writer round reset) or closes.
   - A spec loop at max rounds goes to the spec gate.
   - A parent-close FAILED or SPEC-DEFECT, an archive that does not apply, or a sub-ticket closed by the human, parks the parent: the human amends the spec and re-plans (new sub-tickets under the same parent) or closes the parent.
   - An archive refused for no change folder or no spec store parks the parent the same way, but its spec never entered the spec store: the human closes the parent as applied. Current truth is not updated, and archive appends nothing to `decisions.md`; the human logs any decision with `factory decision add`. If current truth should carry the spec, it is re-intaken as a new ticket.
-  - A PR loop at max rounds, a SPEC-DEFECT, or a reviewer ESCALATE returns to the implementer with the round reset and the human's ruling as findings, or the ticket closes. The human may amend the sub-ticket or the pinned spec first; the amended version is what the implementer and checkers receive. There is no merge-gate override. A budget-killed run re-dispatches the same role on the same inputs, same round (the human may raise that run's budget or amend the sub-ticket first), or the ticket closes. In-flight siblings keep the spec version they received; the human decides whether to re-plan.
+  - A PR loop at max rounds, a SPEC-DEFECT, or a reviewer ESCALATE returns to the implementer with the round reset and the human's ruling as findings, or the ticket closes. The human may amend the sub-ticket or the pinned spec first; the amended version is what the implementer and checkers receive. There is no merge-gate override. A budget-killed run, or a ticket parked on a second EMPTY-OUTPUT, re-dispatches the same role on the same inputs, same round (the human may raise that run's budget or amend the sub-ticket first), or the ticket closes. In-flight siblings keep the spec version they received; the human decides whether to re-plan.
 
 | From | STATUS | Next | Receives |
 |---|---|---|---|
@@ -132,6 +133,8 @@ Rules the table relies on:
 | Gate runner, Reviewer, and/or Verifier | CI FAIL and/or REQUEST-CHANGES and/or FAILED, once all three have reported | Implementer (round +1) if round < {2}, else Human queue | Both checkers' outputs and the CI result |
 | Reviewer | ESCALATE | Human queue | Output |
 | Verifier | SPEC-DEFECT | Human queue | Verifier output |
+| Any role | EMPTY-OUTPUT, the first in a row | The same role again, same round | The same inputs |
+| Any role | EMPTY-OUTPUT, the second in a row | Human queue | Both runs' last messages |
 | Merge gate | Head does not contain current main | Implementer (same round, conflict run): merge main into the branch, or rebase where {force-push allowed} | Conflict output; the new head re-runs CI and both checkers |
 | Merge gate | CI green + APPROVE + VERIFIED on current head + head contains main + piece-8 approvals | Merge; then dispatch sub-tickets that depended on this one. When all sub-tickets have merged, one verifier run on main against the parent's full Acceptance list (every scenario of its pinned delta, with its `verification.md` label). When the parent has one sub-ticket, `main` has not moved since that sub-ticket merged, the sub-ticket's text names every scenario of the parent's pinned delta, and its VERIFIED run checked the merged head against the parent's recorded base, that run stands for the parent-close run and no new run starts. VERIFIED archives the change (Spec store), then closes the parent; FAILED, SPEC-DEFECT or an archive refusal (Spec store: a delta that does not apply, no change folder, or no spec store) parks the parent in the human queue | Parent-close run: pinned parent spec; head = current main; base = the main SHA recorded before the parent's first sub-ticket merged; `{gate commands}` |
 | Weekly audit done, or on demand | — | Retro | Full outputs behind every outcome signal since the last retro (piece 10), current instruction files, every proposal still under evaluation with its metric, and per-role run and outcome counts, broken down by model, for the period and for each prior proposal's window, and the marker ledger: one row per `factory:` comment in the code on the integration branch, with file:line, limit and upgrade trigger, flagged `no-trigger` where it names none, composed by the harness when the retro runs |
@@ -218,6 +221,10 @@ RUNNING CODE
   temporary directory, never the real one: use the wrapper in the
   "Running code" section of your input. That includes every test or
   check command your briefing, ticket or spec gives you.
+- Run every command in the foreground and wait for it to finish.
+  Never end your turn while a command you started is still running:
+  your final message ends your run, and an output you have not yet
+  written is lost.
 - A throwaway HOME does not stop a write to an absolute path. Never
   run anything that could write a protected path outside the
   repository, such as live credentials or production state.
@@ -612,6 +619,12 @@ sub-ticket without collateral damage. You see the diff, the sub-ticket,
 the parent spec, and the repo. You never see the implementer's reasoning
 beyond the PR description.
 
+WHAT YOU RUN
+- Judge the diff by reading it. Do not run the test suite or the gate
+  commands: the verifier runs them on the same head.
+- You may run a narrow command to confirm a specific finding, such as
+  one test or a grep, and cite its output with that finding.
+
 CHECK, IN THIS ORDER
 1. Test integrity: any existing test file changed? Any test weakened,
    skipped, deleted, or rewritten? Any assertion made less specific? Any
diff --git a/docs/prompts/00-preamble.md b/docs/prompts/00-preamble.md
index 2c24a07..9693b64 100644
--- a/docs/prompts/00-preamble.md
+++ b/docs/prompts/00-preamble.md
@@ -42,6 +42,10 @@ RUNNING CODE
   temporary directory, never the real one: use the wrapper in the
   "Running code" section of your input. That includes every test or
   check command your briefing, ticket or spec gives you.
+- Run every command in the foreground and wait for it to finish.
+  Never end your turn while a command you started is still running:
+  your final message ends your run, and an output you have not yet
+  written is lost.
 - A throwaway HOME does not stop a write to an absolute path. Never
   run anything that could write a protected path outside the
   repository, such as live credentials or production state.
diff --git a/docs/prompts/06-code-reviewer.md b/docs/prompts/06-code-reviewer.md
index 38d5596..d391fbb 100644
--- a/docs/prompts/06-code-reviewer.md
+++ b/docs/prompts/06-code-reviewer.md
@@ -3,6 +3,12 @@ sub-ticket without collateral damage. You see the diff, the sub-ticket,
 the parent spec, and the repo. You never see the implementer's reasoning
 beyond the PR description.
 
+WHAT YOU RUN
+- Judge the diff by reading it. Do not run the test suite or the gate
+  commands: the verifier runs them on the same head.
+- You may run a narrow command to confirm a specific finding, such as
+  one test or a grep, and cite its output with that finding.
+
 CHECK, IN THIS ORDER
 1. Test integrity: any existing test file changed? Any test weakened,
    skipped, deleted, or rewritten? Any assertion made less specific? Any
diff --git a/factory/cli.py b/factory/cli.py
index 6535ee6..f9c54d7 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -299,6 +299,16 @@ def _start_build_run(root: Path, cfg: dict, t: dict, meta: dict, d: Path, parent
         meta.update({"branch": t.get("branch"), "base": base, "head": head, "worktree": str(wt)})
 
 
+def run_last_message(a, root, cfg):
+    """Keep the agent's last message with a run that ended EMPTY-OUTPUT, so a human can see why."""
+    d = _run_dir(root, a.run)
+    st = store.read_yaml(d / "meta.yaml").get("status")
+    if st != "EMPTY-OUTPUT":
+        raise Refused(f"{a.run} is {st or 'not finished'}, not EMPTY-OUTPUT: no last message to keep")
+    store.write_text(d / "last-message.md", a.text + "\n")
+    out({"ok": True, "run_id": a.run, "last_message": _rel(root, d / "last-message.md")})
+
+
 def run_cleanup(a, root, cfg):
     d = _run_dir(root, a.run)
     meta = store.read_yaml(d / "meta.yaml")
@@ -332,7 +342,8 @@ def run_finish(a, root, cfg):
     if a.status_override:
         parsed = {"status": a.status_override, "confidence": None, "escalations": []}
     elif not text.strip():
-        parsed = {"status": "KILLED", "confidence": None, "escalations": [], "error": "empty output"}
+        # The agent call reports no reason a run stopped, so an empty output is never a budget kill.
+        parsed = {"status": "EMPTY-OUTPUT", "confidence": None, "escalations": [], "error": "empty output"}
     else:
         parsed = status.parse(text)
         if parsed["status"] is None:
@@ -1440,6 +1451,10 @@ def build_parser() -> argparse.ArgumentParser:
     p.add_argument("--output-file")
     p.add_argument("--status-override")
     p.set_defaults(fn=run_finish)
+    p = rn.add_parser("last-message")
+    p.add_argument("run")
+    p.add_argument("--text", required=True)
+    p.set_defaults(fn=run_last_message)
     p = rn.add_parser("cleanup")
     p.add_argument("run")
     p.set_defaults(fn=run_cleanup)
diff --git a/factory/compose.py b/factory/compose.py
index d85ee69..59aa23f 100644
--- a/factory/compose.py
+++ b/factory/compose.py
@@ -218,12 +218,15 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
         run = [g for (raw, paths), g in zip(gate_entries(cfg), gate_commands(cfg)) if paths is None or raw not in gone]
         where = (f"\n## Where you work\nWorktree: `{meta.get('worktree')}` (branch `{meta.get('branch')}`, "
                  f"base `{meta.get('base')}`, head `{meta.get('head')}`). There is no remote: commit on the "
-                 f"branch; the PR is the branch plus the description you return. Gate commands (run each from "
-                 f"your worktree, exactly as written; each is already wrapped): "
-                 + ("; ".join(f"`{wrap(g, env)}`" for g in run) if run or not skipped
-                    else "none (every gate command is skipped below)") + "\n"
-                 + "".join(f"SKIPPED by the harness for this diff, do not run: `{s['command']}`: {s['reason']}\n"
-                           for s in skipped))
+                 f"branch; the PR is the branch plus the description you return. ")
+        if role == "reviewer":  # the reviewer judges the diff; the verifier runs the gate (doc §6)
+            where += "The verifier runs the gate commands on this head; you do not run them.\n"
+        else:
+            where += ("Gate commands (run each from your worktree, exactly as written; each is already wrapped): "
+                      + ("; ".join(f"`{wrap(g, env)}`" for g in run) if run or not skipped
+                         else "none (every gate command is skipped below)") + "\n")
+        where += "".join(f"SKIPPED by the harness for this diff, do not run: `{s['command']}`: {s['reason']}\n"
+                         for s in skipped)
         parts.append(where)
         if role == "implementer":
             if t.get("merge_refused"):
diff --git a/factory/prompts/preamble.md b/factory/prompts/preamble.md
index 2c24a07..9693b64 100644
--- a/factory/prompts/preamble.md
+++ b/factory/prompts/preamble.md
@@ -42,6 +42,10 @@ RUNNING CODE
   temporary directory, never the real one: use the wrapper in the
   "Running code" section of your input. That includes every test or
   check command your briefing, ticket or spec gives you.
+- Run every command in the foreground and wait for it to finish.
+  Never end your turn while a command you started is still running:
+  your final message ends your run, and an output you have not yet
+  written is lost.
 - A throwaway HOME does not stop a write to an absolute path. Never
   run anything that could write a protected path outside the
   repository, such as live credentials or production state.
diff --git a/factory/prompts/reviewer.md b/factory/prompts/reviewer.md
index a2a7c03..c94b6b9 100644
--- a/factory/prompts/reviewer.md
+++ b/factory/prompts/reviewer.md
@@ -3,6 +3,12 @@ sub-ticket without collateral damage. You see the diff, the sub-ticket,
 the parent spec, and the repo. You never see the implementer's reasoning
 beyond the PR description.
 
+WHAT YOU RUN
+- Judge the diff by reading it. Do not run the test suite or the gate
+  commands: the verifier runs them on the same head.
+- You may run a narrow command to confirm a specific finding, such as
+  one test or a grep, and cite its output with that finding.
+
 CHECK, IN THIS ORDER
 1. Test integrity: any existing test file changed? Any test weakened,
    skipped, deleted, or rewritten? Any assertion made less specific? Any
diff --git a/factory/workflows/build.js b/factory/workflows/build.js
index 1b87d18..48a2dfe 100644
--- a/factory/workflows/build.js
+++ b/factory/workflows/build.js
@@ -63,7 +63,19 @@ async function park(ticket, reason, outputs, phase) {
   log(`${ticket} parked: ${reason}`)
 }
 
+// An EMPTY-OUTPUT run is re-dispatched once, same role, same inputs; a second in a row parks the ticket
+// with both runs. The agent call reports no reason a run stopped, so neither is a budget kill.
 async function runRole(role, ticket, phase) {
+  const first = await runOnce(role, ticket, phase)
+  if (!first || first.status !== 'EMPTY-OUTPUT') return first
+  log(`${role} ${first.runId} (${ticket}): EMPTY-OUTPUT; re-dispatching ${role} once`)
+  const second = await runOnce(role, ticket, phase)
+  if (!second || second.status !== 'EMPTY-OUTPUT') return second
+  await park(ticket, `EMPTY-OUTPUT from ${role}`, [first.runId, second.runId], phase)
+  return null
+}
+
+async function runOnce(role, ticket, phase) {
   const start = await clerk(`${BIN} run start --role ${role} --ticket ${ticket} --model ${MODELS[role]}`, phase, `run start ${role} ${ticket}`)
   if (!start.ok) {
     // A refusal that starts `BLOCKED ` is the harness blocking the run (the sibling-tests check): park
@@ -106,14 +118,18 @@ async function runRole(role, ticket, phase) {
     const sh = `${args.stubs}/${role}-${stubCount[role]}.sh`
     await clerk(`if [ -f ${sh} ]; then (cd ${start.worktree} && sh ${sh}) >/dev/null 2>&1; fi; echo '{"ok": true}'`, phase, `stub script ${role}-${stubCount[role]}`)
   }
-  const killed = out === null || (typeof out === 'string' && out.trim() === '')
-  const fin = killed
-    ? await clerk(`${BIN} run finish ${runId} --status-override KILLED`, phase, `run finish ${role} (killed)`)
-    : await clerk(`${BIN} run finish ${runId}`, phase, `run finish ${role}`)
+  // run finish reads the output file for every run: a missing or blank one is EMPTY-OUTPUT.
+  const fin = await clerk(`${BIN} run finish ${runId}`, phase, `run finish ${role}`)
   if (role === 'reviewer' || role === 'verifier') await clerk(`${BIN} run cleanup ${runId}`, phase, `run cleanup ${role}`)
   if (!fin.ok) { await park(ticket, `harness-bug: run finish ${role}: ${fin.stderr || ''}`, [runId], phase); return null }
   // run finish parked the ticket (the tripwire saw a listed live file change): stop, do not route on STATUS
   if (fin.parked) { log(`${ticket} parked: ${fin.parked}`); return null }
+  // An EMPTY-OUTPUT run keeps the agent's last message, so a human can see why it stopped. A failure
+  // here never parks and never changes the route.
+  const said = typeof out === 'string' ? out.trim() : ''
+  if (fin.status === 'EMPTY-OUTPUT' && said) {
+    await clerk(`${BIN} run last-message ${runId} '--text=${said.slice(-4000).replace(/'/g, "'\\''")}'`, phase, `run last-message ${role}`)
+  }
   log(`${role} ${runId} (${ticket}): ${fin.status}`)
   return { runId, status: fin.status, outputPath }
 }
@@ -134,7 +150,6 @@ async function buildOne(st) {
     if (implemented) {
       const impl = await runRole('implementer', st, 'Build')
       if (!impl) return
-      if (impl.status === 'KILLED') { await park(st, 'budget kill: implementer', [impl.runId], 'Build'); return }
       if (impl.status === 'BLOCKED') { await park(st, 'BLOCKED from implementer', [impl.runId], 'Build'); return }
       if (impl.status !== 'READY-FOR-REVIEW') { await park(st, `harness-bug: unknown STATUS ${impl.status} from implementer`, [impl.runId], 'Build'); return }
       const moved = await clerk(`${BIN} ticket head ${st}`, 'Build', `ticket head ${st}`)
diff --git a/factory/workflows/intake.js b/factory/workflows/intake.js
index 7f0c561..cb10d46 100644
--- a/factory/workflows/intake.js
+++ b/factory/workflows/intake.js
@@ -72,7 +72,19 @@ async function park(reason, outputs, phase) {
   log(`${TICKET} parked: ${reason}`)
 }
 
+// An EMPTY-OUTPUT run is re-dispatched once, same role, same inputs; a second in a row parks the ticket
+// with both runs. The agent call reports no reason a run stopped, so neither is a budget kill.
 async function runRole(role, phase) {
+  const first = await runOnce(role, phase)
+  if (!first || first.status !== 'EMPTY-OUTPUT') return first
+  log(`${role} ${first.runId}: EMPTY-OUTPUT; re-dispatching ${role} once`)
+  const second = await runOnce(role, phase)
+  if (!second || second.status !== 'EMPTY-OUTPUT') return second
+  await park(`EMPTY-OUTPUT from ${role}`, [first.runId, second.runId], phase)
+  return null
+}
+
+async function runOnce(role, phase) {
   const start = await clerk(`${BIN} run start --role ${role} --ticket ${TICKET} --model ${MODELS[role]}`, phase, `run start ${role}`)
   if (!start.ok) { await park(`harness-bug: run start ${role}: ${start.stderr || ''}`, [], phase); return null }
   const runId = start.run_id
@@ -103,13 +115,17 @@ async function runRole(role, phase) {
     await park(`agent call failed: ${role}: ${e && e.message ? e.message : e}`, [runId], phase)
     return null
   }
-  const killed = out === null || (typeof out === 'string' && out.trim() === '')
-  const fin = killed
-    ? await clerk(`${BIN} run finish ${runId} --status-override KILLED`, phase, `run finish ${role} (killed)`)
-    : await clerk(`${BIN} run finish ${runId}`, phase, `run finish ${role}`)
+  // run finish reads the output file for every run: a missing or blank one is EMPTY-OUTPUT.
+  const fin = await clerk(`${BIN} run finish ${runId}`, phase, `run finish ${role}`)
   if (!fin.ok) { await park(`harness-bug: run finish ${role}: ${fin.stderr || ''}`, [runId], phase); return null }
   // run finish parked the ticket (the tripwire saw a listed live file change): stop, do not route on STATUS
   if (fin.parked) { log(`${TICKET} parked: ${fin.parked}`); return null }
+  // An EMPTY-OUTPUT run keeps the agent's last message, so a human can see why it stopped. A failure
+  // here never parks and never changes the route.
+  const said = typeof out === 'string' ? out.trim() : ''
+  if (fin.status === 'EMPTY-OUTPUT' && said) {
+    await clerk(`${BIN} run last-message ${runId} '--text=${said.slice(-4000).replace(/'/g, "'\\''")}'`, phase, `run last-message ${role}`)
+  }
   log(`${role} ${runId}: ${fin.status}${fin.escalations && fin.escalations.length ? ` (+${fin.escalations.length} escalations)` : ''}`)
   return { runId, status: fin.status, escalations: fin.escalations || [] }
 }
diff --git a/tests/factory/test_empty_output.py b/tests/factory/test_empty_output.py
new file mode 100644
index 0000000..ea97fd2
--- /dev/null
+++ b/tests/factory/test_empty_output.py
@@ -0,0 +1,83 @@
+"""A role run that leaves no output is EMPTY-OUTPUT, never a budget kill (T-0032 part C).
+
+The CLI half, black-box through `bin/factory` on a throwaway store: `run finish` labels a run with a
+missing or blank `output.md` EMPTY-OUTPUT, an explicit `--status-override KILLED` still records
+KILLED, and `run last-message` keeps the agent's last message for an EMPTY-OUTPUT run only. The
+workflow half (one re-dispatch, then a park) is checked by the spec's node scenarios.
+"""
+from __future__ import annotations
+
+import json
+import os
+import subprocess
+from pathlib import Path
+
+import pytest
+import yaml
+
+REPO = Path(__file__).resolve().parents[2]
+BIN = REPO / "bin" / "factory"
+
+
+class Store:
+    """A throwaway store with one ticket, T-0001, and one triage run started on it."""
+
+    def __init__(self, tmp_path: Path):
+        self.root = tmp_path / "state"
+        self.env = {**os.environ, "FACTORY_STATE": str(self.root), "PYTHONDONTWRITEBYTECODE": "1"}
+        req = tmp_path / "req.md"
+        req.write_text("# F\n\nDo x.\n")
+        self.ok("ticket", "new", "--file", str(req))
+        self.rid = self.ok("run", "start", "--role", "triage", "--ticket", "T-0001")["run_id"]
+        self.ok("run", "compose", self.rid)
+        self.run_dir = self.root / "runs" / self.rid
+
+    def cli(self, *argv: str) -> subprocess.CompletedProcess:
+        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)
+
+    def ok(self, *argv: str) -> dict:
+        cp = self.cli(*argv)
+        assert cp.returncode == 0, cp.stderr
+        return json.loads(cp.stdout.strip().splitlines()[-1])
+
+    def meta(self) -> dict:
+        return yaml.safe_load((self.run_dir / "meta.yaml").read_text())
+
+    def events(self) -> list[str]:
+        return [json.loads(ln)["event"] for p in sorted((self.root / "log").glob("*.jsonl"))
+                for ln in p.read_text().splitlines() if ln.strip()]
+
+
+@pytest.mark.parametrize("output", [None, "", "  \n\n"])
+def test_run_finish_with_no_or_blank_output_is_empty_output(tmp_path, output):
+    s = Store(tmp_path)
+    if output is not None:
+        (s.run_dir / "output.md").write_text(output)
+    assert s.ok("run", "finish", s.rid)["status"] == "EMPTY-OUTPUT"
+    assert s.meta()["status"] == "EMPTY-OUTPUT"
+    assert "run.finished" in s.events() and "run.killed" not in s.events()
+
+
+def test_status_override_killed_still_records_killed(tmp_path):
+    s = Store(tmp_path)
+    assert s.ok("run", "finish", s.rid, "--status-override", "KILLED")["status"] == "KILLED"
+    assert s.meta()["status"] == "KILLED"
+    assert "run.killed" in s.events()
+
+
+def test_last_message_is_kept_for_an_empty_output_run(tmp_path):
+    s = Store(tmp_path)
+    s.ok("run", "finish", s.rid)
+    text = "The suite is still running; I'll write the review when it ends.\nsecond line"
+    res = s.ok("run", "last-message", s.rid, f"--text={text}")
+    assert res == {"ok": True, "run_id": s.rid, "last_message": f"runs/{s.rid}/last-message.md"}
+    assert (s.run_dir / "last-message.md").read_text() == text + "\n"
+
+
+def test_last_message_is_refused_for_a_run_that_wrote_its_output(tmp_path):
+    s = Store(tmp_path)
+    (s.run_dir / "output.md").write_text("Type: bug\nTitle: x\n\nSTATUS: ACCEPT\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
+    assert s.ok("run", "finish", s.rid)["status"] == "ACCEPT"
+    cp = s.cli("run", "last-message", s.rid, "--text=anything")
+    assert cp.returncode == 2 and "EMPTY-OUTPUT" in cp.stderr
+    assert not (s.run_dir / "last-message.md").exists()
diff --git a/tests/factory/test_gate_paths.py b/tests/factory/test_gate_paths.py
index 8cd4236..c4586b1 100644
--- a/tests/factory/test_gate_paths.py
+++ b/tests/factory/test_gate_paths.py
@@ -120,7 +120,7 @@ def test_a_scoped_command_is_skipped_for_a_diff_that_touches_none_of_its_paths(t
 
 def test_a_diff_that_touches_a_scoped_command_s_paths_runs_it(tmp_path):
     t = Target(tmp_path, SCOPED_GATE, changed="src/a.txt")
-    _, text, meta = t.checker("reviewer")
+    _, text, meta = t.checker()
     line = _gate_line(text)
     assert UNSCOPED in line and "exit 7" in line
     assert _skipped_lines(text) == [] and meta["gate_skipped"] == []

## Human ruling

# Human ruling for the code reviewer on this piece (operator, 2026-10-04, standing for #49 and #41)

For the code reviewer: judge the diff, the PR description and the spec. Do not run the test suite or the gate commands; the verifier runs both on the same commit. A narrow command that confirms one finding is fine, in the foreground. Never end your turn while a command you started is running; your final message is your review, finished in this turn.

The implementer and the verifier work as usual; this ruling changes nothing for them. Placed before the build by the Green session, because the bug this ticket fixes would otherwise stall its own review.

## Human ruling

# Ruling on T-0032.1 (BLOCKED from implementer), operator, 2026-10-06

Operator's choice in the Green session: "Retarget test, keep skip lines".

1. `tests/factory/test_gate_paths.py::test_a_diff_that_touches_a_scoped_command_s_paths_runs_it` is a test to change. It was added by T-0028.1 (`0e99fa7`) after this spec's evidence was taken, so the spec could not list it. Change its `t.checker("reviewer")` to `t.checker()`, which composes a verifier input. The test then checks the same behaviour on the role that still receives the gate commands. Change nothing else in that file.
2. Keep part B.2 as specified for the gate-commands sentence. The reviewer's "Where you work" paragraph says the verifier runs the gate commands and the reviewer does not.
3. Restore the "SKIPPED by the harness for this diff, do not run: `<cmd>`" lines in the reviewer's input, exactly as T-0028 produces them. They are consistent with "you do not run them". The current-truth `gate-commands` requirement ("a reviewer or verifier run ... MUST list that command apart from the commands to run") then stays true, and the pinned spec needs no MODIFIED delta.
4. Re-run the gate commands and record the result. Nothing else changes.
