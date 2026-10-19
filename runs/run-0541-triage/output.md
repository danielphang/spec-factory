Type: chore (documentation only; no behaviour changes)

Title: README: a diagram of a spec's life, covering its versions, changes after the gate, and how current truth and the decision log feed later tickets

Summary:
On 2026-10-12 the operator asked for a README diagram that shows how a request becomes a spec, how that spec flows into the build, and how a change to a spec spreads after the spec gate (the human approval that pins one spec version). README's only flow diagram, under "How a ticket moves", shows a ticket whose spec never changes after the gate. The new diagram (or two) must show five things: the spec's versions through the critic loop, a gate edit and `request-changes`; the two ways to change a spec after the gate (`spec amend`, and a re-spec through `resolve --to spec-gate` that re-plans and supersedes the old sub-tickets), plus `resolve --replan`; `planned_from` linking a sub-ticket to the version it builds; the loop where archive writes current truth and decisions that later tickets' triage, spec writer, critic and planner read; and that the clerk relay exists only on the Workflow-script path. Every edge has to be a route the code has, with its line cited. The existing diagram's clerk node gets a Workflow-path-only label. Following the operator's 2026-10-19 update, the spec raises README's 1,110-line budget to whatever the diagram and caption need, and the operator approves the new number at the gate.

Evidence:
- Request: issue https://github.com/danielphang/spec-factory/issues/104 (operator, 2026-10-12; after #101), plus the operator update of 2026-10-19 appended to the request.
- No duplicate. #104 appears in exactly one row of `dev/issues.md` (line 107), and that row points at T-0049, this ticket. `grep -l "#104\|issues/104" .factory/store/tickets/*.yaml` matches no other ticket. T-0040 to T-0054 are all `closed` except T-0049 (`ready-for-triage`).
- The sequencing is met. `main` is at `81482fe`; T-0048 (#101) is `closed`.
- The update's line references hold at `81482fe`. `wc -l README.md` gives 1109. "How a ticket moves" is the heading at README:141, and the next heading, "Ticket states", is at README:221. The section's diagram opens at README:176 (```` ```mermaid ````) and closes at README:211. The colour classes `human`, `orch` and `store` are defined at README:178-180. The clerk node, at README:209, reads `CL["clerk agent<br/>runs one bin/factory command per record"]:::orch` and says nothing about being Workflow-path only.
- The budget is hard-coded in 7 lines of `.factory/store/openspec/specs/harness-docs/spec.md`: 418, 420, 421, 460, 471, 475 and 479. Line 418 already allows for this change: "a later change that needs more room rai[ses it]". `grep -rn 1110 tests/factory` finds nothing, so no test changes.
- Every route the request names exists in the harness at `81482fe`:
  - `resolve --to spec-gate|checks`: factory/cli.py:799
  - `--replan`: factory/cli.py:803 and factory/human.py:278
  - `approve-spec --edit`: factory/cli.py:788
  - `request-changes`: factory/cli.py:790 and factory/human.py:175
  - `spec amend`: factory/cli.py:717
  - `subticket add` and superseding: factory/cli.py:439, 461-473
  - `planned_from`: factory/cli.py:487, factory/subtickets.py:151, and factory/human.py:78, where an amend keeps `planned_from` ("no plan is superseded")
  - the capability index: factory/compose.py:50, 229 and 271
  - the decision log as input: factory/compose.py:235-237
  - "Only `archive` writes current truth": factory/specstore.py:6
  - `launch-script`: factory/cli.py:823 and factory/launch.py
- The request's acceptance: "the diagram parses (`npx -y @mermaid-js/mermaid-cli` or an equivalent check the writer chooses, run without a network install if possible, else a structural grep); each labelled edge cites a code route in the PR description; the existing diagram still renders."

Capabilities: harness-docs, spec-amendment, sub-ticket-planning, human-resolution, role-inputs, build-dispatch

Assumptions:
- (inference) Only harness-docs changes. It gets a raised line budget in its 7 hard-coded sites and maybe an ADDED scenario saying the diagram is present, as the request suggests. The other five capabilities are named because the diagram draws their routes, and the spec writer has to check edges against their current truth. Whether a diagram-presence scenario is ADDED is left to the writer, because the request says "may need".
- (inference) The request says to check each edge against `factory/cli.py` and `factory/compose.py`. Since the CLI split (T-0047), some of those routes live in `factory/human.py`, `factory/subtickets.py`, `factory/drift.py` and `factory/specstore.py`. I read "cite the line" as "cite the module that holds the route", wherever it is.
- (inference) The request says "archive … appends the Decisions to `decisions.md`". factory/specstore.py:6-7 lists three writers of `decisions.md`: `archive`, `decision add` and `resolve --decision`. The writer should decide whether the loop-back edge shows all three, so the diagram doesn't imply archive is the only one.
- (inference) "One diagram or two" is the writer's call. The request offers both, and the operator sees the result at the gate.
- (inference) The request says to run the parse check without a network install if possible. I did not check whether a Mermaid parser is installed on this machine. `npx -y` fetches from the network, so the writer may fall back to the structural grep the request allows.
- The new budget figure is not given. Per the 2026-10-19 update, the spec proposes it and the operator approves it at the gate. That is the operator's own decision path, so it doesn't make this ticket NEEDS-HUMAN.
- Suggested priority: low (documentation only; nothing is blocked on it). Priority is the operator's call.

Reason: The intent is clear. The operator has already made the one product call, the budget raise, and has delegated the number to the spec gate. Every route the diagram must draw exists in the code at `81482fe`, and the update's line references check out.

Out-of-scope observations:
- `.factory/store/tickets/T-0049.yaml` has `type: null` and a `source:` path under `/private/tmp/…/scratchpad/`, a session scratchpad that may no longer exist. The ticket's `request: requests/T-0049.md` is what counts. I did not change either.

STATUS: ACCEPT
CONFIDENCE: high. I confirmed with grep that there's no duplicate, that the sequencing is met, the line references, the 7 budget sites and every named route at `81482fe`; the open choices (one diagram or two, which parse check, the budget number) were left to the writer and the gate by the request itself.
ESCALATIONS: none
