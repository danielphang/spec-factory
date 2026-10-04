## Critic review, round 2 (spec v2)

Spot-checks made, all from `~/dev/spec-factory` under the fresh-HOME wrapper. `main` is now at `7d57998`, two commits past the `c2750bf` the spec cites: the T-0022.1 merge (`c5bfafa`, which changed `factory/workflows/build.js`, added `tests/factory/test_sibling_tests.py` and touched 20 files outside the store) and a store commit.

- Prior-finding text: Problem paragraph 4 now glosses "instance" where `instance.yaml` is introduced; Evidence bullet 1 opens with "The Nanobot fork, the other repository that runs this factory (instance A)"; Operator steps open with a paragraph that glosses the runtime, the upgrade and `--accept-harness <commit>`, and points to README "Accepting a harness revision" (line 214) and "Upgrading the runtime" (line 231), both of which exist; Decisions bullet 7 glosses "runtime" at its first use there. Decisions bullets 2, 4, 5 and 6 gloss `run_env`, conflict run, integration branch, build workflow, parks and `meta.yaml`.
- Instance A's `instance.yaml` (read only): line 25 `run_env:`, line 26 `UV_CACHE_DIR: /Users/dphang/.cache/uv`, line 27 `UV_PYTHON_INSTALL_DIR: /Users/dphang/.local/share/uv/python`; lines 40-41 are the two gate commands, each setting both variables; line 54 `environment_files: ["uv.lock"]`. Last commit to the file `70c593103` (2026-10-04 10:06). The writer's response is correct and my round-1 citation of lines 25-26 stopped one line short.
- `grep -l VIRTUAL_ENV .factory/state/runs/*/output.md | wc -l` prints 28 today; the four non-build-role matches are run-0274-triage, run-0276-spec_writer, run-0279-critic and run-0283-spec_writer, so the 24 build-role runs the spec counts still hold and the extra one is this ticket's v2 writer, as the bullet predicts.
- `.factory/state/runs/run-0283-spec_writer/scratch/` no longer exists (the harness cleared it). The Evidence bullet says this will happen and quotes the lines that matter, so the claim does not depend on the file.
- Cited harness lines: `factory/compose.py` `run_env()` at 57 and `wrap()` at 74-78 still match the Root cause. `factory/cli.py` `_start_build_run()` now starts at line 267 (was 238); `add_worktree` is at 279 (spec: 249), `add_detached_worktree` at 290 (spec: 261), `copy_environment_files` at 283 and 291. The gate line in the "Where you work" block is at `compose.py:178`. The "Role-context block" paragraph of `docs/design.md` is at line 62. README "Roles, harness, workflows" at 25, "Adopting the factory in a repo" at 270; `dev/build-harness.spec.md` part I at 294. `grep -c 'environment_sync\|VIRTUAL_ENV'` over design, README, build spec, template and `.factory/instance.yaml` is 0 for each.
- Tests to change still complete: `grep -rl 'export HOME=' tests/factory/` matches only `test_run_isolation.py`; the new `test_sibling_tests.py` does not compare wrapper text. The suite now collects 310 tests (the spec's figures are `6 failed, 294 passed` / `300 passed`, from before T-0022.1 added ten).
- Acceptance commands re-run on `7d57998` with the GIVEN fixture written to this run's scratch directory: the wrapper scenario printed `ve=<T31>/venv ph=<T31>/venv fake_python=1 cache=/tmp/t31-cache home=fresh` twice; the implementer-sync scenario printed `first: synced=no ve= venv_on_path=0 cache=0 home=fresh noted=0` then `again: synced=no`; the changelog scenario printed `CONTIGUOUS` then `0`. All three match the verification file's "today" lines, so the NEW items still fail for the stated reason on the current `main`.
- `build.js:72` still parks a refused run start with `harness-bug: run start ${role}: ${start.stderr || ''}` (T-0022.1 added a `blocked` branch ahead of it), so Decisions bullet 5's park reason still holds.

Findings:

[SHOULD-FIX] 1 Root cause bullet 3; Evidence bullets 4 and 5; verification.md changelog item
Problem: `main` moved past `c2750bf` after v2 was written (T-0022.1 merged as `c5bfafa`), so the Evidence sentence "`main` is still at `c2750bf`" is no longer true, `_start_build_run()` is at `factory/cli.py:267-291` with `add_worktree` at 279 and `add_detached_worktree` at 290, the suite collects 310 tests rather than 300, and the changelog's last entry is 54, not 53.
Evidence: `git log --oneline c2750bf..HEAD` (two commits); `grep -n '_start_build_run\|add_worktree\|add_detached_worktree' factory/cli.py`; `pytest --collect-only` tail `310 tests collected`; `grep '^[0-9]*\. ' docs/changelog.md | tail -1` starts `54.`. Nothing of substance is wrong: the symbols, the design, the Tests to change list and every acceptance command still behave as the spec says on the new HEAD, so this does not block.
Suggested fix: Refresh the four numbers (HEAD, cli.py line range and the two line numbers, suite count, last changelog entry) to the current `main`, or replace the line numbers with the symbol names alone.

Prior findings (round 1):
- [BLOCKING] 6 glosses of runtime, accepting a harness revision and instance: RESOLVED. Each term is glossed at first use in the section that uses it, and the README sections the spec points to exist at lines 214 and 231.
- [SHOULD-FIX] 6 glosses in Decisions: RESOLVED. All six terms are glossed at first use.
- [SHOULD-FIX] 4 `UV_PYTHON_INSTALL_DIR` missing from instance A's `run_env`: WITHDRAWN. My round-1 evidence was wrong: the file's `run_env` block is lines 25-27 and already pins both uv variables, as I confirmed by reading it this round. The writer's DISAGREE stands; the tightened step 2 is accurate and a sound precaution.
- [NIT] 1 the `VIRTUAL_ENV` count: RESOLVED. Dated and explained; the count moved from 27 to 28 exactly as the bullet says it will.

Out-of-scope observations:
- The round-1 observations stand: keep the part A prefix in a module constant, not pasted into the f-string (its `${VIRTUAL_ENV:-}` would collide with f-string braces), and the exact-entry `grep -vxF "$VIRTUAL_ENV/bin"` leaves a `bin/` whose spelling differs from `$VIRTUAL_ENV`.
- The implementer's PR will land after T-0022.1, so its changelog entry is 55 and its "Tests to change" prototype figure becomes `6 failed, 304 passed` to `310 passed`; the design's "next contiguously numbered entry, after whatever entries have merged by then" already allows for this.

STATUS: APPROVE
CONFIDENCE: high, every round-1 finding was checked against the v2 text and the repo, three acceptance commands were re-run on the current `main` and match the verification file, and the only new finding is stale line numbers from a merge that landed after v2 was written.
ESCALATIONS: none
