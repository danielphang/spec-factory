Round 1 critique of spec v1 (checker-output-must-name-the-head).

Spot-checks (this checkout, `feat/lionbot-v3`, HEAD `f8f40e0c5`):
- `factory/cli.py:431-433` is the first-match optional check exactly as quoted; `main()` at `factory/cli.py:919-930` maps `Refused` to exit 2 and prints to stderr. `factory/workflows/build.js:139-140` records once per checker with `--output <run>/output.md` (+`--killed`) and parks with `harness-bug: results record <role>: <stderr>` on failure. `/Users/dphang/dev/spec-factory/specs/build-harness.md:288` says the `Commit:` line must equal the current head.
- `tests/factory/test_shepherd.py`: line 264 writes `red.md` with `Commit: HEAD`; line 268 records it directly via `f.ok`; lines 327, 408-409, 489 and all 10 stubs under `tests/factory/fixtures/stubs/` use `Commit: HEAD` and go through `dispatch`, which substitutes the real head at line 648 and writes `runs/<rid>/output.md` at line 649 before the `route` check, so part B's target file exists with `route=False`. No other file under `tests/factory/` calls `results record` (grep empty). `pytest --collect-only tests/factory` → `55 tests collected`.
- Ran three WHEN commands verbatim on today's code: no-commit-line → `exit=0 rows=[reviewer.yaml ] events=1`; earlier-commit-line → `exit=2 rows=[] events=0`; abbreviated-sha-in-backticks → `exit=0 rows=[ci.yaml verifier.yaml ] events=2` (the `\140` octal produced a literal backtick). All match the spec's "today" lines, so the NEW items fail today for the stated reason and the REGRESSION items pass today.
- The real checker prompts write the line in the enforced grammar: `prompts/06-code-reviewer.md:43` `Commit: <head SHA you reviewed>`, `prompts/07-verifier.md:32` `Commit: <head SHA you verified>` (both in `/Users/dphang/dev/spec-factory`), plain `Commit:` at line start. The Risk section's "could not verify how real checkers write the line" is resolvable: the format matches.

Findings:

[SHOULD-FIX] 6 proposal.md › Problem, first paragraph
Problem: The first paragraph describes how the pipeline works but does not state the defect; what is wrong appears in paragraph 2 and who is affected in paragraph 4.
Evidence: Paragraph 1 ends at "...given for exactly the code being merged." with no statement that anything fails; paragraph 2 opens "The recording command does not enforce that guarantee." Not blocking: every system term is glossed on first use and the operator can state what is wrong and for whom without inferring, one paragraph later.
Suggested fix: Move the defect statement into the first paragraph, e.g. end it with "The command that files the verdicts does not enforce this: it accepts a report that names no commit, a non-commit value, or a later different commit, so a verdict on other code can count toward a merge. Affected: the operator and anyone who trusts a merged change was checked as merged."

[NIT] 4 proposal.md › Risk, first bullet
Problem: The Risk bullet says the real checkers' `Commit:` format could not be verified, but the role prompts are on disk and instruct the exact grammar the spec enforces.
Evidence: `/Users/dphang/dev/spec-factory/prompts/06-code-reviewer.md:43` and `prompts/07-verifier.md:32` both put `Commit: <head SHA ...>` as the first output line, no bold, no indent.
Suggested fix: Replace "I could not verify how real checkers write the line" with a citation of those two prompt lines, so the implementer and gate operator know the park-on-format-drift risk is low.

[NIT] 5 proposal.md › Decisions, second bullet
Problem: `build-harness.md:288` says the `Commit:` line "must equal the current head", while the spec accepts any 7-40 hex prefix; the decision keeps today's behaviour but does not name the departure from the design doc.
Evidence: `factory/cli.py:432` already uses `a.head.startswith(...)`; the spec's "An abbreviated SHA remains acceptable" is deliberate.
Suggested fix: Add one clause: "looser than build-harness.md:288's 'equal'; kept because it is today's behaviour and the checkers may abbreviate."

No BLOCKING findings. The NEW scenarios fail today for the stated reason, the REGRESSION scenarios pin the one case (first line wrong, later line right) that a "check only the last line" fix would wrongly start accepting, the accept-path scenarios would fail against a refuse-everything stub, the single existing-test edit is declared with a reason I confirmed, no protected path is touched, and the failure mode of the change (false refusal) parks for a human rather than merging unchecked code.

STATUS: APPROVE
CONFIDENCE: high — every cited path, line and "today" output I checked matched; the one uncertainty the writer left open (real checker format) I resolved from the role prompts.
ESCALATIONS: none
