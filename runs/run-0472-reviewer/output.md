Commit: c8308f2ba30e01db463ee09dff27b778e8819b39 (branch `factory/T-0045.3`, base `1c5a1527f4c1b12b4f24ddb2aca0bfcac0ecfc52`)

## What I checked, in the role's order

1. **Test integrity.** 21 files changed: the new `tests/factory/_fixtures.py` and 20 test files, every one of them listed under the sub-ticket's "Tests to change". `test_instance.py`, `_cli.py`, `conftest.py`, `clean_harness_cli.py` and the four design-block files are not in the diff. No test function is added, removed or edited: every removed hunk in a test file is a module-level helper, constant, class, import or (in `test_shepherd.py`) a docstring line and an empty section header. The helpers that carry assertions (`drifted`, `started`, `assert_refused`, `_build`) move with their asserts intact. I confirmed the move is verbatim: I took every `-` line from the 20 test files and every `+` line of `_fixtures.py` and listed the added lines that were not removed elsewhere. The list is the module docstring, its imports, the eleven section-header comments, and three code lines: `BUILD_STANDIN = '''#!{python}`, `write_text(BUILD_STANDIN.format(` in `BuildStore.__init__`, and `def other_request(tmp_path: Path) -> str:`. Those three are the two renames the PR description declares, nothing else.
2. **Correctness.** Each importer now takes the same object it took before: `test_drive_guard.py` and `test_live_store_guard.py` take the live-store `request` (`r2.md`, "# other") as `other_request as request`; `test_store_branch.py` and `test_store_migrate.py` take the store-branch `request` (`r.md`); `test_build_startup.py` and `test_plan_fields.py` take `js_ok as js`, matching the asserting `js` they imported from `test_subtickets.py`; the `test_instance.py`/`test_p0_cli.py` importers take plain `js`. `FIXTURE_INSTANCE` and `STUBS` are built from `Path(__file__).resolve().parent`, and `_fixtures.py` sits in the same directory, so the paths are unchanged. The module-level names that share one namespace in `_fixtures.py` (`git`, `state`, `head`, `request`, `snapshot`, `spec`, `f`) collide only with methods or with locals that already shadowed them in the original files, so no body resolves a different name than before. The imported pytest fixtures `f` and `target` are module globals in their importers, which is how pytest found them under the old `f = test_spec_amend.f` form too. I ran `ruff check --isolated --select F401,F821,F811,F841` on `tests/factory` in the worktree: 73 findings, all F811 and all "Redefinition of unused `f`/`target`", the imported fixture reused as a test parameter in `test_spec_amend.py` (25), `test_spec_drift.py` (20), `test_drift_siblings.py` (13), `test_live_store_guard.py` (11) and `test_drive_guard.py` (4). No unused or undefined name, so the trimmed imports (`os`, `json`, `sys`, `Path`, `pytest`) were trimmed correctly. The cross-test import command from the Acceptance prints `cross-test imports: 0` on this head.
3. **Scope.** Everything is part D. Two edits are not import lines: the `test_shepherd.py` docstring now says `Shepherd` is in `_fixtures.py`, and the empty "the shepherd" section header is gone. Both are consequences of the move and touch no code. The names moved beyond the D table are the ones the moved bodies need (`SPEC`, `TWO`, `spec`, `FIXTURE_INSTANCE`, `STUBS`, `MAX_SPEC_ROUNDS`, `Run`, `RULE`, the build stand-in) plus `assert_refused` and the live-store `request`, which `test_drive_guard.py` imported from `test_live_store_guard.py` and which the spec's rule ("every name a test file imports from another test file today moves") covers although the table omits them. Not moving them would leave the cross-test count above 0.
4. **Silent behaviour changes.** None. Test code only; the harness is untouched.
5. **Security and data safety.** Nothing new runs or writes; the moved stand-ins write only under `tmp_path`.
6. **Protected paths.** None touched. Sub-ticket declares none.
7. **Coding standard.** A move adds no new helper, type or dependency, so rule 1 has nothing to check. `_fixtures.py` keeps the one `state` copy instead of two (DRY). Lean already.
8. **PR description.** What changed says in words what moved and why, and names the two departures and the table gap up front; Known gaps lists each uncertainty and the marker count. Readable at the gate.

## Findings

None.

## Prior findings

None: round 1.

## Notes for the record

- The implementer's two ESCALATIONS are correct and I repeat them below so the human sees them from the reviewer too. Neither needs a code change: the renames are the smallest change that lets the two `STANDIN`s and the two `request`s share one module, every call site is unchanged, and the alias `other_request as request` keeps the importers' names.
- My verification left one stray file for about a minute: I symlinked `.venv` into the review worktree to run the acceptance command, then removed it. `git status` in the worktree is clean; the head is unchanged.

## Out-of-scope observations

- `MAX_PR_ROUNDS` in `test_shepherd.py:18` is defined and never used (pre-existing, also noted by the implementer).
- `test_store_branch.py:23` keeps its own `RULE`, identical to `_fixtures.py`'s; nothing else imports it.
- Several moved docstrings still name the old file (`test_drive.Store`, `test_instance.STRIP`); prose only.

STATUS: APPROVE
CONFIDENCE: high. The diff is a verbatim move apart from the two declared renames (checked line-set against line-set), imports lint clean, and the cross-test import scenario prints 0 on this head; the suite and the remaining scenarios are the verifier's.
ESCALATIONS:
- Spec departure, for the record: the spec's "with the body unchanged" cannot hold for both members of two clashing pairs once they share one module. `test_drive_build.py`'s `STANDIN` is `BUILD_STANDIN` in `_fixtures.py` (one token changes in `BuildStore.__init__`), and `test_live_store_guard.py`'s `request` is `other_request`, imported back under the old name. Behaviour is unchanged; the spec's D table should be amended to allow the two renames.
- Spec gap, for the record: the D table omits `test_live_store_guard.py`'s `assert_refused` and `request`, which `test_drive_guard.py` imports, and the module-level names the listed bodies depend on. The implementer moved them under the spec's general rule; the table should list them.
