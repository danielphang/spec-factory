Sub-ticket: T-0054.1, `/Users/dphang/dev/spec-factory/.factory/store/tickets/T-0054.1.yaml`. Parent spec v3: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0054/v3.md`.
Branch: `factory/T-0054.1`, one commit, `e12ca71`, on base `308d038`. Worktree: `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0054.1`.

## What changed

Workflow builds no longer stop because the clerk miscopied a reply. The clerk is the small agent that runs one store command for a workflow script and copies its output back. On real runs it retyped a role's model (#109) and spread a one-line JSON reply over several lines (#112). Each slip parked a sub-ticket. For #112, no `resolve` command could return the sub-ticket.

**A. `factory launch-script intake|build`** (new `factory/launch.py`, 57 lines; `factory/cli.py`).
- The command reads `factory/workflows/<name>.js` from the running harness checkout. It requires the line `const LAUNCH = null` exactly once and otherwise refuses with exit 2. It then writes `<name>.js` read-only (0444) into a new `tempfile.mkdtemp(prefix="factory-launch-")` directory. In the copy, that one line becomes `const LAUNCH = {...}`. The object holds `written_by`, `source`, `harness_revision`, `instance` (as `factory paths` prints it), `models`, `max_rounds` and `state_dir`. The command prints `{"ok": true, "script", "source", "harness_revision", "instance"}`.
- Before writing, it removes each `factory-launch-*` directory under the temporary directory that meets three conditions: it is more than 3,600 seconds old; it holds exactly one file, named `intake.js` or `build.js`; and that file contains `"written_by": "factory launch-script"`. It skips every other directory, and any `OSError` or `ValueError` while checking one.
- `config_values()` in `launch.py` is now the one definition of what `factory config` prints. `config_cmd` uses it too.
- `cli.py` gains the `launch-script` subparser, with one positional `name` (`intake` or `build`). It also adds `("launch-script", None)` to `READ_ONLY`, so the command takes `config`'s path through `main()`: the instance is required, the fence is skipped, and the harness lock is checked.

**B. Both workflow scripts honour a launch copy** (`build.js`, `intake.js`).
- Each script gains a comment and the line `const LAUNCH = null` above `INSTANCE`.
- `const INSTANCE = LAUNCH ? LAUNCH.instance : args.instance`.
- Before the config step: a copy given another `args.instance` returns `{ticket, error: "launch copy written for instance <recorded>, launched with <given>"}`.
- The config step is `const cfg = LAUNCH ? { ok: true, ...LAUNCH } : <the clerk call as before>`. The lines after it are unchanged.
- The `// args:` header comments now say a launch copy takes its instance from the copy.

**C. `clerk()` parses a reply spread over several lines** (both scripts). It trims stdout once and tries `JSON.parse` on the whole text. Only when that fails does it run the old scan from the last line up. Every rule after the parse is unchanged.

**D. `factory resolve <id> --to checks`** (`factory/human.py`, `factory/store.py`, `factory/gates.py`).
- A new branch inside `resolve` accepts a ticket that meets four conditions: status `parked`, `parked.from == "ready-for-implementer"`, a reason starting `harness-bug:`, and `store.implemented_since_ready()`.
- Accepted: `store.set_head()` reads the branch tip, then `store._apply_round(t, "pr:init", cfg)` applies the round step, then `move("checks-in-flight", "to-checks", {"head": ...})` writes the history entry, `resolve-<n>.yaml` and the `human.resolved` event.
- Refused: exit 2, nothing written, and the error `--to checks applies to a sub-ticket parked by a harness-bug from ready-for-implementer after its implementer run finished READY-FOR-REVIEW; <id> is <status> (<reason or 'no park'>)`.
- Any other `--to` value is refused with `--to accepts only spec-gate or checks`.
- New in `store.py`:
  - `implemented_since_ready(root, tid)`, beside `log_lines`. It reads the event log in file and line order. A move into ready-for-implementer is any event of the ticket whose `to` is that state, or a `ticket.created` whose `status` is. The newest implementer `run.started` must come after the last such move, and that run's `run.finished` must carry `READY-FOR-REVIEW`.
  - `set_head(root, cfg, t)`, the body of `ticket head` moved from `gates.py` with the conflict bookkeeping. It keeps its one `gitops.repo_root()` call, with `gitops` imported inside the function. `gates.ticket_head` now loads the ticket, calls it and prints the result.
  - `_apply_round`, moved from `cli.py` with its exact text. `ticket transition` calls `store._apply_round`.
- The parser's `--to` has help text naming `spec-gate` and `checks`. The "resolve needs one of …" message now lists `--to spec-gate|checks`. That message change is beyond the design's text.
- Callers, found by grep (coding rule 2):
  - `_apply_round`: `cli.ticket_transition` only, before this change.
  - `ticket head`'s body: `gates.ticket_head`, reached only through the parser.
  - `config` values: `config_cmd`.
  - `clerk()`: every store call in each script. Its behaviour changes only for a stdout whose whole text is one JSON value.

