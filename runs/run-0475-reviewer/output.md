Commit: b1123b0bb2430ff9d23d9302c34e133b522c5aa2 (branch `factory/T-0046.1`, base `34de412`)

## Review

Checked in the role's order. Every claim below is from reading the diff against the pinned spec v3, plus three narrow commands run in the worktree (listed under "What I ran").

1. **Test integrity.** `git diff --stat 34de412...b1123b0` lists eight files, all under `factory/`. No file under `tests/` changed, added or deleted. Spec's Tests to change is `none`; the PR complies.

2. **Correctness, part by part.**
   - **A** `store.ticket_runs` (`store.py:1264-1274`): iterates `sorted(runs.iterdir())`, skips a missing meta and an empty one (`read_yaml` is `yaml.safe_load`, which returns `None` on an empty file, so `not m` catches it as the Decision requires), filters on ticket, optional role and `finished`. Each former `_runs_for(root, tid, role, exclude)` caller becomes `[r for r, _ in ticket_runs(..., finished=True) if r != exclude]`, the same filter. `compose.py:407-408` reads `round` from the yielded meta, as design says. `_last_run_meta` (`compose.py:58-60`) returns the last yielded meta instead of re-reading the file: same value. `critic_rounds`, `_parent_close_verified` (no finished filter, own VERIFIED/head checks, returns the run id) and `clear_scratch` match design A. The three `cli.py` callers of `_runs_for` the spec missed (`_check_drift`, `_planner_needed`, `ticket_head`) were pointed at the same helper with `finished=True`; deleting `_runs_for` as the design orders made this necessary, and the requirement text ("Every caller MUST use that definition") covers it. `grep -rn _runs_for factory bin tests` finds nothing.
   - **B** `store.log_lines` (`store.py:1234-1238`) and `cost._log_records` (`cost.py:920-923`) match design. `_recorded_plan_run` and `log_tail` keep `json.loads` per line, so a malformed line still raises there; `stats._load` keeps its `isinstance`/`ts` filter and sort. `cost.py` still imports nothing from `factory`. `_store_paths` goes from an unsorted to a sorted glob; its result is a set, so nothing a caller sees changes.
   - **C** `store.record_transition` (`store.py:1282-1291`) writes the history entry and event with the same keys in the same order as each replaced site. In `ticket_transition` (`cli.py:157-176`) `frm` is still read at the top for `_check_edge`; nothing between it and the call changes `t["status"]` (`_apply_round` touches only `t["round"]`), so the helper's own `frm` equals it. `t["parked"] = None` is set before the call, as design says. The three hard-coded `"from": "waiting-dependencies"` sites sit inside `status == "waiting-dependencies"` conditions, and `parent_check` inside `status == "planned"`, so the helper's `t["status"]` gives the same value. `approve_spec` and `request_changes` keep their own transitions, as Out of scope requires.
   - **D** `in_flight_runs` is the old comprehension verbatim; `_same_ticket_guard` passes the ticket it loaded by `tid`, so `t["id"] == tid`. Both refusal strings unchanged.
   - **E** `gitops.integration_tip` wraps `rev(repo, integration_branch(cfg, repo))`; the four sites (`cli.py:261`, `335`, `545`, `780`) call it. `_integration_head`'s `except (Refused, OSError)` still encloses the call.
   - **F** `_planner_run`, `_refuse_unless_applies`, `_copy_record`, `_supersede` are the removed lines moved verbatim; each is called at the same point in each branch, and `_supersede` evaluates `t.get("head")` before `_set_aside_failed_rows`, as before.
   - **G** `_harness_bug` is the one f-string the design gives; all 18 sites pass the exact text that sat between `harness-bug: ` and `: {`, including the three conditional expressions and the loop's `what`. The five "unknown STATUS" parks and the `wait` park are untouched. `_cleanup_checker` replaces the three `role in CHECKERS` blocks.

3. **Scope.** Nothing outside the lettered parts. The three extra `cli.py` callers are within A's requirement and are declared in Known gaps.

4. **Silent behaviour changes.** Two, both declared and both within the spec's Decisions or design: an empty `meta.yaml` is skipped (Decision 1), and `clear_scratch` now unlinks a broken-symlink scratch entry and leaves a regular-file one alone (design A spells out exactly this). Neither reaches a refusal, event or park reason.

5. **Security and data safety.** No new paths, no new destructive calls; `rmtree` keeps the same target.

6. **Protected paths.** All eight files are under `factory/**`, which the spec's Risk section declares. Listed under ESCALATIONS for the record.

7. **Coding standard.** Each new helper replaces at least two copies and sits on rung 1 of rule 1. Callers were grepped and named (rule 2). "factory: markers added: none" is stated (rule 3). No new name is a synonym for an existing one (rule 5). No over-building finding: **Lean already.**

8. **PR description.** What changed says in words what changed and leads with the fact that nothing visible changes. One glossing gap, below.

## Findings

- [SHOULD-FIX] PR description: What changed: the first paragraph uses "REGRESSION scenarios" and the table uses "a ticket's runs" and "`meta.yaml`" without saying what they are → a reader new to this project (writing rule 2) cannot tell that REGRESSION/NEW label acceptance checks that must keep or change their output, or that a run is one agent's attempt at one role. One clause each at first use fixes it; the code is unaffected.

## What I ran

In the worktree, inside the fresh-HOME wrapper:
- `uv run --frozen python -c "import factory.cli, factory.drive, factory.stats, factory.compose, factory.specstore, factory.cost"` printed `imports ok`: no name left dangling by the moved code.
- The part-A and part-G grep scenarios printed `0` and `1 1 2`, the spec's expected values.
- `grep -rn _runs_for factory bin tests` printed nothing: the deleted helper has no caller left.
- `git status --short` on the worktree is clean; I removed the `.venv` my import check created there.

## Prior findings

none (round 1)

## Out-of-scope observations

- `record_transition` returns `frm`, as the design specifies, but no caller uses the return value. Not a finding: the design asks for it.

STATUS: APPROVE
CONFIDENCE: high. Every replaced block maps line-for-line onto its helper with the same key order and condition; the implementer's three REGRESSION outputs are byte-identical to the spec's blocks, and my own narrow checks agree with its NEW results.
ESCALATIONS: Protected path `factory/**` touched (`cli.py`, `compose.py`, `cost.py`, `drive.py`, `gitops.py`, `specstore.py`, `stats.py`, `store.py`). The approved spec's Risk section declares `factory/**`, so the merge gate needs no further approval; listed for the record.
