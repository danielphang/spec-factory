## Problem

Work in the spec factory stops and waits for the operator more often than it needs to. Each stop costs a full agent run plus the operator's time, and three of the recurring causes could have been seen coming when the work was planned or specified. The spec factory turns a written request into merged code using a chain of AI agents. A **spec** is the approved design for one request.

Some background. One agent, the **planner**, splits a spec into **sub-tickets**: pieces that are built and merged one after another, each by its own **implementer** agent on its own branch. Sub-tickets of the same spec are **siblings**. A sub-ticket **parks** when the harness stops it until a human rules. The harness is the code that runs the agents and enforces their rules.

The three avoidable causes:

1. **Check labels copied from the whole spec.** Each acceptance check is labelled NEW or REGRESSION. A NEW check must fail before the change, so a pass shows the change did something. A REGRESSION check must pass both before and after. The planner copies each label from the whole spec. A sub-ticket, though, starts from the **integration branch** (the branch every sub-ticket merges into) with its earlier siblings already merged. So a check that an earlier sibling already made pass, or one that always passed, is still labelled NEW. The verifier, the agent that runs the checks, then reports a defective spec, and the sub-ticket parks.
2. **Tests that an earlier sibling added cannot be changed.** An earlier sibling ships tests that pin its interim behaviour. The next sibling changes that behaviour, as the plan intends, and those tests now fail. An implementer may change an existing test only if the spec's "Tests to change" list names it. A human approves that list at the **spec gate**, the sign-off before any code is written, and at that point the sibling's tests did not exist yet. So the implementer stops and reports itself blocked.
3. **A decision overturns a test that nobody listed.** A spec's Decisions section can change behaviour that an existing test pins. Nothing tells the spec writer to look for such tests. Nothing tells the critic, the agent that reviews the spec, to check that they are listed. The implementer then blocks on the test that was left off.

The operator has ruled on who may authorize the second case. The planner may list, for a sub-ticket, tests that an earlier sibling of the same spec added. The harness must check in git that each such test really came from a sibling's merge. If it did not, the sub-ticket parks, as it would today. A test that existed before the spec's first merge still needs the spec gate's list. This change makes that ruling work and fixes the other two causes in the agents' instructions.

## Evidence

