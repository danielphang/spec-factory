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
`/Users/dphang/dev/spec-factory/intake/green-pilot/runs/run-0018-verifier/output.md`

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/intake/green-pilot/runs/run-0018-verifier/wt` (branch `None`, base `b551d97cd9797c72aa2f4b20170a7b2690ff2e58`, head `1f3a58e52f8cba5d651aca2c89bf0a07b2b9a25b`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written): `uv run ruff check nanobot/`; `uv run --extra dev --with neonize==0.3.18.post0 /Users/dphang/dev/nanobot-upstream/scripts/full_suite_gate.py --root . --isolated-home --pytest-args "-n 2 --dist loadfile"`

## Parent spec (v1, pinned): verify every scenario on main

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
