Commit: 53047c59fcd462510650e752a40d3d294f0486fc (branch `factory/T-0044.1`, base `0ba4e4f637a6ab019774f439727b5a15ddc425cf`, one commit)

## Review

Checked in the order the role requires, by reading the diff and running narrow greps in the review worktree.

1. **Test integrity.** Two files under `tests/` change: `tests/factory/test_instance.py` (lines 109 and 354, each losing only the `force_push_allowed` key) and `tests/factory/fixtures/instance/instance.yaml` (line 22 deleted). Both are listed under the spec's Tests to change, and each edit is exactly the one listed. No assertion is weakened beyond the removed key; the `set(cfg) == set(tpl)` comparison at line 113 is untouched, and both sides lose the key together. No test is skipped, deleted or rewritten.

2. **Correctness, against each lettered part.**
   - A. `run_gates` (`gitops.py`), `STATES` and `load_config` (`store.py`), `OPS` (`specstore.py`) are gone. `grep -rn --include='*.py' -e run_gates -e STATES -e '\bOPS\b' -e load_config factory tests` finds only `instance.load_config`, `def load_config` in `instance.py`, and the unrelated `INTAKE_STATES`/`BUILD_STATES`/`IN_FLIGHT_STATES` constants: nothing names a deleted symbol. `subprocess` is still used at `gitops.py:32`, `:80`, `:86`, so its import correctly stays.
   - B. `force_push_allowed` has zero hits under `factory` and `tests`.
   - C. The merged in-flight condition at `cli.py:207` lists the five roles explicitly, as Decisions require, and sits where the implementer branch was, before the reviewer/verifier branch. The two old branches covered disjoint role sets with identical text, so folding them changes no reachable refusal. `prompt_name` is gone; the prompt path reads `a.role` directly. `ensure_gitignore` now appears at `cli.py:227` (run start, after `_start_build_run` returns at `:225`) and `:1465` (`init`) only. The four blank lines after `build_parser` are two.
   - D. `store.py` docstring is its first line only. `specstore.py:9` ends at "(specs pinned as one text)." `compose.py:420` reads `compose: unknown role {role}`; no test names the old text.
   - E. `def repo_root() -> Path:` at `gitops.py:18`; `instance.repo_root(inst)` at `instance.py:81` is a different function and is correctly untouched. No test patches `gitops.repo_root` (the only `repo_root` in `tests/` is the test name at `test_instance.py:247`), so no monkeypatch lambda breaks on the dropped argument. All 12 callers pass nothing; each still uses `cfg` for `integration_branch`, so no parameter went dead.

3. **Scope.** Every hunk maps to a lettered part. `README.md`, `docs/`, `dev/`, `factory/prompts/` unchanged.

4. **Silent behaviour changes.** One, and the spec accepts it: a build run refused inside `_start_build_run` (for example a failing `environment_sync`) no longer writes the store's `.gitignore` block. `init` and every earlier role's run start already wrote it, and `_ensure_block` is idempotent, so the block is present on any store a build run can reach. The PR's Known gaps states this.

5. **Security and data safety.** Nothing: deletions and a dropped parameter.

6. **Protected paths.** None touched. The spec's Risk declares none.

7. **Coding standard.** Rule 2 met: the PR description names every caller of `repo_root` from a grep. No over-building to tag. Lean already.

8. **PR description.** What changed glosses "harness", "in flight" and "compose" at first use, states the change in words with the per-part detail after, and Known gaps names the one path whose behaviour shifts. Readable at the gate as it stands.

## Findings

none

## Prior findings

Not applicable (round 1).

STATUS: APPROVE
CONFIDENCE: high. Every hunk in the diff maps to a lettered part of the approved spec, greps on the head confirm no remaining reference to any deleted name or to a `repo_root(cfg)` call or patch, and the only test edits are the lines the spec lists.
ESCALATIONS: none
