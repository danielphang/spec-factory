## Problem

The harness is the Python code under `factory/` that runs the factory: it records tickets, starts role runs and parks tickets for a human. In that code, seven small operations are written out by hand in two to eighteen places each. Each copy is a place a later fix can miss: a fix to one copy leaves the others with the old behaviour, and nobody notices until a run takes the unfixed path. The cost falls on whoever next changes one of these operations, usually an implementer agent working from a spec, and on the operator who reviews that change.

The seven operations are:
- listing the runs of one ticket, a run being one agent's attempt at one role;
- reading the store's event log, an append-only record of everything the harness did;
- recording a status change on a ticket;
- listing the runs still in flight on a ticket and its sub-tickets;
- reading the newest commit of the integration branch, the branch that finished work merges into;
- four smaller repeats in the command-line module;
- the reason the dispatcher writes when a store command fails and it parks the ticket. The dispatcher is the code in `factory/drive.py` that runs each role and calls the store's commands; a store command is one `bin/factory` call that reads or changes the store, the directory of tickets, runs and logs; a park is a stop that waits for a human, with a reason;

This change gives each operation one definition and points every copy at it. An eighth repeat the request named, the walks over spec Markdown in `specstore.py`, is left as it is (operator, at the spec gate; see Out of scope). Nothing a user or operator sees changes. Every refusal message, park reason, logged event and parse result stays as it is, and the existing tests pass without edits.

## Evidence

I measured everything on `~/dev/spec-factory` at `2b9baf5`. `main` is now at `6ac73f1`, and `git diff --stat 2b9baf5 main -- factory/` prints nothing, so every count and line number below still holds; the only merge since (T-0045.1) changed `tests/` alone. Every command ran through the run's fresh-HOME wrapper. The request took its line numbers at `927bc53`. De-bloat A (T-0044.1) has merged since, so some lines have moved by a few places. Every pattern is still there.

The checks under Acceptance come in two kinds. A NEW check must fail before this change and pass after it; here each one counts the copies of an operation. A REGRESSION check must pass both before and after; here each one pins behaviour that must not move.

**Copies today.** These are the counts that the NEW checks under Acceptance print on `2b9baf5`:

| Operation | Where the copies are | Count today |
|---|---|---|
| 1. Runs of a ticket | `compose.py:16` `_runs_for`, `compose.py:413` (re-reads each meta), `specstore.py:269` `critic_rounds`, `cli.py:1712` `_parent_close_verified`, `store.py:116` `clear_scratch` | 3 runs-directory listings outside `store.py` |
| 2. Event log | `cli.py:671` `_recorded_plan_run`, `cli.py:1760` `log_tail`, `stats.py:72`, `cost.py:129` | 3 `"*.jsonl"` log globs in `cli.py` and `stats.py` |
| 3. Status transition | `cli.py:174-177`, `818-821`, `1000-1003`, `1063-1067`; `approve_spec` at `cli.py:1115-1122` stays as it is | 5 `"ticket.transition"` events in `cli.py` |
| 4. In-flight runs | `cli.py:603`, `drive.py:626` | 2 |
| 5. Integration-branch tip | `cli.py:254`, `328`, `545`, `1693` | `4 0` |
| 6. Smaller `cli.py` repeats | record copies at `1132-1133`, `1198-1199`, `1206-1207`, `1219-1220`, `1248-1249`; set-aside rows plus `results.superseded` at `1196-1197`, `1234-1235`; PLANNED planner-run check at `692-695`, `1651-1654`; validate-and-applies at `620-623`, `1102-1105` | `5 2 2 2` |
| 7. Dispatcher parks | 18 park reasons of the form `harness-bug: <what>: <stderr>` in `drive.py`; checker cleanup at `drive.py:225-226`, `233-234`, `574-575` | `18 3 0` |

The request said the `drive.py` park pattern appears 18 times. `grep -c 'harness-bug:' factory/drive.py` prints 24, because that count also matches the five "unknown STATUS" parks and the `wait` park at `drive.py:529`, which do not carry a command's error text. The 18 that do are the ones this change shares.

**Copies that differ today.** The copies are not all identical, and the design keeps each caller's behaviour:
- Malformed log lines are handled differently. `cost._records` (`cost.py:33-39`) skips a line that is not JSON, and `stats._load` reads through it. `_recorded_plan_run` and `log_tail` call `json.loads` and raise. `log_tail` prints each line's raw text, not a re-encoded event.
- The run filters differ. Each run's directory holds a `meta.yaml`, the run's record (ticket, role, status, when it finished). `_parent_close_verified` does not require `finished`, and the others do. `clear_scratch`, the function that deletes a ticket's finished runs' scratch directories, skips a run whose `meta.yaml` is empty. The other three call `.get` on what `read_yaml` returns, so an empty `meta.yaml` raises `AttributeError` there. `store.write_text` (`store.py:73-75`) is not atomic, so a reader can see an empty `meta.yaml` while a run is being started.

**Behaviour that must not change, measured on the base.** Each REGRESSION check under Acceptance was run on `2b9baf5` and printed the output its THEN states:
- The status-transition scenario prints seven `ticket.transition` events and seven history entries. Four of each come from `ticket transition`, and one each from `ready-implementers` and `parent-check`. The seventh comes from `approve-spec`, which this change leaves alone.
- The refusal scenario prints the "spec not pinned" refusal, the "no recorded planner run" refusal, and the PLANNED refusal from both `subticket add` and `spec tasks`.
- The dispatcher scenario parks three tickets: `harness-bug: run start implementer: …`, `harness-bug: no head for the checkers: …` and `harness-bug: plan whole-spec: …`. Each reason ends in the store command's newline.
- The spec-parser comparison printed `files=264 checks=3918 differ=0`. To show that it can fail, I ran it against a copy of `specstore.py` whose `scenario_blocks` appends one space to each block. It printed `files=264 checks=3918 differ=74`, starting with `scenario_blocks specs/T-0012/v1.md`.
- `uvx ruff check --select F401,F841 factory tests` printed `All checks passed!`.
- The suite scenario printed `577 passed in 296.17s (0:04:56)` and no file names.

