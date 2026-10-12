Commit: a7368d0ff39c534d52cd4d4eecb9d3e463ee95d4 (branch `factory/T-0045.2`, base `6ac73f13f1768bd09a6cc1da3879be8ead51e381`)

How I ran it. I ran everything through the fresh-HOME wrapper. The PR side ran in the run worktree `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0469-verifier/wt`, whose `.venv` I made with `uv sync --frozen`. The base side ran in `git archive 6ac73f1` extracted to `scratch/base`, with a symlink to the same `.venv`. I copied each command verbatim into a scratch script. The NEW-1 and NEW-3 commands came from the sub-ticket. The parent's scenario commands came from `specs/T-0045/v2.md` lines 222, 230, 235 and 243. I checked with `diff` that the NEW-1 text in the sub-ticket matches the copy in v2.md line 218.

Per criterion:
- NEW | "The shared constants and wrappers are defined once" (sub-ticket command) | base: `REPO=1 BIN=1 run=1 js=1 ticket=1 git_repo=2 approved_parent=1`. It fails for the reason the spec states: `git_repo` is still copied in two files. | PR: `REPO=1 BIN=1 run=1 js=1 ticket=1 git_repo=1 approved_parent=1` | PASS
- NEW | "The approved-parent and empty-repository setups are written once" (v2.md:222) | base: `approved-parent sequences: 13`, listing the 13 sites the plan names (test_build_startup.py:22, test_drive_build.py:65, test_environment_sync.py:58, test_gate_paths.py:56, test_redispatch_rows.py:34, test_replan.py:43, test_run_isolation.py:62, test_sibling_tests.py:113, test_spec_amend.py:111, test_subtickets.py:75/147/181, test_superseded_plan.py:46), and `empty-commit repo setups: 11`, listing 11 sites, none in `_cli.py` | PR: `approved-parent sequences: 1 _cli.py:73` and `empty-commit repo setups: 1 _cli.py:63` | PASS
- NEW | "the 14 classes share one `cli`/`ok` pair" (sub-ticket command) | base: all 14 classes on `not CliStore:`, 13 on `own ok:` and 13 on `own cli:`, as the sub-ticket says | PR: `not CliStore: none` / `own ok: test_environment_sync.py:Target` / `own cli: test_drive.py:Store test_environment_sync.py:Target test_shepherd.py:Shepherd` | PASS. `test_results_commit.py:Store` is correctly absent from the third line: it now sets `self.env` once in `__init__` (line 29). Nothing in that file reassigns `self.root` or changes `os.environ` after that, so the per-call environment it used to build was always the same.
- REGRESSION | "Only the duplicate test and its assertions are gone" (v2.md:230) | base: not run | PR: `pair: 2`, `removed: 1`, `removed tests/factory/test_p0_cli.py::test_run_finish_without_output_is_killed`, `added: 0`, `missing: 2`, then `missing test_p0_cli.py::test_run_finish_without_output_is_killed: assert cp.returncode == 0 and js(cp)['status'] == 'KILLED'` and `missing test_p0_cli.py::test_run_finish_without_output_is_killed: assert yaml.safe_load((store / 'runs' / rid / 'meta.yaml').read_text())['status'` (stderr also carried three `tar: Failed to set default locale` lines, which the spec says to ignore) | PASS
- REGRESSION | "The suite is shorter" (v2.md:235) | base: not run | PR: `pairs: 2; test lines before: 19293, after: 19018, change: -275` | PASS
- REGRESSION | "A suite run in a fresh clone passes and adds nothing to the checkout" (v2.md:243) | base: not run | PR: `576 passed in 588.45s (0:09:48)`, then `paths changed: 0` with nothing after it | PASS

Gate suite: PASS
- `git diff --check main...HEAD` (in the worktree, `main` = `6ac73f1` = base): no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `576 passed in 588.53s (0:09:48)`, exit 0.

Scope checks (read from the diff, not the PR description):
- `git diff --stat 6ac73f1 HEAD`: 29 files changed, 122 insertions and 270 deletions, all under `tests/factory/`. No path outside it changed.
- The design-block tests are untouched. The only hunks in `test_coding_standard.py` (block at :72), `test_turn_economy.py` (:49) and `test_writing_standard.py` (:63) are the import line and the fixture's setup, at lines 18/38, 18/90 and 17/33.
- `test_instance.py` changes only at its import line (16) and the deleted `git_repo` (21-28), so T-0044's lines 109 and 354 are untouched.
- Every module-level `approved_parent` caller passes a `js` that is `js_ok`. Four files import `js_ok as js` from `._cli`: test_superseded_plan, test_subtickets, test_redispatch_rows and test_replan. test_build_startup and test_plan_fields get `js` from `test_subtickets`, whose `js` is `js_ok`. So the exit-0 check at each of the five steps holds at every site.
- The remaining `"approve-spec"` calls that are not `approved_parent` calls are in sequences the scenario or the sub-ticket leaves out. Each has an assert, an `--edit`/`--version` argument, a `cp =` capture, or other work between the steps: test_spec_store, test_p0_cli, test_spec_drift, test_drift_siblings, test_capability_index, test_resolve_rulings, test_superseded_plan:60, and the class methods in test_critic_approved_changes, test_merge_protected_paths, test_shepherd and test_whole_spec_plan.

Probes (a scratch script, `scratch/probe.py`, loads `tests/factory/_cli.py` from the worktree with bytecode off):
- `git_repo` on a nested path that does not exist yet → the path is created, branch `main`, 1 commit by `t <t@t>`, and the call returns the path → OK
- `git_repo` called twice on the same path → no error, 2 empty commits. The old `test_instance.py` copy does the same → OK
- `git_repo` on an existing non-empty directory that is not a repository → 1 empty commit, nothing tracked, no error → OK
- `git_repo` on a path with a space in it → 1 commit → OK
- `approved_parent` with an `ok` that only records its calls, a string spec and tid `T-0042` → exactly 5 calls in the spec's order, `spec add T-0042 --file /x/s.md`, last call `approve-spec T-0042`, returns `T-0042`. Nothing is special-cased to `T-0001` → OK
- `approved_parent` with an `ok` that raises on its third call → the error propagates after 3 calls and no later step runs → OK
- `CliStore` subclass that never sets `self.env` → `AttributeError: 'C' object has no attribute 'env'` at the first `cli` call. A loud failure, as intended, because a subclass must build its environment → OK
- `CliStore.ok("no-such-command")` against the real `bin/factory` → `AssertionError` whose message starts `no-such-command: usage: factory ...`, which is the argv plus stderr, as design C.1 says → OK

Disclosed changes I confirmed in the diff:
- The initial-commit identity changes from `f <f@x>` to `t <t@t>` at six sites (for example, `test_environment_sync.py` used `self.git` with `GIT_ID`).
- `test_critic_approved_changes.py`'s `ok` failure message loses stdout.

Neither change affects an assertion, and the suite passes.

Out-of-scope observations:
- `test_spec_amend.py` keeps `REPO` with `# noqa: F401` only because `test_spec_drift.py` imports it from there. ST-3 should remove it.
- A full suite run took 9m48s here. I ran the gate and the fresh-clone run at the same time; the spec measured 4m43s.

STATUS: VERIFIED
CONFIDENCE: high. All three NEW commands fail on base for the reasons the spec states and pass on the PR. All three REGRESSION commands and both gates pass on a7368d0. The probes show the helpers are not special-cased to the tested inputs.
ESCALATIONS: none
