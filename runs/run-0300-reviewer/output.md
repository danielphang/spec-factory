Commit: a074e95923a5d59d40dd408fad22b302b37783df (branch `factory/T-0028.1`, base `d3973c12128a9c1b4a7069c97939d5da5b34742c`, 3 commits: `0e99fa7`, `11a6172`, `a074e95`)

Round 2. The head is unchanged since round 1 (run-0298), so this round re-checks the prior findings and the one escalation against the human ruling, and re-reads the diff for anything round 1 missed. Per the ruling I did not run the suite or the gate commands; the verifier (run-0299) ran them on this head and returned VERIFIED.

## What I checked and how

1. **Test integrity.** `git diff --stat main...HEAD` in the worktree lists 11 files; the only files under `tests/` are the two new files `tests/factory/test_gate_paths.py` (+226) and `tests/factory/test_whole_spec_plan.py` (+228). No existing test file is modified or deleted, as the parent's "Tests to change: none" requires.

2. **Correctness, re-read against parts A, B and C** (file:line in the worktree):
   - `factory/compose.py:44-71` `gate_entries`: the four malformed cases of A.1 each raise `store.Refused` naming `gate_commands entry <i>`, and the text says a command that always runs omits `paths`. `paths: null` is refused because the check is `"paths" in e`, not `e.get("paths")`. `:80` `gate_commands` keeps its signature and `{integration}` substitution. `:83-90` `gate_skips` runs `git diff --name-only base...head -- *paths` only for scoped entries; `gitops.git` (`factory/gitops.py:31-35`) raises `Refused` on a non-zero exit, so a bad pathspec propagates as A.2 asks.
   - `factory/cli.py:214-215`: `gate_entries` runs for `BUILD_ROLES` (`cli.py:25`) before `tripwire.baseline` and `store.next_run_id`, so the refusal reserves nothing. `:277` and `:292-293`: `gate_skipped` is `[]` for every build run and the computed list only for a non-parent-close reviewer or verifier, before `add_detached_worktree`.
   - `compose.py:214-227`: the run list is built over `zip(gate_entries(cfg), gate_commands(cfg))`, both derived from `gate_entries`, so the pairing is by index and only an entry with `paths` can be dropped. With no skip, the joined text and the empty `"".join` leave the block byte-identical to today's.
   - `cli.py:617-621`: `skipped:` is added to the `ci` row only inside the existing unkilled-verifier branch, only when `a.run` is set, `meta.yaml` exists and `gate_skipped` is non-empty. `factory/store.py:244-249`: `record_result` merges `extra` into the row; nothing else in the file changes.
   - `cli.py:462-522`: `plan_whole_spec` refuses in the spec's order (state, in flight, no approved spec), then `_planner_needed` returns the first of four reasons in the spec's order. `compose._runs_for` (`compose.py:14-24`) and `_last_run_meta` (`:39-41`) both read only finished runs, which matches B.1's "latest finished spec-writer run"; an in-flight planner run is caught by the in-flight refusal before it. The seam check uses `specstore.lines_outside_fences` (`specstore.py:77-86`), skips `### Requirement:` lines and matches `\bseams?\b` case-insensitively. The writes follow: `_create_subtickets` with `label: whole-spec`, source `plan:whole-spec`; `plans/<id>.md` and the parent's `plan`; `tasks.md` and `tasks.written` under an active spec store; `plan.skipped` last. The sub-ticket text matches the B.1 template line for line; the parent ticket's `spec`, `in_flight` and `title` keys all exist on every ticket record (`store.py:192-213`).
   - `factory/workflows/build.js:210-227`: `plan whole-spec` first; a refusal parks `harness-bug: plan whole-spec: <stderr>`; `skipped` runs no planner; any other success runs the unchanged planner block; both reach `transition(TICKET, 'planned')`.
   - C.1 to C.4: design-doc hunks are three table rows and no prompt block; changelog entry 56 is last and names `paths`, SKIPPED, `plan whole-spec`, NEEDS-SPLIT and seams and records the T-0016 overturn; build spec and README edits are at the places C.3 and C.4 name. The verifier's VERIFIED on this head covers the acceptance commands.

3. **Scope.** Every changed file is in parts A, B or C. `factory/store.py` is the one file outside the declared protected-path list; the human ruling accepts it as part of A.5.

4. **Silent behaviour changes.** As round 1 said: a malformed or null `gate_commands` now refuses cleanly where it raised `AttributeError` or `TypeError`. Inside the spec's intent. Nothing new found.

5. **Security and data safety.** `paths` go to git after `--`, so a value cannot be read as an option. `plan whole-spec` writes only after every refusal. No secrets, no destructive operations.

6. **Protected paths.** `factory/compose.py`, `factory/cli.py`, `factory/workflows/build.js`, `factory/instance.template.yaml` (declared, class harness) and `factory/store.py` (undeclared, accepted by ruling). Listed under ESCALATIONS for the merge gate's record.

7. **Coding standard.** Rule 1: `_create_subtickets` is a factoring of an existing loop, `gate_skips` reuses `gitops.git`, `gate_entries` is the one parser both `gate_commands` and `run_start` use. Rule 2: the PR description lists every caller of each changed function. Rule 3: "factory: markers added: none" is stated. Lean already.

8. **PR description.** What changed leads with what is removed and for whom, glosses planner, checkers, gate commands and clerk command at first use, and Known gaps names each uncertainty in words. Readable at the gate.

## Findings

- [NIT] `factory/compose.py:218`: a skipped command is matched by its text (`raw not in gone`), so two scoped entries with the same command text and different `paths` both leave the run list when only one is skipped → a configuration nobody has a reason to write, since one entry with both path lists does the same, and the SKIPPED lines would show one entry, making it visible. Declared in the PR description's Known gaps. No change requested.

No BLOCKING or SHOULD-FIX findings. I found nothing in round 2 that round 1 missed.

## Prior findings

- [NIT] `factory/compose.py:218` scoped-duplicate matching: UNRESOLVED by design, declared, no change requested; it stays a NIT.
- ESCALATION, `factory/store.py` undeclared protected path: RESOLVED by the human ruling of 2026-10-05, which accepts the change as part of design part A.5 and names the Risk-list omission a spec gap, not a defect.

## Out-of-scope observations

- The parent spec's Risk list should have named `factory/store.py`; the ruling records this as a spec gap. A later retro may want the spec writer's Risk section to list every file a design part names in words.
- `tests/factory/test_instance.py` (four tests) assumes pytest's `tmp_path` lies outside every `.factory/` instance, so a suite run with `TMPDIR` under the live store fails them for that reason alone (round 1's note). Not this ticket's code.
- `factory/workflows/build.js` `meta.phases[0].detail` still says the planner decomposes the spec; B.2 says nothing else in the script changes, so leaving it was right.

STATUS: APPROVE
CONFIDENCE: high, the head is the one round 1 read line by line, the one open point was a protected-path declaration and the operator has ruled on it, and the verifier passed every gate and acceptance command on this head.
ESCALATIONS:
- Declared protected paths touched, class harness, for the merge gate's record: `factory/compose.py`, `factory/cli.py`, `factory/workflows/build.js`, `factory/instance.template.yaml` (comments only; value unchanged). `factory/store.py` (3 lines, `record_result` gains `extra`) is undeclared but accepted by the operator's ruling of 2026-10-05 as part of design part A.5. The merge gate still needs the human approval row for these paths.
