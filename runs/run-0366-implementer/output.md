Sub-ticket: T-0031.1 (parent T-0031, approved spec v2), branch `factory/T-0031.1` in `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0031.1`, commit `f13e707` on base `b002c95`.

The change is built, and every acceptance scenario of the parent spec prints its expected output. The test-suite gate still fails one case, in an existing test the spec does not list under Tests to change. That test was added after the spec was written, and it hard-codes the old wrapper text. I did not edit it, because only listed tests may change. This PR is BLOCKED until a human allows that one-line edit (ESCALATIONS).

## What changed
The running-code wrapper is the one-line shell prefix each role puts around every command it runs. It gives the command a throwaway HOME. Gate commands, the repository's check commands, reach the roles already inside it.

**A. The wrapper drops an inherited virtual environment.** `factory/compose.py` gains the module constant `DROP_VENV`, with a one-line comment. It holds the spec's prefix verbatim and contains no backtick. `wrap()` puts the prefix right after the opening parenthesis, so the wrapper becomes `(<prefix>export HOME=…[ run_env exports]; <command>)`. The docstring now describes the prefix. The prose of the "Running code" section is unchanged. Gate commands get the prefix through the same `wrap()`.

**B. The `environment_sync` key.** The template `factory/instance.template.yaml` gains `environment_sync: null` after `run_env`, with the comment the spec gives. `compose.environment_sync(cfg)` returns None when the key is absent or null, and the string when it is a non-empty string. Anything else raises `Refused`, and the message names `environment_sync`.

**C. Sync at run start** (`factory/cli.py`).
- `_start_build_run()` calls `compose.environment_sync(cfg)` first, before any worktree or checkout exists.
- The new helper `_sync_environment()` runs the command after `copy_environment_files`, in both branches: the implementer's worktree at every dispatch, and every checker's checkout, including the parent-close verifier's. The parent-close verifier checks the parent ticket after all its sub-tickets merge.
- It runs `subprocess.run(["sh", "-c", compose.wrap(cmd, compose.run_env(cfg))], cwd=wt, capture_output=True, text=True)`. The command's output never reaches run start's stdout.
- On exit 0 it sets `meta["environment_sync"] = cmd`.
- On a non-zero exit it removes a checker's checkout (`gitops.remove_worktree`) and keeps the implementer's worktree. Then it raises `Refused("environment_sync failed in <wt> (exit <code>): <cmd>\n<last 20 lines>")`.
- `meta.yaml` and the in-flight list are written only after `_start_build_run` returns, so a refusal records no run and puts nothing in flight.

**D. The role is told.** When `meta["environment_sync"]` is set, the "Where you work" section of the implementer, reviewer and verifier inputs ends with the spec's `Environment: … already synced. …` line, as its own line. The gate line still ends with its last wrapped command. When the key is not set, the input is unchanged.

**E. Tests.** The `WRAP` constant in `tests/factory/test_run_isolation.py` gains the prefix. The new file `tests/factory/test_environment_sync.py` holds 16 cases (see Tests added/changed).

**F. Documents.**
- `docs/design.md`, "Role-context block" paragraph: adds `environment_sync` to the list of what `instance.yaml` holds. It says the wrapper first takes the inherited environment's `bin/` off `PATH` and unsets `VIRTUAL_ENV` and `PYTHONHOME`. It adds the spec's sentence about `run start` running the sync.
- `docs/changelog.md`: entry 64, the next number after 63.
- `dev/build-harness.spec.md`: a new item under I.3 (see Known gaps for why it is nested).
- `README.md`: extends the wrapper sentence in "Roles, harness, workflows", and step 3 of "Adopting the factory in a repo" now covers `environment_sync`. The status date is already 2026-10-09, today, so it is not bumped.
- No file under `docs/prompts/` or `factory/prompts/` changes.

Callers of the changed functions, found by grep across `factory/`, `bin/` and `agents/`:
- `wrap()` has two callers, both in `compose.compose()`: the "Running code" section (line 200) and the gate line (line 339). The sync adds a third, `cli._sync_environment()`. No other file builds the wrapper: `grep -rln "mktemp -d\|export HOME" factory/ agents/ bin/ docs/prompts` finds only `factory/compose.py`. Fixing the prefix once in `wrap()` covers all of them.
- `_start_build_run()` has one caller, `run_start()`.

## Acceptance results
Every scenario ran verbatim from the worktree root, under the HOME wrapper, after `uv sync --frozen`. The script is `…/run-0366-implementer/scratch/accept.sh`. Paths below are shortened to `<T31>`. On macOS, `mktemp -d` ignores `TMPDIR`, so each scenario's `<T31>` directory landed in the system temp directory, as the scenario intends.

