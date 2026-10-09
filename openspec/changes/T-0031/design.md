## Proposed change
One PR, about 225 changed lines: about 45 in the harness, 150 in a new test file, 5 in two existing tests and about 20 in documents.

**A. The wrapper drops an inherited virtual environment** (`factory/compose.py`, `wrap()`).
- Put this prefix, verbatim, right after the opening parenthesis and before `export HOME=`:
  `[ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; `
  (here `'\n'` is the two characters backslash and `n` inside single quotes, so `tr` gets a newline).
- The wrapper becomes `(<prefix>export HOME="$(cd "$(mktemp -d)" && pwd -P)"[ run_env exports]; <command>)`.
- It must contain no backtick, because it is shown inside backticks.
- Keep it as a module constant with a one-line comment saying what it does.
- Update the docstring. Leave the "Running code" section's prose unchanged.
- Gate commands pick up the prefix through the same `wrap()`.

**B. The `environment_sync` key** (`factory/instance.template.yaml`, `factory/compose.py`).
- Template: add `environment_sync: null` after `run_env`, with a comment. The comment says: one shell command the harness runs in each build checkout at run start, through the running-code wrapper, after the environment files are copied (for example `uv sync --frozen`); null means none; a failure refuses the run.
- `compose.environment_sync(cfg) -> str | None`: absent or null gives None. A non-empty string gives that string. Anything else raises `store.Refused` with text that names `environment_sync`.

**C. Sync at run start** (`factory/cli.py`, `_start_build_run()`).
1. Call `compose.environment_sync(cfg)` first, before any worktree or checkout is created, so that a bad value writes nothing.
2. After the checkout is set up and `copy_environment_files` has run, in both branches (implementer, and checker including the parent-close verifier), if a command is set, run it like this: `subprocess.run(["sh", "-c", compose.wrap(cmd, compose.run_env(cfg))], cwd=wt, capture_output=True, text=True)`. The sync's output must never reach run start's stdout, whose last line stays its JSON.
3. On exit 0, set `meta["environment_sync"] = cmd`.
4. On a non-zero exit:
   - Write `d / "environment-sync.log"` (`d` is the run directory `_start_build_run` receives): the command, the exit code, then the command's stdout and stderr in full.
   - For a checker, remove the checkout it just made (`gitops.remove_worktree`). Keep the implementer's worktree.
   - Raise `Refused(f"environment_sync failed (exit {code}) in {wt}; its command and output are in {log}")`, one line, with no command text and no output.
   - Because `meta.yaml` and the in-flight list are written only after `_start_build_run` returns (`factory/cli.py:225` and `236`), the refusal records no run and puts nothing in flight.

**D. The role is told** (`factory/compose.py`, the "Where you work" block, lines 315-326). When `meta.get("environment_sync")` is set, append this line at the end of the block, after any SKIPPED lines and before `parts.append(where)`, as its own line ending in a newline. It applies to the implementer, reviewer and verifier alike:
`Environment: the harness ran this instance's environment sync, `<command>`, in this checkout through the running-code wrapper before you started, so the environment is already synced. Do not sync it again unless your change alters the files it is built from.`
When the key is not set, the input is as today.

**E. Tests.**
- Make the two edits listed under Tests to change.
- Add `tests/factory/test_environment_sync.py`. It is black-box through `bin/factory`, on throwaway stores, with a copy of the suite's fixture instance where the key is set, in the style of `test_run_isolation.py`. It covers:
  - the composed wrapper run under `sh` with a fake activated environment: `VIRTUAL_ENV` and `PYTHONHOME` are unset, the environment's `bin/` is off `PATH` while the other `PATH` entries stay in order, and a `PATH` with no environment is unchanged;
  - the sync at an implementer start and again at a later dispatch to the same worktree;
  - the sync at a reviewer start and at a parent-close verifier start;
  - the sync's environment: no `VIRTUAL_ENV`, a fresh HOME, the `run_env` exports;
  - a failed sync: exit 2, the one-line refusal with no backtick, `$` or double quote, the log holding the command and its output, nothing in flight, no checker checkout, no `meta.yaml`;
  - a non-string `environment_sync` refused before any checkout is made;
  - the input line present, for an implementer and a reviewer, when the sync ran, and absent when no key is set.

