Commit: 3d23560aa49b96327f707d049b96d52d12bcd323 (main; parent close of T-0019, merges 9853737 for T-0019.1 and 3d23560 for T-0019.2)

Base: 1c5f6a7aa096c39b9a9f355b2dee286ccd3b4a84, exported with `git archive` into a scratch directory, made a one-commit git repo on `main`, then `uv sync --frozen`. PR side: the given worktree, after `uv sync --frozen`. The GIVEN block was written verbatim with `TMPDIR` set to my scratchpad. Each WHEN ran verbatim under bash from the checkout root.

Per criterion:
- NEW | A triage input's wrapper runs a command under a fresh HOME | base: `fresh_home=no real_home_untouched=yes cache=` | PR: `fresh_home=yes real_home_untouched=yes cache=` | PASS
- NEW | Planner and implementer inputs carry the wrapper | base: `planner 0`, `implementer 0` | PR: `planner 1`, `implementer 1` | PASS
- NEW | The implementer's gate commands come wrapped | base: `end` only | PR: the two wrapped commands exactly as expected, then `end` | PASS
- REGRESSION | This repo's gate suite passes under a throwaway HOME, `(export HOME=...; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` | base: not run | PR: `190 passed in 110.55s (0:01:50)`, exit 0 | PASS
- NEW | Variables listed in run_env reach the command | base: `fresh_home=no real_home_untouched=yes cache=` | PR: `fresh_home=yes real_home_untouched=yes cache=/tmp/t0019 cache` | PASS
- NEW | run_env cannot set HOME | base: `exit=0 input=written` | PR: stderr `run_env may not set HOME: the running-code wrapper sets it to a fresh temporary directory`, last line `exit=2 input=absent` (I re-ran it with the streams split: the message is on stderr, and the JSON error is on stdout) | PASS
- NEW | The running-code rule is in every copy and in a run's system prompt | base: all four lines `0 0 0` | PR: `design.md 1 1 1`, `00-preamble.md 1 1 1`, `preamble.md 1 1 1`, `system-prompt.txt 1 1 1` | PASS
- REGRESSION | The preamble block and its copies stay identical | base: not run | PR: `SAME` | PASS
- NEW | Dash-bulleted field lines keep their dependencies | base: all three `ready-for-implementer`, `depends_on: []`, `parallel_safe: false` | PR: the exact expected `subtickets` list (T-0001.2 depends on T-0001.1, T-0001.3 depends on T-0001.2, both `waiting-dependencies`, both `parallel_safe: true`) | PASS
- REGRESSION | Star-bulleted, bold, indented and plain field lines read as before | base: not run | PR: the exact expected list | PASS
- NEW | A sub-ticket with no Depends on line is refused | base: success JSON, `exit=0`, three ticket files | PR: stderr `ST-2: no "Depends on:" line; write "Depends on: none" when it depends on nothing`, `exit=2`, listing `T-0001.yaml` alone | PASS
- NEW | The planner prompt shows the parsed lines in every copy | base: `0 0 0 0 0` for each file | PR: `1 1 1 1 1` for each of the three files | PASS
- REGRESSION | The planner block and its copies stay identical | base: not run | PR: `SAME` | PASS
- NEW | The changelog records the change in order | base: `0`, `CONTIGUOUS` | PR: `1`, `CONTIGUOUS` (entry 48 holds both seams' clauses) | PASS
- NEW | The README describes the wrapper and run_env | base: `0`, `0`, `0` | PR: `1`, `1`, `1` | PASS
- NEW | The design doc and the instance template name run_env | base: `docs/design.md:0`, `factory/instance.template.yaml:0` | PR: `docs/design.md:1`, `factory/instance.template.yaml:1` | PASS
- REGRESSION | The change adds no whitespace errors, `git diff --check main...HEAD; echo "exit=$?"` | base: not run | PR: `exit=0` | PASS. On main, HEAD is main, so this range is empty and proves nothing. I also ran `git diff --check 1c5f6a7 3d23560`, which covers the whole parent's change, and it exited 0.

Gate suite: PASS
- `git diff --check main...HEAD`: exit 0. The range is empty on main; see the last criterion.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `190 passed in 107.37s (0:01:47)`, exit 0.

Probes:
- Plan field lines indented before the bullet (`  - Depends on: none`, and `    * Parallel-safe: no` with `- Depends on: ST-1, T-0001.1`) → read correctly (T-0001.2 depends on T-0001.1, parallel_safe false) → OK
- `- **Depends on**: none` (bold closed before the colon, a form the parser did not read before either) → refused, naming `ST-1` → OK. The failure is now loud, not a silent `[]`.
- `+ Depends on: none` (declared out of scope) → refused, naming the sub-ticket → OK, loud
- Bulleted ID line `- ST-1 / First` → `no sub-tickets found` refusal → OK, as C1 intends (a bullet never starts a sub-ticket)
- `Depends on:` with an empty value → accepted as no dependencies → OK. This is the existing `NONE_RE` behaviour, and the line is present.
- A pairwise `Parallel-safe: yes with ST-3, not with ST-1` → `parallel_safe: true` → OK as specified. The spec declares pairwise reading out of scope, and the planner prompt now tells the planner to write `no`.
- `run_env: {A: 1, T0019_CACHE: "it's $HOME ;rm x", Z: 5}` → wrapper `... A=1 T0019_CACHE='it'"'"'s $HOME ;rm x' Z=5; <command>)` in file order. The probe printed `cache=it's $HOME ;rm x` with a fresh HOME → OK. Quoting is literal, and the number is turned into a string.
- `run_env: [A]` → refused: `run_env must be a mapping ... not a list`, and no input written. `run_env: {1X: a}` → refused: `'1X' is not a variable name`. `{}` and `null` → wrapper with no exports, fresh HOME → OK
- Gate command `echo $HOME > {integration}/h1 && echo $HOME > {integration}/h2` with `run_env: {Q: v}` → rendered with `{integration}` substituted, inside the wrapper. Running it wrote the same fresh temporary HOME to both h1 and h2, not `/Users/dphang` → OK. The subshell export covers both parts of `a && b`.
- `run_env` value containing a backtick (`"... \`x\` ..."`) → CONCERN, not a criterion failure. `shlex.quote` keeps the backtick, and the wrapper is printed inside a markdown backtick span, so the code span ends early. A role or the probe that extracts the wrapper gets a truncated command, which here was a shell syntax error. No realistic cache path holds a backtick, and the spec does not cover such values. See ESCALATIONS.

STATUS: VERIFIED
CONFIDENCE: high. Every scenario ran verbatim on both base and main with the expected split, both gate commands passed, and the probes show the parser and wrapper changes are general, not tied to the test inputs.
ESCALATIONS:
- The whitespace scenario and the `git diff --check main...HEAD` gate check nothing in a parent-close run on main, because HEAD is main and the range is empty. I covered the gap with `git diff --check 1c5f6a7 3d23560` (exit 0). The parent-close verifier's gate commands could take the pre-merge base instead of `main`; that is a harness decision for the operator.
- A `run_env` value containing a backtick breaks the markdown code span that carries the wrapper in `## Running code` and in each gate command (`factory/compose.py`, where `wrap` is used inside backticks). This is outside the spec's criteria. It could be refused in `run_env()` as the `HOME` name is, if the operator wants it closed.