| Scenario | Kind | Before (`b002c95`) | After (`f13e707`) |
|---|---|---|---|
| A role's wrapper and its wrapped gate command drop an inherited virtual environment | NEW | two lines, each `ve=<T31>/venv ph=<T31>/venv fake_python=1 cache=/tmp/t31-cache home=fresh` | two lines, each `ve=unset ph=unset fake_python=0 cache=/tmp/t31-cache home=fresh` |
| An implementer's worktree is synced through the wrapper at every dispatch, and its input says so | NEW | `first: synced=no ve= venv_on_path=0 cache=0 home=fresh noted=0` / `again: synced=no` | `first: synced=yes ve=0 venv_on_path=0 cache=1 home=fresh noted=1` / `again: synced=yes` |
| A checker's checkout is synced before the checker starts, and its input says so | NEW | `synced=no ve= venv_on_path=0 noted=0` | `synced=yes ve=0 venv_on_path=0 noted=1` |
| A failed sync refuses the run start, names the sync, and leaves no run or checker checkout | NEW | `implementer: exit=0 named=0 code=0 output=0` / `reviewer: exit=0 named=0 code=0 output=0` / `in_flight=0 checker_checkouts=1` | `implementer: exit=2 named=1 code=1 output=1` / `reviewer: exit=2 named=1 code=1 output=1` / `in_flight=1 checker_checkouts=0` |
| Without environment_sync, run start and the input are as before | REGRESSION | (not required) `started=yes noted=0 recorded=0 files=0` | `started=yes noted=0 recorded=0 files=0` |
| The design doc, build spec, template and README name the sync and the dropped virtual environment, and no prompt copy changes | NEW | `design=0 design_venv=0 build_spec=0 template=0 readme=0 readme_venv=0 prompts=0` | `design=1 design_venv=1 build_spec=1 template=1 readme=1 readme_venv=1 prompts=0` |
| The changelog records the environment sync as its last entry | NEW | `CONTIGUOUS` / `0` | `CONTIGUOUS` / `4` |
| The environment-sync change adds no whitespace errors | REGRESSION | (not required) `exit=0` | `exit=0` |

What the results show:
- Every NEW "before" output matches what `verification.md` predicted.
- Every "after" output is exactly the scenario's THEN.
- Scenario 1, after: neither the role's wrapper nor the wrapped gate command sees the fake environment. Its `python` is no longer found (`fake_python=0`), and the `run_env` export and the fresh HOME survive.
- Scenario 4, after: `in_flight=1` means the in-flight list is empty, and `checker_checkouts=0` means no checker checkout is left registered.

I also ran the composed wrapper under `sh`, `bash` and `zsh` with `VIRTUAL_ENV=/v PYTHONHOME=/v PATH=/v/bin:/v/bin2:$PATH`. Each printed `unset unset`. The first `PATH` entry became `/v/bin2`: only the exact `/v/bin` entry was removed.

Gate commands, from the worktree on `f13e707`, each exactly as written:
- `(export HOME=…; git diff --check main...HEAD)`: exit 0, no output. The change adds no whitespace errors.
- `(export HOME=…; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`: **`1 failed, 423 passed in 287.22s`**. The one failure is `tests/factory/test_gate_paths.py::test_a_null_absent_or_unscoped_mapping_gate_runs_as_a_string_list_does[gate_commands: [{command: "git diff --check main...HEAD"}]\n]`. Its assertion at line 218 compares the gate line against `want`, built at line 217 as the old wrapper: `` f"`(export HOME=\"$(cd \"$(mktemp -d)\" && pwd -P)\"; {UNSCOPED})`" ``. Part A changes that text by design, so the case fails for the same reason the `WRAP` cases in `test_run_isolation.py` did. With the base's `factory/compose.py` and `factory/cli.py` checked out over this branch, `tests/factory/test_gate_paths.py` passed `26 passed`. The failure is caused by this change.

## Tests added/changed
- Changed: `tests/factory/test_run_isolation.py`, the `WRAP` constant only. Listed under Tests to change. It gains the part A prefix, with `${VIRTUAL_ENV:-}` written as `${{VIRTUAL_ENV:-}}` because the constant is a `str.format` template. No assertion changed, and `SECTION` is unchanged. Without the code change, its 6 cases fail. With it, they pass.
- Not changed, although it needs to be: `tests/factory/test_gate_paths.py` line 217 (see ESCALATIONS).
- Added: `tests/factory/test_environment_sync.py`. It is black-box through `bin/factory`, on throwaway stores, a scratch target with an untracked `uv.lock`, and a copy of the fixture instance with lines appended. Before the code change, 15 of its 16 cases fail. The 16th is the no-key regression case, which passes on both. All 16 pass after. Its cases:
  - The composed wrapper under `sh` with a fake activated environment. `VIRTUAL_ENV` and `PYTHONHOME` end up unset. Each exact `$VIRTUAL_ENV/bin` entry leaves `PATH`, including a repeated one, while a look-alike `…/bin2` and the other entries stay in order. Without an environment, `PATH` is unchanged.
  - The wrapped gate command drops the environment too.
  - Implementer: synced at first dispatch and again at a later dispatch to the same worktree. The second sync reads the `uv.lock` copied at that later start (`lock-v2`), which proves the sync runs after the environment files are copied. `meta.yaml` records the command. The input carries the line, and the gate line still ends with its wrapped command.
  - Reviewer and parent-close verifier: each checkout is synced and each input carries the line.
  - The sync's environment: no `VIRTUAL_ENV`, no `PYTHONHOME`, no environment `bin/` on `PATH`, a HOME other than the caller's, and the `run_env` export.
  - A failed sync, for the implementer and for a reviewer: exit 2. The refusal names `environment_sync`, the checkout, `(exit 3)`, the command, and output from both stdout and stderr. Nothing is in flight and no `meta.yaml` is written. The implementer's worktree is kept. The reviewer's checkout is removed and unregistered.
  - Bad values (`[uv, sync]`, `3`, `''`, `{cmd: x}`), at implementer and reviewer starts: refused with exit 2 and `git worktree list` unchanged.
  - Without the key: no sync, no `environment_sync` in `meta.yaml`, no line in the input.

