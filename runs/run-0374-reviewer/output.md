Commit: a86d154a75c6545d91f87cc79a007d2fe16e5df3 (branch `factory/T-0039.1`, base `b002c95b18b3cd1dad4329cdc4e13b6fe71b18af`)

## What I checked

1. Test integrity. The diff touches one test file, `tests/factory/test_turn_economy.py`, and it is new (`new file mode 100644`). No existing test, CI config, `AGENTS.md`, skill or agent prompt changes. The parent's "Tests to change" is `none`, so nothing was allowed to change and nothing did. `git diff --stat b002c95...a86d154`: `13 files changed, 212 insertions(+)`, no deletions.

2. Correctness against the spec's Proposed change.
   - The bullet text in every one of the twelve document and prompt hunks is the six lines the spec gives, byte for byte, including the two-space continuation indent and the 72-column wrap.
   - Part A: in `factory/prompts/implementer.md:44-49`, `docs/prompts/05-implementer.md:43-48`, `factory/prompts/verifier.md:34-39`, `docs/prompts/07-verifier.md:33-38` and the two design blocks, the bullet sits directly before `- A protected path the sub-ticket declares is not an escalation: the`, so the declared-path bullet stays last under RULES.
   - Part B: in `factory/prompts/reviewer.md:11-16`, `docs/prompts/06-code-reviewer.md:11-16` and the design block, it is the last bullet of WHAT YOU RUN, after `  one test or a grep, and cite its output with that finding.`, before the blank line and `CHECK, IN THIS ORDER`.
   - Part C: planner copies put it after `  siblings to re-verify, so parallel sub-tickets are not free.` as the last RULES bullet. Triage copies put it after `  When unsure between ACCEPT and CLARIFY, choose CLARIFY.`; in `factory/prompts/triage.md:29-34` that is before the blank line and the instance-added "Acceptance items describe behaviour" block, as the spec requires.
   - Design-doc placement: I ran `awk '/^## /{h=$0} /^- Turn economy:/{print NR": "h}' docs/design.md` on the head. Output: `303: ## 1. Triage`, `384: ## 2. Spec writer`, `553: ## 4. Planner / decomposer`, `638: ## 5. Implementer`, `676: ## 6. Code reviewer`, `771: ## 7. Verifier`. The five added bullets each sit under the block the spec names; the line-384 hit is the spec writer's pre-existing #73 bullet, not part of this diff.
   - Part D: `docs/changelog.md:69` is entry 64, after entry 63 and before the `Declined:` line. It names #76 and the date, the five roles, the critic's form, the omitted one-write sentence, the placement, the #74 replay (entry 59) including the critic result, "Nothing else in the five prompts changes", the hook staying with #65, the runtime moving only after the operator's replay, and the rejected preamble line. Every item the spec's Part D lists is present.
   - The `docs/prompts/04-planner.md` and `factory/prompts/planner.md` blobs share the same before and after hashes (`9736991..53fa741`), as they should: the planner's run copy had no instance fill on `main`.

3. Scope. Thirteen files: the twelve the spec's prototype counted (91 added lines, matching the spec's "12 files with 91 added lines and none removed") plus the new test file (121 lines). Nothing outside parts A-D.

4. Silent behaviour changes. None in code. The harness sends the run copies verbatim, so every future run of the five roles reads one more bullet; that is the change the spec asks for, and the spec's Risk section and Operator step 1 own the question of whether the roles then read too little. Nothing reaches live runs until the operator moves the runtime.

5. Security and data safety. The new test builds a throwaway git target under `tmp_path_factory` and a throwaway store via `FACTORY_STATE`, strips the inherited factory environment (`STRIP`), and writes nothing outside `tmp`. No credentials, no absolute paths outside the repository.

6. Protected paths. The ten prompt files the diff touches are exactly the ten the parent's Risk line declares. Listed under ESCALATIONS for the record, per the implementer's rule and check 6.

7. Coding standard. The new test file copies `REPO`, `BIN`, `STRIP`, `FENCE`, a `_cli` wrapper and a `_design_block` regex helper that `tests/factory/test_coding_standard.py:18-31,72` and `tests/factory/test_writing_standard.py:63` already define privately. I checked `tests/factory/conftest.py`: it exports no shared helper, and six test files each carry their own copy (`grep -lE '^STRIP = |^def _cli' tests/factory/*.py | wc -l` → `6`). The repo's standing pattern is a self-contained test module; the only way to reuse would be to import private names from a sibling test module or to add a conftest helper, which this sub-ticket does not ask for. I record it as a NIT, not a `reuse:` BLOCKING, because no importable helper exists on `main`.

8. PR description. What changed opens with the problem and the five roles, glosses "role" and the three prompt copies at first use, and states the placement in words before the file list. Known gaps names the live-model risk and what the fixture does and does not show. One gap against the coding standard's rule 3: Known gaps does not say "factory: markers added: none" (none were added; the diff has no `factory:` comment).

## Findings

- [SHOULD-FIX] PR description: Known gaps: the section does not state `factory: markers added: none`, which coding standard rule 3 requires of every PR description → the operator at the gate cannot tell from the prose whether a deliberate shortcut was recorded or forgotten. One line fixes it; the diff itself has no `factory:` comment, so no code change is needed.
- [NIT] tests/factory/test_turn_economy.py:54-57,85-90,113-117: `REPO`, `BIN`, `STRIP`, `FENCE`, `_cli` and `_design_block` repeat the private helpers of `tests/factory/test_coding_standard.py:18-31,72` and `tests/factory/test_writing_standard.py:63` → a change to how tests reach `bin/factory` or parse a design block must be made in a seventh place. The repo has no shared helper to call today, so this follows the suite's existing pattern; lifting the six copies into `tests/factory/conftest.py` is a separate cleanup, not this ticket.

net: 0 lines possible within this ticket (no shared helper exists on `main` to call; a conftest lift would be a new ticket).

## Prior findings

none (round 1).

## Out-of-scope observations

- Six test modules now carry the same `cli`/`_design_block` boilerplate. A shared `tests/factory/conftest.py` helper would remove about 20 lines per file. Not this ticket.
- `docs/principles.md` principle 13's "Implemented by" line still credits the reading rules to #73 only; the spec leaves it to the operator.

STATUS: APPROVE
CONFIDENCE: high. Every added hunk is the spec's six lines at the spec's anchor, confirmed by reading the diff and by an awk pass over the head's `docs/design.md`; no existing test or line changed; the only finding is a missing one-line rule-3 statement in the PR prose.
ESCALATIONS: Protected paths touched, all declared in the parent's Risk line and listed for the record: `factory/prompts/implementer.md`, `factory/prompts/verifier.md`, `factory/prompts/reviewer.md`, `factory/prompts/planner.md`, `factory/prompts/triage.md`, `docs/prompts/05-implementer.md`, `docs/prompts/07-verifier.md`, `docs/prompts/06-code-reviewer.md`, `docs/prompts/04-planner.md`, `docs/prompts/01-triage.md`. No undeclared protected path is touched.
