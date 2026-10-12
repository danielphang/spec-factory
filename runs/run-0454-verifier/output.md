Commit: 53047c59fcd462510650e752a40d3d294f0486fc (verifier worktree `run-0454-verifier/wt`, detached at that commit, clean). Base: 0ba4e4f637a6ab019774f439727b5a15ddc425cf, which is also `main`'s tip and the merge-base. I checked the base out as a temporary worktree in this run's scratch directory and removed it afterwards. `git diff --stat` base..head shows the 8 files and 20+/57- that the PR description gives. The diff matches the one in my input.

Every command ran through the running-code wrapper (a fresh temporary HOME). I put the NEW commands verbatim into `scratch/new.sh` (quoted heredoc, so the text is unchanged) and ran it from each checkout.

Environment note: the verifier worktree had no `.venv`. On the first try, the second-intake scenario failed with `exit=1` and no `runs` directory. The cause was `ModuleNotFoundError: No module named 'yaml'`: `bin/factory` fell back to the system `python3`. I ran `uv sync --frozen`, the install step the briefing names, and reran the scenario. That is an environment precondition, not a defect in the change. The result below is from the rerun.

Per criterion:
- NEW | The four dead definitions are gone and nothing names them | base `4 0` (FAIL) | PR `0 0` | PASS
- NEW | No harness or test file names the force-push setting | base `4` (FAIL) | PR `0` | PASS
- NEW | Run start carries one intake-and-implementer in-flight refusal, no rename and one store-ignore write | base `2 3 3` (FAIL) | PR `0 2 2` | PASS
- NEW | No harness module has three blank lines in a row | base `1` (FAIL) | PR `0` | PASS
- NEW | The three stale texts are gone | base `3` (FAIL) | PR `0` | PASS
- NEW | The repo-root helper takes no argument and every caller passes none | base `13 0 0` (FAIL) | PR `0 12 1` | PASS
- REGRESSION | The harness has no unused imports or variables (`uvx ruff check --select F401,F841 factory tests`) | base: not run | PR `All checks passed!`, exit 0 | PASS
- REGRESSION | The harness suite passes, and only the force-push test lines change under tests | base: not run | PR `577 passed in 375.30s (0:06:15)`, then `tests/factory/fixtures/instance/instance.yaml`, `tests/factory/test_instance.py` | PASS
- REGRESSION | A second intake run on a ticket is refused with the same text | base: not run | PR `T-0001 already has run run-0001-triage in flight`, `exit=2`, `run-0001-triage` | PASS

Every NEW base value matches the "today" value in the spec's verification.md, and each one fails for the reason the spec states.

Gate suite: PASS
- `git diff --check main...HEAD`: no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `577 passed in 353.85s (0:05:53)`, exit 0 (`scratch/gate-pytest.txt`).

Probes:
- A run record hand-edited to `role: bogus`, then `FACTORY_DISPATCH=1 factory run compose run-0001-triage` → `compose: unknown role bogus`, exit 2 → OK. The compose branch that was kept still refuses, with the new text (Decision: keep the branch, change only its text).
- The store's `.gitignore` deleted, then a triage start on a second ticket → exit 0, and the ignore block (`runs/*/wt/`) is back → OK. The kept write at `cli.py:227` runs for every role, after `_start_build_run` returns, so removing the build-only write leaves a deleted block still restored.
- `factory run start --role nobody` → `unknown role nobody; roles: triage, spec_writer, critic, planner, implementer, reviewer, verifier`, exit 2 → OK. `ROLES` (`cli.py:25`) is exactly the five roles in the merged check plus reviewer and verifier, so every role is still covered by an in-flight check (`cli.py:207-210`).
- A grep over all files outside `.venv`, `.git` and `__pycache__` for `repo_root(` calls that pass an argument, and over `factory bin agents tests README.md` for `run_gates`, `STATES`, `OPS` and `store.load_config` → none left. The only remaining `repo_root(<arg>)` is `instance.repo_root(inst)`, a different function. `subprocess` is still used in `gitops.py` (lines 32, 80, 86) → OK.
- The existing suite still covers the merged refusal: the tests at `test_whole_spec_plan.py:200` (planner), `test_shepherd.py:533` (implementer) and `test_p0_cli.py:97` assert the `already has run … in flight` text, and all pass → OK.

Protected paths: the diff touches only `factory/` (not protected for this repo) and two test files listed under the spec's Tests to change. It touches no `.factory/**`, `bin/factory`, `agents/**`, `pyproject.toml`, `uv.lock` or `docs/prompts/**`.

STATUS: VERIFIED
CONFIDENCE: high. All six NEW criteria fail on base with the stated values and pass on the PR; all three regressions and both gates pass on 53047c5; the probes show the behaviour holds beyond the tested inputs.
ESCALATIONS: none
