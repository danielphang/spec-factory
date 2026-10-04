## Acceptance
- A role's wrapper and its wrapped gate command drop an inherited virtual environment → NEW. Today both lines print `ve=<T31>/venv ph=<T31>/venv fake_python=1 cache=/tmp/t31-cache home=fresh`. The wrapper passes the inherited `VIRTUAL_ENV` and `PYTHONHOME` through, and the fake environment's `python` is found first. Run on `c2750bf` under bash and zsh.
- An implementer's worktree is synced through the wrapper at every dispatch, and its input says so → NEW. Today it prints `first: synced=no ve= venv_on_path=0 cache=0 home=fresh noted=0`, then `again: synced=no`: the `environment_sync` key is ignored and the input has no sync line.
- A checker's checkout is synced before the checker starts, and its input says so → NEW. Today it prints `synced=no ve= venv_on_path=0 noted=0`.
- A failed sync refuses the run start, names the sync, and leaves no run or checker checkout → NEW. Today it prints `implementer: exit=0 named=0 code=0 output=0`, `reviewer: exit=0 named=0 code=0 output=0`, `in_flight=0 checker_checkouts=1`: both runs start, both stay in flight, and the checker's checkout exists.
- Without environment_sync, run start and the input are as before → REGRESSION. Prints `started=yes noted=0 recorded=0 files=0` today.
- The design doc, build spec, template and README name the sync and the dropped virtual environment, and no prompt copy changes → NEW. Today it prints `design=0 design_venv=0 build_spec=0 template=0 readme=0 readme_venv=0 prompts=0`.
- The changelog records the environment sync as its last entry → NEW. Today it prints `CONTIGUOUS`, then `0`: the last entry (53) names none of the four terms.
- The environment-sync change adds no whitespace errors → REGRESSION. Prints `exit=0` today.

