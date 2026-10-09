Sub-ticket: T-0039.1 (parent T-0039, approved spec v2: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0039/v2.md`)
Branch: `factory/T-0039.1`, commit `a86d154` on base `b002c95`. Worktree: `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0039.1`.

## What changed

Five of the factory's seven role prompts now carry the reading rules that the spec writer and critic already had. The five are triage, planner, implementer, code reviewer and verifier. A role is one step of a ticket, run as a separate model agent and steered by its own prompt. The rules tell an agent to batch independent reads, read only the line range a search found, and send long command output to a file in its per-run scratch directory instead of printing it. Every turn re-sends everything read so far, so these rules cut the tokens a run uses. The text added is the critic's six-line "Turn economy" bullet, word for word, and nothing else. No existing line changed.

Each prompt exists in three copies: a block in `docs/design.md`, a verbatim copy under `docs/prompts/`, and the run copy under `factory/prompts/` that the harness sends. All three copies changed in the same way.

- A. Implementer and verifier. The bullet sits in RULES, directly before the bullet `- A protected path the sub-ticket declares is not an escalation: the`, so that bullet stays last. Files: `factory/prompts/implementer.md`, `docs/prompts/05-implementer.md`, `factory/prompts/verifier.md`, `docs/prompts/07-verifier.md`, and the "## 5. Implementer" and "## 7. Verifier" blocks of `docs/design.md`.
- B. Code reviewer. The bullet is the last bullet of WHAT YOU RUN, after `  one test or a grep, and cite its output with that finding.` Files: `factory/prompts/reviewer.md`, `docs/prompts/06-code-reviewer.md`, and the "## 6. Code reviewer" block.
- C. Planner and triage. The bullet is the last RULES bullet in each. For the planner it follows `  siblings to re-verify, so parallel sub-tickets are not free.`, and for triage it follows `  When unsure between ACCEPT and CLARIFY, choose CLARIFY.` In the triage run copy that puts it before the blank line and the instance-added "Acceptance items describe behaviour" block. Files: `factory/prompts/planner.md`, `docs/prompts/04-planner.md`, `factory/prompts/triage.md`, `docs/prompts/01-triage.md`, and the "## 4. Planner / decomposer" and "## 1. Triage" blocks.
- D. Changelog. Entry 64 of `docs/changelog.md` sits after entry 63 and before the closing "Declined:" line. It names #76 and the five roles. It says they gain the critic's form of the rules, without the spec writer's one-write sentence. It cites the #74 replay result (entry 59), says nothing else in the prompts changes, and leaves the enforcing hook with #65. It says the runtime moves only after the operator's replay of implementer and verifier runs. It also records the rejected option of a shared preamble line.

The diff is 13 files with 212 added lines and none removed. 91 of those lines are in the 12 document and prompt files, which matches the spec's prototype, and 121 are in the new test file.

Protected paths touched, all declared in the parent's Risk line: `factory/prompts/implementer.md`, `factory/prompts/verifier.md`, `factory/prompts/reviewer.md`, `factory/prompts/planner.md`, `factory/prompts/triage.md`, `docs/prompts/05-implementer.md`, `docs/prompts/07-verifier.md`, `docs/prompts/06-code-reviewer.md`, `docs/prompts/04-planner.md`, `docs/prompts/01-triage.md`.

## Acceptance results

Every command ran from the worktree root after `uv sync --frozen`, inside the wrapper (a fresh temporary HOME). I also set `TMPDIR` to this run's scratch directory, so the `${TMPDIR}/t0029-prompt.sh` fixture and every `mktemp -d` landed there. The fixture is the GIVEN block of "Implementer and verifier run prompts carry the declared-path rule" in current truth (`.factory/store/openspec/specs/role-escalations/spec.md`, lines 12-33). I ran it once before each pass. Full logs: `scratch/acc-before.txt` and `scratch/acc-after.txt` under the run directory.

- The five role prompts carry the critic's reading paragraph in every copy (NEW).
  - Before: each line printed `<role> copy=SAME doc=0 run=0 writes=0 fill=unchanged`, as the verification predicted. No copy carried the paragraph.
  - After: `triage copy=SAME doc=1 run=1 writes=0 fill=unchanged`, with the same line for planner, implementer, reviewer and verifier. Each design block still equals its `docs/prompts/` file. Each documented copy and each run copy carries the paragraph once. Neither carries "as few writes as you can". Each run copy differs from its documented copy only where it did on `main`.
- Only the paragraph is added, and no other prompt changes (REGRESSION). After: `extra=0 deleted=0 others=0`. Nothing but the paragraph was added to the ten files, no line was removed from them or from `docs/design.md`, and no other prompt or agent file changed. It printed the same on base.
- Implementer, reviewer and verifier runs receive the reading paragraph (NEW).
  - Before: `implementer preamble=1 economy=0 writes=0`, and the same for reviewer and verifier.
  - After: `implementer preamble=1 economy=1 writes=0`, `reviewer preamble=1 economy=1 writes=0`, `verifier preamble=1 economy=1 writes=0`. Each run started (`preamble=1`) and its system prompt carries the paragraph once.
- Triage and planner runs receive the reading paragraph (NEW).
  - Before: `triage preamble=1 economy=0 writes=0`, then `planner preamble=1 economy=0 writes=0`.
  - After: `triage preamble=1 economy=1 writes=0`, then `planner preamble=1 economy=1 writes=0`.
- The changelog records the reading rules for the five roles as its last entry (NEW).
  - Before: `63 CONTIGUOUS`, then `terms=2 footer=1`.
  - After: `64 CONTIGUOUS`, then `terms=7 footer=1`. The entries are numbered 1 to 64 with no gap. The last entry names all seven terms: #76, the five roles and the replay. The file still ends on the "Declined:" line.
- The reading-rules change adds no whitespace errors (REGRESSION). After: `exit=0`.

Gates, each run once on `a86d154` exactly as written in the input:
- `(export HOME=...; git diff --check main...HEAD)`: no output, rc=0.
- `(export HOME=...; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`: `418 passed in 283.33s`, rc=0. The log is `scratch/suite.txt`. uv printed a warning that the inherited `VIRTUAL_ENV` was ignored in favour of the project `.venv`, which is the intended interpreter.

## Tests added/changed

- Added `tests/factory/test_turn_economy.py`, a new file with 10 cases.
  - `test_every_copy_carries_the_bullet_once_at_its_place[<role>]`, once per role. It checks three things. The design block equals the `docs/prompts/` file. Both the documented copy and the run copy hold the six-line bullet exactly once, next to the anchor line the spec gives. Neither copy contains "as few writes as you can".
  - `test_a_run_of_the_role_receives_the_paragraph_once[<role>]`, once per role. It starts a real run of each role through `bin/factory` on a scratch target with a throwaway store. It then checks that the system prompt holds the preamble and the joined paragraph exactly once, and not the one-write sentence.
  - Why: the spec's acceptance commands are shell one-liners that live in the spec, and nothing in the suite would catch it if a later change dropped or moved the bullet.
  - Red then green: I stashed the prompt changes and ran the file on base. All 10 cases failed: the bullet was not found, and the run prompts did not contain the paragraph. With the change, all 10 passed.
- No existing test changed. The parent's "Tests to change" list is empty.

## Known gaps and uncertainties

- None of this shows that the roles still work as well with the rules. The spec names that risk: a verifier that tails a suite log and misses a failure printed earlier. Checking it is Operator step 1, a replay of past implementer and verifier runs with the old and new prompts. It needs live model runs, which this run cannot do.
- The new test's run-prompt fixture moves one ticket through each role's starting status with `ticket set`, including `in_flight=[]`, as `test_coding_standard.py` does. It does not drive real transitions. That is enough to show what each role's prompt contains, but it says nothing about routing.
- I set `TMPDIR` to the scratch directory in addition to the wrapper's fresh HOME, so the fixture's absolute `${TMPDIR}` path stayed inside this run's scratch directory. The commands are otherwise unchanged.

## Out-of-scope observations

- `docs/principles.md` principle 13's "Implemented by" line still credits the reading rules to #73 only. The spec leaves that line to the operator, so I did not change it.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. All six acceptance scenarios match the spec's before and after outputs, the new tests fail on base and pass on the change, and the full suite passes (418).
ESCALATIONS: none
