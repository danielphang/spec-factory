## Proposed change

The paragraph, wrapped as a bullet at 72 columns, is exactly:

```
- Turn economy: every turn re-sends everything read so far, so a
  wasted turn or a long printout costs again on every later turn. Put
  independent reads and commands in one turn. Once grep has found the
  lines you need, read that line range, not the whole file. Send long
  output to a file in your scratch directory and grep or tail it,
  rather than printing it in full.
```

A. Implementer and verifier. In `factory/prompts/implementer.md`, `docs/prompts/05-implementer.md` and the "## 5. Implementer" block of `docs/design.md`, insert the paragraph as a RULES bullet directly before the bullet `- A protected path the sub-ticket declares is not an escalation: the`. Do the same in `factory/prompts/verifier.md`, `docs/prompts/07-verifier.md` and the "## 7. Verifier" block.

B. Code reviewer. In `factory/prompts/reviewer.md`, `docs/prompts/06-code-reviewer.md` and the "## 6. Code reviewer" block, insert the paragraph as the last bullet of WHAT YOU RUN, after the line `  one test or a grep, and cite its output with that finding.`

C. Planner and triage. In `factory/prompts/planner.md`, `docs/prompts/04-planner.md` and the "## 4. Planner / decomposer" block, insert it as the last RULES bullet, after `  siblings to re-verify, so parallel sub-tickets are not free.` In `factory/prompts/triage.md`, `docs/prompts/01-triage.md` and the "## 1. Triage" block, insert it as the last RULES bullet, after `  When unsure between ACCEPT and CLARIFY, choose CLARIFY.` In the run copy, that puts it before the blank line and the "Acceptance items describe behaviour" block.

D. Changelog. Add entry `64. After issue #76 (2026-10-09), ...` directly after entry 63 and before the closing "Declined:" line of `docs/changelog.md`. It says that the implementer, verifier, code reviewer, planner and triage prompts gain #73's three reading rules in the critic's form, without the spec writer's one-write sentence. It cites the #74 replay result (entry 59), says nothing else in the prompts changes and the hook stays with #65, says the runtime moves only after the operator's replay of implementer and verifier runs, and records the rejected preamble line.

The prototype touched 12 files with 91 added lines and none removed.

## Tests to change

none

