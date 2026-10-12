Commit: 3478d1fddf4b207fdf0a04ba34ae5459ec11968c (branch `factory/T-0045.1`, one commit on base `2b9baf506852d6f74124b1f5eadbdd84f6bad52b`)

## What I checked and how

All commands ran from the review worktree through the fresh-HOME wrapper; scripts are in `scratch/`.

1. Test integrity. `git diff --name-only 2b9baf5..HEAD | grep -v '^tests/factory/'` printed nothing: every changed path is under `tests/factory/`, and all 32 are listed under the sub-ticket's "Tests to change" (31 listed files plus the new `_cli.py`). My own AST comparison of every function and class body at any depth, base against head (`scratch/bodies.py`), printed `changed=0 removed=31 added=7`. The 7 added are `_cli.py`'s `cli`, `js`, `js_ok`, `run`, `run_env`, `ticket`, `tree`. The 31 removed are 30 module-level helper copies and `test_p0_cli.py::test_run_finish_without_output_is_killed`, the one deletion the parent's Decision names. No surviving body changed, so the four design-block helpers (`test_writing_standard.py:63`, `test_coding_standard.py:72`, `test_turn_economy.py:49`, `test_decision_log.py:248`) and T-0044's two assertions in `test_instance.py` are byte for byte as before. No assertion was weakened; the only assert-bearing helper that moved, the exit-0 `js`, became `js_ok` and every file whose copy asserted (`test_redispatch_rows`, `test_replan`, `test_resolve_rulings`, `test_store_setup`, `test_subtickets`, `test_superseded_plan`) imports `js_ok as js`, so its callers still get the check.
2. Correctness of the moved bodies. Read against the diff: `cli`, `STRIP`, `CLEAN_CLI`, `tree` are identical to `test_instance.py`'s; `run` is `test_p0_cli.py`'s with `stdin=None` (`subprocess.run(input=None)` is its default, so the plain-form callers behave as before); `run_env` is `test_redispatch_rows.py`'s; `ticket` gained the `tid="T-0001"` default that `test_decision_log.py`'s `ticket(store)` calls need. `_cli.py` is not named `test_*`, so pytest does not collect it (`factory/cli.py` `TEST_FILE_RE` also treats it as a helper file).
3. Imports. `scratch/imports.py`: no import in a changed file is unused except `test_p0_cli.py:13` `REPO`, which carries `# noqa: F401` and is re-exported for `test_role_inputs.py`. All 154 relative imports across `tests/factory` resolve to a module-level name of their source module; my script flagged `V1`/`V2` of `test_spec_amend.py`, but they are a tuple assignment at line 55 (my script does not count that form) and the diff did not touch that line (base line 56, same text). A crude undefined-name scan of the changed files (`scratch/names.py`) found none, so the stdlib imports the implementer removed (`os`, `json`, `subprocess`, `sys`, `yaml`) were used only by the deleted copies.
4. Interim acceptance. The parent's "defined once" command on this head printed `REPO=1 BIN=1 run=1 js=1 ticket=1 git_repo=2 approved_parent=1`, the sub-ticket's expected interim value.
5. Scope. The sub-ticket keeps the `cli` of `test_store_setup.py` (line 28, no launcher split) and `test_harness_lock.py` (line 44, takes a harness argument); both stay. `git_repo` stays in `test_instance.py` and `test_store_setup.py` for ST-2. Nothing from parts B, C or D was done.
6. Silent behaviour changes. Two, both declared under Known gaps and both what the spec asks for: (a) `STRIP` in five files now also strips `FACTORY_DISPATCH`, because the spec moves `test_instance.py`'s six-name tuple unchanged and has every file import it; none of the five sets or reads that variable. (b) `conftest.py` now sets `PYTHONDONTWRITEBYTECODE=1` in the pytest process and `sys.dont_write_bytecode = True`, under one comment line, as the parent's Decision says. The implementer reports `paths changed: 0` on the fresh-clone check; the verifier confirms.
7. Security and data safety: test code only, no new paths outside `tmp_path`, no secrets. Protected paths: none touched.
8. Coding standard: `_cli.py` adds only names the spec lists (rule 1, rung 1: moved from this repo); one name per concept (rule 5). Rule 4: Lean already.
9. PR description: What changed says in words what moved and why; Known gaps name the two deviations with their effect. Terms are glossed at first use (`tests/factory/`, `clean_harness_cli.py`, `FACTORY_DISPATCH`).

## Findings

- [NIT] PR description: What changed, A.2 and Known gaps 1 and 3: `ST-2` and `ST-3` are used without saying what they are → a reader new to the plan has to open it to learn that these are the next two sub-tickets of T-0045 (parts B+C and part D). One parenthetical at first use fixes it (writing standard rule 6).

Lean already.

## Out-of-scope observations

- The parent spec names only `test_store_setup.py` and `test_harness_lock.py` as `cli` functions that stay, but three more module-level call wrappers have differing bodies and were correctly left alone: `test_coding_standard.py:24` and `test_turn_economy.py:76` (`_cli`) assert exit 0 on every call, so swapping them would drop an assertion from module fixtures; `test_writing_standard.py:23` has the same body as `test_store_setup.py`'s, with no launcher split. The parent's acceptance count does not include `cli`, so no scenario is affected. The planner may want ST-2 or a later ticket to record a decision for these three.
- `test_decision_log.py` still imports `yaml` and `json` after its `ticket`/`js` copies left; both are still used elsewhere in the file (my scan found no unused import), so nothing to do.

Prior findings: n/a (round 1)

STATUS: APPROVE
CONFIDENCE: high. I compared every function and class body between base and head myself (0 changed, exactly the 31 expected removals), confirmed all relative imports resolve on this head, and ran the interim "defined once" check; I did not run the suite or the fresh-clone check, which the verifier runs on this head.
ESCALATIONS: none
