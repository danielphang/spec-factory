## Acceptance

- Only the store module lists a ticket's runs → NEW; on `2b9baf5` it prints `3` (`compose.py:20`, `specstore.py:276`, `cli.py:1722`).
- The CLI and the stats report read the event log through a shared reader → NEW; prints `3 0` today (`cli.py:674`, `cli.py:1761` and `stats.py:72` glob the log, and `store.py` has no reader).
- One function records a status transition outside spec approval → NEW; prints `5 0` today.
- Neither spec amend nor the dispatcher builds the in-flight list itself → NEW; prints `2` today (`cli.py:603`, `drive.py:626`).
- One function reads the integration-branch tip → NEW; prints `4 0` today (four call sites in `cli.py`, no helper in `gitops.py`).
- Record copies, row set-asides, planner-run checks and spec apply checks each have one definition → NEW; prints `5 2 2 2` today.
- One line formats a failed-command park and one call cleans up a checker → NEW; prints `18 3 0` today (18 park reasons, three cleanup calls, neither helper defined).
- Status transitions write the same events and history entries → REGRESSION
- Spec pinning and planner-run refusals keep their text → REGRESSION
- The dispatcher parks a refused store command with the same reason → REGRESSION
- The spec parser gives the same result as the base on every spec in the store → REGRESSION
- The refactored harness has no unused imports or variables → REGRESSION
- The harness suite passes and no existing test file changes → REGRESSION

## Responses

