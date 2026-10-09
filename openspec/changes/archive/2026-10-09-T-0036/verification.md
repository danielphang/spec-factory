## Acceptance
- A ticket naming one capability composes inputs with only that capability in full and an index line for each other one → NEW. Today it prints `W: alpha=1 beta=1 gamma=1 alpha-index=n gamma-index=n cites=0`, then `C: alpha=1 beta=1 gamma=1 alpha-index=n gamma-index=n cites=0`, then `P: alpha=0 beta=0 gamma=0 alpha-index=n gamma-index=n cites=0` (re-run on `main` at `9a25809` in this round). Every capability is sent whole, no input holds a capability's path, and there is no index instruction.
- Decisions of other tickets and capabilities reach each role as one index line per ticket → NEW. Today each of the three lines reads `own=1 beta-line=1 gamma-line=1 other=1 indexed= log-path=n grep-cmd=0` (re-run on `main` in this round). The whole log is sent, there is no index or `grep` instruction, and the log's path appears nowhere.
- Without a Capabilities line every capability and every decision reach the writer, critic and planner → REGRESSION. It prints the expected three lines on `main` today (run in this spec's investigation).
- The harness suite passes with the new inputs → REGRESSION. `main` today: `364 passed`.
- A triage input lists every capability by path and requirement, and its prompt asks for the Capabilities line → NEW. Today it prints `triage: alpha-index=n beta-index=n gamma-index=n bodies=0 decisions=0 asks=0`.
- The prompt copies, design, build spec, README and changelog name the capability index → NEW. Today it prints `docs-copy=0 runtime=0 changelog=0 design=n build-spec=n readme=0`, then `whitespace=ok`.

## Responses
Round 2 answers the operator's gate change request (`approvals/T-0036/changes-1.md`, also `.factory/answers/T-0036-gate-changes-2026-10-08.md`) and the round-1 critic findings (`run-0338-critic`). As that request directs, the design, Decisions and scope are unchanged.

- Gate item 1, and critic [SHOULD-FIX] 2 (index instruction paragraphs unchecked): FIXED. Design B3 and B6 now give each index's instruction paragraph as exact, one-line text. The WHEN of "A ticket naming one capability composes inputs with only that capability in full and an index line for each other one" adds `cites=`, a count of `sends that capability in full to the critic`. The WHEN of "Decisions of other tickets and capabilities reach each role as one index line per ticket" adds `grep-cmd=`, a count of `grep ' <ticket id> ' <absolute path of decisions.md>`. THEN lines expect `cites=1 / 1 / 0` and `grep-cmd=1 / 1 / 1` for writer, critic and planner. Both requirements now name the instruction. A build that emits only the bullet lines prints `cites=0` and `grep-cmd=0` and fails. Both WHENs were re-run on `main` at `9a25809` through the fixture. They print `cites=0` and `grep-cmd=0` on every line, as verification.md now records, so both stay NEW.
  - One wording correction rides with this. v1's B3 paraphrase said that citing a path "makes the critic and the planner receive that capability in full". B4 to B7 and the first requirement give the planner no current truth, only the decision lines that name the capability. The exact B3 sentence therefore says what the design does: the capability goes in full to the critic, and its decisions go to the critic and the planner. No behaviour changes.
- Gate item 2, and critic [SHOULD-FIX] 6 (README bullet, design part C): FIXED. The Spec critic row follows the Spec writer row. The Planner row gains only the decision-index clause, with no capability index, which matches B7 and the harness-docs scenario's `readme=3` over the Triage, Spec writer and Spec critic rows.
- Gate item 2, and critic [SHOULD-FIX] 6 (Operator steps glosses): FIXED. "the runtime" is glossed as the pinned checkout the factory runs from, which moves only on an upgrade. The gloss appears in Risk, its first use, and again in step 1. "rubric item 5" is glossed as the critic's consistency check. "SPEC-DEFECT" is glossed as the verifier's verdict that the spec, not the code, is wrong.
- Critic [NIT] 4 (`Capabilities: none` versus a missing line): not applied. Gate item 3 limits this round to items 1 and 2. Design B1 and B4 already make the two cases exact.
- Critic [NIT] 1 (source of the 45-call median): not applied, for the same reason. The figure is the request's own (issue #75, quoted in the triage ticket's Evidence).
- Critic [NIT] 6 (harm stated in Problem's second paragraph): not applied, for the same reason.

## Critic rounds

round 1 · spec v1 · run-0338-critic · APPROVE

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

round 1 · spec v2 · run-0340-critic · APPROVE

Round 2 review of T-0036 v2.

Scope of this round: whether the round-1 findings (`run-0338-critic`) and the operator's gate request (`approvals/T-0036/changes-1.md`) are resolved, and the text that changed. I diffed `specs/T-0036/v1.md` against `v2.md`: the changes are B3 and B6 (exact instruction paragraphs), part C (README bullets), the first two role-inputs requirements and their WHEN/THEN lines (`cites=`, `grep-cmd=`), the matching verification.md "today" lines, the Risk and Operator steps glosses, and a new Responses section. Design, Decisions and scope are otherwise unchanged, as gate item 3 requires.

What I checked myself (on `~/dev/spec-factory`, `main` at `9a25809`, checkout clean before and after):
- Cited paths: `factory/compose.py:168-176` (`add_truth`, `add_decisions` as described), `README.md:84-87` (the four role rows; the Spec writer row still says "current truth for the capabilities it touches").
- Acceptance run as written, no test suite: the harness-docs scenario prints `docs-copy=0 runtime=0 changelog=0 design=n build-spec=n readme=0` then `whitespace=ok`, matching its "today" line.
- The `t0036-store.sh` fixture (copied verbatim from the spec into my scratch directory, `TMPDIR` pointed there, fresh `HOME`) runs to the end on `main`; its triage output carries `Capabilities: beta` at line 4. Scenario 1's WHEN prints exactly the three "today" lines in verification.md, each ending `cites=0`. Scenario 2's WHEN prints `own=1 beta-line=1 gamma-line=1 other=1 indexed= log-path=n grep-cmd=0` for W, C and P, as recorded. Both stay NEW, and the new counts fail today for the reason the spec gives: no index instruction exists.
- The new checks would fail a stub: a build that emits only index bullet lines prints `cites=0` and `grep-cmd=0`; one that puts a capability index into the planner input prints `P: … cites=1`. The expected `cites=1 / 1 / 0` and `grep-cmd=1 / 1 / 1` match B5, B6 and B7.
- The B3 sentence's correction (critic gets the cited capability in full; critic and planner get the decisions naming it) matches B4 to B7 and the first requirement; v1's paraphrase was wrong about the planner, and the Responses section says so.
- Part C now says the Planner row gains only the decision-index clause, consistent with B7 and the `readme=3` count over the Triage, Spec writer and Spec critic rows.
- Glosses: "the runtime" is glossed at its first use in Risk and again in step 1; "rubric item 5" and "SPEC-DEFECT" are glossed in step 2.

Prior findings:
- [SHOULD-FIX] 2 (index instruction paragraphs unchecked): RESOLVED. B3 and B6 give exact one-line text; scenarios 1 and 2 count a fixed phrase from each; verified on `main` as above.
- [SHOULD-FIX] 6 (README bullet, part C): RESOLVED.
- [SHOULD-FIX] 6 (Operator steps glosses): RESOLVED.
- [NIT] 4 (`Capabilities: none` vs missing line): WITHDRAWN (gate item 3 limits this round to items 1 and 2; B1 and B4 are exact, so no implementer question arises).
- [NIT] 1 (source of the 45-call median): WITHDRAWN (same reason; the figure is the request's own).
- [NIT] 6 (harm in Problem's second paragraph): WITHDRAWN (same reason).

Findings: none.

Out-of-scope observations (not findings; unchanged text, not blocking, and I missed it in round 1):
- Operator step 2's `grep -l '^\[[A-Z]*\] 5 '` does not match `[SHOULD-FIX] 5`, because `[A-Z]*` excludes the hyphen, and the sentence before it lists only `[BLOCKING]` and `[NIT]`. `'^\[[A-Z-]*\] 5 '` would catch all three severities. Worth one edit when the spec is next touched; it affects an operator measurement after merge, not the change or its acceptance.

## Verifier results

15c9d2f6498f40909e4a6fc270cd5639772997c8 · T-0036.1 · VERIFIED · run-0343-verifier
