Spec critic, T-0031 spec v3, round 1 of this version (the operator's change request `approvals/T-0031/changes-1.md` preceded it; no earlier critic findings were in my input).

What I checked myself, on `~/dev/spec-factory` at `main` = `8929054` (two commits past the spec's `b002c95`: the T-0039.1 merge, which touched only `factory/prompts/*.md` and added `tests/factory/test_turn_economy.py`):
- Every cited harness line: `factory/compose.py` 147-161 (`run_env`), 164-168 (`wrap`), 315-326 ("Where you work", reviewer line at 318-319, SKIPPED lines at 324-325), 20-21; `factory/cli.py` 215-236 (`gate_entries` check, `next_run_id`, `_start_build_run` call, `meta.yaml` write at 225, in-flight append at 236), 269-299 (`_start_build_run`), 1446-1449; `factory/specstore.py` 277-280; `factory/workflows/build.js` 62 and 84; `factory/prompts/reviewer.md` 9; `tests/factory/test_run_isolation.py` 22 (`WRAP`, used by the five named tests, six cases); `tests/factory/test_gate_paths.py` 217 (`want`). All hold. `gitops.remove_worktree`, `gitops.copy_environment_files`, `gitops.add_detached_worktree` exist (`factory/gitops.py` 59, 65, 54). `~/dev/nanobot-upstream/.factory/instance.yaml` lines 25-27 and 54 say what the spec says (read only).
- Tests pinning changed behaviour: `grep -rn -e 'export HOME' -e environment_sync -e instance.template tests/factory/` finds only the two listed lines plus `test_instance.py` 103 and 351, which compare named template keys and would not see a new `environment_sync` key. No test asserts the "Where you work" block's exact ending or `meta.yaml`'s key set. No current-truth capability in my input quotes the wrapper text, and the decision log says nothing about the wrapper or environments.
- Acceptance commands run as given, under the HOME wrapper (no test suite): the wrapper scenario printed two lines `ve=<T31>/venv ph=<T31>/venv fake_python=1 cache=/tmp/t31-cache home=fresh`; the failed-sync scenario printed `implementer: exit=0 named=0 code=0 shell_chars=0 logged=0`, `reviewer: exit=0 named=0 code=0 shell_chars=0 logged=0`, `in_flight=0 checker_checkouts=1 meta=2`; the documents scenario printed `design=0 design_venv=0 build_spec=0 template=0 readme=0 readme_venv=0 prompts=0`; the changelog scenario printed `CONTIGUOUS` then `0`. Each matches the spec's "today" line, so the NEW items fail today for the stated reason.
- Evidence counts: `grep -l VIRTUAL_ENV .factory/store/runs/*/output.md` now matches 32 (10 implementer, 5 reviewer, 11 verifier, 3 spec_writer, 2 critic, 1 triage); the 26 build-role runs match the spec, the sixth own run is the v3 spec writer.
- Not checked: anything that needs the harness suite or the built change (the `408` / `7 failed` counts, the second implementer dispatch after a `KILLED` finish in the implementer scenario, the prototype's THEN outputs). The spec reports them as run; the verifier will see them.

Findings

[SHOULD-FIX] 4 Proposed change C.1 and Decisions, "refused at run start, before any checkout is made"
Problem: C.1 validates `environment_sync` inside `_start_build_run`, which runs after `store.next_run_id` has already created `runs/<id>/` (cli.py:217, store.py:171-175, "Allocate a run id by creating its directory"), so a bad value does not "write nothing": it leaves an empty run directory, unlike the malformed-gate refusal the spec models it on.
Evidence: cli.py:215 runs `compose.gate_entries(cfg)` with the comment "a malformed gate entry refuses here, before a run id is reserved"; `tests/factory/test_gate_paths.py` 179 and 209 pin that refusal as leaving `runs/` unchanged. Part E's case "a non-string `environment_sync` refused before any checkout is made" would pass with an empty directory left behind.
Suggested fix: call `compose.environment_sync(cfg)` beside `compose.gate_entries(cfg)` at cli.py:215, before the run id is reserved, and have part E's case also assert that `runs/` is unchanged.

[SHOULD-FIX] 5 Proposed change F, `dev/build-harness.spec.md` "add one item after I.3"
Problem: part I is a numbered list of six items, and other parts of the build spec cite its numbers (`I.5` at lines 206, 276, 411 and 507; `I.3` at 511), so inserting after I.3 renumbers I.4 to I.6 and breaks those citations.
Evidence: `dev/build-harness.spec.md` 295-302: "### I. Isolated run per role" followed by items 1 to 6; `grep -n 'I\.[0-9]' dev/build-harness.spec.md`.
Suggested fix: append the new item as I.7 (or state that the writer renumbers every cross-reference, which is more change for no gain).

[NIT] 1 Problem, last paragraph, and Evidence
Problem: three figures are one merge stale: `main` is `8929054`, not `b002c95`; the changelog's last entry is 64 (so the new one is 65, which part F's "or the next free number when it merges" already allows); the suite has grown by `test_turn_economy.py`, so `408 passed` is no longer the base count.
Evidence: `git log --oneline b002c95..HEAD`; `grep '^[0-9]*\. ' docs/changelog.md | tail -1` starts `64.`.
Suggested fix: none needed for the design; the implementer should expect the base count to differ, and the verifier should not treat `408` as the target.

No BLOCKING finding. The Problem's first paragraph says what is wrong (a lost first attempt to a broken Python environment) and for whom (the implementer, reviewer and verifier), and the human-facing sections gloss role, harness, wrapper, gate commands, instance, run_env, runtime, build workflow and clerk on first use. "Tests to change" names exactly the two tests the change breaks, with the reason and the replacement text for each. Protected paths are declared and match the design (`factory/compose.py`, `factory/cli.py`, `factory/instance.template.yaml`). The operator's four change-request items are each addressed in Responses, and the two design changes (log file instead of inline output; input line at the end of "Where you work") follow from facts I confirmed in `build.js:62` and `compose.py:318-325`.

Out-of-scope observations
- Part A's PATH filter sets an empty `PATH` when `$VIRTUAL_ENV/bin` is the only entry (`grep -v` prints nothing). Not a realistic shell; noting it beside the empty-entry edge Risk already names.

Prior findings: none (first critic round on v3).

STATUS: APPROVE
CONFIDENCE: medium, every cited path and four acceptance "today" outputs were checked by hand on this checkout, but the prototype's results and suite counts could only be settled by building the change.
ESCALATIONS: none
