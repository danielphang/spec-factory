# Critic review: T-0057 spec v2 (round 2)

## What I checked

- Scope this round: the four responses, the v1 to v2 diff (Problem paragraphs 1 to 3, the derived-section Decision, Risk, Operator steps, and the `first=` field of one acceptance command), and whether anything unchanged is BLOCKING and missed in round 1.
- `main` is still at `3e4705a`, with no local edits under `factory/`, `tests/`, `README.md` or `docs/`, so the round-1 path checks stand.
- The one acceptance command that changed. The writer said the session refused to re-run it. I ran the GIVEN block and the scenario "The spec writer's next run receives the refusal and its refused output" as the spec gives it, from `/Users/dphang/dev/spec-factory` under the fresh-HOME wrapper with `TMPDIR` in my scratch directory. On `3e4705a` it printed `first=0 heading= message= output= source=`, exactly the stated fails-today line. The ticket ended `awaiting-spec-gate` with one writer run and one critic run, as the verification line describes. The new `first=` pattern counts the section heading, so it no longer depends on the word "refused" appearing elsewhere in the briefing.
- The new Problem text against the writing standard (`docs/writing.md`). Paragraph 1 says what is wrong (the operator approves a spec and the code refuses it over a format mistake) and for whom (the operator). Paragraph 2 glosses the spec gate, the harness, the store, `spec add` and `approve-spec` before Evidence or Decisions use them. Paragraph 3 glosses `verification.md` and `openspec/`, and says a store without `openspec/` gets no check. Paragraph 4 glosses the round and the park. Every term of art the Evidence and Decisions sections lead with now has a gloss earlier in the Problem.
- Approved changes not yet archived: none, unchanged from round 1. T-0056 at the gate touches none of the README lines this change edits, as checked in round 1.
- Not checked, as in round 1: the suite scenario and the count of five breaking tests. The implementer's suite run is the proof.

## Findings

[NIT] 6 Problem, paragraphs 1 and 2
Problem: Paragraph 1 calls the harness "the factory's own code" and paragraph 2 then introduces "the harness" as a new name for the same thing, so the reader meets two names for one concept before the gloss ties them together.
Evidence: v2 diff, Problem paragraph 1 ("the factory's own code refuse it") and paragraph 2 ("The harness is the code that stores specs and moves tickets between agents"); `docs/writing.md` rule 9, one name per concept.
Suggested fix: In paragraph 2 write "The harness, that code, stores specs and moves tickets between agents", or leave it; a careful reader connects the two.

## Prior findings

- [BLOCKING] Gloss of `spec add`, `approve-spec`, `openspec/` and `verification.md`: RESOLVED. Each is glossed in the Problem's second or third paragraph, and "spec gate" and "harness" no longer appear in paragraph 1 before their glosses.
- [SHOULD-FIX] "runtime", "instance", "launch copy": RESOLVED. Risk glosses the instance and names both; Operator step 1 glosses the runtime; step 2 glosses the launch copy.
- [NIT] `first=` counted the word "refused": RESOLVED. The field now counts the section heading; I ran the changed command on `3e4705a` and it prints the stated `first=0`.
- [NIT] The derived "refused" section and its edges: RESOLVED. The Decision states that the section is derived when the input is built, is not a record, and names both edges.

## Out-of-scope observations

- As in round 1: a refusal followed by a good draft leaves no store event of its own, so `factory stats` cannot count bounced specs. The spec rejects a refusal record on purpose. A later ticket if the scorecard wants that figure.

STATUS: APPROVE
CONFIDENCE: high, every round-1 finding is resolved in the text, the one changed acceptance command prints its stated fails-today output on `3e4705a`, and the only new item is a naming nit
ESCALATIONS: none
