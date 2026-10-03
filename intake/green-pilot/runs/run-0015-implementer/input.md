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
`/Users/dphang/dev/spec-factory/intake/green-pilot/runs/run-0015-implementer/output.md`

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/intake/green-pilot/worktrees/T-0001.1` (branch `factory/T-0001.1`, base `b551d97cd9797c72aa2f4b20170a7b2690ff2e58`, head `e28db6a255e8cd0032c67ada62b74b6681cd511d`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written): `uv run ruff check nanobot/`; `uv run --extra dev --with neonize==0.3.18.post0 /Users/dphang/dev/nanobot-upstream/scripts/full_suite_gate.py --root . --isolated-home --pytest-args "-n 2 --dist loadfile"`

## This is a conflict run
The merge gate refused your branch: head does not contain main. The integration branch moved after you branched. Merge it into your branch, resolve any conflict, re-run the gates, commit, and add one note on the resolution to the PR description. Change nothing else.

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

## Reviewer findings on your previous head

Commit: e28db6a255e8cd0032c67ada62b74b6681cd511d

Round 1 review of sub-ticket T-0001.1 (ST-1) on branch `factory/T-0001.1`. The head is one commit over `f8f40e0c5`, which is the merge-base with the input's base `b551d97cd` (the integration branch moved past the fork point; the three-dot diff is the three files below and nothing else).

Findings:
- [NIT] factory/cli.py:442: a bare `Commit:` with its value on the next line (or an empty value) is refused with `results record: Commit:  is not a commit id` (empty value, two spaces). → A human reading the parked-ticket reason (`harness-bug: results record <role>: <stderr>`) sees a message that names nothing; `the value is empty` would say what happened. Refusing this output is correct under the parent's Decision (a `Commit:` line's value must parse on that line), and the PR description discloses the change. Not blocking.

Prior findings: none (round 1).

Checks, in the role's order, with what I ran:

1. Test integrity. `git diff --name-status b551d97cd...e28db6a25`: `M factory/cli.py`, `A tests/factory/test_results_commit.py`, `M tests/factory/test_shepherd.py`. The `test_shepherd.py` hunk is `@@ -265,7 +265,7 @@`: one line, 268, and only the `--output` argument changes from `str(red)` to `str(f.store / "runs" / ver.run_id / "output.md")`; the assertions at 269-274 are untouched. That line is the one the parent lists under Tests to change. `test_shepherd.py:648` confirms the dispatcher writes `output.md` with `Commit: HEAD` replaced by the real head, so the story still records a red verifier and a red ci row for the head. Lines 327, 408-409, 489 and `tests/factory/fixtures/stubs/` are not in the diff. The new file's assertions are specific (exact row lists, exact event lists, exact statuses, the refusal reason on stderr); no skip, xfail or swallowed error. The new tests test the change: against a scratchpad copy of base `f8f40e0c5`'s `factory/` and `bin/` (not in the worktree), the new file gives `4 failed, 5 passed`, and the four failures are exactly the four NEW scenarios (`test_no_commit_line_is_refused`, `test_non_hex_commit_value_is_refused`, `test_later_commit_line_naming_another_commit_is_refused`, `test_verifier_without_commit_line_writes_no_ci_row`).

2. Correctness. `factory/cli.py:431-444` at head: with `--killed`, the old first-match check is kept verbatim (431-434); without it, every `^Commit:.*$` line is collected (436), none refuses (437-438), each must parse with the old grammar anchored to its line (440-442) and be a prefix of `--head` (443-444). Every refusal precedes `store.record_result` (446) and `store.log_event` (452), so nothing is written. I ran all nine WHEN scenarios against this head from the worktree root (`bin/factory` resolved to the worktree's `factory/` package; `factory.__file__` printed under `.../run-0013-reviewer/wt/factory/`), each on a fresh store: the five refusals print `exit=2 rows=[] events=0`; full-head prints `exit=0 rows=[reviewer.yaml ] events=1`; abbreviated-sha-in-backticks prints `exit=0 rows=[ci.yaml verifier.yaml ] events=2`; both killed scenarios print `exit=0 rows=[verifier.yaml ] status=KILLED`. Edge cases the spec implies, same method: trailing text after the value is still accepted; two lines both naming the head are accepted; a 41-hex value, a 6-hex value, `**Commit:** <head>` (the Risk's known parking case) and an indented `  Commit: <head>` are refused; `Commit: deadbeef00` under `--killed` is still refused (as today); CRLF output is accepted. `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 python3 -m pytest -q -p no:cacheprovider tests/factory` on the worktree: `64 passed in 81.29s`, no failures (55 + 9 new).

3. Scope. The three files are design parts A, B and C. No other command, role, prompt or `build.js` change.

4. Silent behavior changes. Two, both required by the parent's Requirement text and both disclosed or implied: (a) a `Commit:` whose value sits on the next line was accepted by the old cross-line `\s*` and is now refused (PR's Known gaps); (b) `results record` without `--killed` and without `--output` used to record `UNKNOWN` and is now refused with "no Commit: line" (an empty output has no such line). `build.js` always passes `--output`, so (b) is reachable only by hand.

5. Security and data safety. The checker output is untrusted text run through two bounded regexes (`{7,40}`, no nested quantifiers); no new file writes, no destructive ops; refusals write nothing.

6. Protected paths. None in the diff. `webui/package-lock.json`, `pyproject.toml`, `uv.lock` and `nanobot/api/**` are not touched; the worktree is clean at head (`git status --short` empty). The sub-ticket declares none; this matches.

7. Maintainability. The `--killed` branch repeats the grammar literal of the loop at 440. Two copies of a one-line regex, explained by the comments at 431 and 435; not worth a finding.

Out-of-scope observations (not caused by this diff; not fixed):
- `uv.lock` is gitignored in this repo (`.gitignore:61`, under "Lock files (project policy)") and untracked in the worktree. So the protected path "uv.lock" names a file the repository does not carry; the implementer's "neonize is missing from the lock" observation is about a local, untracked file. The integration branch's `b551d97cd` ("fix(factory/gate): --extra dev and --root .") and the gate command in this input (`--extra dev --with neonize==0.3.18.post0`) already address the environment failures the implementer reported, so the verifier should not see them on this head with the gate as given.
- The implementer reports the full-suite gate rewriting `webui/package-lock.json` during its run. The harness note already says so and says never to commit it; nothing of the kind is in this commit.
- The parent's own observations stand: `--killed --output <missing file>` raises `FileNotFoundError`, and the `results record` call on `wrong.md` at `test_shepherd.py:333` is dead.

STATUS: APPROVE
CONFIDENCE: high — I read the code at head, ran the factory suite (64 passed) and all nine acceptance scenarios on this worktree, confirmed the four NEW tests fail at base, and the only existing-test edit is the one declared line.
ESCALATIONS: none

## Verifier findings on your previous head

Commit: e28db6a255e8cd0032c67ada62b74b6681cd511d

Checkout: `/Users/dphang/dev/spec-factory/intake/green-pilot/runs/run-0014-verifier/wt`, detached at `e28db6a25`. `git status` was clean before any run. The PR diff (`b551d97cd...e28db6a25`) matches `../diff.patch` except for a trailing newline. It touches three files: `factory/cli.py` (+15/-3), `tests/factory/test_shepherd.py` (one line, :268, `--output` only) and the new file `tests/factory/test_results_commit.py` (131 lines).

Base note: the base I was given, `b551d97cd`, is the tip of the integration branch. It is NOT an ancestor of the head. The branch forked at `f8f40e0c5`, which is 8 commits behind `b551d97cd`. `results_record` is the same at both commits (`git diff f8f40e0c5 b551d97cd -- factory/cli.py` does not touch it). I ran the base column on a `git archive` of `b551d97cd` (scratch copy). `git merge-tree --write-tree b551d97cd e28db6a25` merges cleanly (tree `940fc7432`), and I also ran the factory suite on that merged tree.

Acceptance commands: I extracted all 9 WHEN commands verbatim from input.md lines 174-209 into a script. I ran each line from the repo root under bash and under zsh. Both shells gave the same output on both trees.

Per criterion: NEW/REGRESSION | command | base (b551d97cd) | PR (e28db6a25) | PASS/FAIL
- no-commit-line-is-refused | NEW | WHEN verbatim | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=2 rows=[] events=0` | PASS
- non-hex-commit-value-is-refused | NEW | WHEN verbatim | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=2 rows=[] events=0` | PASS
- later-commit-line-naming-another-commit-is-refused | NEW | WHEN verbatim | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=2 rows=[] events=0` | PASS
- verifier-without-commit-line-writes-no-ci-row | NEW | WHEN verbatim | `exit=0 rows=[ci.yaml verifier.yaml ] events=2` | `exit=2 rows=[] events=0` | PASS
- earlier-commit-line-naming-another-commit-is-refused | REGRESSION | WHEN verbatim | `exit=2 rows=[] events=0` | `exit=2 rows=[] events=0` | PASS
- full-head-sha-is-recorded | REGRESSION | WHEN verbatim | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=0 rows=[reviewer.yaml ] events=1` | PASS
- abbreviated-sha-in-backticks-is-recorded | REGRESSION | WHEN verbatim | `exit=0 rows=[ci.yaml verifier.yaml ] events=2` | `exit=0 rows=[ci.yaml verifier.yaml ] events=2` | PASS
- killed-without-output-records-killed | REGRESSION | WHEN verbatim | `exit=0 rows=[verifier.yaml ] status=KILLED` | `exit=0 rows=[verifier.yaml ] status=KILLED` | PASS
- killed-with-cut-off-output-records-killed | REGRESSION | WHEN verbatim | `exit=0 rows=[verifier.yaml ] status=KILLED` | `exit=0 rows=[verifier.yaml ] status=KILLED` | PASS
- factory-suite-still-passes | REGRESSION | `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory` | `59 passed in 108.21s`, exit 0 | `64 passed in 93.69s`, exit 0 | PASS
  - The count differs from the spec's "today 55" because the base moved. `f8f40e0c5` has 55 tests and `b551d97cd` has 59 (4 tests added in test_shepherd.py and test_spec_store.py). The head is 55 + the 9 new tests = 64.
  - Merged tree `940fc7432` (b551d97cd + this PR): `68 passed in 106.37s`, exit 0, which is 59 + 9. The base's new `test_redispatch_...` uses `Commit: HEAD` only through `dispatch`, which substitutes the head, so the new strict check does not break it.
- Intermediate check (gate) | REGRESSION | see Gate suite | not run on base | PASS on head | PASS

Each NEW criterion fails on base for the reason the spec states (the verdict is recorded), not because a fixture is missing. Each REGRESSION criterion passes on both trees.

Gate suite: PASS
- `uv run ruff check nanobot/` → `All checks passed!`, exit 0.
- `uv run --extra dev --with neonize==0.3.18.post0 /Users/dphang/dev/nanobot-upstream/scripts/full_suite_gate.py --root . --isolated-home --pytest-args "-n 2 --dist loadfile"` → `5 failed, 7167 passed, 25 skipped in 133.46s`, then `the suite ran (7197 tests) ... and its failure set is within the baseline (5 known failure(s))`, exit 0. The 5 failures were:
  - tests/gateway/test_runtime.py::test_default_instance_preserves_released_gateway_paths
  - tests/cli/test_tui_launcher.py::test_launcher_keeps_the_tui_alive_while_an_existing_gateway_recovers
  - two in tests/lionbot/test_service_log_paths.py::TestLogPathsFollowTheInstance
  - tests/config/test_config_paths.py::test_shared_and_legacy_paths_remain_global
- I ran the gate commands exactly as given, with no changes to the environment. Unlike the implementer, I did not need to install anything by hand: `--with neonize` and `--extra dev` covered the environment.
- I did not run the full gate on the merged tree. Only the factory suite was run there.

Probes: these used a non-zero head, `abcdef0123456789abcdef0123456789abcdef01`, to rule out special-casing of the all-zero head the tests use. Each ran `results record` from the wt with `bin/factory`.
- Uppercase abbreviated `Commit: ABCDEF0` → exit 0, recorded → OK (case-insensitive, as decided)
- `Commit: <head> (verified on a clean checkout)` (trailing text) → exit 0, recorded → OK
- Two lines, `Commit: <head>` and ``Commit: `abcdef01` `` → exit 0, recorded → OK
- CRLF line endings, `Commit: <head>\r\n` → exit 0, recorded → OK
- `Commit: <head>0` (41 hex) → exit 2, `... is not a commit id`, nothing written → OK
- `Commit: abcdef` (6 hex) → exit 2, nothing written → OK
- `Commit: abcdef1` (7 hex, wrong prefix) → exit 2, `the output says Commit: abcdef1, not the head abcdef012345` → OK
- Empty output file, not killed → exit 2, `no Commit: line` → OK
- `**Commit:** <head>` → exit 2, `no Commit: line` → OK per spec. The parent's Risk already declares this format would park a ticket.
- `commit: <head>` (lowercase key) → exit 2 → OK (case-sensitive, as decided)
- `Commit:` with the hex on the next line → exit 2, message `Commit:  is not a commit id` (empty value) → OK by spec. The implementer disclosed this. The message is unhelpful but correct.
- `Commit: <head>` then an indented `  Commit: deadbeef00` → exit 0, recorded → CONCERN (minor). Only lines that start at column 0 are checked, which matches the spec's "a line that starts with `Commit:`" and today's anchor. So an indented mismatching line is ignored. This is within the spec, not a FAIL.
- `--killed` with `Commit: deadbeef00` → exit 2, same as before. `--killed` with `Commit: HEAD` → exit 0, KILLED row. Both match today's code: the killed branch is a byte-identical copy of the old check (cli.py:431-434) → OK
- Verifier `Commit: <head>` with `Gate suite: FAIL` → exit 0, rows ci+verifier, 2 events → OK (status parsing unchanged)

Nothing suggests special-casing: the code at `factory/cli.py:431-444` is a general per-line check, and it behaves correctly for a head other than the tested one.

Out-of-scope observations:
- The head is not rebased on the integration tip. It lacks `tests/cli/conftest.py`, which the base added in b7d09a8db and which sets `NANOBOT_SKIP_WEBUI_BUILD=1`. So the gate run on this head ran a real webui build. That build rewrote `webui/package-lock.json` in my verifier worktree (43 deletions) and created `webui/node_modules/`. I left both as the gate left them: my role may only write output.md. This is the cause of the lockfile rewrite the implementer escalated, and it is already fixed on the integration branch. Once merged into `b551d97cd` the conftest will be present.
- The parent's two observations were not exercised here and still stand: the `--killed --output <missing>` crash with FileNotFoundError, and the dead `wrong.md` call at test_shepherd.py:333.

STATUS: VERIFIED
CONFIDENCE: high. I ran all 9 WHEN commands verbatim under bash and zsh on base and head, ran the factory suite on base, head and the merged tree, ran both gate commands as written, and ran 15 probes. Only one minor concern came up, and it is within the spec.
ESCALATIONS: (1) The base I was given (`b551d97cd`) is not an ancestor of the head (which forked at `f8f40e0c5`). The merge is clean and the merged factory suite passes 68/68, but the full-suite gate has not been run on the merged tree. (2) Running the gate on this head rewrote the protected `webui/package-lock.json` in the verifier worktree, because the head predates the base's `tests/cli/conftest.py`. That file is uncommitted and lives only in this run's `wt`. Whoever cleans up the worktree should discard it, and nothing should commit it.

## Gate suite on your previous head
PASS