**E. Tests**: three new files under `tests/factory/`, listed below. No existing file changed.

**F. Documents.**
- `README.md`, 1,108 → 1,109 lines (budget 1,110):
  - "Starting a run": `README.md:699-711` is replaced by the spec's 13-line draft, word for word.
  - The run-start paragraph gains one line: a launch copy carries the models itself.
  - "Where a human decides": `launch-script` is added to "A write is any command except …;", rewrapped with no added line.
  - The **Unstick** row gains `--to checks`, with what it is for and "not yet run on a real ticket".
  - The status date is now 2026-10-19.
- `docs/design.md`:
  - line 44, limit (1): one sentence on the launch copy and on parsing a reply spread over several lines;
  - line 64: `launch-script` added to the read-only list;
  - line 109: the `--to checks` route, after the harness-bug ruling rule.
  - None of these is a prompt block, so `docs/prompts/` does not change.
- `docs/changelog.md`: entry 75, opening `75. After issue #109 `, naming #112, `launch-script` and `--to checks`.

Protected paths touched: `factory/**` (`launch.py`, `cli.py`, `gates.py`, `human.py`, `store.py`, `workflows/*.js`). The spec's Risk section declares them.

## Acceptance results

I copied every WHEN command verbatim out of spec v3 with a script (`scratch/extract.py`). The GIVEN blocks came from v3, `openspec/specs/human-resolution/spec.md` (`t0023-parent.sh`) and `openspec/specs/build-dispatch/spec.md` (`t0032-checks.sh`). I ran each one from the worktree inside the HOME wrapper, with `TMPDIR` set to my scratch directory, under GNU bash 5.3 (`/opt/homebrew/bin/bash`). "Before" was run on `308d038` before any edit. "After" was run on `e12ca71`. Logs: `scratch/base-new.log`, `scratch/base-15.log`, `scratch/pr-accept.log`, `scratch/pr-15.log`.

| # | Scenario | Kind | Before (308d038) | After (e12ca71) |
|---|---|---|---|---|
| 1 | A build launched from its launch copy runs the verifier on the instance's model while the clerk retypes it, and the script itself still parks | NEW | `Error: ENOENT: no such file or directory, open 'no launch copy'`, `copy: checks-in-flight runs=`, then the script's 3 lines | `agent reviewer T-0001.1 model=fable` / `agent verifier T-0001.1 model=opus` / `copy: merged runs=reviewer fable verifier opus` / `agent reviewer T-0001.1 model=fable` / `park T-0001.1: harness-bug: run start verifier: model fable refused for verifier: the instance names opus` / `script: parked runs=reviewer fable`: matches THEN |
| 2 | An intake launched from its launch copy runs triage on the instance's model while the clerk retypes it | NEW | `Error: ENOENT …`, `ready-for-triage runs=` | `agent triage T-0001 model=opus` / `closed runs=triage=opus`: matches |
| 3 | Each launch copy is a one-line change to its script, … | NEW | `intake: where=none changed=206 revision=0 instance=0 writable=no` / `build: where=none changed=310 revision=0 instance=0 writable=no` / `checkout=unchanged store=unchanged dirs=0` | `intake: where=own-dir changed=2 revision=1 instance=1 writable=no` / `build: where=own-dir changed=2 revision=1 instance=1 writable=no` / `checkout=unchanged store=unchanged dirs=2`: matches |
| 4 | launch-script is refused with config's error where the instance has not accepted the running harness, … | NEW | `config=2 launch=2 same=no lock=0 copies=0` | `config=2 launch=2 same=yes lock=1 copies=0`: matches |
| 5 | launch-script removes a launch copy over an hour old and keeps a recent one and a directory that holds no launch copy | NEW | `old=gone other=kept fresh=gone new=none dirs=1` | `old=gone other=kept fresh=kept new=written dirs=3`: matches |
| 6 | A launch copy launched for another instance returns an error naming its own and runs nothing | NEW | `refused=0 agents=0 checks-in-flight runs=0` | `refused=1 agents=0 checks-in-flight runs=0`: matches |
| 7 | A build and an intake whose every store reply is relayed pretty-printed reach the ends they reach with one-line replies | NEW | `result: no JSON on stdout` / `build: T-0001.1 ready-for-implementer` / `result: no JSON on stdout` / `intake: T-0002 ready-for-triage` | `agent implementer T-0001.1 model=opus` / `agent reviewer T-0001.1 model=fable` / `agent verifier T-0001.1 model=opus` / `build: T-0001.1 merged` / `agent triage T-0002 model=opus` / `intake: T-0002 closed`: matches |
| 8 | A sub-ticket parked when its implementer's finish did not parse returns to its checks at the branch tip, and the build then merges it | NEW | `resolve=2 parked head=other pr=0` / `parked implementer_runs=1` | `resolve=0 checks-in-flight head=tip pr=1` / `agent reviewer T-0001.1 model=fable` / `agent verifier T-0001.1 model=opus` / `merged implementer_runs=1`: matches |
| 9 | The route back to checks is refused after a BLOCKED run, after a revise, from the checks, on a tripwire park and on a ticket that is not parked | NEW | each line `exit=2 refused=0 …` | `blocked: exit=2 refused=1 parked store=unchanged` / `revised: …` / `checks: …` (same form) / `tripwire: …` / `unparked: exit=2 refused=1 ready-for-implementer store=unchanged`: matches |
| 10 | Unmarked writes from inside the target are refused while a run is in flight, init included | REGRESSION | not run (it passed on main when the spec was written) | `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`: matches |
| 11 | The refusal names the throwaway store and not the marker | REGRESSION | not run | `rule=1 state=1 marker=0 json=1 inside=1`: matches |
| 12 | A harness acceptance is refused while a run is in flight | REGRESSION | not run | `accept=2 store=unchanged`: matches |
| 13 | A launch copy is written unmarked while a run is in flight, and the target is unchanged | NEW | `launch=2 new=2 copies=0 store=unchanged` | `launch=0 new=2 copies=1 store=unchanged`: matches |
| 14 | The README, the design doc and the changelog describe the launch copy and the route back to checks | NEW | `start=no unstick=no writes=no list=1 fence=no route=no readme=within` / `CONTIGUOUS` / `entries=0 terms=0` / `exit=0` | `start=yes unstick=yes writes=yes list=1 fence=yes route=yes readme=within` / `CONTIGUOUS` / `entries=1 terms=3` / `exit=0`, run after the commit, because its `git diff --check` reads HEAD: matches |
| 15 | The suite passes, no existing test changes, and every test file this change adds fails on the base | NEW | `594 passed in 105.71s` / `changed=0 added=0` | `615 passed in 117.20s` / `changed=0 added=3` / `tests/factory/test_launch_script.py on the base: 4 failed, 1 error` / `tests/factory/test_resolve_to_checks.py on the base: 8 failed` / `tests/factory/test_workflow_launch_copy.py on the base: 7 failed, 1 passed`: matches THEN; every summary includes `failed` |

