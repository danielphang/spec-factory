## Acceptance
Each "today" result below was run in this round on a clone at `b002c95`, under bash and under zsh, with a fresh HOME and `TMPDIR`.
- A role's wrapper and its wrapped gate command drop an inherited virtual environment → NEW. Today both lines print `ve=<T31>/venv ph=<T31>/venv fake_python=1 cache=/tmp/t31-cache home=fresh`. The wrapper passes the inherited `VIRTUAL_ENV` and `PYTHONHOME` through, and the fake environment's `python` is found first.
- An implementer's worktree is synced through the wrapper at every dispatch, and its input says so → NEW. Today it prints `first: synced=no ve= venv_on_path=0 cache=0 home=fresh noted=0`, then `again: synced=no`: the `environment_sync` key is ignored and the input has no sync line.
- A checker's checkout is synced before the checker starts, and its input says so → NEW. Today it prints `synced=no ve= venv_on_path=0 noted=0`.
- A failed sync refuses the run start with a one-line reason, keeps its output in a log, and leaves no run or checker checkout → NEW. Today it prints `implementer: exit=0 named=0 code=0 shell_chars=0 logged=0`, `reviewer: exit=0 named=0 code=0 shell_chars=0 logged=0`, `in_flight=0 checker_checkouts=1 meta=2`: both runs start, both stay in flight, and the checker's checkout exists.
- Without environment_sync, run start and the input are as before → REGRESSION. Prints `started=yes noted=0 recorded=0 files=0` today.
- The design doc, build spec, template and README name the sync and the dropped virtual environment, and no prompt copy changes → NEW. Today it prints `design=0 design_venv=0 build_spec=0 template=0 readme=0 readme_venv=0 prompts=0`.
- The changelog records the environment sync as its last entry → NEW. Today it prints `CONTIGUOUS`, then `0`: the last entry (63) names none of the four terms.
- The environment-sync change adds no whitespace errors → REGRESSION. Prints `exit=0` today.

## Responses
Responses to the operator's change request of 2026-10-09 (`approvals/T-0031/changes-1.md`):
- 1, list the `test_gate_paths.py` test and check the whole suite → FIXED. Tests to change now lists `tests/factory/test_gate_paths.py` line 217, with the reason and the exact new lines, and says nothing else in the file changes. To find any other test that pins the wrapper text or run start's setup, I ran the whole suite on a prototype of parts A to D: `7 failed, 401 passed`. All seven were the six `WRAP` cases and this one case. With the two listed edits: `408 passed`, the same as the unchanged base. A grep for the wrapper's text over `tests/factory/` finds only these two files.
- 2, refresh Evidence and line references → FIXED. Every `compose.py`, `cli.py` and `build.js` line number is re-read on `b002c95`. Store paths now use `.factory/store` (T-0025), on both instances. The `VIRTUAL_ENV` count is re-derived (31 on 2026-10-09). The no-sync repro and every scenario's "today" output were re-run in this round, under bash and zsh. The changelog's last entry is now 63.
- 3, declare protected paths on the Risk line → FIXED. Risk opens with the declaration line, naming the three harness files the change touches: `factory/compose.py`, `factory/cli.py` and `factory/instance.template.yaml`. No other protected path is touched.
- 4, keep the design and Decisions unless the refresh shows a conflict → two conflicts found, so two changes; everything else is kept:
  - The failed-sync refusal no longer carries the command or its output. They go to `runs/<id>/environment-sync.log`, and the refusal names that file. Since 2026-10-04, T-0033 recorded that the build workflow passes a park reason to the shell in double quotes, which expand backticks and `$`. uv's errors contain backticks (Evidence). The failed-sync requirement and scenario change to match. The scenario now also checks that the refusal carries no such character and that the log holds the output. Its "today" output was re-run.
  - The "already synced" line goes at the end of the "Where you work" block, not after the gate-commands line. Since T-0032 the reviewer's input has no gate-commands line, and since T-0028 SKIPPED lines follow it. The scenarios find the line anywhere in the input, so they are unchanged.
  - Also changed: the Decision on where the sync runs adds why the reviewer is still synced (its prompt lets it run one test). Risk adds the empty-`PATH`-entry edge case that run-0366 found, and notes that readers of `runs/` skip a directory with no `meta.yaml`.

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

round 1 · spec v3 · run-0379-critic · APPROVE