## Known gaps and uncertainties
- **The gate fails** on the one unlisted test case above. The spec says the `WRAP` edit was the only test change needed. That held on its prototype base `c2750bf`, but `tests/factory/test_gate_paths.py` was added after that base, in `0e99fa7`, `a074e95` and `c01e7c2`.
- **The I.3 item is nested.** Part F says "add one item after I.3" in `dev/build-harness.spec.md`. I added it as a bullet nested under item 3, not as a new item 4. A new item 4 would renumber I.5 and I.6, which other lines in that file and `dev/build-harness.plan.md` cite by number. The scenario only checks that the file names `environment_sync`.
- **One addition beyond the spec.** When `environment_sync` is set, `_start_build_run` also calls `compose.run_env(cfg)` before any checkout is made. A malformed `run_env` would otherwise raise inside the sync, after a checker's checkout exists, and leave that checkout behind. The cost is 2 lines. With no key set, behaviour is unchanged: a bad `run_env` is still refused at `run compose`, as before.
- **Where the line sits.** The "already synced" line goes at the end of the "Where you work" block, after any `SKIPPED by the harness …` lines. The spec says "after the gate-commands line, as its own line", and it predates the SKIPPED lines. I kept the gate line and its skips together.
- **The output tail splits streams.** The refusal's tail is the last 20 lines of stdout's lines followed by stderr's lines, because the spec's call captures the two separately. Interleaving between the two streams is lost.
- **Prefix edge cases.** The prefix is the spec's text verbatim, and these follow from it:
  - When `VIRTUAL_ENV` is set, a trailing empty `PATH` entry (`a:b:`, meaning the current directory) is dropped by the `tr | grep | paste` round trip.
  - A `PATH` whose only entry is `$VIRTUAL_ENV/bin` becomes empty.
  - With `VIRTUAL_ENV` unset, nothing changes.
- **README placement.** The README says a thing appears above "Where this can go" only after it has run on a real ticket. Part F places the `environment_sync` adoption step in "Adopting the factory in a repo", and the sync has not yet run on a real ticket. I followed the spec.
- **Changelog date.** Entry 64 dates issue #51 to 2026-10-04, from the request's evidence run and operator note. I did not check the issue's own date on GitHub.
- `factory:` markers added: none.

## Out-of-scope observations
- `dev/issues.md` row 51 still reads "T-0031 (spec approved; queued)". The operator updates it at merge.
- In this session, the shell running the implementer had `VIRTUAL_ENV=/Users/dphang/dev/nanobot/.venv-test` and that environment's `bin/` first on `PATH`. That is the exact leak this ticket fixes. `uv run` warned about it on every call.

## Responses to findings
None (round 1).

STATUS: BLOCKED
CONFIDENCE: medium. The code meets every acceptance scenario and its own tests, but the test-suite gate fails one unlisted existing test case that this change breaks by design.
ESCALATIONS:
- **The test-suite gate cannot pass without editing an existing test the spec does not list.** `tests/factory/test_gate_paths.py` line 217, in `test_a_null_absent_or_unscoped_mapping_gate_runs_as_a_string_list_does`, builds its expected gate line from the old wrapper text, `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; …)`. Part A adds the prefix to every wrapped gate command, so one case fails, and passes again with the base code (`26 passed`). The spec's Tests to change lists only the `WRAP` constant in `tests/factory/test_run_isolation.py`. This file was added after the spec's prototype base, so the spec's "only edit needed" claim no longer holds on `b002c95`. Decide: allow the one-line edit, adding the part A prefix to `want` on line 217 with no assertion removed, by amending the spec's Tests to change or by a ruling. The fix round then makes that edit, and the gate is expected to go to `424 passed`, though that run has not happened yet.