Gate commands, each run exactly as written from the worktree on `e12ca71`:
- `git diff --check main...HEAD`, wrapped: no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, wrapped: `615 passed in 115.16s (0:01:55)`, exit 0. Afterwards the system temporary directory held no `factory-launch-*` directory.

Current-truth pins from harness-code that the spec's Risk section names, run on `e12ca71`:

| Check | Output | Expected |
|---|---|---|
| repo-root helper: `repo_root(cfg` callers, `gitops.repo_root()` sites, its definition | `0 12 1` | `0 12 1` |
| `"ticket.transition"` literals in the CLI modules and in `store.py` | `1 1` | `1 1` |
| `"*.jsonl"` in the CLI modules and in `store.py` | `0 1` | `0 1` |
| run listing outside `store.py` | `0` | `0` |
| integration-tip reads and `integration_tip` definitions | `1 1` | `1 1` |
| `factory/cli.py` line count and pinned definitions | `877 3` | under 900, and `3` |
| modules that import `factory.cli` | `factory/__main__.py factory/drive.py factory/stats.py` | the same three |
| `uvx ruff check --select F factory` | `All checks passed!` | the same |
| `uvx ruff check --select F401,F841 factory tests` | `All checks passed!` | the same |

The pinned definition lists of `drift.py`, `common.py`, `setup.py`, `gates.py` and `human.py` print exactly their current-truth strings. `t0047-moved.py` prints `pairs=5 added=13 removed=6 lines=157`. The spec's Risk section predicts this: that scenario measures T-0047's split, so it counts this change's new and moved definitions. `_apply_round` moved with its exact text and is not counted.

## Tests added/changed

No existing test file changed. Three new files:

- **`tests/factory/test_launch_script.py`** (5 tests): the CLI half of `launch-script`.
  - For each script: the copy differs from it in one line, and that line's JSON holds exactly `written_by`, `source`, the revision and instance `paths` prints, and the `models`, `max_rounds` and `state_dir` `config` prints. The copy is mode 0444, alone in its own `factory-launch-*` directory. The printed JSON is as designed. The store is unchanged.
  - Under a lock that names another revision, it is refused with `config`'s stderr byte for byte, and writes no copy.
  - It runs unmarked while a run is in flight, beside a refused `ticket new`, and the target is unchanged.
  - Cleanup removes an hour-old copy. It keeps three directories: a fresh copy, an old directory with a non-copy `build.js`, and an old copy with a second file beside it.
  - An autouse fixture points `TMPDIR` inside the test's `tmp_path`. `launch()` fails a test whose copy lands outside it. This is coding rule 6's guard for the new outside path.
