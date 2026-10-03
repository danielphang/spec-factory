## Context for this run (composed by the harness, not part of the request)

Repository: `nanobot`, the lionbot fork. This checkout is the TARGET generation: branch
`feat/lionbot-v3` at `~/dev/nanobot-upstream` (upstream base tag `lionbot-v3-base`). The
REFERENCE generation is the production fork at `~/dev/nanobot` (branch `feat/lionbot-next`,
"blue"): read it only to observe what the feature does today; never copy its test names,
line numbers or commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Running things here: `uv run <cmd>` from the repo root (never pip). Tests run serially with
`PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider <path>`.
Lint: `uv run ruff check nanobot/`. Acceptance commands must be runnable as written on this checkout.

The request is a legacy "faux spec": a document that mixes the durable intent (what the
operator needs the bot to do) with one generation's implementation record (test names,
file:line citations, commit SHAs, ledger status, verification narrative, a prior
implementation profile). Treat the implementation record as evidence of what the reference
generation did, not as requirements. Carry forward only what the requester needs; anything
that can be re-derived from the code at build time does not belong in the spec. Where the
request's status says the capability is already built on this checkout, verify that before
writing NEW criteria; a NEW criterion that already passes proves nothing.

Build half, as this repo runs it today: there is no remote and no CI service. "Open a PR" means
commit on your branch in your worktree and return the PR description; "push" means commit; the
"CI result" is the gate suite (the gate commands in your input: lint, and the full-suite gate,
which passes when no test fails outside the port's known-failure baseline), which the verifier
runs on the head and reports as `Gate suite: PASS|FAIL`. A merged sub-ticket is a local
`--no-ff` merge into the integration branch. Never push, never touch another worktree. Running the
gate rewrites `webui/package-lock.json` and creates `webui/node_modules/`: never commit either; stage
the files you changed by name, not with `git add -A`.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. For
every role but the implementer that is the only file you may create or modify. The implementer
also changes files in its own worktree and commits there, and nowhere else. Then return the same text as your final message.
## Output file
`/Users/dphang/dev/spec-factory/intake/green-pilot/runs/run-0019-planner/output.md`

## Approved spec (v1, pinned)

=== proposal.md
## Problem
The spec factory is a pipeline of AI agents that turns a request into merged code. Before a change merges, two checker agents look at it: a reviewer, which reads the diff, and a verifier, which runs the acceptance commands and the test suite. A script called the build loop runs each checker. It then records the checker's verdict with a small command, `factory results record`, which files the verdict in a results table keyed by commit. Next it asks the store what to do with the ticket. When something needs a person, the build loop "parks" the ticket, which stops work on it and writes down a reason for the operator.

A checker run can be killed: the agent hits a budget or session limit and returns nothing. The intended outcome is a park with reason `budget kill: <role>`, which tells the operator to send the same work out again. That is what happens today, but only on paper. When the build loop records a killed checker, the recording command crashes. The build loop always passes the path of the run's output file, and a killed run never writes that file. The command opens the file before it checks whether the run was killed. Because recording failed, the build loop parks the ticket with reason `harness-bug: results record <role>`. That reason tells the operator the factory itself is broken, and it hides the real cause (an ordinary budget kill).

Who is affected: the operator. Every killed reviewer or verifier run is reported as a factory defect, so the operator investigates the factory instead of re-dispatching the work. No work is lost: the ticket still stops for a human.

## Evidence
- Request: GitHub danielphang/spec-factory#18. It was found by the spec writer of #16 (green-pilot T-0001) as an out-of-scope observation.
- Code on this checkout (`/Users/dphang/dev/nanobot-upstream`, branch `feat/lionbot-v3`, HEAD `f8f40e0c5`):
  - `factory/workflows/build.js:139` records every checker with `results record … --output ${r.outputPath} --run …`, and appends ` --killed` when the run's status is KILLED. When that call fails, `build.js:140` parks with `harness-bug: results record ${role}: <stderr>`.
  - A run counts as killed when the agent returns null or empty text (`build.js:91`). It is then closed with `run finish <id> --status-override KILLED` (`build.js:93`). `run finish` writes `output.md` only when `--output-file` is given (`factory/cli.py:255`), so a killed run has no `output.md` unless the agent wrote one before it died.
  - `factory/cli.py:425` (`results_record`) reads `Path(a.output).read_text(...)` whenever `--output` is given, before the `if a.killed:` branch at line 426.
  - Once both checker rows exist, `ticket join` already returns `park` with `budget kill: <roles>` when a row is KILLED (`factory/cli.py:532-533`). A killed verifier writes no `ci` row, and the join allows for that (`cli.py:436`, `cli.py:524-525`). The right reason exists. Only the recording step fails before it.
  - The test suite misses this because its stand-in for the build loop records killed checkers without `--output` (`tests/factory/test_shepherd.py:642-645`), which is not how `build.js:139` calls the command.
- Reproduced black-box with `bin/factory` against a throwaway store, run from the repo root under both bash and zsh. The exact commands are the WHEN lines in the spec below.
  - A reviewer APPROVE is recorded, then a killed verifier is recorded the way `build.js` does it (`--output` names the run's missing `output.md`, plus `--killed`). Result: `reviewer=0 verifier=1 decision=wait reason=results missing for the current head: verifier, ci`. Recording exits 1 with `FileNotFoundError`. In the build loop that exit becomes `harness-bug: results record verifier: …`.
  - The same with the roles swapped: `verifier=0 reviewer=1 decision=wait reason=results missing for the current head: reviewer`.
  - A killed verifier whose partial output names another commit (`Commit: deadbeef00`): `exit=2 rows=[] status=` (refused). In the build loop that is also a `harness-bug:` park.
  - A killed verifier with no `--output`: `exit=0 rows=[verifier.yaml ] status=KILLED`. This is the path the test fixture uses, and it works.
- The factory suite today: `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory` → `55 passed in 70.71s`.

## Root cause
`results_record` in `factory/cli.py`. It reads the `--output` file unconditionally when the flag is present (line 425). Only after that does it look at `--killed` (line 426). The build loop always passes `--output`, and a killed run has no file at that path, so the read raises `FileNotFoundError`. `main()` turns that into exit 1 (`cli.py` `main`, the `except Exception` branch). A second, smaller failure has the same cause. If a killed run did leave a partial output, the `Commit:` check (lines 431-433) still runs on it. A stale `Commit:` line then refuses the record (exit 2), which also parks as `harness-bug:`.

## Out of scope
- `factory/workflows/build.js` (a protected path): unchanged. Its call shape (`--output` always, `--killed` when killed) is what this change makes work.
- Without `--killed`, `results record` behaves exactly as it does at the time this is built, including #16's `Commit:` checks and the error when the `--output` file is missing.
- The join's routing, its reasons, the merge gate, and the rule that a killed verifier writes no `ci` row.
- The existing test fixture's killed path in `tests/factory/test_shepherd.py` (it records without `--output`). It stays as it is. The new test uses the build loop's call shape instead.
- The `--head` validation and the stale-result rule.

## Open questions
none

## Decisions
- With `--killed`, `results record` does not open the `--output` file at all. A missing file is not the only case covered: a killed run's output is never read. This is the requester's proposed fix ("does not read `--output` when `--killed` is given (a killed row needs no output)"), and the operator approved it in advance. Only tolerating a missing file would leave the second failure in Root cause in place: a killed run whose partial output has a stale `Commit:` line would still park as `harness-bug:`, the misleading reason this ticket removes.
- As a result, a killed run's output is no longer checked for its `Commit:` line. This changes one case that #16's spec keeps "exactly as today": a killed output that names another commit is now recorded KILLED instead of refused. That check protected nothing. A KILLED row can never satisfy the merge gate, which requires `ci PASS`, `APPROVE` and `VERIFIED` (`factory/cli.py:467-470`), and the join parks on it. #16's two killed scenarios (no `--output`, and a cut-off output with no `Commit:` line) still record KILLED and still pass.
- The fix goes in `factory/cli.py`, not `build.js`, so the build loop stays unchanged and the command works for both callers (with or without `--output`).
- The requirements are ADDED under capability `checker-results` (the capability #16's change uses). Current truth (`openspec/specs/`) is empty on this checkout. If #16's change is archived first, its requirement `killed-run-recording-is-unchanged` stays true, and these requirements sit beside it under new names.
- Sequencing: build after #16 (green-pilot T-0001 / T-0001.1) merges, on top of its `results_record`, as the operator's note requires. Every acceptance result below was checked against both the current code and a simulation of #16's change.

## Risk
- Blast radius: the `--killed` path of one function, `results_record` in `factory/cli.py`. Its callers are the build loop's checker step (`build.js:139`) and tests. Recording an unkilled run is unchanged. After the change, every killed checker records a KILLED row and exits 0, and the join parks it as `budget kill: <role>`. A killed run's partial output is no longer looked at by this command (see Decisions). It is still kept in the run folder for the operator.
- Merge-order risk: #16 rewrites the same few lines. Building after #16 merges, as required, avoids a conflict. The implementer should drop #16's killed-only `Commit:` branch if it becomes unreachable, rather than leave dead code.
- Protected paths touched: none. `factory/cli.py` and `tests/factory/` are outside `factory/workflows/**` and `factory/config.yaml`.
- Guardrail paths touched: none. No existing test is edited. One new test file is added.

=== design.md
## Proposed change
A. `factory/cli.py`, `results_record`: read the `--output` file only when `--killed` is not given. Today that is line 425: `text = Path(a.output).read_text(encoding="utf-8") if a.output and not a.killed else ""`. After #16 merges, apply the same rule to #16's version of the read. With `--killed`, the function records the KILLED row (and no `ci` row, as today) without opening or checking the output. With #16 merged, its killed-only `Commit:` check then has nothing to look at. Remove that branch so the `Commit:` checks apply only to unkilled runs. Do not change anything else in the unkilled path.
B. New test file `tests/factory/test_killed_checker.py`. It covers both checker roles (one test, parametrized over `verifier` and `reviewer`). It brings a sub-ticket to checks with the existing `built_to_implementer` helper (`from .test_shepherd import built_to_implementer`; this relative import works under the current pytest setup, checked in a scratch run), dispatches the implementer and the other checker normally, then runs the killed checker exactly as `build.js:91-94` and `:139` do:
   1. `run start`, then `run compose`.
   2. `run finish <id> --status-override KILLED`, then `run cleanup <id>`.
   3. `results record <st> --head <ticket head> --role <role> --output <store>/runs/<id>/output.md --run <id> --killed`, asserting first that the file does not exist.
   4. Act on the join with the shepherd's `act_on_join`.
   Then it asserts the sub-ticket is parked with reason `budget kill: <role>`. Every CLI call goes through the shepherd's `ok()`, so a non-zero exit fails the test with its stderr.

Size: about 3 changed lines in `factory/cli.py` (a few more if #16's killed branch is removed), and a new test file of about 35 lines.

I checked this design in scratch copies of `factory/`, `bin/` and `tests/factory/`, not in this checkout:
- (i) This checkout with part A: every WHEN below gave its PR result. `tests/factory` plus a sketch of part B gave `57 passed`.
- (ii) A simulation of #16's change (its part A, and part B's fixture edit) without this fix: the base results below, and the part B sketch failed in both cases with `FileNotFoundError: … runs/run-0007-verifier/output.md` (and `…run-0007-reviewer…`). The rest passed: `2 failed, 55 passed`.
- (iii) The same simulation with part A: the PR results below, and `57 passed`.

## Tests to change
none

=== specs/checker-results/spec.md
## ADDED Requirements

### Requirement: killed-checker-parks-as-budget-kill
When a reviewer or verifier run is killed and the build loop records it the way it does today (passing `--output` with the run's output path, which a killed run never wrote, and `--killed`), `factory results record` SHALL record a KILLED row and exit 0, so that `factory ticket join` decides `park` with reason `budget kill: <role>`.

#### Scenario: killed-verifier-without-output-file-parks-as-budget-kill
- GIVEN a throwaway store whose ticket's head is set directly in its ticket file (a stand-in for `ticket head`, which needs a git branch), and a reviewer APPROVE already recorded for that head
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; sed "s/^head: null\$/head: '$H'/" $S/tickets/T-0001.yaml > $S/t.yaml && mv $S/t.yaml $S/tickets/T-0001.yaml; printf "Commit: $H\nFindings: none\nSTATUS: APPROVE\nCONFIDENCE: high\nESCALATIONS: none\n" > $S/rev.md; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role reviewer --output $S/rev.md --run R1 >/dev/null 2>&1; a=$?; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role verifier --output $S/runs/R2/output.md --run R2 --killed >/dev/null 2>&1; b=$?; echo "reviewer=$a verifier=$b $(FACTORY_STATE=$S bin/factory ticket join T-0001 2>/dev/null | sed -n 's/.*"decision": "\([^"]*\)", "reason": "\([^"]*\)".*/decision=\1 reason=\2/p')"` (run from the repo root)
- THEN it prints `reviewer=0 verifier=0 decision=park reason=budget kill: verifier`

#### Scenario: killed-reviewer-without-output-file-parks-as-budget-kill
- GIVEN the same throwaway store, with a verifier VERIFIED (`Gate suite: PASS`) already recorded for the head
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; sed "s/^head: null\$/head: '$H'/" $S/tickets/T-0001.yaml > $S/t.yaml && mv $S/t.yaml $S/tickets/T-0001.yaml; printf "Commit: $H\nPer criterion: all pass\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high\nESCALATIONS: none\n" > $S/ver.md; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role verifier --output $S/ver.md --run R1 >/dev/null 2>&1; a=$?; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role reviewer --output $S/runs/R2/output.md --run R2 --killed >/dev/null 2>&1; b=$?; echo "verifier=$a reviewer=$b $(FACTORY_STATE=$S bin/factory ticket join T-0001 2>/dev/null | sed -n 's/.*"decision": "\([^"]*\)", "reason": "\([^"]*\)".*/decision=\1 reason=\2/p')"` (run from the repo root)
- THEN it prints `verifier=0 reviewer=0 decision=park reason=budget kill: reviewer`

#### Scenario: killed-record-without-output-flag-still-records-killed
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role verifier --run R1 --killed >/dev/null 2>&1; echo "exit=$? rows=[$(ls $S/results/$H 2>/dev/null | tr '\n' ' ')] status=$(sed -n 's/^status: //p' $S/results/$H/verifier.yaml 2>/dev/null)"` (run from the repo root)
- THEN it prints `exit=0 rows=[verifier.yaml ] status=KILLED`

### Requirement: killed-run-output-is-not-read
With `--killed`, `factory results record` MUST record KILLED without reading or checking the `--output` file, whatever that file holds. Without `--killed`, the output file MUST still be read and checked as before.

#### Scenario: killed-output-naming-another-commit-records-killed
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; printf 'Commit: deadbeef00\nPer criterion: (cut off)\n' > $S/o.md; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role verifier --output $S/o.md --run R1 --killed >/dev/null 2>&1; echo "exit=$? rows=[$(ls $S/results/$H 2>/dev/null | tr '\n' ' ')] status=$(sed -n 's/^status: //p' $S/results/$H/verifier.yaml 2>/dev/null)"` (run from the repo root)
- THEN it prints `exit=0 rows=[verifier.yaml ] status=KILLED`

#### Scenario: unkilled-record-with-missing-output-file-still-fails
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role reviewer --output $S/missing.md --run R1 >/dev/null 2>&1; echo "exit=$? rows=[$(ls $S/results/$H 2>/dev/null | tr '\n' ' ')] events=$(cat $S/log/*.jsonl | grep -c '"event": "result\.')"` (run from the repo root)
- THEN it prints `exit=1 rows=[] events=0`

#### Scenario: factory-suite-passes-with-killed-checker-change
- WHEN `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory` (run from the repo root)
- THEN it exits 0 and reports no failed tests

=== verification.md
## Acceptance
- killed-verifier-without-output-file-parks-as-budget-kill → NEW. Today it prints `reviewer=0 verifier=1 decision=wait reason=results missing for the current head: verifier, ci`: recording the killed verifier exits 1 with `FileNotFoundError`, which `build.js:140` turns into a `harness-bug: results record verifier: …` park. Same output on a simulation of #16 merged.
- killed-reviewer-without-output-file-parks-as-budget-kill → NEW. Today it prints `verifier=0 reviewer=1 decision=wait reason=results missing for the current head: reviewer`. Same on the #16 simulation.
- killed-record-without-output-flag-still-records-killed → REGRESSION. Today it prints `exit=0 rows=[verifier.yaml ] status=KILLED`. This is the call shape the test fixture uses, the second caller the fix must keep working.
- killed-output-naming-another-commit-records-killed → NEW. Today it prints `exit=2 rows=[] status=` (refused by the `Commit:` check, which runs on a killed run's output). Same on the #16 simulation, since #16 keeps the killed check.
- unkilled-record-with-missing-output-file-still-fails → REGRESSION. Today it prints `exit=1 rows=[] events=0`. This guards against the fix skipping the read for every run instead of only killed ones.
- factory-suite-passes-with-killed-checker-change → REGRESSION. Today `55 passed in 70.71s` on this checkout. When this ticket is built, the count also includes #16's new tests and this change's new test file.

How verified: I ran every WHEN above verbatim, under bash and zsh, on this checkout (HEAD `f8f40e0c5`) for the "today" results. All of them were run from the repo root of each copy. I also ran them in three scratch copies of `factory/`, `bin/` and `tests/factory/` outside this checkout:
- this checkout with design part A;
- a simulation of #16's change without part A;
- that simulation with part A.
On the #16 simulation without A, the results matched "today" above. With A, on either base, every THEN line held, and `tests/factory` plus a sketch of part B gave `57 passed`. Without A, the sketch failed in both roles with `FileNotFoundError`. The #16 simulation is my reading of #16's approved design part A and its part B fixture edit, not #16's actual implementation (not merged yet; its worktree `factory/T-0001.1` is still at `f8f40e0c5`).

Out-of-scope observations:
- `tests/factory/test_shepherd.py:642-645`: the shepherd's killed path records without `--output`, which is not how `build.js:139` calls `results record`. That divergence is why the suite never caught this bug. Making the fixture mirror `build.js` would be an edit to an existing test, so this spec adds a new test with the build loop's call shape instead.
- The working tree of this checkout shows `M webui/package-lock.json` (a protected dependency path). It was there before this run started and was not touched by it.
