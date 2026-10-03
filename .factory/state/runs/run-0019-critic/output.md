Spec T-0005 v1, round 1. Spot-checks run on `~/dev/spec-factory` `main` at `0811bc1` and on a scratch clone where I applied Proposed change A–E exactly as written.

**What I checked**

- Cited paths and lines (rubric 1): `docs/spec-factory.md:286-299` is the FORMAT block with the ten named sections, Out of scope at 293 reads "what must NOT change", Risk at 295 reads "blast radius; every protected path this will touch"; RUBRIC at 308-321 with rubric 2 ending "no item names a test function or internal symbol." at 312; the Spec approval gate row is line 120 and reads exactly the quoted text; `specs/build-harness.md:158` (verbatim render), `:276` (`## Responses`), `:282` (`## Acceptance`), `:308` (`approve-spec` copies "Tests to change" and Risk paths); `plans/build-harness.md:145` (BH-3). Retro's "tightening an existing rule" is at `docs/spec-factory.md:569`. All match.
- Evidence reproduced on `main`: `grep -rn 'Operator steps\|operator step' docs specs plans prompts README.md` exit 1; both prompt-block diffs clean (exit 0); `git diff --check` clean. On `~/dev/nanobot-upstream` (`feat/lionbot-v3`, read only): `grep -rn -i 'operator step' factory/` exit 1; `factory/prompts/` holds `context.md critic.md planner.md preamble.md spec_writer.md triage.md`, no `design-doc.md`; last commit on `spec_writer.md` is `0f2e29136`. Matches the spec's Evidence and its Out-of-scope observation.
- Acceptance commands (rubric 2): on `main`, criteria 1, 3, 5, 6, 7 print `0`, `0`, `0`, `CONTIGUOUS LAST-IS-OTHER`, clean, as stated. On the scratch branch with A–E applied, all ten criteria print the stated results: `6`; clean + `1` exit 0; `3`; clean + `1` exit 0; `1`; `CONTIGUOUS LAST-IS-OPERATOR-STEPS`; clean exit 0; `0` exit 1; empty exit 1; clean exit 0. `git diff --stat main...HEAD` on that branch is `docs/spec-factory.md | 10 ++++++++--`, `prompts/02-spec-writer.md | 3 +++`, `prompts/03-spec-critic.md | 4 +++-`, 14 insertions and 3 deletions, matching the spec. The inserted continuation lines carry exactly 20 leading spaces, so criterion 1's `^                    [^ ]` filter captures both. The routing table extracted by criterion 7's range is 31 lines on `main`.
- Operator decision (rubric 4): `intake/state/requests/T-0005.md` Answer 1 says option (a), "actions on live or protected state that only the operator can perform after merge", "not acceptance", "the human approves it at the spec gate", "routing does not change", "The critic checks that such steps sit in this section and not under Acceptance", "No tracked post-merge obligation". Proposed change A–C and the Out of scope list follow it clause by clause. The two writer choices ("actions or checks"; extending rubric 2 rather than adding item 7) are stated in Open questions with their reason and left to the gate, so nothing is decided silently. The request's "criterion 8 (live soak)" is real text in the request, which grounds the "or checks" widening.
- Scope and protected paths (rubric 3, 4): three files, one PR. Risk declares `prompts/02-spec-writer.md` and `prompts/03-spec-critic.md` (generated, protected) and the §2/§3 blocks (guardrail, agent prompts), which is every protected or guardrail path the diff touches (criterion 9 enforces it). "Tests to change: none" is correct for a repo with no test files.
- Consistency (rubric 5): `intake/state/tickets/T-0001.yaml` is `awaiting-spec-gate`; its spec v1 Proposed change E appends Changelog entry 34 and its criterion 9 is `grep -c '^34\. .*continuation.*none'` → `1`. See the one finding below.

**Findings**

[SHOULD-FIX] 5 Risk, final paragraph (merge-order dependency)
Problem: "Whichever merges second must renumber its entry" treats the two orders as symmetric, but T-0001's pinned criterion 9 hard-codes `^34\.`, so if this ticket merges first and T-0001 renumbers to 35, T-0001's own acceptance fails as written and would need an `--amend-spec`.
Evidence: `intake/state/specs/T-0001.md:84` reads `grep -c '^34\. .*continuation.*none'` → `1`; this spec's criterion 6 is number-agnostic, T-0001's is not.
Suggested fix: state in Risk that T-0001 should merge first (this ticket then takes 35), or that merging this ticket first obliges a T-0001 spec amendment; no change to the Acceptance list is needed.

[NIT] 2 Acceptance, criterion 1
Problem: criterion 1 confirms the section's content but not its position, so a build that inserts it anywhere in the FORMAT block (not after Risk, as Proposed change A says) still passes.
Evidence: the command filters on `^## Operator steps ` and its continuation lines only; criterion 8 guards deletions, not order.
Suggested fix: optional; a `grep -n` comparing the line numbers of `^## Risk `, `^## Operator steps ` and `^## Responses ` in `prompts/02-spec-writer.md` would pin it, but the implementer has the exact placement in A, so I do not block on it.

No blocking issues. The spec is grounded, every acceptance item fails today for the stated reason and passes against the as-written change, the scope is one small PR with every protected path declared, and the operator's decision is carried without silent additions. An implementer can start from Proposed change A–E without a question.

STATUS: APPROVE
CONFIDENCE: high, every cited line, every evidence command and all ten acceptance commands were re-run by me on `main` and on a scratch application of the change, with matching output.
ESCALATIONS: none
