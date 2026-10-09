Sub-ticket: T-0031.2 (parent T-0031, approved spec v3, `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0031/v3.md`)
Branch: `factory/T-0031.2`, one commit `da50576` on base `2bd9969`. Worktree: `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0031.2`.

## What changed
Build roles lost their first attempt to a broken Python environment. Their shells inherited the launching session's activated virtual environment (here `/Users/dphang/dev/nanobot/.venv-test`, which this run's own shell also had). Their fresh checkouts also had no `.venv`. The build roles are the implementer, the reviewer and the verifier. This change fixes both problems.

- **A. Wrapper** (`factory/compose.py`). The running-code wrapper is the shell prefix every role puts around each command, and the harness puts around each gate command. A new module constant `_DROP_VENV` holds the spec's prefix, verbatim, with a one-line comment. `wrap()` now emits `(<prefix>export HOME=...[ run_env exports]; <command>)`, and its docstring says so. The "Running code" prose is unchanged. Gate commands get the prefix through the same `wrap()`. I grepped the callers of `wrap()` before editing: `compose.py` (the Running code section and the gate-commands line) and, new in this change, `cli._sync_environment`.
- **B. Key** (`factory/instance.template.yaml`, `factory/compose.py`). The template gains `environment_sync: null` after `run_env`, with the comment the spec asks for. `compose.environment_sync(cfg)` returns None when the key is absent or null. It returns a non-empty string as given. Any other value raises `store.Refused` with text that names `environment_sync`.
- **C. Sync at run start** (`factory/cli.py`). `_start_build_run` reads the key first, before any checkout is made. The new `_sync_environment` runs after `copy_environment_files` in both branches. That covers the implementer and every checker, including the parent-close verifier. The checker branch runs it before `diff.patch` is written. It runs `subprocess.run(["sh", "-c", compose.wrap(cmd, compose.run_env(cfg))], cwd=wt, capture_output=True, text=True)`, so its output never reaches stdout. On exit 0 it sets `meta["environment_sync"]`. On a non-zero exit it does three things:
  - It writes `runs/<id>/environment-sync.log`, holding the command, the exit code, and the full stdout and stderr.
  - For a checker, it removes the checkout with `gitops.remove_worktree`. The implementer's worktree is kept.
  - It raises `Refused("environment_sync failed (exit N) in <wt>; its command and output are in <log>")`.
  Because the refusal comes before `meta.yaml` and the in-flight list are written, no run is recorded.
