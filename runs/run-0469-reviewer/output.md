Commit: a7368d0ff39c534d52cd4d4eecb9d3e463ee95d4 (branch `factory/T-0045.2`, base `6ac73f13f1768bd09a6cc1da3879be8ead51e381`)

## What I checked

Read the whole diff (29 files, +122/−270 by `git diff --stat`; all 28 test files it touches are in the sub-ticket's "Tests to change", and `_cli.py` is the helper module). Confirmed by `git diff --name-only` that nothing outside `tests/factory/` changed (0 paths). I did not run the suite or the gate commands; the verifier does.

1. **Test integrity.** No test function, assertion or expected value changed. Every removed block is a module-level or class-level helper (`approved_parent` in `test_build_startup.py`, `git_repo` in `test_instance.py` and `test_store_setup.py`, 13 `cli`/`ok` pairs, 13 five-call sequences, 11 empty-repository setups) replaced by a call to the shared one. `git diff ... -- tests/factory/test_instance.py | grep -c '^[-+].*assert'` prints `0`: T-0044's two assertions are untouched. The design-block tests in `test_coding_standard.py`, `test_turn_economy.py` and `test_writing_standard.py` are outside the hunks (hunks at lines 35-41, 87-93 and 30-36 respectively); only their fixtures' setup lines change. No skip, xfail or swallowed error added.
2. **Correctness.** `git_repo` (`_cli.py:60-66`) is the `test_instance.py` body verbatim: `mkdir(parents=True, exist_ok=True)`, `git init -q -b main`, empty commit as `t <t@t>`, returns the path. `approved_parent` (`_cli.py:69-77`) runs exactly the five calls design B.2 names and returns `tid`. `CliStore` (`_cli.py:80-90`): `cli` runs `[BIN, *argv]` with `capture_output=True, text=True, env=self.env, cwd=REPO`; `ok` asserts exit 0 with argv and stderr in the message and returns `js(cp)`, which is the same last-stdout-line parse the deleted copies did (`_cli.py:45-46`). The three static acceptance commands, run on this head through the fresh-HOME wrapper, print `REPO=1 BIN=1 run=1 js=1 ticket=1 git_repo=1 approved_parent=1`; `approved-parent sequences: 1 _cli.py:73` and `empty-commit repo setups: 1 _cli.py:63`; and `not CliStore: none` / `own ok: test_environment_sync.py:Target` / `own cli: test_drive.py:Store test_environment_sync.py:Target test_shepherd.py:Shepherd`. Each matches the sub-ticket's THEN. `test_results_commit.py:Store` dropping its `cli` is allowed by the spec ("unless that class sets `self.env` once in `__init__`"); `grep -n 'monkeypatch\|os.environ\|self.root\s*='` on the file finds only the `__init__` lines 27 and 29, so the environment is not rebuilt later. The `test_build_startup.py` and `test_plan_fields.py` callers write the request and spec, create the ticket, then call the shared helper, as the sub-ticket and the Decision ("ticket creation stays with the caller") require.
3. **Scope.** Only parts B and C. `test_whole_spec_plan.py:Parent` keeps its own five-call sequence (the spec-writer-run form, not in the 13) and `test_sibling_tests.py:build`'s bare `git init` stays, both correctly left alone. Unused-import removals follow from the deletions; `uvx ruff check --isolated --select F` on the base tree and on this head report the same 4 pre-existing F811 findings in `test_drive_guard.py` and nothing else, and `--select F401` on the head prints `All checks passed!`.
4. **Silent behaviour changes.** Three, all inside test fixtures and all named in Known gaps: commit identity `t <t@t>` at six former `f <f@x>` sites, `exist_ok=True` in `make_target`, and `CliStore.ok`'s message dropping stdout for `test_critic_approved_changes.py`. `grep` for `f@x|GIT_AUTHOR|author` across the six files finds only `GIT_ID` in `test_environment_sync.py`, which is an environment dict for later commits, not an assertion on the initial commit. None is observable outside the suite.
5. **Security and data safety.** Nothing new; all git calls run inside `tmp_path`.
6. **Protected paths.** None touched.
7. **Coding standard.** Rule 1: each new definition sits on rung 1 (moved from an existing copy). Rule 2: the PR description names the callers of the deleted `approved_parent` and of `git_repo`, found by grep. Rule 3: `factory: markers added: none` is stated. Lean already.
8. **PR description.** What changed glosses the suite, the spec gate and `ok(*argv)` at first use, says in words what moved and why, and quotes each acceptance output with what it shows. Known gaps lists the three behaviour changes and the repeated four lines at five call sites with the Decision that causes them.

Findings: none

Prior findings: none (round 1)

Out-of-scope observations:
- `test_harness_lock.py:54` keeps its own `git(path, *argv)` helper, still used at lines 60, 275 and 281; the parent's Out of scope leaves the `git` variants alone.
- The `# noqa: F401` on `test_spec_amend.py:21` carries `REPO` only for `test_spec_drift.py:26`; ST-3 removes that import and should drop the noqa with it.

STATUS: APPROVE
CONFIDENCE: high. The diff is a mechanical replacement of copied helpers with the shared ones, no test body or assertion changes, and the three static acceptance checks print the sub-ticket's expected output on this head; the suite result rests with the verifier.
ESCALATIONS: none