**F. Documents.**
- `docs/design.md`, in the "Role-context block" paragraph:
  - add `environment_sync` to the parenthetical list of what `instance.yaml` holds;
  - say that the running-code wrapper first drops an inherited virtual environment (its `bin/` off `PATH`, `VIRTUAL_ENV` and `PYTHONHOME` unset);
  - add one sentence: when the instance names an `environment_sync` command, `run start` runs it through that wrapper in each build checkout before the role starts, refuses the run if it fails (keeping the output in the run's `environment-sync.log`), and the role's input says the environment is already synced.
- `docs/changelog.md`: append the next contiguously numbered entry (64 on today's `main`, or the next free number when it merges). It records parts A to D in prose and names `environment_sync`, `VIRTUAL_ENV`, `PYTHONHOME` and the "already synced" line.
- `dev/build-harness.spec.md`, part I: add one item after I.3. It says that each build checkout runs the instance's `environment_sync`, if set, through the running-code wrapper at `run start`, before the role starts, and that a failure refuses the run with its output in `runs/<id>/environment-sync.log`.
- `README.md`:
  - In "Roles, harness, workflows", extend the wrapper sentence (line 30): the wrapper also drops a Python virtual environment inherited from the launching shell (`VIRTUAL_ENV`, `PYTHONHOME`, and its `bin/` on `PATH`).
  - In "Adopting the factory in a repo", step 3: set `environment_sync` to the command that installs the repo's environment, so each build checkout starts synced.
  - Bump the status date if the merge falls on a later day.
- No copy under `docs/prompts/` or `factory/prompts/` changes: no prompt block names the wrapper's contents.

## Tests to change
- `tests/factory/test_run_isolation.py`, the `WRAP` constant (line 22) only. It holds the exact expected wrapper text that five tests (six cases) compare against: `test_triage_input_carries_the_section_right_after_the_output_file`, `test_planner_and_implementer_inputs_carry_the_section_once`, `test_implementer_gate_commands_come_wrapped`, `test_run_env_is_exported_after_home_in_file_order_and_quoted` and both cases of `test_empty_or_null_run_env_exports_nothing`. Part A changes that text by design. The constant gains the part A prefix, with `${VIRTUAL_ENV:-}` written as `${{VIRTUAL_ENV:-}}` because the constant is a `str.format` template. The prototype's replacement for line 22, which made those six cases pass:

```python
WRAP = ('([ -z "${{VIRTUAL_ENV:-}}" ] || PATH=$(printf %s "$PATH" | tr : \'\\n\' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); '
        'unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"{vars}; {cmd})')
```

  No assertion is removed or loosened, and `SECTION` is unchanged.
- `tests/factory/test_gate_paths.py`, line 217 only: the `want` string in `test_a_null_absent_or_unscoped_mapping_gate_runs_as_a_string_list_does`. It builds the expected wrapped gate command from the old wrapper text, so its unscoped-mapping case fails once part A adds the prefix. The expected text gains the part A prefix before `export HOME=`, with `${VIRTUAL_ENV:-}` written as `${{VIRTUAL_ENV:-}}` because the string is an f-string. Nothing else in the file changes: the test's other two cases (`want` empty), its assertions and every other test stay as they are. The prototype's replacement for line 217 (two lines, same indentation):

```python
    want = (f"`([ -z \"${{VIRTUAL_ENV:-}}\" ] || PATH=$(printf %s \"$PATH\" | tr : '\\n' | grep -vxF \"$VIRTUAL_ENV/bin\" | paste -sd: -); "
            f"unset VIRTUAL_ENV PYTHONHOME; export HOME=\"$(cd \"$(mktemp -d)\" && pwd -P)\"; {UNSCOPED})`" if UNSCOPED in gate else "")
```

- No other existing test changes. The whole suite went from `7 failed, 401 passed` with the prototype to `408 passed` with these two edits, the same count as the unchanged base (Evidence).