- [BLOCKING] Decisions, first paragraph: unglossed `meta.yaml` and `clear_scratch` → FIXED. The first Decision now says "the run's record file" and "the scratch clean-up", then glosses both: `meta.yaml` as the record file each run's directory holds, `clear_scratch` as the function that deletes finished runs' scratch directories. Evidence ("Copies that differ today", run filters) glosses both at their first mention too. The second Decision also now says what `log_tail`, `stats.py` and `test_cost_once.py` are, rather than naming them bare.
- [SHOULD-FIX] Problem and Evidence: "dispatcher", "store command", NEW/REGRESSION → FIXED. Problem bullet 7 glosses the dispatcher (the code in `factory/drive.py` that runs each role and calls the store's commands), a store command (one `bin/factory` call that reads or changes the store) and the store. Evidence opens with a paragraph saying what a NEW check and a REGRESSION check are.
- [NIT] The integration-tip and park-format checks pin "at most one" → FIXED. Each WHEN now also counts the helper's definition: `grep -c '^def integration_tip(' factory/gitops.py` (THEN `1 1`, today `4 0`) and `grep -cE '^def _(harness_bug|cleanup_checker)\(' factory/drive.py` (THEN `1 1 2`, today `18 3 0`). I ran both on `main` (`6ac73f1`) and they printed `4 0` and `18 3 0`. I renamed the park-reason helper from `_failed` to `_harness_bug`, because `drive.py:664` already defines `_fail`, which prints a failure and exits; the rename is recorded in Decisions.
- Out-of-scope observation: `cli.py:999-1003` should be `1000-1003` → FIXED in the Evidence table and design part C. I also corrected `817-821` to `818-821`, where the ready-implementers release sets the status.

## Critic rounds

round 1 · spec v1 · run-0466-critic · REVISE

## Critic review: T-0046 spec v1 (round 1)

What I checked, on `~/dev/spec-factory` at `6ac73f1` (`main`; `factory/` is unchanged since the spec's `2b9baf5`, the only merge since is T-0045.1, which touches `tests/` alone):

- Grounding: every cited path, function and line range in Evidence and design.md exists where the spec says (`compose.py:16` `_runs_for`, `specstore.py:269` `critic_rounds`, `cli.py:1712` `_parent_close_verified`, `store.py:116` `clear_scratch`, `cli.py:671`/`1760`, `stats.py:72`, `cost.py:33-39`/`129`, the five `ticket.transition` sites, `cli.py:603`/`drive.py:626`, the four `rev(repo, integration_branch(...))` sites, the F sites, `drive.py:192`/`453`/`517`/`353`/`529`, `drive.py:226`/`234`/`575`, `specstore.py:102`/`158`/`305`/`324`/`350`, `cli.py:358` `_heading`, `cli.py:1187`, `test_shepherd.py:79`, `test_cost_once.py:19`). All 18 `harness-bug` parks of the shared form read `X.get('stderr') or ''`; the other six (five "unknown STATUS", the `wait` park) are the ones the spec leaves alone. `cost.py` imports nothing from `factory`; `stats.py` imports `_records` from `factory.cost`.
- All eight NEW scenarios run as written on the base print exactly the "today" values the Acceptance list states: `3`, `3 0`, `5 0`, `2`, `4`, `5 2 2 2`, `18 3`, `3 8`. The `0 5` target of the last one is right: of today's eight `lines_outside_fences` loops, five are replaced (lines 107, 164, 307, 332, 356) and three stay (`parse_delta` 128, `scenario_names` 155, the requirement-statement loop 371), plus the two new helpers.
- Three REGRESSION scenarios run as written, fixture files in my scratch directory (`TMPDIR` set there), through the fresh-HOME wrapper: "Spec pinning and planner-run refusals keep their text" printed the four lines the THEN gives; "The dispatcher parks a refused store command with the same reason" printed the three park lines the THEN gives, each ending in `\n`; "The spec parser gives the same result as the base" printed `files=265 checks=3940 differ=0` and nothing after (265 because the store has grown by this spec's v1 since the writer ran it; the THEN is parametric). I did not run the status-transition scenario or the suite.
- Behaviour-preservation by reading: `record_transition`'s four callers all do append-history, save, log in that order with the same fields; `ticket_transition` alone adds `round` to both, which the design passes through. `_blocks` as specified reproduces `requirement_blocks` (boundary at `## `/`### `, `rstrip()+"\n"`) and `scenario_blocks` (boundary via `_heading`, bare `rstrip()`). `section` as specified reproduces all three walks; `acceptance_labels`' fence skip is kept at the caller. `_recorded_plan_run`, `log_tail` and `stats._load` already read files in sorted order, so `log_lines`/`_log_records` change no order; `cost._store_paths` builds a set, so its new ordering is unobservable.
- Tests: no test under `tests/factory` names a replaced or deleted function (the grep matches only three test-function names), and I found no test that pins the `AttributeError` on an empty `meta.yaml` that Decision 1 removes. "Tests to change: none" stands.
- Open tickets: T-0045 (approved, planned, its .1 already merged) edits only `tests/`; this spec edits only `factory/`. The suite scenario's `git diff ... main...HEAD -- tests` is merge-base relative, so it holds whichever order the rest of T-0045 and this ticket merge in. No conflict.

### Findings

[BLOCKING] 6 — Decisions, first paragraph
Problem: The operator's first Decisions sentence hangs on two factory names that nothing has glossed: `meta.yaml` and `clear_scratch`.
Evidence: "The shared run iterator skips a run whose `meta.yaml` is empty, as `clear_scratch` does today." Evidence mentions both (bullet 4 of "Copies that differ today", the table) but says of neither what it is; the operator has to infer that `meta.yaml` is the record a run's directory carries and that `clear_scratch` is the harness function that deletes finished runs' scratch directories. The rubric makes an unglossed system term in the first paragraph of a human-facing section blocking even when a careful reader could work it out.
Suggested fix: Gloss both once at the first mention, e.g. "a run whose `meta.yaml` (the record file in the run's directory) is empty, as `clear_scratch`, the function that removes finished runs' scratch directories, does today", or gloss them in Evidence where they first appear.

[SHOULD-FIX] 6 — Problem (bullet 7), Evidence (paragraphs 1 and 2)
Problem: Three more factory terms appear to the operator without a gloss: "the dispatcher" and "store command" (Problem, bullet 7), and the acceptance labels "NEW"/"REGRESSION" (Evidence, "the counts that the NEW scenarios under Acceptance print", "Each REGRESSION scenario").
Evidence: Read as the gate operator: "the dispatcher" is the driver code in `drive.py` that runs role processes and calls the store CLI; a "store command" is one `bin/factory` call; NEW/REGRESSION are this factory's labels for a check that must fail before the change and one that must keep passing. None of this is said. Not in a section's first paragraph, so not blocking.
Suggested fix: One clause each at first use: "the dispatcher, the code that runs each role and calls the store's commands", "a store command (one `bin/factory` call)", and "NEW scenarios (checks that fail before the change) … REGRESSION scenarios (checks that must keep passing)".

[NIT] 2 — ADDED Requirements, scenarios "One function reads the integration-branch tip" and "One line formats a failed-command park …"
Problem: A THEN of `1` is also satisfied by a wrong fix that adds no helper and leaves one call site, so these two checks pin "at most one" rather than "exactly the helper".
Evidence: Today the regexes match 4 and 18 lines; after the change the one remaining match is meant to be the helper body, but a leftover `gitops.rev(repo, gitops.integration_branch(cfg, repo))` in `cli.py` with a differently written helper also prints `1`. The code reviewer reads the diff, so this is cheap insurance, not a gap that matters.
Suggested fix: Optionally add to each WHEN a count of the helper's definition, e.g. `$(grep -c '^def integration_tip(' factory/gitops.py)` and `$(grep -c '^def _failed(' factory/drive.py)`, with THEN `1 1` / `1 1 1`; or leave as is.

Not raised as findings: the NEW scenarios grep internal names (`specstore.applies(root, deltas)`, `lines_outside_fences(`), which the rubric discourages; this ticket's subject is the code's own shape, and the harness-code current truth and T-0045's Decisions already take that line. The spec-parser comparison compares HEAD with its merge base, so on `main` after merge it compares the file with itself; the spec shows it can fail on a mutated copy, and the verifier runs it on the branch, where it is meaningful.

### Out-of-scope observations
- `cli.py:999-1003` in the Evidence table is `1000-1003` in the file (the `s["status"]` line is 1000). Cosmetic.

round 2 · spec v2 · run-0468-critic · APPROVE

## Critic review: T-0046 spec v2 (round 2)

Scope of this round: whether the three round-1 findings are resolved, and the text the v1→v2 diff changed. Unchanged text was reviewed in round 1 and is not re-reviewed.

What I checked, on `~/dev/spec-factory` at `6ac73f1` (`HEAD` = `main`; `git log 6ac73f1..main` is empty and `git diff --stat 2b9baf5 main -- factory/` prints nothing, so the spec's base still describes the code):

- The two revised NEW WHENs, run as written from the repo root, print the "today" values the spec states: the integration-tip check prints `4 0`; the park-format check prints `18 3 0`. `grep -c 'harness-bug:' factory/drive.py` still prints `24`, matching the Evidence paragraph that explains the 18-of-24.
- `drive.py:664` is `def _fail(result: dict) -> None:`, as the new Decision says; nothing in `factory/drive.py` or `tests/factory/` defines or names `_harness_bug` or `_failed`, so the renamed helper collides with nothing and no test pins either name (the three greps that match "harness_bug" are test-function names about park reasons, not the helper).
- The corrected line ranges hold: `cli.py:818-821` is the ready-implementers release (status set, history append, save, `ticket.transition` log with by `ready-implementers`); `cli.py:1000-1003` is the dependant release in `merge` with by `merge`.
- Read as the gate operator: the first Decision now says "record file" and "scratch clean-up" before it names `meta.yaml` and `clear_scratch`, and glosses both in the same sentence. Problem bullet 7 glosses the dispatcher, a store command and the store. Evidence's new second paragraph defines NEW and REGRESSION checks before the table uses them. The second Decision now says what `factory log tail`, the cost report, the stats report and `test_cost_once.py` are. No new unglossed system term was introduced by the changed text.
- Open tickets: unchanged from round 1. T-0045 edits `tests/` only; this spec edits `factory/` only; the suite scenario's `main...HEAD` diff is merge-base relative and holds in either merge order.

### Findings

No blocking issues.

[NIT] 6 — Problem, bullet 2
Problem: "the store's event log" names the store one bullet before bullet 7 glosses it ("the directory of tickets, runs and logs").
Evidence: Problem bullets 2 and 7. Not a first paragraph, and "store" is near enough to a general term that a technical reader does not stall; recorded so the writer can move the gloss if touching the text anyway.
Suggested fix: Optionally move "the store, the directory of tickets, runs and logs" to its first mention in bullet 2, or leave as is.

### Prior findings (round 1)

- [BLOCKING] 6 — Decisions, first paragraph: unglossed `meta.yaml` and `clear_scratch` → RESOLVED. Both are glossed at first mention in Decisions and again in Evidence.
- [SHOULD-FIX] 6 — Problem (bullet 7), Evidence: "dispatcher", "store command", NEW/REGRESSION → RESOLVED. All three glossed where first used.
- [NIT] 2 — integration-tip and park-format checks pin "at most one" → RESOLVED. Each WHEN now also counts the helper definition; THENs `1 1` and `1 1 2`; today's values `4 0` and `18 3 0` confirmed by running them.

### Out-of-scope observations
- none new. The round-1 observation (`999-1003` → `1000-1003`) is fixed, and the writer's extra correction (`817-821` → `818-821`) is right.

## Verifier results

b1123b0bb2430ff9d23d9302c34e133b522c5aa2 · T-0046.1 · VERIFIED · run-0476-verifier
