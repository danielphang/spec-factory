## Findings

No blocking issues. Round 2: I reviewed only the resolution of my round-1 findings and the text that changed (Operator steps, Risk bullets 3-4, Decisions bullet 3, design part C, scenario 2 and its verification note). No new findings.

## Prior findings (round 1)

- [BLOCKING] 6, Operator steps item 1: RESOLVED. Item 1 now names the event ("Before the upgrade step moves the runtime checkout (`~/dev/spec-factory-harness`, the copy the factory runs from)") and the policy's path. `.factory/answers/queue-preapproval-policy.md:10` reads "a standards or prompt change still gets the operator's acceptance test before the runtime moves", so the spec's statement that the policy requires the test but does not set its steps is accurate. Risk bullet 4 glosses the runtime checkout, the upgrade step (README has an "Upgrade" row at line 319), "instance" and `--accept-harness` before Operator steps uses them, and items 2 and 3 use the glossed phrase. A reader new to the system can now follow all three steps without a translator.
- [SHOULD-FIX] 2, scenario "a run's system prompt carries the scratch rule": RESOLVED. The check now greps for the precedence clause and THEN is exactly `1`. I ran the revised command verbatim through the Running code wrapper on a throwaway store from `~/dev/spec-factory` at `d15d833`: it printed `0`, matching the stated "today" value. I wrote design part C's reflowed block to a scratch file: the clause `takes precedence over any other instruction to use a session scratchpad` sits on one line (`grep -c` prints `1`) and the block's longest line is 74 characters, under the current preamble's 79, so the identity check across the three copies is not put at risk by the reflow.
- [NIT] 4, Decisions third bullet: RESOLVED. The bullet now states that a spec writer's prototype is gone before the critic or the gate operator reads the spec, that it survives only while the ticket is parked, and that a writer who wants the gate to see one must put what it showed in the spec.

## What I checked this round

- `git rev-parse --short HEAD` in `~/dev/spec-factory` is `d15d833`, the revision the spec's "today" values cite. The working tree has only store changes under `.factory/state/`, none under `factory/`, `docs/` or `tests/`, so the scenario ran against the code the spec describes.
- `grep -n scratchpad factory/prompts/preamble.md docs/prompts/00-preamble.md` finds nothing, so the clause is genuinely new and a stub that only mentions a session scratchpad elsewhere still prints `0`.
- The round-1 checks of cited paths, evidence rows, scenarios 1, 3 and the parked-ticket scenario, scope and Risk stand; none of that text changed.

## Out-of-scope observations

- Operator step 1 sends the operator to a policy that requires an acceptance test but does not define one. The spec says so honestly; defining the test belongs to the policy, not this ticket.
- Design F says the new test file covers "scenarios 1 to 7"; the eighth (documents) and ninth (suite) scenarios are grep and pytest checks the verifier runs directly. Consistent, just noting the count for the implementer.

STATUS: APPROVE
CONFIDENCE: high. All three round-1 findings are fixed as described; I re-ran the revised acceptance command and confirmed the policy citation and the reflowed preamble text myself.
ESCALATIONS: none
