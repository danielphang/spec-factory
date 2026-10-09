Round 1 review of T-0036 v1.

What I checked myself (on `~/dev/spec-factory`, `main` at `9a25809`):
- Cited paths and lines: `factory/compose.py:33-37, 160-163, 168-176, 177, 182, 187-188, 203, 205-206, 224, 229` (all as described); `factory/cli.py:1563` (`READ_ONLY`); `factory/instance.py:56-64` (`find()`); `README.md:9, 84-87`; `docs/design.md:94, 115-120, 301-308`; `dev/build-harness.spec.md:280` and item 90 (`:478`); the four cited test ranges; `tests/factory/test_instance.py:292-293`. All exist and say what the spec says.
- Acceptance run as written: the harness-docs scenario prints `docs-copy=0 runtime=0 changelog=0 design=n build-spec=n readme=0` then `whitespace=ok`, matching the "today" line. The `t0036-store.sh` fixture runs to the end on `main` (four runs composed, triage output carries `Capabilities: beta`), and scenario 1 prints exactly the three "today" lines verification.md gives. The same store, read with scenario 2's greps, gives `own=1 beta-line=1 gamma-line=1 other=1 indexed= log-path=n` for all three roles, as claimed. `init` on a throwaway `FACTORY_STATE` initialises only that store (`factory/cli.py:1045-1095`), so the fixture writes nothing in the checkout.
- Store figures: this store 10 capabilities, 123,530 B of current truth, `decisions.md` 32,365 B / 97 lines; Nanobot 22 capabilities, 410,318 B, 71,430 B / 240 lines, `cron-agent-runs` 72,889 B; `run-0337-spec_writer/input.md` 171,618 B. All match Evidence.
- Tests pinning today's inputs: besides the four the spec names, `tests/factory/test_role_inputs.py` (planner, implementer, checker and round-2 critic inputs) and `tests/factory/test_run_isolation.py:96-103` (triage input layout, sources) compose with stub triage outputs that have no `Capabilities:` line, or no triage run, so B4's fallback keeps them; the triage index is appended after the Request part, so the "section right after the output file" check holds. `grep -rn Capabilities tests/ factory/ docs/design.md README.md` prints nothing. "Tests to change: none" stands.
- Consistency: T-0030's approved spec (v2, planned, not archived) also adds `specs/role-inputs/spec.md`, with different requirement names, so the two deltas append to one capability without clashing. The changelog's numbered form (`59. After issue #74 (2026-10-08), where …`) matches the criterion's regex.

What I could not check: the projection table (the `measure.py` prototype lived in the writer run's scratch, which the harness has cleared) and "a writer run makes a median of 45 calls" (run `meta.yaml` records no call count). Acceptance does not depend on either.

Findings:

[SHOULD-FIX] 2 specs/role-inputs/spec.md, scenarios 1 and 4
Problem: Nothing in acceptance checks the index headings' instruction paragraphs, which Decisions make the only place the roles learn that the list is complete, that an item is opened by its path, and that citing a path hands the capability to the critic (prompt edits are rejected).
Evidence: Scenario 1 greps bullet lines for path and requirement name; scenario 2 greps `-LINE` markers and the log path; scenario 4 greps the same for triage. A fix that emits only the bullet lines passes all three.
Suggested fix: In the existing WHENs, count one fixed sentence from each paragraph, for example the `grep ' <ticket id> '` instruction in the decision index and the "cites … in full" sentence in the capability index, and add them to the THEN lines.

[SHOULD-FIX] 6 design.md, part C, README bullet
Problem: "the Spec critic row (`:86`) and the Planner row (`:87`) follow the same pattern" reads as the planner row also naming the capability index, but B7 gives the planner none and the acceptance expects `readme=3` from the Triage, Spec writer and Spec critic rows only.
Evidence: `README.md:87` Planner row; harness-docs scenario regex `^\| (Triage|Spec writer|Spec critic) \(`.
Suggested fix: Say the Planner row gains only the decision-index clause ("the decision log's lines for this ticket and its capabilities, and a decision index for the rest").

[SHOULD-FIX] 6 proposal.md, Operator steps
Problem: Step 1 uses "the runtime" and step 2 uses "rubric item 5" and "verifier SPEC-DEFECT results" without a gloss; the operator at the gate has met none of them in Problem, Evidence or Decisions.
Evidence: Read the section as a reader new to the system; "runtime" first appears in Decisions' sentence about the fence and in Risk, never explained.
Suggested fix: One clause each: "the runtime (the pinned checkout the factory runs from, which moves only on an upgrade)", "the critic's consistency check, its rubric item 5", and "verifier runs that end SPEC-DEFECT, the verdict that the spec, not the code, is wrong".

[NIT] 4 proposal.md, Decisions, first and third bullets
Problem: A triage output whose line reads `Capabilities: none` gives an index-only input (the name set is empty, not absent), while a missing line gives today's whole input; the design (B1, B4) makes this exact, but the Decisions the operator reads leave the two cases to be inferred.
Evidence: B1 returns None only for a missing run or line; Decisions bullet 1 says only that `none` is ignored.
Suggested fix: Add one sentence to the third bullet: "A line that names nothing, such as `Capabilities: none`, is not this case: the role then gets the index alone, plus whatever its spec cites."

[NIT] 1 proposal.md, Problem, second paragraph
Problem: "a writer run makes a median of 45 calls" has no source in Evidence and cannot be re-derived from the store.
Evidence: `run-0337-spec_writer/meta.yaml` holds no call or turn count.
Suggested fix: Name where the figure comes from (issue #75, the workflow log) or drop the number and keep "many calls".

[NIT] 6 proposal.md, Problem, first paragraph
Problem: The first paragraph says what happens (three roles get the whole store) but leaves the harm, cost paid on every call and the needed part crowded out, to the second paragraph.
Evidence: Problem paragraphs 1 and 2.
Suggested fix: Move "so the unused part is paid for many times over, and it crowds out the part the agent needs" into the first paragraph.

Out-of-scope observations:
- The `specs/<name>/spec.md` pattern in B2 also matches a spec's own delta headers (`=== specs/harness-docs/spec.md`), so every capability a spec modifies reaches the critic and planner in full. This is a good consequence; the design could say it is intended.
- T-0030.4 (waiting-dependencies) will edit the same README role rows; whichever merges second rebases over a text conflict, not a design conflict.

STATUS: APPROVE
CONFIDENCE: high, the cited lines, the fixture and both NEW "today" outputs were checked on `main`; the projection and the call count were not checkable and acceptance does not rest on them.
ESCALATIONS: none
