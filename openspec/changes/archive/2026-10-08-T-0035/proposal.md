## Problem

The factory runs each ticket through a chain of AI agents, each with its own prompt (its "role"). Two of them shape a spec before a human approves it: the **spec writer**, which turns an accepted ticket into a spec, and the **critic**, which reviews that spec against a rubric and either approves it, sends it back once, or escalates to the human.

Issue #73 (merged as `05cf8f9`) gave both roles rules meant to save tokens. The critic got four: a per-claim cap (settle any one claim with at most two file paths and one command), a no-build rule (no clone, worktree or prototype of the change), a no-test-suite rule, and three reading rules (batch independent reads, read only the line range grep found, send long output to a file). On 2026-10-08 the operator replayed three past intakes, tickets the factory had already taken from request to approved spec, with the old and new prompts. The writer's rules cut its tokens by about 37% at the same quality, and the operator accepted them. The critic's rules saved no tokens. They also made it check less, and it missed a real defect on two of the three tickets. One of those defects the old prompt had confirmed with a small experiment in a throwaway git repository, which the no-build rule now forbids.

So the critic as it stands on `main` is a worse reviewer at no saving. The operator decided to take out the per-claim cap and the no-build rule, keep the no-test-suite rule and the reading rules, and leave the writer's rules alone. The runtime, the pinned copy of the harness that actually runs tickets, has not yet picked up #73. It is meant to pick up #73's writer rules and this revert together, so that no live critic runs under the rules the operator rejected.

## Evidence

- Operator's acceptance record, `.factory/answers/T-0034-acceptance-2026-10-08.md` (T-0034 is the ticket that applied #73): "Critic: no token change (0.71→0.72M, 1.0→0.93M, 1.67→1.63M); verified less and missed real findings on two of three. Not accepted." and "Operator's choice: "Writer only: revert critic part first"."
- The request's replay table: on #51 the critic missed the Nanobot `UV_PYTHON_INSTALL_DIR` risk the original prompt found; on #57 it missed the brace-list declaration bug the original confirmed with a scratch git test. The replay files themselves (`eval73/` in another session's scratch directory) were not read for this spec.
- The rules sit in three copies of the critic prompt, identical in this section. `git grep -n 'Ground any one claim'` on `main` (`49ea4c7`) prints `docs/design.md:469`, `docs/prompts/03-spec-critic.md:43` and `factory/prompts/critic.md:43`. The PROCESS section there reads:
  ```
  Spot-check at least 2 cited paths and 1 acceptance command yourself.
  Ground any one claim with at most 2 paths and 1 command. Run no test
  suite and build nothing: no clone, worktree or prototype of the change.
  Pick an acceptance command that runs no test suite, and run it as the
  spec gives it. A claim you could settle only by running a test suite or
  building the change is a finding for the writer, or a question; say
  what you could not check.
  ```
  `git show f25dffe` shows that the #73 commit added these lines (all but the first) and the Turn economy paragraph after them.
