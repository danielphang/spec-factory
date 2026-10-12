Sub-ticket: T-0044.1 (parent T-0044, approved spec v2, `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0044/v2.md`)
Branch: `factory/T-0044.1` in `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0044.1`, head `53047c59fcd462510650e752a40d3d294f0486fc`, one commit on base `0ba4e4f637a6ab019774f439727b5a15ddc425cf` (`main`'s tip when the branch was made).

## What changed

This change only removes and tidies code in the harness, the Python package `factory/` that runs the spec factory. No refusal, verdict, route or log event that a command can reach changes. 8 files, 20 insertions, 57 deletions.

A. **Dead definitions.** These are deleted:
- `run_gates` in `factory/gitops.py`, with its docstring and the two blank lines before it. The file now ends at `remove_worktree(repo, temp)`. `subprocess` is still used at `gitops.py:32` and `:80`, so its import stays.
- `STATES` in `factory/store.py`.
- `load_config` in `factory/store.py`, with one of the two blank-line pairs around it.
- `OPS` in `factory/specstore.py`.

`RESULT_ROLES` and `Refused` stay. Ruff reports no unused import afterwards.

B. **The unread setting.** The line `force_push_allowed: false` is deleted from `factory/instance.template.yaml` and from `tests/factory/fixtures/instance/instance.yaml`. In `tests/factory/test_instance.py`, line 109 drops `and cfg["force_push_allowed"] is False`, and line 354's key tuple drops `"force_push_allowed",`. The tuple still fits on its two lines, so it was not re-wrapped. The `set(cfg) == set(tpl)` assertion at line 113 is unchanged.

C. **Run start, in `factory/cli.py`.**
- The implementer and the intake roles each had an in-flight check with the same refusal text. They are now one check, in the implementer branch's old place, before the reviewer/verifier branch: `if a.role in ("triage", "spec_writer", "critic", "planner", "implementer") and t["in_flight"]:`. ("In flight" means the ticket already has a run that has started and not finished.) The reviewer/verifier branch and every later check keep their order.
- `prompt_name = a.role` is deleted. The role prompt is now read from `PROMPTS / f"{a.role}.md"`.
- `store.ensure_gitignore(root)` is deleted from `_start_build_run`. The call in `run_start` (now `cli.py:227`) and the one in `init` (now `cli.py:1465`) stay.
- The four blank lines after `build_parser` are cut to two.

D. **Stale text.**
- The docstring of `factory/store.py` is now only its first line. The promise of a "commit-and-push" step and "Every write goes through here" are gone.
- `factory/specstore.py`: the sentence now ends at "(specs pinned as one text)." It was not re-wrapped: joining it to the line above would pass 100 characters.
- `factory/compose.py`: the role refusal in compose now reads `compose: unknown role {role}`. Compose is the step that writes a run's input file.

E. **`gitops.repo_root`.** The signature is now `def repo_root() -> Path:`. I grepped every caller (`grep -n 'repo_root' factory/*.py tests -r`) and found 12 calls to `gitops.repo_root(cfg)`: 11 in `cli.py` and 1 in `compose.py:110`. All 12 now call `gitops.repo_root()`. The calls to `instance.repo_root(...)` at `cli.py:1339`, `:1435` and `:1530` and in `instance.py` are a different function and were left alone. In `tests/`, `repo_root` appears only in a test name (`test_instance.py:247`, which tests `instance.repo_root`). No caller's `cfg` parameter became unused: each one still passes `cfg` to `gitops.integration_branch`. So no parameter changed.

`README.md`, `docs/` and `dev/` are unchanged, as the spec says.

## Acceptance results

All commands were run from the worktree through the running-code wrapper (a fresh temporary HOME). The "after" runs were on head `53047c5`. The full "after" output is in `scratch/accept-after.txt`.

| Scenario | Kind | Before (on `0ba4e4f`) | After |
|---|---|---|---|
| The four dead definitions are gone and nothing names them | NEW | `4 0` | `0 0` |
| No harness or test file names the force-push setting | NEW | `4` | `0` |
| Run start carries one intake-and-implementer in-flight refusal, no rename and one store-ignore write | NEW | `2 3 3` | `0 2 2` |
| No harness module has three blank lines in a row | NEW | `1` | `0` |
| The three stale texts are gone | NEW | `3` | `0` |
| The repo-root helper takes no argument and every caller passes none | NEW | `13 0 0` | `0 12 1` |
| The harness has no unused imports or variables (`uvx ruff check --select F401,F841 factory tests`) | REGRESSION | not run (regression) | `All checks passed!`, exit 0 |
| The harness suite passes, and only the force-push test lines change under tests | REGRESSION | not run (regression) | `577 passed in 390.55s (0:06:30)`, then `tests/factory/fixtures/instance/instance.yaml` and `tests/factory/test_instance.py` |
| A second intake run on a ticket is refused with the same text | REGRESSION | not run (regression) | `T-0001 already has run run-0001-triage in flight`, then `exit=2`, then `run-0001-triage` |

Every NEW "before" value matches the value the spec's `verification.md` gives for today.

Gate commands, each run exactly as written from the worktree on `53047c5`:
- `git diff --check main...HEAD`: no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `577 passed in 388.61s (0:06:28)`, exit 0. The output is in `scratch/gate-pytest.txt`.

## Tests added/changed

- `tests/factory/test_instance.py` line 109: removed only `and cfg["force_push_allowed"] is False`. The key no longer exists in the template, so the assertion would raise `KeyError`. This line is listed under the spec's Tests to change.
- `tests/factory/test_instance.py` line 354: removed only `"force_push_allowed",` from the key tuple. The same reason applies, and the line is listed.
- `tests/factory/fixtures/instance/instance.yaml` line 22: deleted the key line. Line 354 compares the fixture's keys with the template's keys, and the line is listed.
- No test was added. The NEW acceptance commands are the checks for this change. They are grep and ruff commands over the source, and they failed before the change as the spec describes. A new test file would also break the suite scenario, which allows only the two files above to change under `tests/`. The existing suite still covers the merged in-flight refusal, as `verification.md` notes, and the second-intake scenario checks its text end to end.

## Known gaps and uncertainties

- The `.gitignore` write removed from `_start_build_run` used to run before the worktree was created. Now the only write at run start comes after `_start_build_run` returns. Suppose a build run is refused after its worktree was created, for example by a failing `environment_sync`. That run start no longer writes the store's `.gitignore` block. In practice the block is already there: `init` writes it, and so does every earlier role's run start on the same store (triage onward). `_ensure_block` is idempotent. The spec's Decisions accept this choice. I did not add a test for this path.
- `uv run` created a `.venv` in the worktree. Git ignores it, and `git status` is clean.
- factory: markers added: none.

## Out-of-scope observations

- The module docstring at `factory/gitops.py:5` says the target repo is `repo_root` (FACTORY_REPO, else the parent of the instance directory). That is still accurate after part E, so it was left alone.
- `docs/design.md` and `dev/build-harness.spec.md` still describe `force_push_allowed`. The spec leaves them on purpose (proposal, Out of scope and Decisions). The live `instance.yaml` files of both instances still carry the key. Deleting it there is the spec's optional operator step.

## Responses to findings

Not applicable (round 1).

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every NEW command failed before the change and passes after, with the spec's exact values. Both gates and all three regression commands pass on head `53047c5`.
ESCALATIONS: none