All commands ran in `~/dev/spec-factory` at `0b1abad` (today's `main`), or in clones of it in this run's scratch directory.

**The planner copies the label and may list only the spec's tests.** Every copy of the planner prompt says the same:

```
docs/design.md:509:    it needs, labelled NEW or REGRESSION the same way
docs/design.md:510:  Tests to change: none | the subset of the parent's list this one touches
```

`docs/prompts/04-planner.md:33-34` and `factory/prompts/planner.md:33-34` hold the same two lines. "The same way" means as the whole spec labelled them. A sub-ticket's list may only be a subset of the spec's list, so the planner has no way to authorize a test a sibling adds.

**Only the spec gate authorizes a test edit.** `docs/design.md:146` (the spec approval gate) calls the approved "Tests to change" list "the only authorization to alter an existing test". The preamble every agent reads says the same: "only those listed under "Tests to change" in the human-approved spec" (`docs/design.md:235`, `factory/prompts/preamble.md:63`). The code reviewer blocks any changed test "unless the spec lists that test" (`docs/design.md:588`, `factory/prompts/reviewer.md:10`).

**Nothing makes the spec writer look for tests a decision overturns.** The spec writer's format asks only for "existing tests the intended change breaks, and why" (`docs/design.md:376`). The critic checks that listed tests are "genuinely" broken (`docs/design.md:413`). Nothing checks for a test that is missing.

**The parks happened.** In this repository, the verifier returned SPEC-DEFECT, its verdict for a defective spec, on three sub-tickets of one spec. Each time a NEW check already passed at the sub-ticket's own start:

| Sub-ticket | Verifier run | What the verifier found |
|---|---|---|
| T-0012.2 | run-0057 | `records-untouched` printed `0` on base and PR: "it passes on base too" |
| T-0012.5 | run-0071 | `responses-unchanged`: "on base it compares the file with itself and passes before any edit" |
| T-0012.6 | run-0092 | `no-old-paths-in-live-files` printed `exit=1` on base and PR, because "T-0012.2 and T-0012.5 have already cleaned" those files |

The first two are checks that always pass. The third passed because earlier siblings had already done the work. On the Nanobot repository, which the factory also builds, two sub-tickets of its spec T-0002 parked as "BLOCKED from implementer". Its sub-ticket T-0002.5 (`run-0147-implementer/output.md:87`) reported "The gate suite cannot pass until three T-0002.4 tests may change": the tests pinned T-0002.4's interim "not yet available" replies. `git log --diff-filter=A -- tests/policy/test_commands.py` there prints `37b8a9796 … (T-0002.4)`: the file was new in that earlier sibling. Its sub-ticket T-0002.2 (`run-0129-implementer/output.md:102`) reported that `test_interactive_agent_routes_a_complete_user_turn` pins exact CLI metadata, which decision D22 changes. D22 is that spec's decision to mark messages from the local command line. The spec's "Tests to change" left that test off.

**No harness code enforces "Tests to change" today.** `grep -rn "Tests to change\|tests_to_change\|diff-filter" factory bin agents`, leaving out `factory/prompts/`, prints only three lines from `agents/` prompt templates. No code reads the list. The merge step, `merge_cmd` (`factory/cli.py:528`), checks only the checkers' verdicts and that the branch contains the integration branch.

**The data a harness check needs is already recorded.** When a sub-ticket merges, `merge_cmd` writes `merge: {base_before, main_after}` on it (`factory/cli.py:553`). Those are the integration branch's commits just before and just after its merge. On the first sibling's merge it also writes the parent's `parent_base` (`factory/cli.py:560-561`), the integration branch before any sibling merged. So git can tell which sibling's merge first added a file.

**A prototype of this change works.** I built parts A to E in a scratch clone and ran every scenario of this spec on it and on an unchanged clone. On the unchanged clone, each NEW scenario printed the wrong output that `verification.md` gives. On the prototype, each printed its THEN. The REGRESSION scenarios printed their THEN on both. The harness suite passed on the prototype, `265 passed`. So no existing test breaks. I also ran the prototype's reader over every sub-ticket text stored in both repositories' stores. It found no entry: no existing sub-ticket would be refused. The one text that uses the phrase "(added by" (Nanobot T-0002.6) uses it in its Parallel-safe field, which the check does not read.

## Root cause

- Labels: the planner prompt block (`docs/design.md` §4, lines 507-509, and its copies) tells the planner to copy each check's label from the whole spec.
- Sibling tests: the same block limits a sub-ticket's "Tests to change" to a subset of the spec's list (line 510). `docs/design.md:46` (piece 8, the guardrail rule) and `:146` (the spec approval gate) make the spec gate the only authority for a test edit. The preamble (`:233-235`) and the code reviewer's first check (`:585-588`) repeat that rule.
- Decisions: the spec writer's FORMAT (`docs/design.md:376`) and the critic's rubric (`:405`, `:413`) never ask whether a behaviour-changing Decision overturns an existing test.
- Run start, `run_start` in `factory/cli.py:198`, refuses an implementer run only for state and in-flight reasons. The build workflow's `runRole` (`factory/workflows/build.js:68`) parks every refused run start as `harness-bug: …`, which `resolve --ruling` does not accept (`factory/cli.py:748`).

## Out of scope

- The implementer may not change a test on its own judgement, even if it says so in its PR description. The requester ruled this out.
- The merge gate still does not compare a diff's changed tests with "Tests to change". It does not today (`factory/cli.py:528`), and this change does not add that.
- A test that existed before the spec's first sub-ticket merged can still change only if the approved spec lists it.
- The harness does not check the planner's NEW and REGRESSION labels. Part A is a prompt rule.
- The harness does not read the new "Interim tests" field.
- The agent definition templates in `agents/` are not changed. They are stale copies already: `agents/factory-planner.md` differs from `factory/prompts/planner.md` before this change. They tell the agent to read the run's `system-prompt.txt` first, which carries the new text.
- No record in either store is edited, and nothing under `~/dev/nanobot-upstream` is written.

## Open questions

none

## Decisions

- A sub-ticket's "Tests to change" may list a test file that an earlier sibling of the same parent added, one line each: `` `<file>[::<test>]` (added by <sibling ID>): <reason> ``. The harness reads only lines of that form inside the "Tests to change" field, and checks the file, not the test function. Rejected: checking test functions. The implementer rule puts new tests in new files, so a file is what a sibling adds, and git records files.
- A listed file counts as added by a sibling when it is absent at the parent's `parent_base`, and the first commit since then on the integration branch that added it lies inside one merged sibling's recorded merge (reachable from its `main_after`, not from its `base_before`). Any merged sibling of the parent counts, including those from an earlier plan. The sibling ID on the line is for the reader and is not matched. Rejected: matching the named ID, because the planner's IDs (`ST-1`) differ from the store's (`T-0001.1`) and the operator's rule names no particular sibling.
- The check runs in `run start` for every implementer run of a sub-ticket: first dispatch, fix rounds and catch-up runs. Every dispatch passes through that one place. Rejected: checking when the plan is added, when no sibling has merged yet. Rejected: checking at the merge gate, after the implementer has already edited the test. Rejected: checking where a waiting sub-ticket is released, which happens in two places and never for a sub-ticket with no dependencies.
- A failed check refuses the run start with exit 2, writes nothing, and gives an error that starts `BLOCKED from harness:` and names the file. The build workflow parks the sub-ticket with that error as the reason, so `resolve --ruling` handles it like an implementer's BLOCKED. That is what the operator's "parks for the operator, as today" describes. Rejected: a new kind of park with its own resolve verb. Rejected: having `run start` park the ticket itself, which would break the rule that a refusal writes nothing.
- The preamble's guardrail sentence and the code reviewer's test-integrity check also accept a sibling entry that the harness has checked. Without them, the implementer and reviewer would still treat the edit as forbidden, and the park would remain.
- The earlier sibling names the tests a later sibling will break under a new planner field, "Interim tests". The harness does not read it.
- The critic's check for an omitted test goes under rubric 1 (Grounded), where the requester asked for it.
- The requester's acceptance, a re-plan and re-spec of Nanobot T-0002 that the operator compares side by side, is an Operator step, not an acceptance scenario. Running it needs the Nanobot store and real agents, which a verifier must not touch.

## Risk

- Protected paths this change touches. Harness: `factory/cli.py`, `factory/subtickets.py`, `factory/gitops.py`, `factory/workflows/build.js`, and `factory/prompts/{preamble,planner,spec_writer,critic,reviewer}.md`. Generated: `docs/prompts/{00-preamble,02-spec-writer,03-spec-critic,04-planner,06-code-reviewer}.md`, each re-copied from its design-doc block. The PR therefore needs the operator's protected-path approval at merge. It does not touch `.factory/**`, `bin/factory`, `agents/**`, `pyproject.toml`, `uv.lock`, `~/dev/nanobot-upstream/**` or `~/.nanobot/**`.
- Guardrail paths: the agent prompts above change, which is the point of this ticket. One new test file is added, `tests/factory/test_sibling_tests.py`. No existing test changes.
- Blast radius. Once an instance accepts the new harness revision, the preamble change reaches every role run on that instance. The new refusal fires only for an implementer run of a sub-ticket whose "Tests to change" field has an `(added by …)` line. No stored sub-ticket in either repository has one today. The workflow change affects only a run start refusal whose error starts `BLOCKED `. No such refusal exists today.
- A wrong check would park a legitimate sub-ticket. The operator then amends the sub-ticket's text and rules, as with any BLOCKED park. A check that is too loose would let a planner authorize an edit to a test that existed before the spec. The scenarios cover both directions.
- Overlap with tickets in flight. T-0025, the store's move to its own branch, is being built and edits README and the changelog. T-0027, the request to amend a pinned spec, may edit the critic prompt. The changelog check finds this entry by its text, not by its position, so merge order does not matter. Text conflicts are resolved at merge.

## Operator steps

These checks use real agents on the Nanobot repository's records. Only the operator should run them. Do them after this change merges, and before the Nanobot instance accepts the new harness revision, which is what makes its runs use the new prompts. Work on a copy of Nanobot's store, so nothing in that repository is written.

1. Copy `~/dev/nanobot-upstream/.factory/state` to a throwaway directory `C`. In `C`, delete `tickets/T-0002.*.yaml`, so that the planner plans from scratch. From `~/dev/spec-factory`, run with `FACTORY_INSTANCE=~/dev/nanobot-upstream/.factory FACTORY_STATE=C`: `bin/factory ticket set T-0002 status=ready-for-planner in_flight=[]`, then `bin/factory run start --role planner --ticket T-0002`, then `bin/factory run compose <run>`. Run one planner agent on the composed input. Do not run the build workflow: its build phase would create branches in the Nanobot repository. Check the plan. The sub-ticket that makes the list-edit subcommands available should list the earlier sibling's `tests/policy/test_commands.py` tests under "Tests to change" as `(added by …)`. That earlier sibling should name them under "Interim tests". Each check should be labelled against its own sub-ticket's base.
2. In the same copy, set T-0002 to `ready-for-spec-writer` and run one spec writer run the same way. Its "Tests to change" should name `tests/cli/test_agent_interactive.py::test_interactive_agent_routes_a_complete_user_turn` with decision D22, the marker for messages from the local command line.
3. Compare both outputs with the original plan and spec side by side. If either check fails, do not accept the revision on the Nanobot instance; reopen this ticket.

