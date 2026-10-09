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

STATUS: APPROVE
CONFIDENCE: high, every changed line was diffed against v1, both amended WHENs and the harness-docs command were re-run on `main` at `9a25809` and match verification.md, and the gate's three items are met.
ESCALATIONS: none
