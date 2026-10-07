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

