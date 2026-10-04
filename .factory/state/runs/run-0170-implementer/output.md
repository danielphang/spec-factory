Sub-ticket: T-0019.1 (T-0019-S1, "Role runs under a throwaway HOME"), parent T-0019 approved spec v2 (issue #36)
Branch: `factory/T-0019.1` in `/Users/dphang/dev/spec-factory/.factory/state/worktrees/T-0019.1`, base `1c5f6a7`, head `5f43cba` (one commit; 8 files, 252 insertions, 5 deletions).

## What changed

Before this change, roles ran tests with the operator's real home directory as `HOME`. On the Nanobot instance, that let a test overwrite the live bot's permission file. Now every role input the harness composes carries a ready-made wrapper. The wrapper runs a command with `HOME` set to a fresh temporary directory, and the gate commands come already wrapped. (Gate commands are the instance's check commands that the implementer and verifier must run.) The wrapper is guidance a role follows. It does not stop the operating system from writing anywhere.

- **A, the preamble rule.** The shared preamble is the rules text at the top of every role's prompt. In `docs/design.md` it gains a `RUNNING CODE` section, placed after the protected-paths placeholder line and before `GUARDRAIL PATHS`, with the parent's wording. `docs/prompts/00-preamble.md` is re-copied from that block, and `factory/prompts/preamble.md` is byte-identical to the copy.
- **B1, the run_env reader.** `factory/compose.py` gains `run_env(cfg)` (line 57). It reads the new instance key `run_env`, and an absent or null key counts as empty. It raises `store.Refused` (exit 2) if the value is not a mapping, if a name does not match `[A-Za-z_][A-Za-z0-9_]*`, or if a name is `HOME`. Each message names `run_env` and the offending name. The reader takes the `cfg` that `compose` already receives, so `factory/instance.py` is not edited.
- **B2, the wrapper.** `wrap(command, env)` (line 74) returns `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"<vars>; <command>)`. For each `run_env` entry, in file order, `<vars>` adds a space, `NAME=` and `shlex.quote(str(value))`.
- **B3, the section in every input.** `compose` adds a `## Running code` section, with the parent's text, directly after `## Output file`. Every role gets it. The section is not a store source, so `input_sources` is unchanged. `run_env` is read before anything is built, so a refused value means `cli.run_compose` never writes `input.md`.
- **B4, wrapped gate commands.** In "Where you work", each gate command goes through `wrap` after `{integration}` is replaced. The text now reads "exactly as written; each is already wrapped". Callers, found by grep: `compose.compose` is called only from `factory/cli.py:274` (`run_compose`). `gate_commands` is called only from `compose.py`, and I left it unchanged, so its output is still the bare commands.
- **B5.** `factory/instance.template.yaml` adds `run_env: {}` after `environment_files`, with the comment the parent asks for.
- **B6.** In the **Role-context block** paragraph of `docs/design.md` (line 54), the `instance.yaml` list now names "the variables kept for code runs (`run_env`)". The paragraph also ends with the parent's three sentences on the "Running code" section.
- **E1 (S1 clause only).** `docs/changelog.md` adds entry 48, "After issue #36 (2026-10-04): …", with the S1 clause. It sits after entry 47 and before `Declined:`. `main` had no `After issue #36` entry, so this sub-ticket adds the entry. When S2 merges, it adds its clause to entry 48.
- **E2, E3.** `README.md`: the **Roles.** paragraph gains the two sentences, the first on one line. In "Adopting the factory in a repo", step 3 gains "Set `run_env` for any tool whose cache lives under HOME, so it still finds that cache from inside the fresh temporary HOME.", with everything from "so it still finds" on one line. The status header already reads 2026-10-04, today's date, so it is unchanged.
- **E4.** `dev/build-harness.spec.md` is untouched, as the parent says.
- **F1.** New file `tests/factory/test_run_isolation.py`, described under "Tests added/changed".

## Acceptance results

All commands ran from the worktree root after `uv sync --frozen`, with the parent's fixture GIVEN block run verbatim first. I ran each block inside an outer `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; …)`, so no probe ran with my real `HOME`.

| Scenario | Kind | Before (base `1c5f6a7`) | After (head `5f43cba`) |
|---|---|---|---|
| A triage input's wrapper runs a command under a fresh HOME | NEW | `fresh_home=no real_home_untouched=yes cache=` | `fresh_home=yes real_home_untouched=yes cache=` |
| Planner and implementer inputs carry the wrapper | NEW | `planner 0` / `implementer 0` | `planner 1` / `implementer 1` |
| The implementer's gate commands come wrapped | NEW | `end` only | `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`, `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`, `end` |
| This repo's gate suite passes under a throwaway HOME | REGRESSION | not run (runs once, after) | `182 passed in 100.01s (0:01:40)`, exit 0. The 11 new tests are included: 171 existing + 11 = 182. |
| Variables listed in run_env reach the command | NEW | `fresh_home=no real_home_untouched=yes cache=` | `fresh_home=yes real_home_untouched=yes cache=/tmp/t0019 cache` |
| run_env cannot set HOME | NEW | `exit=0 input=written` | stderr `run_env may not set HOME: the running-code wrapper sets it to a fresh temporary directory`, then `exit=2 input=absent` |
| The running-code rule is in every copy and in a run's system prompt | NEW | all four `0 0 0` | `design.md 1 1 1`, `00-preamble.md 1 1 1`, `preamble.md 1 1 1`, `system-prompt.txt 1 1 1` |
| The preamble block and its copies stay identical | REGRESSION | `SAME` | `SAME` |
| The README describes the wrapper and run_env | NEW | `0`, `0`, `0` | `1`, `1`, `1` |
| The design doc and the instance template name run_env | NEW | `docs/design.md:0`, `factory/instance.template.yaml:0` | `docs/design.md:1`, `factory/instance.template.yaml:1` |
| The changelog records the change in order | NEW | `0`, `CONTIGUOUS` | `1`, `CONTIGUOUS`; entry 48 carries the S1 clause |
| The change adds no whitespace errors | REGRESSION | `exit=0` (empty diff) | `exit=0` |
| Only declared files change, no existing test changes | NEW | (empty) | exactly the 8 declared files: `README.md`, `docs/changelog.md`, `docs/design.md`, `docs/prompts/00-preamble.md`, `factory/compose.py`, `factory/instance.template.yaml`, `factory/prompts/preamble.md`, `tests/factory/test_run_isolation.py` |

What the "after" results show:
- `fresh_home=yes` means the probe ran under a `HOME` other than the caller's, and wrote its file there.
- `real_home_untouched=yes` means nothing was written to the caller's `HOME`.
- `cache=/tmp/t0019 cache` means a `run_env` value containing a space reached the command intact.

Gate commands, each run once on head `5f43cba`, in the wrapped form the parent requires:
- `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)` exited 0.
- `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` printed `182 passed`, exit 0. This is the same run as the REGRESSION row above.

Also: `ruff check factory/compose.py tests/factory/test_run_isolation.py` printed `All checks passed!`. Ruff is not a gate here.

## Tests added/changed

Added `tests/factory/test_run_isolation.py`, with 11 cases. Each drives `bin/factory` on a throwaway store. The cases that change `instance.yaml` use a copy of the suite's fixture instance.
- The triage input has exactly one `## Running code` section, right after `## Output file`, with the exact B3 text. `sources` is still only `requests/T-0001.md`.
- The planner and implementer inputs each carry the section once, with the bare wrapper.
- The implementer's gate command is rendered wrapped, after "exactly as written; each is already wrapped", and never bare.
- `run_env: {ZED: '/tmp/a b', ALPHA: "it's", N_1: 3}` produces ` ZED='/tmp/a b' ALPHA='it'"'"'s' N_1=3`, in file order and shell-quoted. The same string appears in the wrapper and in the wrapped gate command.
- A null `run_env` and `run_env: {}` both export nothing.
- Four refusals: `HOME`, `1BAD`, `A-B` and a list value. Each exits 2, its stderr names `run_env` and the offending name or type, and no `input.md` is written.
- A compound command `touch "$HOME/probe" && echo …`, run twice through the wrapper with a fake real `HOME`:
  - both halves see the same fresh, symlink-resolved `HOME` and the `run_env` variable;
  - the two runs get different homes;
  - the fake real `HOME` stays empty.

I watched them fail before the change: 11 failed on base. I changed no existing test.

## Known gaps and uncertainties

- **This repo has no `run_env` until the operator sets it.** Until Operator step 3 adds `run_env` for uv here, a wrapped test run in a fresh worktree that has no `.venv` resolves Python from an empty temporary home. It then builds `.venv` on the first system Python on `PATH`, and downloads every package again. I created this worktree's `.venv` with `UV_CACHE_DIR` and `UV_PYTHON_INSTALL_DIR` exported to the real uv paths, which is what step 3 would set. So the 182-test run used uv's managed CPython 3.12.13, not Homebrew's 3.14. Neither instance's `.factory/instance.yaml` was changed; that is out of scope.
- **Odd value types.** `run_env` values go through `str()`, as B2 specifies. A null value (`X: ~`) is therefore exported as the string `None`, and a YAML boolean as `True` or `False`. The parent does not ask for either case to be refused, so I did not refuse them.
- **The README runs ahead of its own rule.** "Maintaining this page" says a thing appears above "Where this can go" only after it has run on a real ticket. Parts E2 and E3 ask for present-tense README text now, before the runtime has moved to this revision. I followed the spec.
- **The wrapper is not a sandbox.** A command can still write an absolute path, and each run leaves its temporary directory behind. Both are stated in the parent and the design doc, and both are out of scope.
- **Gate commands that would break the wrapper.** A gate command with a shell comment (`#`) or a backtick would break the wrapped form or its rendering. The parent checked both instances' gate commands, and none has either character. Nothing here validates them.
- `factory:` markers added: none.

## Out-of-scope observations

- My shell had inherited `VIRTUAL_ENV=/Users/dphang/dev/nanobot/.venv-test`. uv warned that it does not match the project's `.venv` and ignored it, so the suite ran on the worktree's own `.venv`.
- `.factory/context.md`, this repo's briefing, still gives the bare test command. The new `## Running code` section and the preamble rule tell a role to wrap it. Changing the briefing is an instance-file change, out of scope here.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command ran before the change and after it, with the results above. The full suite passed under a throwaway HOME: 182 tests, 0 failures.
ESCALATIONS: none
