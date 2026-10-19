## Problem
`README.md` is the page a new reader learns this system from. Its one flow diagram, under "How a
ticket moves", shows only the simple case. A request becomes a spec. A human approves the spec at
the spec gate, the one sign-off before any code is written. The build then carries it to a closed
ticket, and the spec never changes on the way.

In practice a spec changes often, and the diagram draws none of it. A spec goes through numbered
versions while the reviewing agent (the critic) sends it back. The human can edit it at the gate.
After the gate it can be amended, or sent back to the gate for a new plan that replaces the
unbuilt parts of the old one. When a ticket closes, its spec is folded into current truth: one
document per capability that says what the system does now. Its decisions go into the decision
log, the file of standing decisions every later ticket must follow. The agents on later tickets
read both. README describes each of these routes in prose, in different sections. No diagram shows
how a change to a spec spreads, which is what the operator asked for.

Two smaller faults come with it. The existing diagram shows a "clerk" agent relaying every record
to the store. The clerk exists only when the pipeline runs as a Claude Code Workflow script. The
other way to run it, `factory drive`, calls the harness (the code that enforces the pipeline's
rules) in its own process and has no clerk. Second, README has a line budget of 1,110 lines,
written into the checks on the documents, and it is at 1,109 lines. Any diagram breaks that
budget. This change raises it to 1,185 lines, a figure the operator approves at this gate.

## Evidence
- README at `81482fe` is 1,109 lines (`wc -l README.md`). "How a ticket moves" runs from
  README:141 to README:219. Its one diagram is README:176-216, with its caption at README:218-219.
  The clerk node at README:209 reads `CL["clerk agent<br/>runs one bin/factory command per
  record"]:::orch` and says nothing about which way of running the pipeline it belongs to.
- Every route the new diagram draws is in the code at `81482fe`. design.md part E lists each edge
  with its file and lines. The routes agree with current truth in `openspec/specs/role-inputs/spec.md`,
  `openspec/specs/spec-amendment/spec.md`, `openspec/specs/sub-ticket-planning/spec.md` and
  `openspec/specs/human-resolution/spec.md`.
- The request says the planner receives current truth. It does not: `factory/compose.py:325` gives
  the planner the decision log only (`add_decisions()  # no current truth for the planner`). The
  diagram draws what the code does.
- `factory/specstore.py:6-7` names three writers of the decision log: `archive`, `decision add` and
  `resolve --decision`. The diagram draws all three.
- No Mermaid parser is installed here. `which mmdc` finds nothing, and the repo has no
  `node_modules`. The acceptance check is therefore structural.
- To check the draft anyway, I installed `mermaid@11.17.2` and `jsdom` from npm into this run's
  scratch directory (`--ignore-scripts`, throwaway HOME). I ran `mermaid.parse` on every Mermaid
  block of a prototype README built from design.md parts A to C. All 7 blocks printed `ok`, the
  two in "How a ticket moves" as `flowchart-v2`: both diagrams parse. A copy with one brace
  dropped and one quote unclosed printed `FAIL Parse error` for both blocks, so the parse check
  does catch errors.
- The prototype is 1,173 lines. On it, the five scenarios of this change print what their THEN
  lines say. On README at `81482fe`, the NEW ones print `classes=0 … later=0`,
  `workflow=0 launch=0 drive=0`, `blocks=1 bad=0` and `names=0` (verification.md). The structural
  check printed `blocks=2 bad=2` on the broken copy, so it catches the same two faults the parser
  caught.
- I ran every WHEN of current truth `harness-docs` (80 commands) on a scratch clone at `81482fe`,
  then again with the prototype README committed. Exactly three outputs changed, each from
  `readme=within` to `readme=over`. Those are the three requirements that hard-code 1,110 (spec
  lines 418-421, 460-471, 475-479), restated here with 1,185. With 1,185 they print what their
  THEN lines say on the prototype. No other capability's scenarios read README (`grep -l README.md
  openspec/specs/*/spec.md` finds only `harness-docs`).
- `grep -rln '1110\|clerk agent<br\|How a ticket moves' tests/` finds no test that reads README's
  text, so no test changes.

## Root cause
README's diagram (README:176-216) was drawn before the routes that change a spec after the gate
existed. Later tickets added `spec amend`, the drift check, re-planning and the role inputs, and
each described itself in prose: the **Gate**, **Amend**, **Unstick** and **Record** rows of "Where
a human decides" (README:858-861) and the "Spec amendment and drift" and "Re-plan after a
re-spec" entries (README:954-962). The clerk label dates from before `factory drive`
(`factory/drive.py:1`, "the dispatcher as an ordinary process, with no clerk"). The line budget is
hard-coded in three `harness-docs` requirements: "README stays within its line budget" (spec line
418), and the #108 and #109 records (lines 460 and 475).

## Out of scope
- No behaviour change. No file under `factory/`, `bin/`, `agents/` or `tests/` changes.
- `docs/design.md`, `docs/changelog.md` and `docs/prompts/` are unchanged.
- The existing diagram changes only on its clerk node line. Its intake and build subgraph labels,
  "(agents, driven by the script)", are left as they are; see Out-of-scope observations.
- Re-ports onto a new upstream base (#103 part C) and the prompt blocks (#83 C).
- Every other README section, except the status date and one row of "Regenerating this page from
  scratch".

## Open questions
none

## Decisions
- One new diagram, in a new subsection "How a spec changes and feeds later tickets" placed
  directly after the first diagram of "How a ticket moves", before "Ticket states". Rejected:
  two diagrams, because the second repeats the three colour lines and the gate node and adds no
  route.
- README's line budget rises from 1,110 to 1,185 lines: the prototype's 1,173 lines plus 12 lines
  of slack. The operator approves the figure at this gate. A later change that needs more room
  still raises it in its own spec.
- The decision log is drawn with all three of its writers, so the diagram does not imply that
  `archive` is the only one.
- The planner's input edge carries the decision log only, as `factory/compose.py:325` does. This
  corrects the request, which said the planner also reads current truth.
- The acceptance check of the diagrams is structural: balanced quotes and brackets, an opening
  `flowchart LR` and a closed fence. Rejected: running `npx -y @mermaid-js/mermaid-cli`, which
  needs a network install and a browser download. The spec writer's parse of the prototype is
  recorded under Evidence, and the operator step below checks the rendering.
- The "How a ticket moves" row of "Regenerating this page from scratch" names the modules the new
  diagram is drawn from, so a rebuild of the page can redraw it.
- No changelog entry. `docs/changelog.md` records changes to `docs/design.md`, which this change
  leaves alone.
- One "parked ticket" node stands for both a parked sub-ticket and a parked parent. Each edge
  label names the command that applies.

## Risk
The change is documentation only, in `README.md`. A wrong edge would mislead a reader; it cannot
change what the pipeline does. The three restated budget requirements are the only current truth
whose checks change. Each still checks the same documents, against a higher bound.
Protected paths: none

## Operator steps
- After merging and pushing `main`, open `README.md` on GitHub and confirm that both diagrams
  under "How a ticket moves" render. GitHub renders Mermaid. That is a full render, which no
  acceptance command here can do without a network install.