- **D. Input line** (`factory/compose.py`, "Where you work"). When `meta["environment_sync"]` is set, the section gains the spec's `Environment: ...` line, word for word. It comes after any SKIPPED lines and before `parts.append(where)`.
- **E. Tests.** The two listed edits are made, each matching the spec's prototype text. The new test file is `tests/factory/test_environment_sync.py`, listed below.
- **F. Documents.**
  - `docs/design.md`, "Role-context block" paragraph: `environment_sync` is added to the list of what `instance.yaml` holds. The wrapper sentence now says it first drops an inherited virtual environment (`VIRTUAL_ENV`, `PYTHONHOME`, its `bin/` off `PATH`). One sentence is added on the sync, the refusal and its log, and the "already synced" input line.
  - `docs/changelog.md`: entry 66 (issue #51) records parts A to D and the rejected alternatives.
  - `dev/build-harness.spec.md`, part I: a sub-item under I.3 (see Known gaps).
  - `README.md`: one sentence added after the wrapper sentence in "Roles, harness, workflows". In "Adopting the factory in a repo", step 3 now says to set `environment_sync`. The status date is already 2026-10-09, today, so it was not bumped.
  - No file under `docs/prompts/` or `factory/prompts/` changes.

## Acceptance results
How they ran: each command was run from the worktree root after `uv sync --frozen`, through the wrapper (fresh HOME). The fixture file is the spec's GIVEN block, written verbatim to `$TMPDIR/t0031-env.sh`, with `TMPDIR` set to this run's scratch directory. The scenario commands were copied verbatim into `scratch/acc.sh`. The before outputs are in `scratch/acc-before.txt` and the after outputs in `scratch/acc-after.txt`. The after run was repeated under zsh, and S1 to S4 printed the same.

| Scenario | Before (base `2bd9969`) | After (`da50576`) |
|---|---|---|
| NEW wrapper and gate drop the inherited venv | two lines `ve=<T31>/venv ph=<T31>/venv fake_python=1 cache=/tmp/t31-cache home=fresh` | two lines `ve=unset ph=unset fake_python=0 cache=/tmp/t31-cache home=fresh` |
| NEW implementer synced at every dispatch | `first: synced=no ve= venv_on_path=0 cache=0 home=fresh noted=0` / `again: synced=no` | `first: synced=yes ve=0 venv_on_path=0 cache=1 home=fresh noted=1` / `again: synced=yes` |
| NEW checker synced | `synced=no ve= venv_on_path=0 noted=0` | `synced=yes ve=0 venv_on_path=0 noted=1` |
| NEW failed sync refuses | `implementer: exit=0 named=0 code=0 shell_chars=0 logged=0` / `reviewer: exit=0 ...` / `in_flight=0 checker_checkouts=1 meta=2` | `implementer: exit=2 named=1 code=1 shell_chars=0 logged=1` / `reviewer: exit=2 named=1 code=1 shell_chars=0 logged=1` / `in_flight=1 checker_checkouts=0 meta=0` |
| REGRESSION without the key | `started=yes noted=0 recorded=0 files=0` | `started=yes noted=0 recorded=0 files=0` |
| NEW documents | `design=0 design_venv=0 build_spec=0 template=0 readme=0 readme_venv=0 prompts=0` | `design=1 design_venv=1 build_spec=1 template=1 readme=1 readme_venv=1 prompts=0` |
| NEW changelog | `CONTIGUOUS` / `0` | `CONTIGUOUS` / `4` |
| REGRESSION whitespace | `exit=0` | `exit=0` |

Every NEW "before" matches the spec's verification.md "today" output.

Gates on `da50576`, each run exactly as written:
- `git diff --check main...HEAD`: no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `496 passed in 309.94s`. That includes the 10 new tests and the two edited ones. The spec's figure of 408 was measured at `b002c95`; `main` has gained tests since.

## Tests added/changed
- Added `tests/factory/test_environment_sync.py`, 10 tests. It is black-box through `bin/factory`, on throwaway stores, with a copy of the fixture instance and a scratch target repo. It covers:
  - the composed wrapper under `sh` with a fake activated venv: both variables are unset, and only the exact `<venv>/bin` entry leaves `PATH`, with the other entries kept in order (a `<venv>/binx` entry stays). A `PATH` with no venv is unchanged.
  - an implementer sync at the first and at a later dispatch;
  - a reviewer sync, and a parent-close verifier sync;
  - the sync's environment: no `VIRTUAL_ENV` or venv `bin/`, a fresh HOME, and the `run_env` export;
  - a failed sync, for both the implementer and the reviewer: exit 2, a single line with no backtick, `$` or double quote and no command text or output, the log holding the command, its output and `exit: 3`, a run directory holding only the log, nothing in flight, no checker checkout, and the implementer's worktree kept;
  - malformed values (`[uv, sync]`, `""`, `3`) refused with no worktree and no run directory;
  - with no key: nothing recorded, no input line and a clean worktree, for an implementer and a reviewer.
  With the `factory/` changes stashed, 9 of the 10 failed for the expected reasons. The no-key test passed, as a regression test should.
- Changed `tests/factory/test_run_isolation.py`, the `WRAP` constant only. Part A changes the expected wrapper text by design. This is the replacement the spec gives.
- Changed `tests/factory/test_gate_paths.py`, the `want` line only, in `test_a_null_absent_or_unscoped_mapping_gate_runs_as_a_string_list_does`. The reason is the same, and this is also the spec's replacement.
- No other existing test changed.

## Known gaps and uncertainties
- **Deviation, refusal timing.** Spec part C.1 says to call `compose.environment_sync(cfg)` first in `_start_build_run` "so that a bad value writes nothing". The run directory is reserved before `_start_build_run` runs. A refusal there would leave an empty `runs/<id>/` behind. So I also call it in `run_start` next to `compose.gate_entries(cfg)`, before the run id is reserved, as that function already does (`factory/cli.py:218`). `_start_build_run` still reads the key first (line 367). A malformed value therefore leaves no run directory, and the test asserts that.
- **Placement in the build spec.** Part F says "add one item after I.3". Renumbering I.4 to I.6 would break references elsewhere: `dev/build-harness.spec.md` lines 97, 206, 411 and 507, and `dev/build-harness.plan.md`. So the addition is an indented sub-item of I.3, and the numbers stay as they are.
- **README tense.** README's "Maintaining this page" says behaviour appears above "Where this can go" only after it has run on a real ticket. The spec asks for the two README sentences in this PR, and I followed the spec. The sync has not yet run on a real ticket, because neither instance sets the key yet (Operator steps).
- **Test without `PYTHONHOME`.** The new tests launch `bin/factory` with `VIRTUAL_ENV` and the venv `bin/` on `PATH`, but not `PYTHONHOME`. Pointing `PYTHONHOME` at the fake venv breaks the harness's own interpreter ("No module named 'encodings'"). The wrapper test covers `PYTHONHOME`.
- **Sync time limit.** As the spec's Risk says, the sync has no time limit and runs inside the clerk's `run start` call.
- `factory:` markers added: none.

## Out-of-scope observations
- On macOS, `mktemp -d` ignores `TMPDIR` in this environment. So the scenarios' temporary targets went to `/var/folders/.../T/`, not this run's scratch directory. Only the fixture file and the logs are in scratch.
- The operator's step to set `environment_sync` on each instance is still pending, by design.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. All eight acceptance commands and both gates were run on `da50576` and printed the expected output, and the four NEW scenarios that test behaviour printed the spec's "today" output on the base.
ESCALATIONS: none
