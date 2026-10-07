Type: bug

Title: Merge gate merges protected-path changes the approved spec never declared, and the reviewer prompt promises a check the gate does not run

Summary: The merge gate is the harness's last check before it merges a sub-ticket's branch into `main`. Today it never looks at which files a change touches. So it merges a change to a protected path even when the approved spec never declared that path. A protected path is one listed in the instance's `protected_paths`, such as the harness's own code, `.factory/` and the copied prompts. A reviewer's APPROVE that lists such paths under ESCALATIONS also merges. The operator has ruled how the gate should work, as a standing rule for every instance. The approved spec's Risk list is the authorization. At merge, the gate refuses each changed protected path that the pinned spec's Risk list does not declare, names each one, and parks the ticket for a human ruling. The pinned spec is the version the operator approved at the spec gate. A declared path merges with no further approval. The design doc's per-PR approval text, the reviewer prompt's check 6 and their prompt copies are reworded to match, with a changelog entry. The requester also folds in a routing bug. When a sub-ticket's code reviewer escalates, `resolve --ruling` sends it to the critic. It should go back to its checks, with the ruling in the checkers' input.

Evidence:
- Request: issue #57 (https://github.com/danielphang/spec-factory/issues/57). It comes from part D of #56, an independent review of the harness on 2026-10-05.
- The gate checks no paths. `factory/cli.py` `merge_cmd` (lines 645-687) checks four things: the ticket state; that the recorded head is the branch tip; that the ci, reviewer and verifier rows read PASS, APPROVE and VERIFIED; and that the head contains the integration branch. No line reads the changed paths, `protected_paths` or the spec's Risk list. I re-read it on this run.
- The prompt promises the check. `factory/prompts/reviewer.md` lines 24-27 (check 6) say a reviewer lists protected paths under ESCALATIONS and that "the merge gate will require a human approval". The same text is at `docs/design.md` line 642 and `docs/prompts/06-code-reviewer.md` line 26.
- The design doc asks for a per-PR approval, which the operator's answer replaces. `docs/design.md` line 21 names "a PR touching a protected path" as one of five human gates. Line 23 says a protected-path change "needs a human approval record before it merges". Line 48 (piece 8) says "any other guardrail or protected path needs a human approval on the PR itself". Line 154 says "the merge gate does not merge without it".
- The gap was hit in a real run. On 2026-10-04 T-0028.1 (#48) parked because its reviewer (run-0298) escalated a 3-line change to `factory/store.py`. The approved spec asks for that change in part A.5, but its Risk list does not declare the file. The reviewer noted that no merge check reads the declaration.
- The routing bug is in the code. In `factory/cli.py` `resolve`, the `--ruling` branch (line 872) sends any ESCALATE park whose reason lacks the word "planner" to `ready-for-critic`. That includes a sub-ticket parked by its code reviewer. T-0028.1's ruling had to be placed by hand at `.factory/store/approvals/T-0028.1/ruling-1.md`, followed by `resolve --redispatch`.
- The operator's answer (Answer 1, on the operator's 2026-10-05 approval, relayed by the Green session) chose option 1 and made it standing: "It is harness behaviour, so it applies to every instance, including the Nanobot fork." The same answer leaves one choice open for the spec gate. Option 3 would add a per-head human approval for paths that change the factory's own rules.
- Cost the answer measured: 19 of the last 20 merges here touched a protected path. A per-PR approval would have stopped nearly every merge.
- Duplicate search: none. `dev/issues.md` line 64 lists #57 as "not in intake (first after #41)". #56 (line 63) is the umbrella review it came from. Its other children, #58 to #60, are separate findings. The closed T-0028 and T-0029 tickets added no path check to `merge_cmd`.
- No reference fix: the request names no Nanobot-side commit, so there is no as-built fix to compare against.

Assumptions (my inferences, not the requester's statements):
- "Parent base" means the `main` commit the sub-ticket's branch started from. The gate compares it with the commit it is judging, so changes merged in from `main` are not counted against this ticket.
- The pinned spec is the parent ticket's approved spec version. A sub-ticket gets its protected paths from its parent: when the planner is skipped, `factory/cli.py` line 535 writes "Protected paths: the parent's Risk list." The requester's test "a declaration in a different ticket's spec does not count" fits this reading.
- Some `protected_paths` entries lie outside the repository (`~/dev/nanobot-upstream/**`, `~/.nanobot/**` in `.factory/instance.yaml` lines 14-19). A repository diff can never contain them. The new check covers only the in-repo patterns, and that is not a gap.
- Scope is protected paths only. The existing guardrail rule for tests is a separate check: an existing test may change only when the pinned spec lists it under "Tests to change". This request leaves that rule as it is.
- The new refusal parks the ticket. A human ruling then either accepts the change under the approved design or sends it back. Who acts on each outcome, and how, is left to the spec writer. The fold-in covers only a reviewer ESCALATE on a sub-ticket. A budget-kill park is #41's, as the comment says, and #41 is closed.
- `instance.yaml` and the prompt files are protected paths, so a change to the factory's own rules gets the same check (requester's part D). Whether those paths also need a per-head approval is option 3, which the operator left open for the spec gate.

Reason: ACCEPT. The intent is clear, and the one product call has been answered as a standing rule. Because the fix changes a documented human gate, the spec goes to the operator at the spec gate, as Answer 1 says. The pre-approval policy does not cover it. That spec gate is where option 3 can still be chosen.

Suggested priority (a suggestion only): next. The requester asks for "first after #41". #41 is closed and went live on 2026-10-07 (`dev/issues.md` line 48, runtime `8bfa72d`).

Out-of-scope observations:
- `factory/prompts/reviewer.md` and `docs/prompts/06-code-reviewer.md` differ at line 52: "After round 2" against "After round {2}". This is the expected placeholder fill, not a defect. A fix to check 6 re-copies that block, so I note it here.

STATUS: ACCEPT
CONFIDENCE: high. I re-read the gate and resolve code, the design doc's gate text and the instance config on this run, and the operator's answer settles the one open decision.
ESCALATIONS: none
