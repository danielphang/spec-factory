Commit: a074e95923a5d59d40dd408fad22b302b37783df (branch `factory/T-0028.1`, base `a69aaf48bd386e9c4d04acf3c1b4e9e0b2e79883`, 3 commits)

## What I checked and how

1. **Test integrity.** `git diff --name-only --diff-filter=MD main...HEAD -- tests/` printed nothing: no existing test file is modified or deleted. The only test changes are the two new files `tests/factory/test_gate_paths.py` and `tests/factory/test_whole_spec_plan.py`, which the sub-ticket names. `tests/factory/test_run_isolation.py` and `tests/factory/test_instance.py` are untouched, as the parent's "Tests to change: none" requires.

2. **Correctness, read against design parts A, B and C.**
   - A.1 `factory/compose.py:44-71` `gate_entries`: string → `(cmd, None)`; mapping → checks exactly the four malformed cases the spec lists (non-string non-mapping, unknown key, bad `command`, bad or empty `paths`, `paths: null` included because `"paths" in e` is tested); every refusal names `gate_commands entry <i>` and says a command that always runs omits `paths`. Absent or null `gate_commands` is empty. `gate_commands(cfg)` keeps its signature and `{integration}` substitution (`:80`).
   - A.2 `:83-90` `gate_skips` runs `git diff --name-only base...head -- *paths` only for entries with `paths` and records `{command, status: SKIPPED, reason}` with the 9-char SHAs the spec gives. Git errors propagate from `gitops.git`.
   - A.3 `factory/cli.py:214-215` calls `gate_entries` for `BUILD_ROLES` before `tripwire.baseline` and `next_run_id`, so the refusal reserves nothing. `_start_build_run` (`:277`, `:292-293`) sets `gate_skipped = []` for every build run and the computed list only for a reviewer or verifier that is not a parent close, before `add_detached_worktree`. The base for a non-parent-close checker is the integration branch head, so `base...head` is the sub-ticket's own changes.
   - A.4 `compose.py:214-227`: the run list is built by index over `zip(gate_entries, gate_commands)`, and only an entry with `paths` can be dropped, so an unscoped copy of a skipped command still runs (commit `a074e95`). With no skips, `"; ".join(...)` is unchanged and the appended `"".join(...)` is empty, so the text is byte-identical to today's; `test_implementer_gate_commands_come_wrapped` passing unedited confirms it. The all-skipped text is exactly `none (every gate command is skipped below)`.
   - A.5 `cli.py:617-621` reads `runs/<run>/meta.yaml` only inside the existing `a.role == "verifier" and not a.killed` branch and passes `{"skipped": ...}` only when the list is non-empty; the `ci` status still comes from the `Gate suite:` regex. `factory/store.py:244-249` `record_result` gains `extra` merged into the row, nothing else changes in that file.
   - A.6 `factory/instance.template.yaml:21-25` is comments only; the value stays `gate_commands: []`.
   - B.1 `cli.py:462-522`: `_create_subtickets` is the factored loop; `subticket_add` still runs its dependency and duplicate checks first and prints the same JSON. `plan_whole_spec` refuses in the spec's order (state, in flight, no approved spec), then `_planner_needed` returns the first of the four reasons in the spec's order (`store.subtickets_of`, `compose._runs_for(..., "planner", "")`, latest *finished* spec-writer run's status via `_last_run_meta`, seam heading via `specstore.lines_outside_fences` with `^#{2,3}\s`, the `### Requirement:` exemption and `\bseams?\b` case-insensitive), then the change-folder refusal worded as `spec tasks`, then the writes: sub-ticket `<id>.1` with `label: whole-spec`, source `plan:whole-spec`, `depends_on: []`, `parallel_safe: True`, the parent's spec versions; `plans/<id>.md` and the parent's `plan`; `tasks.md` plus `tasks.written` under an active spec store; `ticket.created` then `plan.skipped` with `ticket`, `subticket`, `reason`. The sub-ticket text matches the spec's template line for line.
   - B.2 `factory/workflows/build.js:210-227`: `plan whole-spec` first; `!ok` parks `harness-bug: plan whole-spec: <stderr>`; `skipped` logs and runs no planner; any other success (including a bare `{"ok": true}`) runs the unchanged planner block; both paths reach `transition(TICKET, 'planned')`. Nothing else in the script changed.
   - C.1 to C.4: the three `docs/design.md` hunks are the routing-table row, row 11 and the `tasks.md` row; no prompt block is touched (`git diff --name-only main...HEAD -- docs/prompts factory/prompts agents` is empty, and the design.md hunks are all table rows). Changelog entry 56 is last and names all five terms. `dev/build-harness.spec.md` edits are at the command list, phase 1 and the `ci` row paragraph. README: "How a ticket moves", step 3 and the "Build, local-only" bullet; the stale sentence is gone; the status date already reads 2026-10-04.

3. **Acceptance commands I ran myself on the worktree** (fresh-HOME wrapper, `TMPDIR` = this run's scratch):
   - `git diff --check main...HEAD` → exit 0, no output.
   - Changelog check → `CONTIGUOUS`, `5`.
   - Documents check → `design=1 gate=1 build=1 readme=1 skipped=1 stale=0 prompts=0`.
   - `git diff --name-only main...HEAD -- .factory | grep -c .` → `0`.
   - Both build-dispatch node scenarios with the T-0023 fixture (extracted verbatim from `.factory/store/specs/T-0023/v2.md`, the block at line 228): `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop`, `park: harness-bug: plan whole-spec: T-0001 has no approved spec`; and `start: planner`, `park: harness-bug: subticket add: stub stop`. Both exactly as the THEN says.
   - Gate suite `uv run --frozen pytest -q -p no:cacheprovider tests/factory` → `4 failed, 350 passed in 393.90s`. The four failures are all in `tests/factory/test_instance.py` (`test_init_refused_outside_a_git_work_tree`, `test_command_outside_any_instance_refused_and_writes_nothing`, `test_no_fallback_even_with_a_store_named`, `test_paths_outside_any_instance`) and are caused by my environment, not the branch: with `TMPDIR` under `.factory/store/runs/...`, pytest's `tmp_path` lies inside the live `.factory/` instance, so the CLI's walk-up finds `/Users/dphang/dev/spec-factory/.factory` instead of "no instance" (the error text in the log says exactly that). Re-run with the default `TMPDIR`, `tests/factory/test_instance.py` → `22 passed in 4.20s`. None of the four touches code this branch changes. All 44 tests of the two new files passed in the full run; the implementer's `354 passed` is consistent with a run whose tmp lies outside the instance.

4. **Scope.** Every changed file is in parts A, B or C. The only file outside the sub-ticket's lettered parts' *declared* path list is `factory/store.py`, which A.5 names in words ("`store.record_result` gains an optional `extra`") but the Risk list omits. See ESCALATIONS.

5. **Silent behaviour changes.** `gate_commands(cfg)` now refuses a malformed entry (via `gate_entries`) where it previously raised `AttributeError` on a mapping; a `gate_commands: null` is now empty instead of a `TypeError`. Both are strict improvements inside the spec's intent. Compose of a retro run (not a build role) would also hit `gate_entries` through `gate_commands` if the config were malformed; the spec's "every implementer, reviewer and verifier run start" refusal is the stated scope and the retro case is only a clearer error, not a lost check.

6. **Security and data safety.** `paths` are passed to git as positional pathspecs after `--`, so a value cannot become a git option. No secrets, no destructive ops. `plan whole-spec` writes only after every refusal (tests snapshot the store before and after each refusal).

7. **Protected paths.** `factory/compose.py`, `factory/cli.py`, `factory/workflows/build.js`, `factory/instance.template.yaml` (declared) and `factory/store.py` (undeclared). Listed under ESCALATIONS.

8. **Coding standard** (`/Users/dphang/dev/spec-factory-harness/docs/coding.md`): nothing to report. New functions carry docstrings that say why, not what; the `bad()` closure keeps the refusal text in one place; no swallowed errors.

9. **PR description.** What changed is in words, glosses planner, checkers, gate commands and clerk command at first use, and Known gaps names every uncertainty I found myself (store.py, README present tense, scoped-duplicate matching, changelog "before" drift). Readable by the operator at the gate.

## Findings

- [NIT] `factory/compose.py:218`: a skipped command is matched by its text (`raw not in gone`), so two *scoped* entries with the same command text and different `paths` both leave the run list when only one is skipped → a configuration nobody has a reason to write (one entry with both path lists does the same), and the SKIPPED lines would show one entry, making it visible. Unscoped copies are safe and tested. The PR description declares this. No change requested.

No BLOCKING or SHOULD-FIX findings. On the code alone this earns APPROVE; the status below is set by check 6, not by a defect.

## Prior findings

none (round 1)

## Out-of-scope observations

- `tests/factory/test_instance.py` (four tests) assumes pytest's `tmp_path` lies outside every `.factory/` instance. A suite run with `TMPDIR` under the live store, as this run's "Scratch directory" rule implies, fails them for that reason alone. Either the briefing's "TMPDIR for the fixtures" should be read as fixtures only (as I read it on the second run), or those tests should set `FACTORY_INSTANCE` to nowhere explicitly. Not this ticket's code.
- `README.md:94-95` and `:471` describe the two skips in the present tense above "Where this can go", which the page's "Ground truth only" rule reserves for behaviour that has run on a real ticket. The approved spec (C.4) asks for the present-tense sentences, and the implementer used the page's existing "is tested, and has not yet run on a real ticket" hedge, which `main` already uses twice. Spec and page rule conflict; the spec, human-approved, wins here. The operator may want the README rule to say that a spec can place a tested-but-unrun behaviour above the line with that hedge.
- `factory/workflows/build.js` `meta.phases[0].detail` still says the planner decomposes the spec; B.2 says nothing else in the script changes, so the implementer was right to leave it.

STATUS: ESCALATE
CONFIDENCE: high, every acceptance command I re-ran prints its expected text on `a074e95`, the full suite passes apart from four environment-caused `test_instance.py` failures that pass with the default temp directory, and the only open point is a protected-path declaration, not a defect.
ESCALATIONS:
- `factory/store.py` (protected, class harness) is changed on this branch: `record_result` gains the optional `extra` parameter (`factory/store.py:244-249`, 3 lines). The parent spec's design part A.5 asks for exactly this change in words, but neither the parent's Risk list nor the sub-ticket's "Protected paths" list names the file, so under check 6 the sub-ticket does not declare it. The implementer flagged the same gap. The operator decides at the gate: accept the change as part of A.5 (the merge gate then needs the human approval row for the declared harness paths anyway), or ask for `skipped:` to be written another way. The code is otherwise ready to merge.
- Declared protected paths touched, class harness, for the merge gate's record: `factory/compose.py`, `factory/cli.py`, `factory/workflows/build.js`, `factory/instance.template.yaml` (comments only; value unchanged). New files under `tests/factory/` as the Risk list says.
