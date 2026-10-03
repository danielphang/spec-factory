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
`/Users/dphang/dev/spec-factory/intake/green-pilot/runs/run-0021-verifier/output.md`

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/intake/green-pilot/runs/run-0021-verifier/wt` (branch `factory/T-0002.1`, base `dd09a7cb1242d1e6e4637817498f5eae9f55a2f8`, head `d8a11792727455830cb78d4417f56a51104e0120`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written): `uv run ruff check nanobot/`; `uv run --extra dev --with neonize==0.3.18.post0 /Users/dphang/dev/nanobot-upstream/scripts/full_suite_gate.py --root . --isolated-home --pytest-args "-n 2 --dist loadfile"`

## Sub-ticket T-0002.1

### ST-1 / A killed checker records KILLED without reading its output, so the ticket parks as `budget kill: <role>`

Depends on: none. The parent's external precondition, #16 (T-0001.1) merged, is already met at `1f3a58e52`.
Parallel-safe: yes. It is the only sub-ticket.

Parent: the approved spec v1 above (proposal.md, design.md, specs/checker-results/spec.md, verification.md for the change "killed checker parks as budget kill", GitHub danielphang/spec-factory#18). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: design parts A and B.
- A. `factory/cli.py`, `results_record`: read the `--output` file only when `--killed` is not given (today line 430). With `--killed`, record the KILLED row (and no `ci` row, as today) without opening or checking the output. Remove #16's killed-only `Commit:` branch (today lines 436-439), so that the `Commit:` checks run only for unkilled runs. Leave the unkilled path unchanged.
- B. New file `tests/factory/test_killed_checker.py`: one test, parametrized over `verifier` and `reviewer`. It brings a sub-ticket to checks with `built_to_implementer` and dispatches the implementer and the other checker normally. It then runs the killed checker the way `build.js:91-94` and `:139` do: `run start`, `run compose`, `run finish <id> --status-override KILLED`, `run cleanup <id>`, assert `<store>/runs/<id>/output.md` does not exist, `results record ... --output <that path> --run <id> --killed`, and `act_on_join`. Finally it asserts the sub-ticket is parked with reason `budget kill: <role>`. Every CLI call goes through the shepherd's `ok()`.

Acceptance (each WHEN runs verbatim from the parent's specs/checker-results/spec.md, from the repo root):
- killed-verifier-without-output-file-parks-as-budget-kill (NEW). WHEN: the parent's scenario command (a reviewer APPROVE is recorded, then the verifier is recorded with `--output $S/runs/R2/output.md --run R2 --killed`, then `ticket join`). THEN it prints `reviewer=0 verifier=0 decision=park reason=budget kill: verifier`.
- killed-reviewer-without-output-file-parks-as-budget-kill (NEW). WHEN: the parent's scenario command (a verifier VERIFIED is recorded, then the reviewer is recorded with `--output $S/runs/R2/output.md --run R2 --killed`, then `ticket join`). THEN it prints `verifier=0 reviewer=0 decision=park reason=budget kill: reviewer`.
- killed-record-without-output-flag-still-records-killed (REGRESSION). WHEN: the parent's scenario command (`results record ... --role verifier --run R1 --killed`, no `--output`). THEN it prints `exit=0 rows=[verifier.yaml ] status=KILLED`.
- killed-output-naming-another-commit-records-killed (NEW). WHEN: the parent's scenario command (`--output $S/o.md --killed`, where o.md holds `Commit: deadbeef00`). THEN it prints `exit=0 rows=[verifier.yaml ] status=KILLED`.
- unkilled-record-with-missing-output-file-still-fails (REGRESSION). WHEN: the parent's scenario command (`--role reviewer --output $S/missing.md --run R1`, no `--killed`). THEN it prints `exit=1 rows=[] events=0`.
- factory-suite-passes-with-killed-checker-change (REGRESSION). WHEN `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory`. THEN it exits 0 and reports no failed tests. The count now includes #16's `tests/factory/test_results_commit.py` and the new `test_killed_checker.py`, so it is above the spec's earlier `55 passed`.
- Intermediate check (NEW): `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory/test_killed_checker.py`. THEN it reports `2 passed` (verifier and reviewer). Before part A is applied, it fails in both cases with `FileNotFoundError`. The implementer shows that red run, so the test is known to catch the bug.
- Intermediate check (REGRESSION): `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory/test_results_commit.py` still passes, unedited. #16's killed scenarios (no `--output`, and a cut-off output with no `Commit:` line) still record KILLED, and its unkilled `Commit:` checks are unchanged.
- Gate suite (REGRESSION): `uv run ruff check nanobot/` and the full-suite gate pass. The verifier reports `Gate suite: PASS`.

Tests to change: none. The parent's list is "none". `tests/factory/test_shepherd.py` and `tests/factory/test_results_commit.py` stay unedited. Only the new file `tests/factory/test_killed_checker.py` is added.
Protected paths: none. The parent's Risk section says "Protected paths touched: none". `factory/workflows/build.js` is not edited. Do not stage `webui/package-lock.json` (already `M` in this checkout) or `webui/node_modules/`. Stage by name.
Out of scope: `factory/workflows/build.js` and its call shape. The unkilled `results record` path, including #16's `Commit:` checks and the error for a missing `--output` file. The join's routing and reasons, the merge gate, and the rule that a killed verifier writes no `ci` row. The `--head` validation and the stale-result rule. The killed path of the existing fixture at `tests/factory/test_shepherd.py` (it records without `--output`), which stays as it is.

---

## Shared plan context (from the plan; applies to every sub-ticket)

## Plan

The spec fits one PR: about 3-10 changed lines in one function (`results_record` in `factory/cli.py`) plus one new test file of about 35 lines. Part A without part B would leave the fix with no in-suite test of the build loop's call shape, and part B without part A fails (the spec's own check (ii): `2 failed`). Splitting the two would make neither half independently mergeable with a passing suite, and gives no easier review or rollback. One sub-ticket.

Sequencing precondition (spec Decisions: "build after #16 merges"): checked on this checkout, and it is met. `git log` on `feat/lionbot-v3` shows `1f3a58e52 Merge factory/T-0001.1: results record refuses a checker output whose Commit: lines do not all name the head (T-0001.1)`, and HEAD is `dd09a7cb1`. `factory/cli.py:424-449` now holds #16's version: line 430 `text = Path(a.output).read_text(encoding="utf-8") if a.output else ""`, and lines 436-439 hold the killed-only `Commit:` branch (`if a.killed:  # a killed run's output may be cut off: ...`). This is the branch the spec's Risk section says to remove once it is unreachable. `tests/factory/test_killed_checker.py` does not exist yet. `built_to_implementer` (`tests/factory/test_shepherd.py:390`), `ok` (`:631`) and `act_on_join` (`:763`) exist.

