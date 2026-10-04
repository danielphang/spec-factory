Commit: 5f43cba12a208e095e48872471e4f6f2f9dc47f5 (branch `factory/T-0019.1`; base `1c5f6a7aa096c39b9a9f355b2dee286ccd3b4a84`)

How I ran it
- PR: the given worktree `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0172-verifier/wt`, at head `5f43cba`, with a clean `git status`. I created `.venv` with `uv sync --frozen` under a throwaway HOME, with `UV_CACHE_DIR` and `UV_PYTHON_INSTALL_DIR` pointed at the real uv directories, which is what Operator step 3 will set. The interpreter is CPython 3.12.13. I unset the inherited `VIRTUAL_ENV`.
- Base: a local `git clone` of the worktree in my scratchpad, checked out at `1c5f6a7` as `main`, and synced the same way.
- Fixtures: I ran the parent's GIVEN block once, verbatim, extracted from input.md lines 328-362. It wrote the four `$TMPDIR/t0019-*.sh` scripts.
- Throwaway HOME: following the plan's shared note ("Never run tests with the real HOME"), I ran each WHEN verbatim from the checkout root inside an outer `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; ...)`. The command text was unchanged. The probe scripts compare against the caller's HOME, so the outer throwaway HOME is the "real" HOME they check.

Per criterion:
| Kind | Command | Base (1c5f6a7) | PR (5f43cba) | Result |
|---|---|---|---|---|
| NEW | A triage input's wrapper runs a command under a fresh HOME | `fresh_home=no real_home_untouched=yes cache=` | `fresh_home=yes real_home_untouched=yes cache=` | PASS |
| NEW | Planner and implementer inputs carry the wrapper | `planner 0` / `implementer 0` | `planner 1` / `implementer 1` | PASS |
| NEW | The implementer's gate commands come wrapped | `end` only | the two wrapped gate strings, then `end` | PASS |
| REGRESSION | `(export HOME=...; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` | not run | `182 passed in 110.64s (0:01:50)`, rc=0. `tests/factory/test_run_isolation.py` alone: `11 passed in 3.31s` | PASS |
| NEW | Variables listed in run_env reach the command | `fresh_home=no real_home_untouched=yes cache=` | `fresh_home=yes real_home_untouched=yes cache=/tmp/t0019 cache` | PASS |
| NEW | run_env cannot set HOME | `exit=0 input=written` | stderr `run_env may not set HOME: the running-code wrapper sets it to a fresh temporary directory`, then `exit=2 input=absent`. A separate run showed the message on stderr; stdout carries the `{"ok": false, ...}` JSON | PASS |
| NEW | The running-code rule is in every copy and in a run's system prompt | all four lines `0 0 0` | `design.md 1 1 1`, `00-preamble.md 1 1 1`, `preamble.md 1 1 1`, `system-prompt.txt 1 1 1` | PASS |
| REGRESSION | The preamble block and its copies stay identical | not run | `SAME` | PASS |
| NEW | The README describes the wrapper and run_env | `0`, `0`, `0` | `1`, `1`, `1` | PASS |
| NEW | The design doc and the instance template name run_env | `docs/design.md:0`, `factory/instance.template.yaml:0` | `docs/design.md:1`, `factory/instance.template.yaml:1` | PASS |
| NEW | The changelog records the change in order | `0`, `CONTIGUOUS` | `1`, `CONTIGUOUS`. Entry 48 carries the parent's E1 S1 clause word for word, and no S2 clause | PASS |
| REGRESSION | `git diff --check main...HEAD; echo "exit=$?"` | not run | `exit=0` | PASS |
| NEW | `git diff --name-only main...HEAD \| sort` | empty | exactly the 8 declared files: `README.md`, `docs/changelog.md`, `docs/design.md`, `docs/prompts/00-preamble.md`, `factory/compose.py`, `factory/instance.template.yaml`, `factory/prompts/preamble.md`, `tests/factory/test_run_isolation.py` | PASS |

Every NEW criterion failed on base for the reason the parent's verification.md gives, and passed on the PR.

Gate suite: PASS
- `git diff --check main...HEAD` ran verbatim inside the whitespace criterion above and exited 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` ran inside the throwaway-HOME wrapper, as the REGRESSION criterion: 182 passed, rc=0. It is the wrapped form this change hands to verifiers. I did not also run it with the real HOME, because the plan's shared note forbids that.

Probes:
- A `run_env` value with shell metacharacters, `'$(touch $T19/pwned) it''s $HOME;x'`, plus an empty value `B2: ''`. The wrapper rendered `T0019_CACHE='$(touch ...) it'"'"'s $HOME;x' B2=''`, and the probe printed the literal value. The file `pwned` was not created. → OK
- A gate command using `{integration}` and `&&`, `test -d {integration} && touch "$HOME/g1" && echo ...`, with `run_env: {UVC: /x y}`, rendered in an implementer input. `{integration}` was replaced before wrapping, and `UVC='/x y'` was exported. Run with `sh -c`, both halves saw the same fresh HOME, which held `g1`. The outer HOME stayed empty, and rc was 0. → OK
- A spec_writer input, a role the criteria do not test, carries `## Running code` once, between `## Output file` and `## Request (raw)`. In the code, the section sits in the initial `parts` list of `compose`, before any branch by role (`factory/compose.py` diff). → OK
- Bad `run_env` values. `{1: x}` gives `exit=2 input=absent`, with `run_env: 1 is not a variable name ...`. `"str"` gives `exit=2 input=absent`, with `run_env must be a mapping ..., not a str`. `{home: /x}` is accepted and exported as `home=/x`. That is correct, since `home` is not `HOME`. → OK
- A `run_env` value that contains a backtick (`` `id` ``). The shell quoting is still correct, but the backtick ends the backticked span in the "Running code" section early. A role reading the section, or the spec's probe script, gets a truncated wrapper, `'; <command>)`, which does not run (`unexpected EOF while looking for matching '`). Nothing was executed. No criterion and no part of B covers backticks in values, so this is not a FAIL. → CONCERN (see ESCALATIONS)

STATUS: VERIFIED
CONFIDENCE: high. I ran every acceptance command on the PR and every NEW one on base, and each result matches the spec's stated before and after. The full suite passed under a throwaway HOME. The probes show the wrapper, the quoting and the refusals working on inputs beyond the tested ones.
ESCALATIONS:
- A `run_env` value containing a backtick breaks the rendered wrapper. The composer puts the wrapper inside a Markdown code span, so a role copying it gets a truncated, unrunnable command, and nothing refuses the value. The implementer's Known gaps raise the same risk for gate commands only. Neither instance's planned `run_env` (uv paths) has a backtick, so this is low risk. If it matters, a follow-up could refuse backticks in `run_env` values and gate commands.