## Responses
- [BLOCKING] glosses of runtime, accepting a harness revision and instance → FIXED. Problem now says what an instance is where `instance.yaml` is introduced. Evidence names instance A as the other repository that runs the factory. Operator steps open with a short paragraph: the runtime is the separate checkout pinned to one harness revision, it is moved first, and each instance then accepts the revision with `--accept-harness <commit>`. The paragraph points to README's "Upgrading the runtime" and "Accepting a harness revision". Decisions' first use of "runtime" carries the same gloss.
- [SHOULD-FIX] glosses in Decisions → FIXED. `run_env` (the variables an instance gives the wrapper to export), conflict run (an implementer run after the merge step refused the branch), integration branch (the branch finished tickets merge into), build workflow (the script that dispatches the build roles), parks (stops the ticket for a human) and `meta.yaml` (the run's record file) are each glossed at first use. The Driver is glossed in Operator step 2.
- [SHOULD-FIX] `UV_PYTHON_INSTALL_DIR` missing from instance A's `run_env` → DISAGREE with the premise, wording tightened anyway. `grep -n -E 'run_env|UV_CACHE_DIR|UV_PYTHON_INSTALL_DIR' ~/dev/nanobot-upstream/.factory/instance.yaml` prints `25:run_env:`, `26:  UV_CACHE_DIR: /Users/dphang/.cache/uv`, `27:  UV_PYTHON_INSTALL_DIR: /Users/dphang/.local/share/uv/python`. `git -C ~/dev/nanobot-upstream show HEAD:.factory/instance.yaml` has the same three lines, and the file's last commit is `70c593103` (2026-10-04 10:06). So `run_env` already pins both variables, and the sync would find uv's managed Pythons. The critic's citation of lines 25-26 stops one line short. Step 2 now names both variables. It also tells the Driver to check that `run_env` covers every uv variable its gate commands set before it sets the key, because that is the condition the critic's concern rests on.
- [NIT] the `VIRTUAL_ENV` count → FIXED. Evidence now gives the dated count, 27 on 2026-10-04: 24 implementer, reviewer and verifier runs, plus this ticket's own triage, spec writer and critic runs. It also says the count grows as this ticket's runs land.
- Also changed: the Evidence repro pointed to round 1's scratch file, which the harness has since cleared. I re-ran the repro in this round on a fresh clone at `c2750bf`, with the same result, and the bullet now cites `.factory/state/runs/run-0283-spec_writer/scratch/repro-nosync.txt`. design.md, both spec files and the Acceptance list are unchanged from v1.

## Critic rounds

round 1 · spec v1 · run-0279-critic · REVISE

## Critic review, round 1 (spec v1)

Spot-checks made, all from `~/dev/spec-factory` at `c2750bf` (the spec's cited HEAD), under the fresh-HOME wrapper:

- Cited paths and lines: `factory/compose.py` `run_env()` at 57-71 and `wrap()` at 74-78 (an f-string returning `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"{exports}; {command})`, no deactivation); `factory/cli.py` `_start_build_run()` at 238-263, `add_worktree` at 249, `add_detached_worktree` at 261, `copy_environment_files` at 254 and 262, no command run; `tests/factory/test_run_isolation.py` line 22 `WRAP = '(export HOME=...{vars}; {cmd})'`; `store.Refused` (`factory/store.py:25`), `gitops.remove_worktree` (`factory/gitops.py:59`), `store.next_run_id` (`factory/store.py:171`); the "Where you work" block in `factory/compose.py:175-179`, whose gate line ends with the last wrapped command; `docs/design.md:60` "Role-context block" paragraph; `dev/build-harness.spec.md:294` part I with items 1-6; README "Roles, harness, workflows" (line 25) and "Adopting the factory in a repo" step 3 (line 270); changelog's last entry is 53; `grep environment_sync|VIRTUAL_ENV` over design, README, build spec and both instance files finds nothing. Refusals print to stderr and exit 2 (`factory/cli.py:1480-1483`). `build.js:68` parks with `harness-bug: run start ${role}: ${stderr}`. Instance A's `instance.yaml` has `environment_files: ["uv.lock"]` and `run_env: {UV_CACHE_DIR: ...}`, as Operator step 2 says.
- Acceptance commands run on a throwaway store from the fixture block: scenario 1 (wrapper) printed `ve=<T31>/venv ph=<T31>/venv fake_python=1 cache=/tmp/t31-cache home=fresh` twice; scenario 4 (no key) printed `started=yes noted=0 recorded=0 files=0`; the failed-sync scenario printed `implementer: exit=0 named=0 code=0 output=0`, `reviewer: exit=0 named=0 code=0 output=0`, `in_flight=0 checker_checkouts=1`. All three match the verification file's "today" lines, so the NEW items fail today for the stated reason and the regression item passes.
- The part A prefix, run verbatim under `sh`, `bash` and `zsh` with `VIRTUAL_ENV=/x/venv PYTHONHOME=/x/venv PATH=/x/venv/bin:/usr/bin:/bin`, printed `ve=unset ph=unset path=/usr/bin:/bin`; with no `VIRTUAL_ENV`, PATH was unchanged.
- The suite collects 300 tests today, matching the spec's `300 passed` figure.
- Operator step 1's command: a fresh clone at `c2750bf` under a fresh HOME, with the inherited venv's `bin/` dropped from PATH, ran `uv sync --frozen` with exit 0 in 1 s, after which `uv run --no-sync --frozen python -c 'import yaml'` printed `yaml ok` (`scratch/sync.log`).

Findings:

[BLOCKING] 6 Operator steps, step 1; Evidence, first bullet
Problem: The first paragraph of Operator steps says "the runtime is upgraded and this instance accepts the new harness" and Evidence opens with "The Nanobot instance", and neither "runtime", "accepts the harness" nor "instance" is glossed anywhere in the spec, so an operator new to this system has to infer that the factory runs from a separate checkout which must be upgraded, and that each repository's instance must accept the new harness revision before it runs it.
Evidence: Read Problem, Evidence, Decisions and Operator steps for a gloss of "instance", "runtime" and "accept"; Problem glosses "role", "harness", "wrapper", "gate commands" and `instance.yaml` only. `README.md` lines 214-240 ("Accepting a harness revision", "Upgrading the runtime") are where those terms are defined, and the spec does not point there.
Suggested fix: In the Problem's third paragraph, gloss "instance" where `instance.yaml` is introduced ("a repository that runs the factory is an instance; its configuration is `instance.yaml`"), and in Operator step 1 add one clause: "the runtime, the separate checkout the factory runs from, is upgraded to this harness revision, and this instance records that it accepts it (README, 'Accepting a harness revision')".

[SHOULD-FIX] 6 Decisions, bullets 2, 4, 5 and 6
Problem: Later Decisions use `run_env`, "conflict run", "integration branch", "parks the ticket", "the build workflow" and `meta.yaml` without saying what each is, so the reader has to guess what an export through `run_env` does or what parking means.
Evidence: Decisions bullet 2 "`run_env` exports still come after the deactivation"; bullet 4 "a conflict run merges the integration branch in"; bullet 5 "The build workflow then parks the ticket"; bullet 6 "the run's `meta.yaml` records". None is glossed earlier in the human-facing sections.
Suggested fix: Add a few words at each first use: `run_env` "(the variables an instance lists for the wrapper to export)", "a conflict run (an implementer run after the merge gate refused the branch)", "parks the ticket (stops it for a human)", "`meta.yaml` (the run's record)".

[SHOULD-FIX] 4 Operator steps, step 2
Problem: Instance A's gate commands pin `UV_PYTHON_INSTALL_DIR` as well as `UV_CACHE_DIR`, so a sync run under a fresh HOME with only `UV_CACHE_DIR` in `run_env` may not find uv's managed Python and would refuse every build run start on that instance until the Driver adds the second variable.
Evidence: `~/dev/nanobot-upstream/.factory/instance.yaml` lines 25-26 (`run_env: {UV_CACHE_DIR: /Users/dphang/.cache/uv}`) and lines 40-41 (gate commands carry `UV_CACHE_DIR=... UV_PYTHON_INSTALL_DIR=/Users/dphang/.local/share/uv/python`). The spec's step 2 mentions only the cache.
Suggested fix: In step 2, tell the Driver to put every uv variable its gate commands set, `UV_PYTHON_INSTALL_DIR` included, into `run_env` before setting `environment_sync`, since the sync sees only `run_env` and the fresh HOME.

[NIT] 1 Evidence, second bullet
Problem: The count "matches 25 run outputs" is 26 on the live store today because runs land between writing and reading; the bullet's point stands.
Evidence: `grep -l VIRTUAL_ENV .factory/state/runs/*/output.md | wc -l` prints 26 at `c2750bf` with the uncommitted store.
Suggested fix: Say "at least 24 role runs" or date the count; no other change.

No scoping, consistency or hidden-decision findings: the change fits one PR, `Tests to change` names only the `WRAP` constant whose six cases part A breaks by design, every protected path touched is under Risk, and the sync's placement (every run start, both branches, through the wrapper, refuse on failure) is decided in the open with the rejected options named.

Out-of-scope observations:
- `factory/compose.py` `wrap()` is an f-string; the part A prefix contains `${VIRTUAL_ENV:-}`, so the implementer must keep it in the separate module constant design A names rather than paste it into the f-string. The design already says "module constant", so no spec change.
- The exact-entry match `grep -vxF "$VIRTUAL_ENV/bin"` leaves a `bin/` whose PATH spelling differs from `$VIRTUAL_ENV` (for example a symlinked prefix). Activate scripts write the same string, and Risk says "only the exact entry", so this is noted, not asked for.

round 2 · spec v2 · run-0284-critic · APPROVE

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
