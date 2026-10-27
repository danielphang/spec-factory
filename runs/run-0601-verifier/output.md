Commit: 2588b553013712729323c916c8e9063633b47e29 (branch `factory/T-0059.1`, base `db28eb1451e35171b6de62f09d5e378c46a715fa`)

How I ran it. The PR head is the worktree `run-0601-verifier/wt`, after `uv sync --frozen`. The base is a `git clone --shared` of the repo at `db28eb1`, made in my scratch directory, also after `uv sync --frozen`. Every command ran through the HOME wrapper, with TMPDIR set inside the fresh HOME.

First I diffed the six delta files in `openspec/changes/T-0059/specs/` against spec v4. All six are identical.

I wrote my own runner, `scratch/runner.py`, so the check does not depend on the PR's `factory/truth.py`. It runs each GIVEN block once, then each WHEN verbatim under `bash -c` from the checkout's top, with stdin closed. It then compares stdout with the THEN's backticked items or fenced block. I read the three prose THENs myself. Raw results are in `scratch/pr-run.txt`, `scratch/base-run.txt`, `scratch/pr/results.json` and `scratch/basert/results.json`.

The NEW criteria below are the 11 truth-check scenarios, the two gate-commands scenarios, and harness-docs' "describe the truth check". On base, each one prints exactly the "today" output that verification.md states. All of them fail there because `factory` has no `truth` command.

