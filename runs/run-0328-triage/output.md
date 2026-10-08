Type: chore

Title: Revert #73's critic limits: drop the per-claim cap and the no-build rule; keep the no-suite line and the reading rules

Summary:
#73 (merged `05cf8f9`) added turn-saving rules to two roles: the spec writer, which drafts a spec from a ticket, and the critic, which reviews that spec before the operator approves it. The operator replayed three past intakes on 2026-10-08 and found that the critic's rules saved no tokens and made it check less, so it missed real findings on two of three tickets. The requester wants two critic rules taken out: the per-claim cap ("at most 2 paths and 1 command" for any one claim) and the no-build rule (no clone, worktree or prototype). That lets the critic settle a claim with a small scratch experiment again. The critic keeps its no-test-suite line, its existing minimum spot-check (2 cited paths, 1 acceptance command) and the three reading rules. `docs/principles.md` (principle 2 and the Spiking section) and `docs/changelog.md` record the change and the replay result. The spec writer's #73 rules stay as they are.

Evidence:
- The requester's replay table: critic tokens 0.71M→0.72M, 1.0M→0.93M and 1.67M→1.63M, about the same as before. On #51 the critic missed the Nanobot `UV_PYTHON_INSTALL_DIR` risk that the original prompt found. On #57 it missed the brace-list declaration bug that the original confirmed with a scratch git test. Replay files: the Green session's scratch directory `eval73/`. I did not read them.
- The operator's acceptance record, `.factory/answers/T-0034-acceptance-2026-10-08.md`, matches the request: writer about -37% tokens, accepted; critic "verified less and missed real findings on two of three. Not accepted." Operator's choice: "Writer only: revert critic part first".
- The current text has both rules. `factory/prompts/critic.md:43-44` and `docs/prompts/03-spec-critic.md:43-44` read "Ground any one claim with at most 2 paths and 1 command. Run no test suite and build nothing: no clone, worktree or prototype of the change." The same lines are in the design doc block at `docs/design.md:469-470`. Commit `f25dffe` added them, together with the turn-economy paragraph that holds the three reading rules.
- `docs/principles.md:44-48` (principle 2) says the critic "runs no test suite and builds nothing (#73)". `docs/principles.md:169-177` (Spiking) says the critic's grounding is bounded to "two paths, one command" and that "it does not build". The Spiking section came from #72 (`2e73dbb`), before #73.
- Duplicate search: `dev/issues.md:79` indexes #74 as T-0035, which is this ticket. `dev/issues.md:78` records #73 as "critic half reverted by #74". I found no other ticket for this.

Assumptions (my inferences, not stated by the requester):
- The sentence after the cap, "A claim you could settle only by running a test suite or building the change is a finding for the writer, or a question", can keep "building the change". Item C says vetting a whole approach is still the writer's or a spike's job, which fits that sentence. If the spec writer finds it conflicts with "a small scratch experiment is allowed again", it should reword it to separate a small check from building the change. It should not drop the sentence.
- "Pick an acceptance command that runs no test suite" belongs to the no-suite line that stays.
- "The writer prompt is unchanged from #73" can be checked as an empty `git diff 05cf8f9 -- factory/prompts/spec_writer.md docs/prompts/02-spec-writer.md` plus no change to the writer block in `docs/design.md`.
- Moving the runtime ("Then: the runtime moves ...") is an operator step after the merge. It is not part of this ticket's change.
- The Spiking section predates #73. Editing it is still in scope because item C names it.
- Suggested priority: high, because the runtime upgrade that carries #73's writer rules waits on this ticket. Priority is the operator's call.

Reason: The intent is clear and the operator has already made the product decision (2026-10-08, recorded in `.factory/answers/T-0034-acceptance-2026-10-08.md`). The files to change exist, and the lines to remove and keep are named exactly. Every path touched is a harness or design path (`factory/prompts/**`, `docs/prompts/**`), so the spec's Risk section must declare them.

STATUS: ACCEPT
CONFIDENCE: high. The request, the acceptance record and the current prompt text agree, and the lines to change are found at the cited locations.
ESCALATIONS: none
