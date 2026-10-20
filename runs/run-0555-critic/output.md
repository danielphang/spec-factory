# Critic review: T-0058 spec v2 (round 2)

Round 2, so this review covers whether the round-1 findings were resolved and the text that changed between v1 and v2. The v1-to-v2 diff touches Problem items 1 and 3, the first two Decisions bullets, one GIVEN line in the store-setup scenario, the suite line under Acceptance, and the new Responses section. Nothing else moved.

What I checked, on `main` at `788a201`, from `~/dev/spec-factory`:
- `factory/status.py` lines 37-49 still build `tail` from every non-blank line below ESCALATIONS and make `[esc_head, *tail]` the item list, with the comment naming "option (b)" and the 2026-10-01 decision. The spec's gloss "the code calls it rule (b)" matches the comment.
- `factory/cli.py` lines 851-855 still return for `init`, `paths` and `stats` before `instance.guard` at line 863, with the comment "ignore --accept-harness". `factory/setup.py:187` still calls `read_bytes()` with no handler.
- Ran the acceptance command "The design doc states the footer rule and the refusal in the lock clause" under the running-code wrapper. It printed `footer=0 lock=0`, so the item is NEW and fails today as the spec says.
- `- GIVEN` lines are an established scenario form: ten current-truth capabilities use them, build-dispatch five times, so the new GIVEN line follows the store's own convention.
- Approved changes not yet archived: none, so no cross-ticket setup conflict to check.

Not checked: the suite scenario (the writer reports `615 passed in 79.30s` on the base, which I did not rerun), and whether `attribution.pr` changes a `claude -p` reply; the spec says the same and rejects that route for stated reasons.

## Prior findings (round 1)

- [BLOCKING] 6 Decisions, first bullet, `rule (b)` and `parse()` unglossed → RESOLVED. Problem item 1 now attaches "(the code calls it rule (b))" to the 2026-10-01 rule, and the Decisions bullet reads "the trailer parser, `parse()` in `factory/status.py`, drops…". The second bullet also now glosses `factory drive` and the Workflow-script path at first use. Read as the operator new to the system, the first paragraph of each human-facing section now stands on its own.
- [SHOULD-FIX] 6 Decisions, #114 bullet, `stale_agents` used as a known name → RESOLVED. Problem item 3 now introduces it as the JSON field init lists a differing copy under.
- [NIT] 2 store-setup scenario, mode-000 read assumes a non-root user → RESOLVED. The scenario carries a GIVEN line saying so; WHEN and THEN are unchanged.

## Findings

No new findings. The changed text introduces no new term of art without a gloss, no new decision, and no change to any scenario's WHEN or THEN. The round-1 assessment stands: scope fits one PR, each lettered part serves one of the four issues, "Tests to change" names the one test the #115 decision breaks, the three protected paths are declared under Risk, and the overturned T-0043 decision is named with a standing replacement.

STATUS: APPROVE
CONFIDENCE: high, every round-1 finding is fixed in the text as the Responses describe, the cited code lines are unchanged on the base and one NEW acceptance command fails today as stated
ESCALATIONS: none