Spec critic, T-0031 spec v3, round 1 of this version (the operator's change request `approvals/T-0031/changes-1.md` preceded it; no earlier critic findings were in my input).

What I checked myself, on `~/dev/spec-factory` at `main` = `8929054` (two commits past the spec's `b002c95`: the T-0039.1 merge, which touched only `factory/prompts/*.md` and added `tests/factory/test_turn_economy.py`):
- Every cited harness line: `factory/compose.py` 147-161 (`run_env`), 164-168 (`wrap`), 315-326 ("Where you work", reviewer line at 318-319, SKIPPED lines at 324-325), 20-21; `factory/cli.py` 215-236 (`gate_entries` check, `next_run_id`, `_start_build_run` call, `meta.yaml` write at 225, in-flight append at 236), 269-299 (`_start_build_run`), 1446-1449; `factory/specstore.py` 277-280; `factory/workflows/build.js` 62 and 84; `factory/prompts/reviewer.md` 9; `tests/factory/test_run_isolation.py` 22 (`WRAP`, used by the five named tests, six cases); `tests/factory/test_gate_paths.py` 217 (`want`). All hold. `gitops.remove_worktree`, `gitops.copy_environment_files`, `gitops.add_detached_worktree` exist (`factory/gitops.py` 59, 65, 54). `~/dev/nanobot-upstream/.factory/instance.yaml` lines 25-27 and 54 say what the spec says (read only).
- Tests pinning changed behaviour: `grep -rn -e 'export HOME' -e environment_sync -e instance.template tests/factory/` finds only the two listed lines plus `test_instance.py` 103 and 351, which compare named template keys and would not see a new `environment_sync` key. No test asserts the "Where you work" block's exact ending or `meta.yaml`'s key set. No current-truth capability in my input quotes the wrapper text, and the decision log says nothing about the wrapper or environments.
- Acceptance commands run as given, under the HOME wrapper (no test suite): the wrapper scenario printed two lines `ve=<T31>/venv ph=<T31>/venv fake_python=1 cache=/tmp/t31-cache home=fresh`; the failed-sync scenario printed `implementer: exit=0 named=0 code=0 shell_chars=0 logged=0`, `reviewer: exit=0 named=0 code=0 shell_chars=0 logged=0`, `in_flight=0 checker_checkouts=1 meta=2`; the documents scenario printed `design=0 design_venv=0 build_spec=0 template=0 readme=0 readme_venv=0 prompts=0`; the changelog scenario printed `CONTIGUOUS` then `0`. Each matches the spec's "today" line, so the NEW items fail today for the stated reason.
- Evidence counts: `grep -l VIRTUAL_ENV .factory/store/runs/*/output.md` now matches 32 (10 implementer, 5 reviewer, 11 verifier, 3 spec_writer, 2 critic, 1 triage); the 26 build-role runs match the spec, the sixth own run is the v3 spec writer.
- Not checked: anything that needs the harness suite or the built change (the `408` / `7 failed` counts, the second implementer dispatch after a `KILLED` finish in the implementer scenario, the prototype's THEN outputs). The spec reports them as run; the verifier will see them.

Findings

[SHOULD-FIX] 4 Proposed change C.1 and Decisions, "refused at run start, before any checkout is made"
Problem: C.1 validates `environment_sync` inside `_start_build_run`, which runs after `store.next_run_id` has already created `runs/<id>/` (cli.py:217, store.py:171-175, "Allocate a run id by creating its directory"), so a bad value does not "write nothing": it leaves an empty run directory, unlike the malformed-gate refusal the spec models it on.
Evidence: cli.py:215 runs `compose.gate_entries(cfg)` with the comment "a malformed gate entry refuses here, before a run id is reserved"; `tests/factory/test_gate_paths.py` 179 and 209 pin that refusal as leaving `runs/` unchanged. Part E's case "a non-string `environment_sync` refused before any checkout is made" would pass with an empty directory left behind.
Suggested fix: call `compose.environment_sync(cfg)` beside `compose.gate_entries(cfg)` at cli.py:215, before the run id is reserved, and have part E's case also assert that `runs/` is unchanged.

[SHOULD-FIX] 5 Proposed change F, `dev/build-harness.spec.md` "add one item after I.3"
Problem: part I is a numbered list of six items, and other parts of the build spec cite its numbers (`I.5` at lines 206, 276, 411 and 507; `I.3` at 511), so inserting after I.3 renumbers I.4 to I.6 and breaks those citations.
Evidence: `dev/build-harness.spec.md` 295-302: "### I. Isolated run per role" followed by items 1 to 6; `grep -n 'I\.[0-9]' dev/build-harness.spec.md`.
Suggested fix: append the new item as I.7 (or state that the writer renumbers every cross-reference, which is more change for no gain).

[NIT] 1 Problem, last paragraph, and Evidence
Problem: three figures are one merge stale: `main` is `8929054`, not `b002c95`; the changelog's last entry is 64 (so the new one is 65, which part F's "or the next free number when it merges" already allows); the suite has grown by `test_turn_economy.py`, so `408 passed` is no longer the base count.
Evidence: `git log --oneline b002c95..HEAD`; `grep '^[0-9]*\. ' docs/changelog.md | tail -1` starts `64.`.
Suggested fix: none needed for the design; the implementer should expect the base count to differ, and the verifier should not treat `408` as the target.

No BLOCKING finding. The Problem's first paragraph says what is wrong (a lost first attempt to a broken Python environment) and for whom (the implementer, reviewer and verifier), and the human-facing sections gloss role, harness, wrapper, gate commands, instance, run_env, runtime, build workflow and clerk on first use. "Tests to change" names exactly the two tests the change breaks, with the reason and the replacement text for each. Protected paths are declared and match the design (`factory/compose.py`, `factory/cli.py`, `factory/instance.template.yaml`). The operator's four change-request items are each addressed in Responses, and the two design changes (log file instead of inline output; input line at the end of "Where you work") follow from facts I confirmed in `build.js:62` and `compose.py:318-325`.

Out-of-scope observations
- Part A's PATH filter sets an empty `PATH` when `$VIRTUAL_ENV/bin` is the only entry (`grep -v` prints nothing). Not a realistic shell; noting it beside the empty-entry edge Risk already names.

Prior findings: none (first critic round on v3).