**What the tests reach.** No test under `tests/factory/` names any function this change replaces or deletes (`grep -rnE "_runs_for|_recorded_plan_run|critic_rounds|_parent_close_verified|clear_scratch|_set_aside_failed_rows|_integration_head|lines_outside_fences|requirement_blocks|scenario_blocks|_records\b" tests/factory` matches only three test function names). `tests/factory/test_cost_once.py:19` loads `factory/cost.py` by its file path, as module `factory_cost`, and `cost.py` imports nothing from the `factory` package today. The request lets it keep its own log reader for that reason. I did not test whether an import from `factory` would load there. `docs/`, `dev/` and `README.md` name none of these functions.

Current truth: `openspec/specs/harness-code/spec.md` (given in full in my input); the related capabilities are those triage named. No other capability was opened.

## Root cause

Each copy was written when its caller was written, and a later copy did not reuse the earlier one. For example, `cli._parent_close_verified` re-implements `compose._runs_for` with a different filter. The definitions this change adds and the callers each one replaces are listed in design.md.

## Out of scope

- Splitting `cli.py` into modules (T-0047, De-bloat D), which follows this ticket.
- The walks over spec Markdown in `specstore.py`: the section walks in `acceptance_labels`, `decisions_of` and `intent_of`, and the block walks in `requirement_blocks` and `scenario_blocks`. The operator cut this part at the spec gate (2026-10-12). These functions feed the archive step, which writes approved requirements into current truth by exact text, so a one-character slip would corrupt that record silently; sharing them saves about 20 lines. They stay as they are.
- The STATUS-trailer search shared by `status.py` and `subtickets.py` (issue #68).
- The Workflow scripts `factory/workflows/intake.js` and `factory/workflows/build.js` (issue #89). Their park reasons stay byte-identical because `drive.py`'s reasons stay byte-identical.
- `approve_spec`'s transition record (`cli.py:1115-1122`). `test_shepherd.py:79` checks that `approval.recorded` comes before `change.pinned`, and the transition event comes after both.
- The run listing in `stats._load` (`stats.py:66`). It reads every run of a store given by path, in flight or not, and adds fields of its own, so it is not a copy of operation 1.
- The other history appends (`cli.py:988` merge, `:1137` request-changes, `:1166` resolve, `store.py:139` park). They log a different event or none.
- Any change to a refusal message, park reason, event field, verdict, command or document.
- Edits to existing test files. New test files are allowed but not required.

## Open questions

none

## Decisions

- The shared run lister skips a run whose record file is empty, as the scratch clean-up does today. (The record file is `meta.yaml`, which each run's directory holds; the clean-up is `clear_scratch`, the function that deletes finished runs' scratch directories.) The other three callers would otherwise crash with `AttributeError` if they read the record while a run started in parallel is still writing it. This is the one difference from today's behaviour, and it can happen only during that write. Rejected: an iterator that hands back an empty meta for each caller to handle, which would leave the ticket, role and finished filters copied at every caller.
- The event log gets two readers. `store.log_lines` yields raw lines and leaves malformed-line handling to the caller, so `factory log tail` still prints raw text and the command-line readers still raise on a line that is not JSON. A new `cost._log_records` keeps the cost report's skip-malformed behaviour and is shared with the stats report (`stats.py`). `cost.py` stays free of imports from the `factory` package, as the request allows, because a test (`test_cost_once.py`) loads it by file path. Rejected: one strict reader for all four callers, which would change what `factory stats` does with a malformed line.
- The dispatcher's shared piece is a function that formats the park reason, not one that parks. Three of the 18 sites pick their reason inside a conditional expression (`drive.py:192`, `453`, `517`), and a helper cannot `return` from its caller. It is named `_harness_bug` so that it is not confused with `drive.py`'s existing `_fail` (`drive.py:664`), which prints a failure and exits.
- Part H of v2, one walker for spec sections and heading blocks, is cut (operator, spec gate, 2026-10-12): the most risk for the least saving. The spec-parser comparison stays as a REGRESSION check, because part A changes `specstore.critic_rounds`.
- The helpers' names and modules follow the request where it gave them (`store.record_transition`, `store.in_flight_runs`, a gitops helper, `section(text, heading)`). Where it did not, design.md names them.

## Risk

The change refactors eight harness modules: `cli.py`, `compose.py`, `cost.py`, `drive.py`, `gitops.py`, `specstore.py`, `stats.py` and `store.py`. Every ticket, run and archive passes through this code, so a slip changes live behaviour on both instances once the runtime is upgraded.

The archive path's spec parser is not refactored (part H cut). The spec-parser comparison under Acceptance still checks `specstore.py` against the base over every spec in this repo's store, since part A edits `critic_rounds` in that file.

The highest-risk part is G. `resolve --ruling` matches the park prefix `harness-bug: run start implementer:` (`cli.py:1187`), so that reason's text must not change.

Estimated size: about 200 to 300 changed lines, with a net fall of about 70.

Protected paths: `factory/**`