---

## Parent spec (v1, pinned)

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

## PR description (the implementer's output)

Sub-ticket: T-0002.1 (ST-1, parent: danielphang/spec-factory#18). Branch `factory/T-0002.1`, worktree `/Users/dphang/dev/spec-factory/intake/green-pilot/worktrees/T-0002.1`, base `dd09a7cb1`, head `d8a117927`.

What changed:
- A. `factory/cli.py`, `results_record`:
  - The output read is now `Path(a.output).read_text(encoding="utf-8") if a.output and not a.killed else ""`, with a one-line comment saying why. With `--killed`, the `--output` file is never opened.
  - #16's killed-only `Commit:` branch (`if a.killed:  # a killed run's output may be cut off: ...`, 4 lines) is removed. With `--killed` the text is always `""`, so that branch could never fire.
  - The unkilled `Commit:` checks are untouched. Only their `else:` became `if not a.killed:`.
  - Nothing else changed. The killed path still writes no `ci` row (`if a.role == "verifier" and not a.killed`, unchanged).
  - Diff: 3 insertions, 6 deletions.
- B. New file `tests/factory/test_killed_checker.py`, 35 lines. One test, parametrized over `verifier` and `reviewer`. It:
  - calls `built_to_implementer`, dispatches the implementer, then the other checker normally, and asserts the join says `wait`;
  - runs the killed checker the way `build.js` does: `ticket head`, `run start`, `run compose`, `run finish <id> --status-override KILLED`, `run cleanup <id>`;
  - asserts `<store>/runs/<id>/output.md` does not exist;
  - runs `results record <st> --head <head> --role <role> --output <that path> --run <id> --killed`, then `act_on_join(st, rid)`;
  - asserts the results row is `KILLED`, the state is `parked`, and the reason is `budget kill: <role>`.
  Every CLI call goes through `Shepherd.ok()`.

Acceptance results (WHEN lines run verbatim from the worktree root; script at scratchpad `acc.sh`, which copies the spec's WHEN lines one for one):

| Criterion | Before (base dd09a7cb1) | After (d8a117927, bash and zsh) |
|---|---|---|
| killed-verifier-without-output-file-parks-as-budget-kill (NEW) | `reviewer=0 verifier=1 decision=wait reason=results missing for the current head: verifier, ci` | `reviewer=0 verifier=0 decision=park reason=budget kill: verifier` |
| killed-reviewer-without-output-file-parks-as-budget-kill (NEW) | `verifier=0 reviewer=1 decision=wait reason=results missing for the current head: reviewer` | `verifier=0 reviewer=0 decision=park reason=budget kill: reviewer` |
| killed-record-without-output-flag-still-records-killed (REGRESSION) | `exit=0 rows=[verifier.yaml ] status=KILLED` | `exit=0 rows=[verifier.yaml ] status=KILLED` |
| killed-output-naming-another-commit-records-killed (NEW) | `exit=2 rows=[] status=` | `exit=0 rows=[verifier.yaml ] status=KILLED` |
| unkilled-record-with-missing-output-file-still-fails (REGRESSION) | `exit=1 rows=[] events=0` | `exit=1 rows=[] events=0` |

Every base result matches the spec's "today" result, so no criterion was already passing before the fix.

- Intermediate (NEW), `pytest ... tests/factory/test_killed_checker.py`:
  - Before part A: `2 failed in 6.09s`. Both cases failed in `Shepherd.ok` on `results record ... --killed: factory: FileNotFoundError: [Errno 2] No such file or directory: '.../state/runs/run-0007-verifier/output.md'` (and `run-0007-reviewer`).
  - After part A: `2 passed in 6.18s`.
- Intermediate (REGRESSION), `pytest ... tests/factory/test_results_commit.py`, unedited: `9 passed in 1.47s` after the change.
- factory-suite-passes-with-killed-checker-change (REGRESSION), `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory`: `70 passed in 71.76s`, exit 0.
- Gate suite (REGRESSION), each command run from the worktree exactly as written:
  - `uv run ruff check nanobot/`: `All checks passed!`, exit 0.
  - The full-suite gate: exit 0, `5 failed, 7173 passed, 25 skipped in 126.21s`, and "its failure set is within the baseline (5 known failure(s))". The 5 known failures are:
    - `tests/gateway/test_runtime.py::test_default_instance_preserves_released_gateway_paths`
    - `tests/cli/test_tui_launcher.py::test_launcher_keeps_the_tui_alive_while_an_existing_gateway_recovers`
    - `tests/lionbot/test_service_log_paths.py::...test_the_default_instance_is_unchanged`
    - `tests/lionbot/test_service_log_paths.py::...test_an_explicit_default_config_resolves_the_same_way`
    - `tests/config/test_config_paths.py::test_shared_and_legacy_paths_remain_global`
  - I also ran `uv run ruff check tests/factory/test_killed_checker.py factory/cli.py` (not a gate): `All checks passed!`

Tests added/changed:
- Added `tests/factory/test_killed_checker.py`. This is part B. It is the only in-suite test that uses the build loop's call shape (`--output` naming a missing file, plus `--killed`).
- Changed: none. `tests/factory/test_shepherd.py` and `tests/factory/test_results_commit.py` are unedited.

Known gaps and uncertainties:
- After this change, a killed run's partial output is not checked at all, including its `Commit:` line. This is intended (spec Decisions), and it changes one case #16 kept: a killed output naming another commit is now recorded KILLED instead of refused (exit 2). #16's two killed scenarios in `test_results_commit.py` (no `--output`, and a cut-off output with no `Commit:` line) still pass.
- The new test imports `built_to_implementer` from `.test_shepherd`, as the design says. If that helper's signature changes, this test breaks with it.
- The test does not run `build.js`, which needs the Workflow runtime. It copies the build loop's call sequence by hand from `build.js` lines 91-94 and 139, read on this head. If `build.js` changes its call shape, this test will not notice.
- The full-suite gate runs with `--isolated-home`. Its own footer says it does not certify the bash `[U*]` units or HOME hermeticity. Neither is touched by this change.

Out-of-scope observations:
- The gate run did not leave `webui/package-lock.json` or `webui/node_modules/` staged or modified in `git status` here. After the commit, `git status --short` was empty. Only `factory/cli.py` and `tests/factory/test_killed_checker.py` were staged, by name.
- `tests/factory/test_shepherd.py`'s `dispatch(..., killed=True)` still records without `--output`, unlike `build.js`. I left it as it is, as the ticket says.

Responses to findings (round 2+): n/a (round 1).

STATUS: READY-FOR-REVIEW
CONFIDENCE: high, every acceptance command was run before and after the change and matched the spec's results exactly (under bash and zsh), the new test was seen red with the expected FileNotFoundError, and both gates passed.
ESCALATIONS: none

## Diff `dd09a7cb1242d1e6e4637817498f5eae9f55a2f8...d8a11792727455830cb78d4417f56a51104e0120`

diff --git a/factory/cli.py b/factory/cli.py
index 6bce29897..f9f74d7a3 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -427,17 +427,14 @@ def results_record(a, root, cfg):
         raise Refused("results record: --role reviewer|verifier")
     if not re.fullmatch(r"[0-9a-f]{40}", a.head or ""):
         raise Refused(f"results record: --head must be a full commit SHA, got {a.head!r}")
-    text = Path(a.output).read_text(encoding="utf-8") if a.output else ""
+    # A killed run's output is never read: the build loop passes --output even when the run wrote none.
+    text = Path(a.output).read_text(encoding="utf-8") if a.output and not a.killed else ""
     if a.killed:
         st = "KILLED"
     else:
         parsed = status.parse(text)
         st = parsed["status"] or "UNKNOWN"
-    if a.killed:  # a killed run's output may be cut off: check only a hex Commit: line it does have
-        cm = re.search(r"^Commit:\s*`?([0-9a-fA-F]{7,40})`?\b", text, re.M)
-        if cm and not a.head.startswith(cm.group(1).lower()):
-            raise Refused(f"results record: the output says Commit: {cm.group(1)}, not the head {a.head[:12]}")
-    else:  # every Commit: line must name the head; with none, the verdict is for no known commit
+    if not a.killed:  # every Commit: line must name the head; with none, the verdict is for no known commit
         lines = re.findall(r"^Commit:.*$", text, re.M)
         if not lines:
             raise Refused("results record: the output has no Commit: line")
diff --git a/tests/factory/test_killed_checker.py b/tests/factory/test_killed_checker.py
new file mode 100644
index 000000000..b30dd08c4
--- /dev/null
+++ b/tests/factory/test_killed_checker.py
@@ -0,0 +1,35 @@
+"""A killed checker, recorded the way the build loop records it, parks as a budget kill.
+
+build.js marks a run KILLED when the agent returns nothing (`build.js` runRole: `run finish
+--status-override KILLED`, then `run cleanup`), and records every checker with
+`results record ... --output <the run's output.md> --run <id>`, adding `--killed` for a killed
+run. A killed run never wrote that output file. The shepherd's own killed path records without
+`--output`, so this test drives the build loop's call shape directly.
+"""
+from __future__ import annotations
+
+import pytest
+
+from .test_shepherd import built_to_implementer
+
+
+@pytest.mark.parametrize("role", ["verifier", "reviewer"])
+def test_a_killed_checker_recorded_with_its_missing_output_parks_as_a_budget_kill(tmp_path, role):
+    f, tid, (st,) = built_to_implementer(tmp_path)
+    f.dispatch("implementer", st)
+    other = "reviewer" if role == "verifier" else "verifier"
+    f.dispatch(other, st)
+    assert f.last_join["decision"] == "wait"  # the killed checker has not reported yet
+
+    head = f.ok("ticket", "head", st)["head"]
+    rid = f.ok("run", "start", "--role", role, "--ticket", st)["run_id"]
+    f.ok("run", "compose", rid)
+    assert f.ok("run", "finish", rid, "--status-override", "KILLED")["status"] == "KILLED"
+    f.ok("run", "cleanup", rid)
+    output = f.store / "runs" / rid / "output.md"
+    assert not output.exists()  # a killed run wrote no output
+    f.ok("results", "record", st, "--head", head, "--role", role, "--output", str(output), "--run", rid, "--killed")
+    f.act_on_join(st, rid)
+
+    assert f.results(st)[role] == "KILLED"
+    assert f.state(st) == "parked" and f.ticket(st)["parked"]["reason"] == f"budget kill: {role}"
