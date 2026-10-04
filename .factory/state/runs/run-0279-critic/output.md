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

STATUS: REVISE
CONFIDENCE: high, every cited path and three of the eight acceptance commands were run on the cited HEAD and behave as the spec says; the only blocking item is a glossing gap in the operator-facing sections.
ESCALATIONS: none
