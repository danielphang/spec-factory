Type: bug

Title: Merge gate does not check protected paths, and the reviewer prompt promises a check it never runs

Summary: The merge gate is the last check before the harness merges a sub-ticket's branch into `main`. It merges a change to a protected path (a path whose change needs human sign-off, such as the harness's own code and prompts) without looking at which paths the change touches. So a reviewer's APPROVE that lists protected paths under ESCALATIONS still merges. An undeclared protected-path change also merges if both checkers pass it. Because the factory edits its own harness and prompts, this gate is the one meant to guard self-modification. The requester also asks to fold in a related routing bug: `resolve --ruling` on a sub-ticket that its code reviewer parked sends it to the critic, when it should go back to its checks with the ruling in the checkers' input.

Evidence:
- Request #57 (https://github.com/danielphang/spec-factory/issues/57), from #56 part D (independent review, 2026-10-05).
- The gate checks no paths. I read `factory/cli.py` `merge_cmd` (lines 645-687). It checks four things: the ticket state, that the head is the branch tip, the ci PASS / reviewer APPROVE / verifier VERIFIED rows, and that the head contains the integration branch. No line reads the diff's paths, `protected_paths` or the spec's Risk list.
- The prompt promises the check. `factory/prompts/reviewer.md` line 24-27, check 6: "If it does, list them under ESCALATIONS, finish the review, and give the STATUS the code earns; the merge gate will require a human approval." The same text is in `docs/design.md` line 640-643 and `docs/prompts/06-code-reviewer.md`.
- The design doc says the same. `docs/design.md` line 21 lists "a PR touching a protected path" as one of five human gates. Line 48 (piece 8, the guardrail and protected-path piece) and line 154 add that "the merge gate does not merge without" a human approval row.
- The gap was hit in a real run. T-0028.1 (#48) parked on 2026-10-04 because its reviewer (run-0298) escalated a 3-line change to `factory/store.py`. The approved spec asks for that change in part A.5, but its Risk list does not declare the file. The reviewer noted that no merge check reads the declaration.
- The routing bug is real. `factory/cli.py` `resolve`, the `--ruling` branch: any ESCALATE park whose reason does not contain "planner" goes to `ready-for-critic`. T-0028.1's park reason was "ESCALATE from reviewer" (`.factory/store/tickets/T-0028.1.yaml`). The operator's ruling had to be placed by hand at `.factory/store/approvals/T-0028.1/ruling-1.md`. That file says why: "`resolve --ruling` routes a sub-ticket's reviewer escalation to the critic."
- T-0029 (#49) had already recorded the wording mismatch as out of scope.
- Duplicate search: there is none. T-0033 in the store is this request. #56 is the umbrella review it came from. The T-0028 and T-0029 tickets are closed. Neither added a path check to `merge_cmd`.

Assumptions (my inferences, not the requester's statements):
- In the requester's words, "parent base" means the `main` commit the sub-ticket's branch started from. The gate would compare that with the commit it is judging.
- In this repo almost every merge touches a protected path. The command I ran checked the last 20 merge commits on `main` for changes under `factory/`, `bin/factory`, `agents/`, `pyproject.toml`, `uv.lock`, `docs/prompts/` or `.factory/`. It reported "19 of 20 recent merges touch protected paths". This matters for the question below.
- The routing fold-in covers only an ESCALATE raised by a sub-ticket's code reviewer. A budget-kill park (the harness stopping a role that ran over its limit) is #41's, as the comment says.

Question for human:
How should the merge gate decide that a protected-path change may merge? The requester's proposal (part A) changes a documented gate, so I am not accepting it as a plain bug fix. The design doc (lines 21, 23, 48 and 154) asks for a human approval on each PR that touches a protected path. The proposal instead treats approving the spec's Risk list at the spec gate as that approval. The spec gate is the point where the operator signs off a design before any code is written. In this repo 19 of the last 20 merges touched a protected path, so the choice decides whether nearly every merge waits for a human.
1. The approved Risk list is the authorization (the requester's proposal). At merge, the gate refuses any changed protected path that the pinned spec's Risk list does not declare. It names each such path and parks the ticket for a human ruling. A declared path merges with no further approval. The design doc's per-PR gate (lines 21, 23, 48, 154) and reviewer check 6 are reworded to match, with a changelog entry and re-copied prompt files.
2. Build the design as written. Any changed protected path needs a human-signed approval row for that head, whether the spec declares it or not. An undeclared path is also refused. Only the reviewer prompt's wording changes. Nearly every merge in this repo would then wait for the operator.
3. Split by class. Declared paths merge on the Risk approval, as in option 1. But paths that change the factory's own rules (the harness, `.factory/`, prompts) also need a per-head human approval row, as in option 2. The design doc names the classes that need this.

Is the answer a standing decision that later tickets must follow? For example, should every target instance, including the Nanobot fork, use the same rule for protected paths at merge?

Suggested priority (a suggestion only): the requester asks for "first after #41". #41 closed and went live on 2026-10-07 (`dev/issues.md`, runtime `8bfa72d`), so this would be next.

Out-of-scope observations:
- `factory/prompts/reviewer.md` and `docs/prompts/06-code-reviewer.md` differ in one line: line 52 says "After round 2" in one file and "After round {2}" in the other. That is the expected placeholder fill and not a defect. I note it only because a fix for part C re-copies the block.

STATUS: NEEDS-HUMAN
CONFIDENCE: high. I read the gate's code, the design doc's gate text and the T-0028.1 records directly; the conflict between proposal A and design.md lines 21, 48 and 154 is in the text itself.
ESCALATIONS: none