- **`tests/factory/test_workflow_launch_copy.py`** (8 tests): the scripts under node, with a stand-in clerk that runs each command for real and miscopies on request, as decision 12 allows.
  - A build from a launch copy runs implementer, reviewer, verifier and every clerk call on the instance's models, while the stand-in clerk names `sonnet` for all four. It then merges.
  - `build.js` launched as it is still parks at the verifier's run start, as T-0050's backstop does. This test also passes on the base, as intended.
  - An intake from a launch copy runs triage on `opus` while the clerk names `fable`.
  - A copy of either script given another instance returns the error and makes no agent call.
  - A build and an intake whose every reply is pretty-printed merge and close.
  - A sub-ticket returned by `resolve --to checks` merges with one implementer run.
- **`tests/factory/test_resolve_to_checks.py`** (8 tests): the route.
  - #112's park returns to `checks-in-flight` at the branch tip with `round.pr` 1. The history entry, `resolve-1.yaml` and the `human.resolved` event all carry `to-checks`.
  - A later round (2) is unchanged.
  - The blocked, revised, checks, tripwire and unparked cases are refused, naming the status, with the store byte-identical (worktrees excluded).
  - Another `--to` value names both routes.

On a git checkout of the base, all 21 new tests failed before I edited any code. One of them, the as-launched backstop test, failed only because of my own assertion bug: stderr's trailing newline. I fixed the assertion, not the code. In the spec's base-tree mechanics (scenario 15) one test errors instead of failing; see Known gaps.

## Known gaps and uncertainties

- **Scenario 3 does not parse under macOS `/bin/sh`.** That shell is bash 3.2, and it reports `syntax error near unexpected token 'newline'` on the `$(case … esac)` inside the command. I ran every WHEN under bash 5.3. On the base, bash 5.3 and zsh both print the "today" output verification.md records, so the spec's author used a newer shell. A verifier using `sh` on this machine will see the syntax error whatever the code does.
- **Not run in Claude Code's Workflow tool.** I could not run it here. Whether it loads a script from the temporary directory, and whether the auto-mode classifier lets it run, is Operator step 1, as the Risk section says.
- **Instance comparison is exact string equality.** A copy given the same instance path with a trailing slash or through a symlink returns the "launched with" error. This follows the design's text.
- **A copy launched without `args.state` gets no `FACTORY_STATE` in its clerk commands.** It takes `STATE` from `LAUNCH.state_dir`, as the clerk path takes it from `config`. If the session that ran `launch-script` had `FACTORY_STATE` set and the Workflow clerk's shell does not, two things diverge: the role agents read run files under the recorded store, and the clerk's commands go to the instance's own store. The design does not set `STATE` from `LAUNCH` before `ENV` is built, so I did not either. Setting `let STATE = args.state || (LAUNCH && LAUNCH.state_dir) || null` would close it, but that is a design decision for the spec.
- **The refusal when `const LAUNCH = null` does not occur exactly once is untested.** Testing it needs a harness checkout with an edited script. I read the code path; I did not run it.
- **The "resolve needs one of …" usage message** now says `--to spec-gate|checks`. The design names only the `--to` refusal and the help text. No test pins this message.
- **On the base tree in scenario 15**, `test_launch_script.py` reports `4 failed, 1 error`. The error is the `target` fixture: `factory init` cannot read the harness revision of a `git archive` tree, which is not a git checkout. On a git checkout of the base, all five tests fail with `invalid choice: 'launch-script'`.
- **Size.** The change is 690 lines added and 74 removed. `factory/` accounts for 177 added and 54 removed; the new tests for 490. The design estimated under 400 lines with tests and docs. The node driver and the fixture classes are most of the test lines.
- **One ruff finding in the new tests.** `ruff --select F` on them reports F811 for the `target` fixture parameter. `test_live_store_guard.py` uses the same idiom, and the pinned ruff commands pass.
- **No `AGENTS.md`.** This repository has none, so step 1 of the process read none.
- `factory:` markers added: none.

## Out-of-scope observations

- `MAX_PR` in `build.js` is still set and never read, as the spec notes.
- The `STATE` gap above may deserve its own small ticket if the operator ever launches copies with a throwaway `FACTORY_STATE`.

## Responses to findings

None: this is round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high: every acceptance command prints its THEN on `e12ca71`, both gates pass and the harness-code pins hold; the Workflow tool itself is unverified, as the spec's Risk section says.
ESCALATIONS: none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
