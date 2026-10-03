Type: bug

Title: Harness: `results record` accepts a checker output with no `Commit:` line, a non-SHA `Commit:` value, or a stale later `Commit:` line, and records it against the current head

Summary:
The merge gate only goes ahead when every reviewer/verifier verdict on the branch's current commit is green, and each checker says which commit it checked on a `Commit:` line. Today `factory results record` refuses an output only when its first `Commit:` line names a different hex commit. An output with no `Commit:` line, or with a non-hex value such as `Commit: HEAD`, is accepted and recorded as if it checked the head being recorded, so a verdict on an older or unnamed commit can count toward a merge. The requester needs `factory results record` to refuse (exit 2, nothing written) an output that has no `Commit:` line, whose `Commit:` value is not a hex commit id, or whose last `Commit:` line does not name the head being recorded. A KILLED run (no output) keeps today's behaviour.

Evidence:
- Request: GitHub https://github.com/danielphang/spec-factory/issues/16 (open; filed 2026-10-02). Independent validator on the build half (green `e2f612272` re-check): "A missing `Commit:` line is accepted. `Commit: HEAD` (not hex) is accepted. Only the first `Commit:` line is checked." Build spec part H: the checker's `Commit:` line must equal the current head (`/Users/dphang/dev/spec-factory/specs/build-harness.md:288`).
- Verified on this checkout (`/Users/dphang/dev/nanobot-upstream`, branch `feat/lionbot-v3`, HEAD `f8f40e0c5`): `factory/cli.py:431-433` in `results_record` is
  `cm = re.search(r"^Commit:\s*`?([0-9a-fA-F]{7,40})`?\b", text, re.M)` / `if cm and not a.head.startswith(...)`: raise Refused`. With no match the check is skipped. `results_record` refusals exit 2 via `main()` (`factory/cli.py:925-928`).
- Ran that regex (python3) on three inputs: no `Commit:` line -> no match (accepted); `Commit: HEAD` -> no match (accepted); `Commit: 2986a2f6f` followed by `Commit: deadbeef00` -> matches only the first line. All three claims in the request reproduce.
- The intake harness pin (`intake/HARNESS_PIN` = `2986a2f6f`) differs from HEAD in `factory/cli.py` by one inserted line at :207 only; `results_record` logic is identical at the pin.
- Duplicate search: GitHub issues #1-#17 (open and closed) and intake tickets T-0001..T-0011 in `intake/state` - none covers the `Commit:` check. `issues/README.md` indexes #16 as this pilot. No duplicate.

Assumptions:
- (Inference) "Hex commit id" keeps today's accepted form: 7-40 hex characters, optionally in backticks, compared as a prefix of the full head SHA. The request does not say whether an abbreviated SHA remains acceptable; today's check accepts one, so I assume it stays accepted.
- (Inference) "Nothing written" means no results row and no `result.recorded` / `result.stale-discarded` log event for the refused call, matching how the existing wrong-commit refusal behaves.
- (Inference) The refusal applies to both roles `results record` accepts (reviewer and verifier), and the verifier's derived `ci` row is not written either when its output is refused.
- (Inference) "A KILLED run (no output) is unchanged" means `--killed` with no `--output` still records KILLED without any `Commit:` check.

Reason (ACCEPT): intent, failure, and desired behaviour are stated concretely and reproduce on this checkout; no product decision is needed. Suggested priority (suggestion only, a human call): high for the factory, since it closes a hole in the merge gate's one guarantee, with a small blast radius.

Out-of-scope observations:
- `tests/factory/test_shepherd.py:333` calls `results record` on `wrong.md` before line 334 writes that file; the call's result is overwritten and never asserted. Harmless, but the line is dead.

STATUS: ACCEPT
CONFIDENCE: high, the defect reproduces from the code on this checkout and the requested behaviour is fully specified apart from the scope gap escalated below
ESCALATIONS:
- The request's Scope ("`factory/cli.py` and one new test file") does not match the codebase. An existing test depends on the behaviour being removed: `tests/factory/test_shepherd.py:263-268` (in the "merge waits for every checker" test) writes `red.md` containing `Commit: HEAD` and records it directly with `results record ... --output red.md` through `f.ok`, which asserts exit 0. Under the proposed fix that call exits 2 and the test fails. Fixing it means changing an existing test (point the call at the run's `output.md`, where the harness substitutes the real head, or write the SHA into the fixture). Guardrails allow that only if the approved spec lists the test under "Tests to change". The spec writer should declare it, and the human approving the spec should know the scope is cli.py plus one existing-test fixture edit plus a new test file. The other `Commit: HEAD` fixtures (`test_shepherd.py:327, 408-409, 489` and the checker stubs under `tests/factory/fixtures/stubs/`) pass through `dispatch`, which substitutes the real head (`test_shepherd.py:648`) before recording at :710, so I expect them unaffected. I read this from the code and did not run it.
