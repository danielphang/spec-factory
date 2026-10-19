## Acceptance
- The spec's-life diagram draws every route after the critic → NEW. Today README has no such subsection, and it prints `classes=0 request=no edit=no amend=no respec=no replan=no ruling=no planned=no drift=no truth=no log=no writers=no later=0`.
- The clerk node names the Workflow-script path, the launch copy and factory drive → NEW. Today the node says none of the three, and it prints `clerk=1 workflow=0 launch=0 drive=0`.
- Both diagrams of How a ticket moves have balanced quotes and brackets → NEW. Today the section holds one diagram, and it prints `blocks=1 bad=0`. The existing diagram's half of the check (`bad=0`) already holds and must keep holding.
- The How a ticket moves row names the five modules → NEW. Today the row names none of them, and it prints `row=1 names=0`.
- README is at most 1,185 lines → REGRESSION. README is 1,109 lines today; the prototype is 1,173.
- README describes init's report of a differing agent copy → REGRESSION (restated unchanged).
- The changelog records issue 108 in one entry without a numbering gap → REGRESSION (restated unchanged).
- README stays within its line budget and both documents pass the whitespace check → REGRESSION.
- The README, the design doc and the changelog describe the launch copy and the route back to checks → REGRESSION.

## Out-of-scope observations
- The budget figure is hard-coded in three requirements, so every change that grows README past the bound must restate all three. A later docs change could have the #108 and #109 requirements check "its line budget" through the one budget requirement instead.
- The existing diagram's subgraph labels, "intake workflow (agents, driven by the script)" and "build workflow (agents, driven by the script)", also describe only the Workflow-script path, since `factory drive` runs the same routes without a script. The ticket names only the clerk node, so they are left alone.
- `.factory/store/tickets/T-0049.yaml` has `type: null` and a `source:` path under a session scratchpad, as triage noted. Not touched.

## Critic rounds

round 1 · spec v1 · run-0543-critic · APPROVE

# Critic review: T-0049 spec v1 (README diagram of a spec's life)

## What I checked

- Cited README lines at `81482fe`: README is 1,109 lines; "How a ticket moves" is line 141, its diagram opens at 176, the clerk node is line 209, the caption is 218-219, `### Ticket states` is 221, the regeneration row is 1096. All match the spec.
- Cited code: `factory/compose.py:325` (planner gets the decision log, no current truth), `factory/specstore.py:6-7` (three writers of the log), `factory/drive.py:1` (no clerk), `factory/workflows/build.js:18-20,45-50`, `factory/human.py:146,148,190-196,330-334`, `factory/drift.py:50,56-58`, `factory/cli.py:487`, `factory/specstore.py:405-417`, `factory/subtickets.py:159-175`. Each says what the spec and the part E table say it says.
- The three MODIFIED requirements: I compared each against current truth `harness-docs` with 1,110 replaced by 1,185. All three are identical apart from the figure. `grep '1110\|1,110'` in that truth finds exactly those three requirements (lines 418-421, 460-471, 475-479), and no other capability reads README.
- Tests: `grep -rln README tests/` finds only fixtures that write a stub README into a scratch repo (`_fixtures.py:478`, `test_harness_lock.py:253,274`). No test reads README's text or the budget. "Tests to change: none" holds.
- Acceptance: I built a prototype README in my scratch directory by applying parts A, B and C exactly as the spec gives them. It is 1,173 lines, the spec's figure. I ran all five scenario commands on today's README and on the prototype. Today they print exactly the "today" outputs the spec records (`classes=0 … later=0`, `clerk=1 workflow=0 launch=0 drive=0`, `blocks=1 bad=0`, `row=1 names=0`, `readme=within`). On the prototype each prints exactly its THEN line. On a copy with one bracket dropped and one quote unclosed, the structural check prints `blocks=2 bad=2`.
- Parse: node is installed here, so I installed `mermaid@11` and `jsdom` into my scratch directory under a throwaway HOME and ran `mermaid.parse` on both blocks of the prototype's "How a ticket moves". Both print `ok flowchart-v2`. The broken copy's second block prints `Parse error`. The spec's parse claim under Evidence holds.
- Consistency: no approved change is unarchived. Decision T-0054 13 kept the 1,110 budget because nothing in T-0054 needed more; the request's 2026-10-19 update authorises raising it here, and the spec puts the figure to the operator at this gate. Open issues #21 and #55 mention README but neither touches this section.
- The request: every bullet of the request is drawn (versions, gate edit, request-changes, pinned version, amend, drift, re-spec, superseded sub-tickets, replan, planned_from, archive to current truth and the log, later-ticket inputs, clerk label). The spec's correction of the planner's input is right per `compose.py:325`.
- Writing: the Problem's first paragraph says what is wrong (the one diagram shows only the case where the spec never changes) and for whom (a new reader). Spec gate, critic, current truth, decision log, clerk, `factory drive` and harness are each glossed at first use.

## Findings

[SHOULD-FIX] 6 Evidence, second bullet
Problem: "design.md part E lists each edge with its file and lines" reads, to a gate reader, as a claim about the repo's design document `docs/design.md`, which Out of scope says is unchanged.
Evidence: the repo has `docs/design.md`; the bullet means part E of this spec's own design file, which the operator has not read when reading Evidence.
Suggested fix: write "part E of this spec's design (the edge-to-code table copied into the PR description) lists each edge with its file and lines".

[NIT] 1 Out-of-scope observations, third bullet
Problem: it says `.factory/store/tickets/T-0049.yaml` has `type: null`; the record has `type: chore`.
Evidence: `grep '^type:' .factory/store/tickets/T-0049.yaml` prints `type: chore`.
Suggested fix: drop the `type: null` clause and keep the note about the `source:` path.

[NIT] 6 Proposed change, part B
Problem: "runs one bin/factory command per record, all but the settings the launch copy carries" treats the settings as records; they are configuration the launch copy fills in.
Evidence: `factory/workflows/build.js:18-20` says the launch copy carries the models, round limits and store "no clerk relays them".
Suggested fix: "relays every record; the settings come from the launch copy, and factory drive needs no clerk" or similar; the scenario checks only the three phrases, so the wording is free.

No blocking findings. The change is one README edit of about 70 lines, every edge is grounded in code I spot-checked, the acceptance commands fail today for the stated reasons and pass on a prototype built exactly as specified, both diagrams parse, and the only decision with weight (the budget) is explicit and goes to the operator at this gate.

## Verifier results

17fba148d8ecf5475b7aa7ddef46193437886317 · T-0049.1 · VERIFIED · run-0546-verifier
