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
`/Users/dphang/dev/spec-factory/intake/green-pilot/runs/run-0014-verifier/output.md`

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/intake/green-pilot/runs/run-0014-verifier/wt` (branch `factory/T-0001.1`, base `b551d97cd9797c72aa2f4b20170a7b2690ff2e58`, head `e28db6a255e8cd0032c67ada62b74b6681cd511d`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written): `uv run ruff check nanobot/`; `uv run --extra dev --with neonize==0.3.18.post0 /Users/dphang/dev/nanobot-upstream/scripts/full_suite_gate.py --root . --isolated-home --pytest-args "-n 2 --dist loadfile"`

## Sub-ticket T-0001.1

### ST-1 / `results record` refuses a checker output whose `Commit:` lines do not all name the head

Parent: the approved spec "checker-output-must-name-the-head" (v1, pinned: proposal.md, design.md, specs/checker-results/spec.md, verification.md in this change). Read it for context. Do NOT implement parts outside this sub-ticket.

Depends on: none
Parallel-safe: yes (it is the only sub-ticket)
Scope: design parts A, B, C. All of the parent.
- A: `factory/cli.py` `results_record`. Without `--killed`, there must be at least one `Commit:` line. Every `Commit:` line must parse as 7-40 hex characters (optionally in backticks) and be a prefix of `--head`. Each refusal raises `Refused` before any `store.record_result` or `store.log_event` call. With `--killed`, keep today's check exactly.
- B: in the merge-gate story of `tests/factory/test_shepherd.py`, change the `results record --role verifier` call at line 268 so its `--output` is `f.store / "runs" / ver.run_id / "output.md"` instead of `red.md`. Assertions are unchanged.
- C: new file `tests/factory/test_results_commit.py`. It drives `bin/factory` as a subprocess against a temporary `FACTORY_STATE` and covers each scenario below.

Acceptance (each WHEN is run verbatim from the repo root, exactly as written in the parent's specs/checker-results/spec.md):
- no-commit-line-is-refused: WHEN reviewer output with no `Commit:` line is recorded. THEN `exit=2 rows=[] events=0`. NEW
- non-hex-commit-value-is-refused: WHEN reviewer output with `Commit: HEAD` is recorded. THEN `exit=2 rows=[] events=0`. NEW
- later-commit-line-naming-another-commit-is-refused: WHEN the output has `Commit: <head>`, then later `Commit: deadbeef00`. THEN `exit=2 rows=[] events=0`. NEW
- verifier-without-commit-line-writes-no-ci-row: WHEN verifier output with `Gate suite: PASS` and no `Commit:` line is recorded. THEN `exit=2 rows=[] events=0`. NEW
- earlier-commit-line-naming-another-commit-is-refused: WHEN the output has `Commit: deadbeef00`, then `Commit: <head>`. THEN `exit=2 rows=[] events=0`. REGRESSION
- full-head-sha-is-recorded: WHEN the output has `Commit: <40-hex head>`. THEN `exit=0 rows=[reviewer.yaml ] events=1`. REGRESSION
- abbreviated-sha-in-backticks-is-recorded: WHEN verifier output has ``Commit: `0000000` ``. THEN `exit=0 rows=[ci.yaml verifier.yaml ] events=2`. REGRESSION
- killed-without-output-records-killed: WHEN `--killed` is passed with no `--output`. THEN `exit=0 rows=[verifier.yaml ] status=KILLED`. REGRESSION
- killed-with-cut-off-output-records-killed: WHEN `--killed` is passed with an `--output` that has no `Commit:` line. THEN `exit=0 rows=[verifier.yaml ] status=KILLED`. REGRESSION
- factory-suite-still-passes: WHEN `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory`. THEN it exits 0 with no failed tests. The count grows from today's 55 by the number of tests in the new file. REGRESSION
- Intermediate check (gate suite, not a parent scenario): WHEN `uv run ruff check nanobot/` and the full-suite gate. THEN lint is clean and no test fails outside the port's known-failure baseline. REGRESSION

Tests to change: `tests/factory/test_shepherd.py` line 268 only (parent's Tests to change). The other `Commit: HEAD` fixtures go through `dispatch`, which substitutes the head. They stay untouched: lines 327, 408-409 and 489, and the stubs under `tests/factory/fixtures/stubs/`.
Protected paths: none. The parent's Risk declares none, and `factory/cli.py` is not under `factory/workflows/**` or `factory/config.yaml`.
Out of scope:
- `factory/workflows/build.js` (protected), roles, prompts, routing and every other `factory` command.
- `--head` validation.
- The stale-result rule (`result.stale-discarded`).
- Status parsing and the derived `ci` row for accepted outputs.
- The `--killed --output <missing file>` `FileNotFoundError` crash (parent's out-of-scope observation).
- The dead `results record` call on `wrong.md` at `test_shepherd.py:333` (parent's out-of-scope observation).
- Accepting other `Commit:` formats (for example `**Commit:**`). The parent's Risk notes this as a possible way to park a ticket. It is not a change to make here.

---

## Shared plan context (from the plan; applies to every sub-ticket)

## Plan: one sub-ticket

The spec fits in one PR: about 20 lines in `factory/cli.py`, 1 line in `tests/factory/test_shepherd.py` and one new test file. It cannot be split so that each piece can be merged on its own. Part A without part B fails `tests/factory`: `test_shepherd.py:264` writes `Commit: HEAD` into `red.md` and `:268` records it through `f.ok`. The spec's scratch run says this exits 2 under A. Part B without A changes nothing. Part C's tests fail until A lands. Splitting off C as a follow-up would only add one more merge and re-verify cycle, so A, B and C stay together.

Cited code confirmed on this checkout (HEAD `f8f40e0c5`, branch `feat/lionbot-v3`):
- `factory/cli.py:419` `def results_record`, with the first-match check at `:431-433`.
- `tests/factory/test_shepherd.py:264` (`red.md` with `Commit: HEAD`) and `:268` (the direct `results record ... --output str(red)` call).
- `:648` (the dispatcher replaces `Commit: HEAD` with the head in the run's `output.md`).
- `bin/factory` exists.
- `tests/factory/test_results_commit.py` does not exist yet.

---

## Parent spec (v1, pinned)

=== proposal.md
## Problem
The spec factory is a pipeline of AI agents that turns a request into merged code. Before a change merges, two independent checker agents look at it: a reviewer (reads the diff) and a verifier (runs the acceptance commands and the test suite). Each checker ends its report with a verdict (for example APPROVE or VERIFIED) and a `Commit:` line naming the git commit it looked at. A small command, `factory results record`, files each verdict in a results table keyed by commit. The merge step then merges a branch only if the table holds a passing verdict from every checker for the commit currently at the tip of that branch (the "head"). The guarantee the operator relies on is that every approval counted toward a merge was given for exactly the code being merged.

The recording command does not enforce that guarantee. It refuses a report only when the first `Commit:` line names a different commit as a hex id. It accepts and files against the current head:
- a report with no `Commit:` line at all;
- a report whose `Commit:` value is not a commit id (for example `Commit: HEAD`);
- a report whose first `Commit:` line names the head but a later `Commit:` line names some other commit.

So a checker that looked at an older commit, or did not say which commit it looked at, can still count toward a merge. Who is affected: the operator and anyone downstream who trusts that a merged change was checked as merged.

## Evidence
- Found by an independent validator of the build half (GitHub danielphang/spec-factory#16): "A missing `Commit:` line is accepted. `Commit: HEAD` (not hex) is accepted. Only the first `Commit:` line is checked." The build spec, part H, says the checker's `Commit:` line must equal the current head (`/Users/dphang/dev/spec-factory/specs/build-harness.md:288`).
- Code on this checkout (`/Users/dphang/dev/nanobot-upstream`, branch `feat/lionbot-v3`, HEAD `f8f40e0c5`), `factory/cli.py:431-433`:
  ```
  cm = re.search(r"^Commit:\s*`?([0-9a-fA-F]{7,40})`?\b", text, re.M)
  if cm and not a.head.startswith(cm.group(1).lower()):
      raise Refused(...)
  ```
  With no match the check is skipped. `re.search` finds only the first matching line. Refusals exit 2 through `main()` (`factory/cli.py:918-930`).
- Reproduced black-box with `bin/factory` on a throwaway store (head = forty zeros, ticket T-0001). Each line is `exit / rows written under results/<head>/ / result.* log events`:
  - no `Commit:` line, reviewer: `exit=0 rows=[reviewer.yaml ] events=1`
  - `Commit: HEAD`, reviewer: `exit=0 rows=[reviewer.yaml ] events=1`
  - `Commit: <head>` then later `Commit: deadbeef00`, reviewer: `exit=0 rows=[reviewer.yaml ] events=1`
  - no `Commit:` line, verifier with `Gate suite: PASS`: `exit=0 rows=[ci.yaml verifier.yaml ] events=2`
  - for comparison, first line `Commit: deadbeef00` then `Commit: <head>`: `exit=2 rows=[] events=0` (refused today)
  The exact commands are the WHEN lines in the spec below. I ran each under both bash and zsh with the same results.
- The build loop calls this command once per checker (`factory/workflows/build.js:139`). It passes `--output <run>/output.md` on every call, and adds `--killed` when the checker run was killed.

## Root cause
`results_record` in `factory/cli.py` (lines 419-444). The commit check is optional: it only fires when a hex value is found. It looks only at the first `Commit:` line. A `Commit:` line with a non-hex value fails the regex and is treated like no line at all.

## Out of scope
- No change to roles, prompts, routing, `factory/workflows/build.js` (a protected path) or any other command.
- `--head` validation (must be a full 40-hex SHA) stays as it is.
- With `--killed`, behaviour is exactly as today, with or without `--output`.
- The stale-result rule (a result for a head that is not the ticket's current head is logged as `result.stale-discarded`) is unchanged.
- The status parsing and the verifier's derived `ci` row are unchanged for accepted outputs.

## Open questions
none

## Decisions
- Every `Commit:` line in the output must name the head, not only the last one. The request says "last". Checking only the last line would start accepting an output whose first line names another commit and whose last line names the head, and today that output is refused. Checking every line covers each refusal the request names and keeps today's refusal.
- A `Commit:` line is a line that starts with `Commit:`, case-sensitive, as today. Its value is 7 to 40 hex characters (either case), optionally in backticks, and must be a prefix of the full head SHA. Trailing text after the value stays allowed, as today. An abbreviated SHA remains acceptable.
- "Nothing written" means: no results row (and so no derived `ci` row for a verifier), no `result.recorded` or `result.stale-discarded` log event, and exit 2 with the reason on stderr. This matches how the current wrong-commit refusal behaves.
- `--killed` keeps today's behaviour exactly, whether or not `--output` is given. A KILLED row can never satisfy the merge gate. `build.js` also passes `--output` on killed runs, where a cut-off output need not carry a `Commit:` line.

## Risk
- Blast radius: one function in `factory/cli.py`, used only by the build loop's checker step and by tests. After the change, a checker report with a missing, malformed or mismatched `Commit:` line makes `results record` exit 2. `build.js:140` then parks the sub-ticket with reason `harness-bug: results record <role>: <stderr>` instead of counting the verdict. This is intended, but a checker that formats the line differently (for example `**Commit:** abc…`) will now park the ticket for a human. No real reviewer or verifier output exists yet in the pilot store to check the format against. I could not verify how real checkers write the line.
- Protected paths touched: none. `factory/cli.py` is not under `factory/workflows/**` or `factory/config.yaml`.
- Guardrail path touched: one existing test fixture call in `tests/factory/test_shepherd.py`, declared under Tests to change.

=== design.md
## Proposed change
A. `factory/cli.py`, `results_record`: replace the optional first-match check (lines 431-433) with a strict check that applies when `--killed` is not given:
   1. Collect every line of the output that starts with `Commit:`. If there are none, refuse: `results record: the output has no Commit: line`.
   2. For each such line, parse the value with today's grammar (optional backtick, 7-40 hex, optional backtick, word boundary). If it does not parse, refuse and name the offending value (for example `results record: Commit: HEAD is not a commit id`). If it parses but the lowercased value is not a prefix of `--head`, refuse with today's message (`the output says Commit: <value>, not the head <head[:12]>`).
   3. All refusals raise `Refused` before any `store.record_result` or `store.log_event` call, so nothing is written. This is the same placement as today's check.
   When `--killed` is given, keep today's check unchanged (first hex `Commit:` line, refuse only on mismatch; no line means no check).
B. `tests/factory/test_shepherd.py`, in the merge-gate story: change the direct `results record ... --role verifier --output <red.md>` call (line 268) so its `--output` is the dispatched run's `output.md` (`f.store / "runs" / ver.run_id / "output.md"`). In that file the dispatcher has already replaced `Commit: HEAD` with the real head (line 648). The story's assertions stay as they are.
C. New test file `tests/factory/test_results_commit.py`. It drives `bin/factory` as a subprocess against a temporary `FACTORY_STATE`, as `tests/factory/test_shepherd.py` does. It covers each scenario in the spec below: refusals leave no row and no `result.*` event, and the accepted forms record.

Size: about 20 changed lines in `factory/cli.py`, 1 in `test_shepherd.py`, and a new test file of about 100 lines.

I checked this design in a scratch copy of `factory/`, `bin/` and `tests/factory/` (not in this checkout). Without part B the factory suite failed only in the merge-gate story (`results record: Commit: HEAD is not a commit id`, exit 2). With part B it was `55 passed`. All nine WHEN commands below gave the PR results stated in their THEN lines.

## Tests to change
- `tests/factory/test_shepherd.py` line 268 (in the merge-gate story). It writes `red.md` with `Commit: HEAD` (line 264) and records it directly with `results record --output red.md` through `f.ok`, which asserts exit 0. Under the fix that output has a non-hex `Commit:` value, so the call exits 2 and the story fails. The change points the call at the run's `output.md`, which has the same content with the real head substituted. The behaviour under test (a red verifier and a red ci row block the merge) is unchanged. The other `Commit: HEAD` fixtures (lines 327, 408-409, 489 and the stubs under `tests/factory/fixtures/stubs/`) go through `dispatch`, which substitutes the real head. They passed unchanged in the scratch run.

=== specs/checker-results/spec.md
## ADDED Requirements

### Requirement: checker-output-must-name-the-head
`factory results record` without `--killed` SHALL refuse with exit 2, and write no results row and no `result.*` log event, unless the output has at least one line starting with `Commit:` and every such line's value is a 7-40 character hex commit id (optionally in backticks) that is a prefix of the `--head` being recorded.

#### Scenario: no-commit-line-is-refused
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; printf 'Findings: none\nSTATUS: APPROVE\nCONFIDENCE: high\nESCALATIONS: none\n' > $S/o.md; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role reviewer --output $S/o.md --run R1 >/dev/null 2>&1; echo "exit=$? rows=[$(ls $S/results/$H 2>/dev/null | tr '\n' ' ')] events=$(cat $S/log/*.jsonl | grep -c '"event": "result\.')"` (run from the repo root)
- THEN it prints `exit=2 rows=[] events=0`

#### Scenario: non-hex-commit-value-is-refused
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; printf 'Commit: HEAD\nFindings: none\nSTATUS: APPROVE\nCONFIDENCE: high\nESCALATIONS: none\n' > $S/o.md; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role reviewer --output $S/o.md --run R1 >/dev/null 2>&1; echo "exit=$? rows=[$(ls $S/results/$H 2>/dev/null | tr '\n' ' ')] events=$(cat $S/log/*.jsonl | grep -c '"event": "result\.')"` (run from the repo root)
- THEN it prints `exit=2 rows=[] events=0`

#### Scenario: later-commit-line-naming-another-commit-is-refused
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; printf "Commit: $H\nFindings: none\nCommit: deadbeef00\nSTATUS: APPROVE\nCONFIDENCE: high\nESCALATIONS: none\n" > $S/o.md; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role reviewer --output $S/o.md --run R1 >/dev/null 2>&1; echo "exit=$? rows=[$(ls $S/results/$H 2>/dev/null | tr '\n' ' ')] events=$(cat $S/log/*.jsonl | grep -c '"event": "result\.')"` (run from the repo root)
- THEN it prints `exit=2 rows=[] events=0`

#### Scenario: verifier-without-commit-line-writes-no-ci-row
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; printf 'Per criterion: none\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high\nESCALATIONS: none\n' > $S/o.md; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role verifier --output $S/o.md --run R1 >/dev/null 2>&1; echo "exit=$? rows=[$(ls $S/results/$H 2>/dev/null | tr '\n' ' ')] events=$(cat $S/log/*.jsonl | grep -c '"event": "result\.')"` (run from the repo root)
- THEN it prints `exit=2 rows=[] events=0`

#### Scenario: earlier-commit-line-naming-another-commit-is-refused
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; printf "Commit: deadbeef00\nFindings: none\nCommit: $H\nSTATUS: APPROVE\nCONFIDENCE: high\nESCALATIONS: none\n" > $S/o.md; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role reviewer --output $S/o.md --run R1 >/dev/null 2>&1; echo "exit=$? rows=[$(ls $S/results/$H 2>/dev/null | tr '\n' ' ')] events=$(cat $S/log/*.jsonl | grep -c '"event": "result\.')"` (run from the repo root)
- THEN it prints `exit=2 rows=[] events=0`

#### Scenario: full-head-sha-is-recorded
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; printf "Commit: $H\nFindings: none\nSTATUS: APPROVE\nCONFIDENCE: high\nESCALATIONS: none\n" > $S/o.md; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role reviewer --output $S/o.md --run R1 >/dev/null 2>&1; echo "exit=$? rows=[$(ls $S/results/$H 2>/dev/null | tr '\n' ' ')] events=$(cat $S/log/*.jsonl | grep -c '"event": "result\.')"` (run from the repo root)
- THEN it prints `exit=0 rows=[reviewer.yaml ] events=1`

#### Scenario: abbreviated-sha-in-backticks-is-recorded
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; printf 'Commit: \1400000000\140\nPer criterion: none\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high\nESCALATIONS: none\n' > $S/o.md; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role verifier --output $S/o.md --run R1 >/dev/null 2>&1; echo "exit=$? rows=[$(ls $S/results/$H 2>/dev/null | tr '\n' ' ')] events=$(cat $S/log/*.jsonl | grep -c '"event": "result\.')"` (run from the repo root; `\140` is a backtick, so the line reads ``Commit: `0000000` ``)
- THEN it prints `exit=0 rows=[ci.yaml verifier.yaml ] events=2`

### Requirement: killed-run-recording-is-unchanged
`factory results record --killed` MUST record a KILLED row as it does today, both with no `--output` and with an `--output` that has no `Commit:` line.

#### Scenario: killed-without-output-records-killed
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role verifier --run R1 --killed >/dev/null 2>&1; echo "exit=$? rows=[$(ls $S/results/$H 2>/dev/null | tr '\n' ' ')] status=$(sed -n 's/^status: //p' $S/results/$H/verifier.yaml 2>/dev/null)"` (run from the repo root)
- THEN it prints `exit=0 rows=[verifier.yaml ] status=KILLED`

#### Scenario: killed-with-cut-off-output-records-killed
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; printf 'Per criterion: (cut off)\n' > $S/o.md; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role verifier --output $S/o.md --run R1 --killed >/dev/null 2>&1; echo "exit=$? rows=[$(ls $S/results/$H 2>/dev/null | tr '\n' ' ')] status=$(sed -n 's/^status: //p' $S/results/$H/verifier.yaml 2>/dev/null)"` (run from the repo root)
- THEN it prints `exit=0 rows=[verifier.yaml ] status=KILLED`

#### Scenario: factory-suite-still-passes
- WHEN `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory` (run from the repo root)
- THEN it exits 0 and reports no failed tests (today: `55 passed`)

=== verification.md
## Acceptance
- no-commit-line-is-refused → NEW; today it prints `exit=0 rows=[reviewer.yaml ] events=1` (the verdict is recorded).
- non-hex-commit-value-is-refused → NEW; today it prints `exit=0 rows=[reviewer.yaml ] events=1`.
- later-commit-line-naming-another-commit-is-refused → NEW; today it prints `exit=0 rows=[reviewer.yaml ] events=1` (only the first line is checked).
- verifier-without-commit-line-writes-no-ci-row → NEW; today it prints `exit=0 rows=[ci.yaml verifier.yaml ] events=2`.
- earlier-commit-line-naming-another-commit-is-refused → REGRESSION; today it prints `exit=2 rows=[] events=0`.
- full-head-sha-is-recorded → REGRESSION; today it prints `exit=0 rows=[reviewer.yaml ] events=1`.
- abbreviated-sha-in-backticks-is-recorded → REGRESSION; today it prints `exit=0 rows=[ci.yaml verifier.yaml ] events=2`.
- killed-without-output-records-killed → REGRESSION; today it prints `exit=0 rows=[verifier.yaml ] status=KILLED`.
- killed-with-cut-off-output-records-killed → REGRESSION; today it prints `exit=0 rows=[verifier.yaml ] status=KILLED`.
- factory-suite-still-passes → REGRESSION; today `55 passed in 61.15s`. After the change it passes only with the declared fixture edit (design part B).

How verified: I ran every WHEN above, verbatim, under bash and zsh. I ran them on this checkout (HEAD `f8f40e0c5`) for the "today" results, and on a scratch copy of `factory/`, `bin/` and `tests/factory/` with design parts A and B applied for the post-change results. All THEN lines held. That scratch copy is outside this checkout and is not the implementation.

Out-of-scope observations:
- `factory/workflows/build.js:139` passes `--output <run>/output.md` on killed checker runs, but nothing creates that file for a killed run (`run finish --status-override KILLED` writes no output). So `results record --killed --output <missing file>` crashes with `FileNotFoundError` (exit 1; reproduced). The build loop then parks the sub-ticket as `harness-bug: results record <role>` instead of `budget kill: <role>`. The fix would be in `build.js` (protected) or in `results_record`'s file read. Not addressed here.
- `tests/factory/test_shepherd.py:333` calls `results record` on `wrong.md` before line 334 writes that file. The result is overwritten and never asserted (dead line; noted by triage too).

## PR description (the implementer's output)

Sub-ticket: T-0001.1 (ST-1, "`results record` refuses a checker output whose `Commit:` lines do not all name the head"). Parent: approved spec "checker-output-must-name-the-head" v1.
Branch: `factory/T-0001.1` in `/Users/dphang/dev/spec-factory/intake/green-pilot/worktrees/T-0001.1`, base `f8f40e0c550c86d34a5b80ef273c7b4943abf412`, head `e28db6a25` (one commit). Nothing was pushed.

## What changed

- **A. `factory/cli.py` `results_record` (lines 431-444 at head).** The first-match check is now split on `--killed`:
  - With `--killed`, the old code is kept exactly: first hex `Commit:` line, refuse only on a mismatch, and no check when there is no line.
  - Without `--killed`:
    1. Collect every line matching `^Commit:.*$` (re.M). If there are none, refuse with `results record: the output has no Commit: line`.
    2. Match each line with the existing grammar, now anchored to that line: `Commit:\s*`?([0-9a-fA-F]{7,40})`?\b`. If a line does not match, refuse with `results record: Commit: <value> is not a commit id`. If it matches but the lowercased value is not a prefix of `--head`, refuse with the existing message `the output says Commit: <v>, not the head <head[:12]>`.
    3. Every refusal raises `Refused` (exit 2) before any `store.record_result` or `store.log_event` call, in the same place as the old check.
- **B. `tests/factory/test_shepherd.py:268`.** The merge-gate story's direct `results record --role verifier` call now passes `--output str(f.store / "runs" / ver.run_id / "output.md")` instead of `str(red)`. No assertions changed. This is the only line changed in that file.
- **C. New file `tests/factory/test_results_commit.py`** with 9 tests, one per scenario. Each test runs `bin/factory` as a subprocess against a temporary `FACTORY_STATE` (one ticket, head = forty zeros).
  - Refusal tests check: exit 2, the reason on stderr, no files under `results/<head>/`, and no `result.*` log events.
  - Accept tests check: the rows written, the `result.recorded` events, and the row statuses.
  - Killed tests check for a single `verifier.yaml` row with status KILLED.

## Acceptance results

I ran all nine WHEN commands verbatim from the worktree root under both bash and zsh. Both shells gave the same output, before and after. The script is at `/private/tmp/claude-501/-Users-dphang-dev-nanobot/c69bfd1d-97a6-43e3-9d5a-a517c28d382c/scratchpad/acc.sh`.

| Scenario | Kind | Before (base f8f40e0c5) | After (head e28db6a25) |
|---|---|---|---|
| no-commit-line-is-refused | NEW | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=2 rows=[] events=0` |
| non-hex-commit-value-is-refused | NEW | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=2 rows=[] events=0` |
| later-commit-line-naming-another-commit-is-refused | NEW | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=2 rows=[] events=0` |
| verifier-without-commit-line-writes-no-ci-row | NEW | `exit=0 rows=[ci.yaml verifier.yaml ] events=2` | `exit=2 rows=[] events=0` |
| earlier-commit-line-naming-another-commit-is-refused | REGRESSION | `exit=2 rows=[] events=0` | `exit=2 rows=[] events=0` |
| full-head-sha-is-recorded | REGRESSION | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=0 rows=[reviewer.yaml ] events=1` |
| abbreviated-sha-in-backticks-is-recorded | REGRESSION | `exit=0 rows=[ci.yaml verifier.yaml ] events=2` | `exit=0 rows=[ci.yaml verifier.yaml ] events=2` |
| killed-without-output-records-killed | REGRESSION | `exit=0 rows=[verifier.yaml ] status=KILLED` | `exit=0 rows=[verifier.yaml ] status=KILLED` |
| killed-with-cut-off-output-records-killed | REGRESSION | `exit=0 rows=[verifier.yaml ] status=KILLED` | `exit=0 rows=[verifier.yaml ] status=KILLED` |

The NEW criteria failed before as the spec describes, and the REGRESSION criteria passed before. The spec matches reality.

**factory-suite-still-passes:** `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory`
- Before: `55 passed in 92.01s`.
- After: `64 passed in 62.69s (0:01:02)`, exit 0. That is 55 + the 9 new tests. I ran it with the worktree's own `.venv/bin/pytest` (checked with `uv run which pytest`).

**Red step:** the new test file run against the base code gave `4 failed, 5 passed`. The 4 failures were the 4 NEW scenarios, all at the `returncode == 2` assertion.

**Gate: lint.** `uv run ruff check nanobot/` printed `All checks passed!` (exit 0). I also ran ruff on `factory/cli.py` and the new test file: `All checks passed!`.

**Gate: full suite.** `uv run scripts/full_suite_gate.py --isolated-home --pytest-args "-n 2 --dist loadfile"` passed in the end, but only after I changed the worktree's environment. In order:
1. **First attempt: exit 2.** `pytest is not importable under .../T-0001.1/.venv/bin/python3`. The fresh worktree `.venv` had no dev extra installed. I ran `uv sync --frozen --all-extras`, which does not change `uv.lock` or `pyproject.toml`.
2. **Second attempt: exit 1, `FAIL: 10 failure(s) NOT in the baseline`.**
   - 9 failed with `ModuleNotFoundError: No module named 'neonize'`: in `tests/lionbot/test_upstream_seams.py` (5), `tests/lionbot/test_auto_mention.py` (3) and `test_typing_hooks.py::...test_a_connected_channel_does_send` (1).
   - `tests/agent/test_mcp_reconnect_crash.py::test_mcp_reconnect_during_shutdown_does_not_crash` failed with a TimeoutError.
   - I checked out base `f8f40e0c5` (detached, in this worktree) and ran the same 4 files there: the same 10 tests failed in the same way (`10 failed, 57 passed, 1 skipped`). They fail without this change, so it did not cause them.
   - The cause is the environment. `neonize` is in neither `pyproject.toml` nor `uv.lock`, but the green checkout's `.venv` has `neonize 0.3.18.post0` and `mcp 1.29.1`. The lock pins `mcp 1.30.0`.
3. **Third attempt: exit 0.** I installed those two versions into this worktree's `.venv` only, with `uv pip install --python .venv/bin/python "neonize==0.3.18.post0" "mcp==1.29.1"`, which changes no project file. The 10 tests then passed (`67 passed, 1 skipped`). I ran the gate as `.venv/bin/python scripts/full_suite_gate.py --isolated-home --pytest-args "-n 2 --dist loadfile"` (the form the gate's own error message gives), so that `uv run` would not re-sync `mcp` back to 1.30.0. Result: `5 failed, 7297 passed, 20 skipped`, `the suite ran (7322 tests) and its failure set is within the baseline (5 known failure(s))`, exit 0.

## Tests added/changed

- **Added:** `tests/factory/test_results_commit.py`, 9 tests, one per parent scenario (factory-suite-still-passes is the suite run itself). This is part C.
- **Changed:** `tests/factory/test_shepherd.py:268`, the `--output` argument only. This is the one line listed under "Tests to change". The story's `red.md` has a literal `Commit: HEAD`, which part A now correctly refuses (exit 2), and that would break `f.ok`. The dispatched run's `output.md` has the same content with the real head substituted (`test_shepherd.py:648`). The behaviour under test is unchanged: a red verifier and a red ci row block the merge.
- No other existing test, fixture or stub was touched. Lines 327, 408-409 and 489 and `tests/factory/fixtures/stubs/` are unchanged.

## Known gaps and uncertainties

- **One change beyond the spec's list (multi-line `Commit:`).** The old regex `^Commit:\s*...` with re.M could match across a newline, so a bare `Commit:` with the hex on the next line was accepted. The new check matches within one line, so that output is now refused, with a message whose value is empty (`Commit:  is not a commit id`). Under the spec ("a line that starts with `Commit:`" whose value must parse) this is intended, but it is a change the spec does not list. The `--killed` path keeps the old cross-line behaviour exactly.
- **Not run: A without B.** I did not separately confirm that part A fails the merge-gate story when part B is left out. The parent's scratch run reports this. I relied on reading `test_shepherd.py:264-268` together with the new refusal.
- **The gate depends on the environment.** On a `.venv` synced strictly from `uv.lock` (no `neonize`, `mcp 1.30.0`), the full-suite gate FAILs with 10 tests outside the baseline, and it does so at base too. A verifier running the gate on this head will see the same result unless its environment matches the green checkout's `.venv`. I changed no project dependency file. I only installed packages into this worktree's untracked `.venv`.
- **How real checkers write the line is still unverified.** As the parent's Risk says, a checker that writes `**Commit:** ...` will now be refused and its ticket parked. I did not change that, since it is out of scope.

## Out-of-scope observations

- **The full-suite gate rewrites a protected file.** Something in the gate's pytest run executes a real JS package install in `webui/`. It created `webui/node_modules/` and rewrote `webui/package-lock.json` (a protected path): 43 lines deleted, dropping `@radix-ui/react-separator`. The mtimes, 18:48:26, fall inside the gate run, and it happened again on the third gate run. I restored the file both times with `git checkout -- webui/package-lock.json`. It is not in the commit, and the working tree is clean at `e28db6a25`. I did not identify which test does this. The likely area is the webui auto-build path (`ensure_webui_bundle`) reached through a test that is not mocked. This needs a look: any role that runs the gate and then commits with `-a` would commit a protected-path change.
- **`neonize` is missing from the lock.** Both lionbot seam tests and production code need it, but it is in neither `pyproject.toml` nor `uv.lock`, and green's `.venv` also drifts from the lock on `mcp` (1.29.1 vs 1.30.0). A worktree synced from the lock cannot pass the gate.
- The parent's own observations stand untouched: `--killed --output <missing file>` crashes with `FileNotFoundError`, and the `results record` call on `wrong.md` at `test_shepherd.py:333` is dead.

## Responses to findings

None. This is round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. All nine WHEN commands gave the required results under bash and zsh, `tests/factory` passed 64/64, and the gate passed. The one caveat is that the gate passed only after I matched this worktree's untracked `.venv` to the green checkout's environment (above).
ESCALATIONS: The full-suite gate rewrites `webui/package-lock.json` (protected path) during its run (I restored it, and it is not committed). The gate also FAILs on a `.venv` synced strictly from `uv.lock`, because `neonize` is not a declared dependency. That failure is environmental and identical at base, but the verifier's `Gate suite` result will depend on which environment it uses.

## Diff `b551d97cd9797c72aa2f4b20170a7b2690ff2e58...e28db6a255e8cd0032c67ada62b74b6681cd511d`

diff --git a/factory/cli.py b/factory/cli.py
index 80185e0fd..aa2ea2c3d 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -428,9 +428,20 @@ def results_record(a, root, cfg):
     else:
         parsed = status.parse(text)
         st = parsed["status"] or "UNKNOWN"
-    cm = re.search(r"^Commit:\s*`?([0-9a-fA-F]{7,40})`?\b", text, re.M)
-    if cm and not a.head.startswith(cm.group(1).lower()):
-        raise Refused(f"results record: the output says Commit: {cm.group(1)}, not the head {a.head[:12]}")
+    if a.killed:  # a killed run's output may be cut off: check only a hex Commit: line it does have
+        cm = re.search(r"^Commit:\s*`?([0-9a-fA-F]{7,40})`?\b", text, re.M)
+        if cm and not a.head.startswith(cm.group(1).lower()):
+            raise Refused(f"results record: the output says Commit: {cm.group(1)}, not the head {a.head[:12]}")
+    else:  # every Commit: line must name the head; with none, the verdict is for no known commit
+        lines = re.findall(r"^Commit:.*$", text, re.M)
+        if not lines:
+            raise Refused("results record: the output has no Commit: line")
+        for line in lines:
+            cm = re.match(r"Commit:\s*`?([0-9a-fA-F]{7,40})`?\b", line)
+            if not cm:
+                raise Refused(f"results record: Commit: {line[len('Commit:'):].strip()} is not a commit id")
+            if not a.head.startswith(cm.group(1).lower()):
+                raise Refused(f"results record: the output says Commit: {cm.group(1)}, not the head {a.head[:12]}")
     stale = t.get("head") is not None and a.head != t.get("head")
     rows = [store.record_result(root, t["id"], a.head, a.role, st, a.run)]
     if a.role == "verifier" and not a.killed:
diff --git a/tests/factory/test_results_commit.py b/tests/factory/test_results_commit.py
new file mode 100644
index 000000000..0908d5855
--- /dev/null
+++ b/tests/factory/test_results_commit.py
@@ -0,0 +1,131 @@
+"""`factory results record` files a checker's verdict only for the commit the checker names.
+
+Each case drives `bin/factory` as a subprocess against a throwaway store (FACTORY_STATE), the
+same way the scenarios in the change "checker-output-must-name-the-head" do: one ticket, a
+head of forty zeros, one checker output, then look at the exit code, the rows written under
+results/<head>/ and the `result.*` events in the log.
+"""
+from __future__ import annotations
+
+import json
+import os
+import subprocess
+from pathlib import Path
+
+import pytest
+import yaml
+
+REPO = Path(__file__).resolve().parents[2]
+BIN = REPO / "bin" / "factory"
+HEAD = "0" * 40
+REVIEWER_TAIL = "Findings: none\nSTATUS: APPROVE\nCONFIDENCE: high\nESCALATIONS: none\n"
+VERIFIER_TAIL = "Per criterion: none\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high\nESCALATIONS: none\n"
+
+
+class Store:
+    def __init__(self, tmp: Path):
+        self.root = tmp / "store"
+        self.tmp = tmp
+        req = tmp / "r.md"
+        req.write_text("# x\n\nthe thing\n")
+        cp = self.cli("ticket", "new", "--file", str(req))
+        assert cp.returncode == 0, cp.stderr
+        self.tid = json.loads(cp.stdout.strip().splitlines()[-1])["id"]
+
+    def cli(self, *argv: str) -> subprocess.CompletedProcess:
+        env = {**os.environ, "FACTORY_STATE": str(self.root), "PYTHONDONTWRITEBYTECODE": "1"}
+        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)
+
+    def record(self, role: str, output: str | None, *extra: str) -> subprocess.CompletedProcess:
+        argv = ["results", "record", self.tid, "--head", HEAD, "--role", role, "--run", "R1", *extra]
+        if output is not None:
+            o = self.tmp / "o.md"
+            o.write_text(output)
+            argv += ["--output", str(o)]
+        return self.cli(*argv)
+
+    def rows(self) -> list[str]:
+        d = self.root / "results" / HEAD
+        return sorted(p.name for p in d.iterdir()) if d.exists() else []
+
+    def result_events(self) -> list[dict]:
+        evs = []
+        for p in sorted((self.root / "log").glob("*.jsonl")):
+            evs += [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
+        return [e for e in evs if e["event"].startswith("result.")]
+
+    def status(self, role: str) -> str:
+        return yaml.safe_load((self.root / "results" / HEAD / f"{role}.yaml").read_text())["status"]
+
+
+@pytest.fixture
+def s(tmp_path):
+    return Store(tmp_path)
+
+
+def _refused(s: Store, cp: subprocess.CompletedProcess, reason: str) -> None:
+    assert cp.returncode == 2, cp.stderr
+    assert reason in cp.stderr
+    assert s.rows() == []
+    assert s.result_events() == []
+
+
+# ----- refused: nothing is written -----------------------------------------------------------
+
+def test_no_commit_line_is_refused(s):
+    cp = s.record("reviewer", REVIEWER_TAIL)
+    _refused(s, cp, "no Commit: line")
+
+
+def test_non_hex_commit_value_is_refused(s):
+    cp = s.record("reviewer", "Commit: HEAD\n" + REVIEWER_TAIL)
+    _refused(s, cp, "Commit: HEAD is not a commit id")
+
+
+def test_later_commit_line_naming_another_commit_is_refused(s):
+    cp = s.record("reviewer", f"Commit: {HEAD}\nFindings: none\nCommit: deadbeef00\nSTATUS: APPROVE\n")
+    _refused(s, cp, "Commit: deadbeef00, not the head")
+
+
+def test_verifier_without_commit_line_writes_no_ci_row(s):
+    cp = s.record("verifier", VERIFIER_TAIL)
+    _refused(s, cp, "no Commit: line")
+
+
+def test_earlier_commit_line_naming_another_commit_is_refused(s):
+    cp = s.record("reviewer", f"Commit: deadbeef00\nFindings: none\nCommit: {HEAD}\nSTATUS: APPROVE\n")
+    _refused(s, cp, "Commit: deadbeef00, not the head")
+
+
+# ----- accepted: the verdict is filed against the head ----------------------------------------
+
+def test_full_head_sha_is_recorded(s):
+    cp = s.record("reviewer", f"Commit: {HEAD}\n" + REVIEWER_TAIL)
+    assert cp.returncode == 0, cp.stderr
+    assert s.rows() == ["reviewer.yaml"]
+    assert [e["event"] for e in s.result_events()] == ["result.recorded"]
+    assert s.status("reviewer") == "APPROVE"
+
+
+def test_abbreviated_sha_in_backticks_is_recorded(s):
+    cp = s.record("verifier", "Commit: `0000000`\n" + VERIFIER_TAIL)
+    assert cp.returncode == 0, cp.stderr
+    assert s.rows() == ["ci.yaml", "verifier.yaml"]
+    assert [e["event"] for e in s.result_events()] == ["result.recorded", "result.recorded"]
+    assert s.status("verifier") == "VERIFIED" and s.status("ci") == "PASS"
+
+
+# ----- --killed: unchanged, a KILLED row with or without a cut-off output ---------------------
+
+def test_killed_without_output_records_killed(s):
+    cp = s.record("verifier", None, "--killed")
+    assert cp.returncode == 0, cp.stderr
+    assert s.rows() == ["verifier.yaml"]
+    assert s.status("verifier") == "KILLED"
+
+
+def test_killed_with_cut_off_output_records_killed(s):
+    cp = s.record("verifier", "Per criterion: (cut off)\n", "--killed")
+    assert cp.returncode == 0, cp.stderr
+    assert s.rows() == ["verifier.yaml"]
+    assert s.status("verifier") == "KILLED"
diff --git a/tests/factory/test_shepherd.py b/tests/factory/test_shepherd.py
index 3744c934b..8cd792166 100644
--- a/tests/factory/test_shepherd.py
+++ b/tests/factory/test_shepherd.py
@@ -265,7 +265,7 @@ def test_a_merge_waits_for_every_checker_and_refuses_a_red_gate(tmp_path):
     assert f.last_join["decision"] == "wait" and f.last_join["missing"] == ["verifier", "ci"]  # the join waits for every row
     ver = f.dispatch("verifier", st, stub_path=red, route=False)
     head = f.ticket(st)["head"]
-    f.ok("results", "record", st, "--head", head, "--role", "verifier", "--output", str(red), "--run", ver.run_id)
+    f.ok("results", "record", st, "--head", head, "--role", "verifier", "--output", str(f.store / "runs" / ver.run_id / "output.md"), "--run", ver.run_id)
     assert f.results(st) == {"reviewer": "APPROVE", "verifier": "FAILED", "ci": "FAIL"}
     cp = f.cli("merge", st)  # the gate reads the table: APPROVE is not enough when ci and the verifier are red
     assert cp.returncode == 2 and "ci is FAIL" in cp.stderr and f.repo_rev("main") != head