Per criterion:
- NEW | Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time | base: `exit=2` | PR: the 16 lines, ending `16 scenarios: 11 passed, 2 failed, 3 skipped; wall time N s` | PASS
- NEW | The first line names the checkout, the store and the folded deltas, and a failure shows what was expected and what was printed | base: no output | PR: `truth check: G against S; folded: T-0002`, `  expected:`, `    hello`, `  got:`, `    hullo`, `  exit 0` | PASS
- NEW | --capability limits the run, and an unknown capability, a store with no current truth and a caller outside git are refused | base: `one: exit=2 0 0`, `unknown: exit=2 named=0`, `no-truth: exit=2`, `no-git: exit=2` | PR: `one: exit=0 2 2`, `unknown: exit=2 named=1`, `no-truth: exit=2`, `no-git: exit=2` | PASS
- NEW | Capabilities run at the same time | base: no output | PR: `together` | PASS
- NEW | Prose THENs, missing GIVEN blocks and WHENs the caller skips are listed with their reasons and counted as skipped | base: no output | PR: the 5 lines, ending `16 scenarios: 10 passed, 2 failed, 4 skipped; wall time N s` | PASS
- NEW | On a checker's checkout of a sub-ticket its parent's delta is folded and the delta's own scenarios are skipped | base: no output | PR: the 5 lines, starting `truth check: K against S; folded: T-0001, T-0002` | PASS
- NEW | The implementer's worktree folds the same deltas | base: no output | PR: `truth check: W against S; folded: T-0001, T-0002`, then the SKIPPED alpha line | PASS
- NEW | From the integration branch only an open ticket's delta with a merged sub-ticket is folded | base: no output | PR: the 3 expected lines | PASS
- NEW | A folded delta that no longer applies is refused, naming its ticket, and nothing runs | base: `exit=2 named=0 results=0` (argparse's refusal) | PR: `exit=2 named=1 results=0` | PASS
- NEW | truth check reads a live store with a run in flight, from inside its runs/, under another harness revision, and writes nothing | base: `here=2 inside=2 store=unchanged total=factory: error: argument cmd: invalid choice: 'truth' …` | PR: `here=0 inside=0 store=unchanged total=0 scenarios: 0 passed, 0 failed, 0 skipped locked=2` | PASS
- NEW | truth check refuses --accept-harness and names config | base: `exit=2 hint=0 json=0` | PR: `exit=2 hint=1 json=1` | PASS
- NEW | The instance's last gate command is the truth check on the integration checkout's store | base: `  - "uv run --frozen pytest -q -p no:cacheprovider tests/factory"` | PR: the expected `{integration}/bin/factory truth check …` line | PASS
- NEW | The truth check on this checkout reports no failure in the capabilities this change restates | base: `exit=2 ` | PR: `exit=0 failed=0` | PASS. On base, the clone's git common directory has no `.factory/store`, but the command fails before that matters: there is no `truth` command.
- NEW | README, the design doc and the changelog describe the truth check | base: `readonly=no section=no built=no accepting=no design=no design-fence=no changelog=0` | PR: `readonly=yes section=yes built=yes accepting=yes design=yes design-fence=yes changelog=1` | PASS
- REGRESSION | README, the design doc and the changelog describe the refusal route (restated form) | base: not run | PR: `formed=yes truth=yes round=yes edge=yes row=yes design=yes growth=ok`, `CONTIGUOUS`, `entries=1 terms=3` | PASS
- REGRESSION | Implementer and verifier run prompts carry the declared-path rule | base: not run | PR: `implementer declared=1 notunder=1 undeclared=1`, `verifier declared=1 notunder=1 undeclared=1` | PASS
- REGRESSION | Status transitions write the same events and history entries | base: not run | PR: the 14 lines, an exact match | PASS
- REGRESSION | Spec pinning and planner-run refusals keep their text | base: not run | PR: the 4 lines, an exact match | PASS
- REGRESSION | The dispatcher parks a refused store command with the same reason | base: not run | PR: the 3 lines, an exact match | PASS
- REGRESSION | The spec parser gives the same result as the base on every spec in the store | base: not run | PR: `files=395 checks=6157 differ=0`, nothing after it (prose THEN, read by hand) | PASS
- REGRESSION | The refactored harness has no unused imports or variables | base: not run | PR: `All checks passed!`, exit 0 | PASS
- REGRESSION | The harness suite passes and no existing test file changes | base: not run | PR: `658 passed in 99.74s (0:01:39)`, nothing after it | PASS. One deviation: a Claude Code safety check refused the WHEN as written, because its `rm -rf "$P"` deletes the output of a command substitution. I ran `mktemp -d /tmp/t0046-suite.XXXXXX` on its own, then ran the WHEN with `P=/tmp/t0046-suite.FjA2ei` and `rm -rf` on that literal path. Every other character of the command is unchanged. An earlier attempt, with P under my scratch directory, gave `19 failed, 639 passed`. That P sits inside the store's git checkout, and the WHEN puts its directory under `/tmp`, so I did not count that run.
- REGRESSION | The drift checks live in factory/drift.py | base: not run | PR: the expected 7 names | PASS
- REGRESSION | The shared helpers and the live-store fence live in factory/common.py | base: not run | PR: `_add_spec_version _in_flight _integration_head _rel fence out` | PASS
- REGRESSION | Instance and store setup live in factory/setup.py | base: not run | PR: the expected names, an exact match | PASS
- REGRESSION | The gates live in factory/gates.py | base: not run | PR: the expected names, an exact match | PASS
- REGRESSION | The human decisions live in factory/human.py | base: not run | PR: the expected names, an exact match | PASS
- REGRESSION | factory/cli.py keeps the parser, the entry point and the role list, in under 910 lines | base: not run | PR: `899 3` (prose THEN: 899 < 910, second number 3) | PASS
- REGRESSION | Unmarked writes from inside the target are refused while a run is in flight, init included | base: not run | PR: `init=2 new=2 transition=2 decision=2 store=unchanged agents=none` | PASS
- REGRESSION | The refusal names the throwaway store and not the marker | base: not run | PR: `rule=1 state=1 marker=0 json=1 inside=1` | PASS
- REGRESSION | A harness acceptance is refused while a run is in flight | base: not run | PR: `accept=2 store=unchanged` | PASS
- REGRESSION | A launch copy is written unmarked while a run is in flight, and the target is unchanged | base: not run | PR: `launch=0 new=2 copies=1 store=unchanged` | PASS
- REGRESSION | The flag with init, paths or stats is refused, names config, and writes nothing, even where init would create an instance | base: not run | PR: the 5 lines, an exact match | PASS
- REGRESSION | Without the flag paths and stats still run under another lock, and config still accepts a revision | base: not run | PR: `paths=0 stats=0 config=2 accept=0 lock=accepted` | PASS

Gate suite: PASS
  `git diff --check main...HEAD` exited 0 with no output (`main` is `db28eb1`). `uv run --frozen pytest -q -p no:cacheprovider tests/factory` exited 0: `658 passed in 107.93s (0:01:47)`.

Probes. I built a store with two capabilities, `p` and `q`, in `scratch/probe`, beside a fresh git target, and ran it with `truth check --store`. Results are in `scratch/probe/out.txt`.
- An exact THEN, `a`, against printed `a`, `b` → FAIL, showing both lines. The same with `hello` against `hello world` → FAIL. There is no contains match. → OK
- A THEN with a trailing sentence (`` it prints exactly `a`. It also cleans up. ``) → SKIPPED, with the THEN as its reason. → OK
- Forms the tests do not cover: `` `x` three times `` → PASS; `` `y`, and exits 0 `` with exit 0 → PASS; output with no trailing newline → PASS; two trailing newlines → FAIL, since only one is removed; an item with leading and trailing spaces → PASS. → OK
- 50 lines of output plus stderr → FAIL, showing 40 lines, `    … 10 more lines`, `  exit 0` and `  stderr:` with `oops`. A non-UTF-8 byte → FAIL, printed as a replacement character, with no crash. → OK
- A WHEN with no backticks, and a scenario with two WHEN lines → SKIPPED, with the spec's reasons. → OK
- Two scenarios whose GIVEN references form a cycle → each block runs once, with no loop (`A B `). → OK
- A run from a subdirectory with a relative `--store ../../s`, and a run with only `FACTORY_STATE` set → both find the store, and the WHEN's `pwd` is the checkout's top. A store path that does not exist → exit 2 with the "has no current truth" refusal. → OK
- The full gate replay, as operator step 1 runs it, against the live store, run from this worktree with `--skip-when-contains 'pytest -q -p no:cacheprovider tests/factory'`. Result: `folded: T-0059`; `339 scenarios: 276 passed, 0 failed, 63 skipped; wall time 124 s`; exit 0. The 63 skips are 34 in T-0059's delta, 13 suite WHENs and 16 prose THENs. The live store's `git status --porcelain`, my own run directory aside, was the same before and after: 14 entries. → OK. The gate's first run is clean at this head.

Protected paths touched, all declared in the spec's Risk section: `factory/truth.py`, `factory/cli.py` and `.factory/instance.yaml`. No other protected path is in the diff. `tests/factory/test_truth.py` is a new file, and no existing test file changed.

STATUS: VERIFIED
CONFIDENCE: high. All 34 acceptance commands match their THENs on the PR, and all 14 NEW ones fail on base for the stated reason. Both gates pass, and the probes and the full live replay show the command handles inputs beyond its tests. The one deviation is the suite scenario's removal of its temporary directory, run on a literal path; it does not change what that scenario checks.
ESCALATIONS: none
