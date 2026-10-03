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