- `docs/principles.md:44-45` (principle 2) lists among its mechanisms "the critic's PROCESS section, which runs no test suite and builds nothing (#73, `factory/prompts/critic.md`)". The Spiking section (heading at line 169, paragraph at lines 171-178; from #72, `2e73dbb`) says the critic's grounding is bounded to "two paths, one command" and ends "it does not build". Spiking is the last section of the file (178 lines).
- `git grep` for `at most 2 paths`, `build nothing`, `builds nothing`, `does not build`, `two paths, one command` and `no clone, worktree` finds no hit in `README.md`, `dev/` or `tests/factory/`. So no README text, build-spec text or existing test pins these rules.
- The repository's current truth, the archived requirements that describe it as built, pins the old rule in its `harness-docs` capability, in three requirements: "The spec writer and the critic carry the turn-economy rules" (its scenario expects the cap and no-build phrases, `critic ... doc=6/6`), "Spec writer and critic runs receive the turn-economy rules" (expects `suite=1 cap=1` on the phrase `Run no test suite and build nothing`), and "The documents record the turn-economy change" (expects principle 2 to say `runs no test suite and builds nothing (#73, ...)`). A fourth, "Nothing else in the two prompts changes", says the change MUST NOT remove a line of the critic prompt. This change removes lines, so all four are restated below.
- I prototyped the change in a scratch clone (`scratch/proto`, the edit script `scratch/edit.py`, both in this run's directory) and ran every scenario below on both the base checkout and the prototype, each under a throwaway HOME. Base output is quoted under verification.md; on the prototype every scenario printed its THEN line exactly. On the prototype, `tests/factory/test_writing_standard.py` and `tests/factory/test_coding_standard.py`, which check that each design block equals its `docs/prompts/` copy, printed `10 passed in 2.31s`. The prototype's `git diff --stat main...HEAD` is 5 files, 31 insertions, 20 deletions.

## Root cause

The critic's PROCESS section in `docs/design.md` (the "## 3. Spec critic" block, lines 467-474), `docs/prompts/03-spec-critic.md:42-47` and `factory/prompts/critic.md:42-47` carries the per-claim cap and the no-build sentence #73 added. `docs/principles.md` principle 2 (lines 44-45) and the Spiking section (heading at line 169, paragraph at lines 171-178) describe those rules as the critic's design. Per the replay, the critic's cost is mostly its fixed start-up context, so capping its checks did not lower its cost; it lowered what it found.

## Out of scope

- The spec writer prompt, in all three copies: it stays exactly as #73 left it.
- The critic's rubric, round limit, output format, its minimum spot-check (2 cited paths, 1 acceptance command), its no-test-suite rule, its acceptance-command rule and its three reading rules.
- Any other prompt, `agents/`, the shared preamble, `README.md` (it names none of the removed rules) and `dev/build-harness.spec.md` (likewise).
- `dev/issues.md`'s index row for #74: the operator's own `dev:` commits maintain it.
- Moving the runtime to the merged revision: an operator step after merge, not this change.
- Re-running the replay: an operator step, not acceptance.

## Open questions

none

## Decisions

- This change overturns part of a standing decision, one that later tickets must keep, recorded on 2026-10-08 for T-0034, the ticket that applied #73: "The critic runs no test suite and builds nothing ... Standing: a later change to the critic prompt keeps this rule". The no-test-suite half stands. The no-build half and the per-claim cap (T-0034's other 2026-10-08 decision) are removed. Authority: the operator's choice in `.factory/answers/T-0034-acceptance-2026-10-08.md`. Standing: later changes to the critic prompt keep the no-suite rule and do not re-add a per-claim cap or a no-build rule without new evidence.
- The critic prompt gains one sentence that allows a small experiment in its scratch directory to confirm a finding. Without it, the kept sentence "A claim you could settle only by ... building the change is a finding" reads as the old ban. The kept sentence still covers building or trying out the change itself, which the request's item C (its `docs/principles.md` change) leaves to the writer or to a spike, a ticket built only to test whether an approach works. Rejected: deleting the kept sentence. The triage role, which sorts a request before the spec writer sees it, asked to keep it, and it still tells the critic what to do with a claim it cannot check.
- The no-suite line gains its reason, "the implementer and the verifier run it", as the request's item B (its list of what the critic keeps) gives. `Pick an acceptance command that runs no test suite, and run it as the spec gives it.` and the Turn economy paragraph stay word for word.
- The Spiking section records the replay result, as the request's item C asks ("Record the replay result"). The changelog entry records it too.
- Of the current-truth requirements that #73 added, four are restated (MODIFIED), because each states the rule being removed or forbids removing a critic line. Other current-truth requirements that check the diff of their own change (for example "The documents record the live-store guard", which expects no prompt copy to change) are left as they are, as #73 left them. Their scenarios describe their own change, not standing behaviour.
- "Writer unchanged from #73" is checked as no difference from `05cf8f9` in either writer prompt file, plus the writer's design block equal to its `docs/prompts/` copy. Together these mean the design block is unchanged too.

## Risk

- Blast radius: every critic run after the operator moves the runtime. The critic may spend more turns per review, for example on a scratch experiment. The replay shows the version with no cap and no build ban at about the same token cost. No routing, store, CLI or workflow code changes.
- Protected paths this change touches:
  - `factory/prompts/critic.md` (harness)
  - `docs/prompts/03-spec-critic.md` (generated; re-copied from the design doc block, never edited apart from it)
- Not protected, also changed: `docs/design.md`, `docs/principles.md`, `docs/changelog.md`.

## Operator steps

1. After merge, move the runtime to a revision that holds both `05cf8f9` (#73) and this change, and accept it with `--accept-harness`, as the request's "Then" line says.
2. Optional: re-run the critic replay on #51 and #57 with the merged critic prompt, to confirm it finds the `UV_PYTHON_INSTALL_DIR` risk and the brace-list declaration bug again. The result belongs in the acceptance record, not in this ticket's checks.
3. Update `dev/issues.md`'s #74 row once merged.

