Sub-ticket: T-0015.1, "Add the coding standard and point the implementer, reviewer, spec writer, critic and retro at it" (parent T-0015, issue #20, approved spec v2). Branch `factory/T-0015.1`, head `27d6d63fcb2f5c03d64696f6769abf871e4f2bc0`, base `61d92bef32d05c89bb9187f8455f4eb298b2a99f`, one commit. Worktree `/Users/dphang/dev/spec-factory/.factory/state/worktrees/T-0015.1`.

## What changed

The factory's two coding roles now get a coding standard, a page that tells them how to keep a change as small as the ticket allows. The implementer is the agent that writes the code for one sub-ticket. The code reviewer is the agent that judges that code before it merges. Before this change, neither role's prompt named any coding standard. A smaller rule tells the spec writer to cut parts the ticket does not need. The retro is the planned agent that proposes prompt changes. Its design now lists `factory:` comments as one of its inputs. 17 files, 235 lines added and 15 removed (`git diff --stat main...HEAD`).

- **A. The page.** `docs/coding.md` is new. Its text is byte-identical to the block in the parent's part A: `diff` of the spec block against the file printed nothing. It opens with a precedence rule: a target repository's own instructions win where they disagree with the page. It then has five rules, each with a `Check:`, `Principle:`, `Before (` and `After:` line. The five rules are reuse before writing, grep every caller, `factory:` shortcut markers, tagged review findings, and one name per concept.
- **B. Pointer lines.** Implementer step 4 keeps its sentence and gains `Follow the coding standard at {coding standard}.` Code reviewer check 7, "Maintainability, only where it will cause real problems. Not style.", is replaced by a check against the coding standard, with the tag and severity the page gives. Each edit is in all three copies: `docs/design.md`, `docs/prompts/` and `factory/prompts/`.
- **C. The harness fills the path.** `{coding standard}` is a placeholder that the harness must replace with a real path when a run starts. `factory/instance.py` gains `fill_standards(text)`. It replaces `{writing standard}` and `{coding standard}` with the absolute paths of `docs/writing.md` and `docs/coding.md` in the running harness checkout. `fill_preamble` now calls it in place of its own `{writing standard}` line. `run_start` in `factory/cli.py` now passes the role prompt through it before appending it to the preamble. Before this change, the role prompt was appended unfilled. `fill_preamble` has one caller, `factory/cli.py:218` (`grep -rn fill_preamble --include='*.py' --include='*.js' .`). After the change the only placeholders in `factory/prompts/` are the two coding-standard lines and the preamble's writing-standard line.
- **D. Spec-stage cut.** The spec writer's RULES gain "Cut before you specify…" directly after the Size rule. Critic rubric 3 ends "…; a lettered part the ticket's intent does not need is a finding." Each edit is in all three copies.
- **E. The marker ledger, text only.** The marker ledger is the retro's planned list of every `factory:` comment in the code. It is now named in three places: the retro's INPUT block (`docs/design.md` §8, re-copied to `docs/prompts/08-retro.md`), the Routing table's Retro row, and the build spec's `retro-input` sentence and item 66. No code builds the ledger yet.
- **F. Records and test.** Three records now say how `{coding standard}` is filled: `docs/design.md`'s role-context paragraph, `dev/build-harness.spec.md`'s placeholder sentence and changelog entry 44. Entry 44 sits after 43 and before "Declined:", and it credits ponytail. `README.md` gains one row after the `docs/writing.md` row. The new test file is `tests/factory/test_coding_standard.py`.

The edits were applied by a script that refused to change a file unless its anchor text occurred exactly once. No edit was placed by line number.

## Acceptance results

The commands were run verbatim from the worktree on its branch. The "before" results come from the worktree at `61d92be`, before any edit, and match the spec's "today" results. The "after" results come from committed head `27d6d63`.

| # | Scenario | Before | After |
|---|---|---|---|
| 1 | coding-page-has-five-checkable-rules (NEW) | `missing` | `rules=1,2,3,4,5 check=5 principle=5 before=5 after=5 precedence=first` |
| 2 | coding-page-has-every-requested-phrase (NEW) | 13 `missing: …` lines, `found=0 of 13` | only `found=13 of 13` |
| 3 | tag-table-severities (NEW) | `reuse= stdlib= native= yagni= delete= ` | `reuse=BLOCKING stdlib=SHOULD-FIX native=SHOULD-FIX yagni=SHOULD-FIX delete=SHOULD-FIX ` |
| 4 | pointer-line-in-every-copy (NEW) | six lines end `:0`, the last three `:1` | six lines end `:1`, the last three `:0` |
| 5 | implementer-and-reviewer-prompts-name-the-page (NEW) | `implementer standard=[] unfilled=0`, `reviewer standard=[] unfilled=0`, `file=absent` | `implementer standard=[/Users/dphang/dev/spec-factory/.factory/state/worktrees/T-0015.1/docs/coding.md] unfilled=0`, the same path for `reviewer`, `file=present` |
| 6 | cut-rule-and-probe-in-every-copy (NEW) | six lines `:0` | six lines `:1` |
| 7 | marker-ledger-named-in-design-and-build-spec (NEW) | `design=0 retro=0 buildspec=0 row=0` | `design=2 retro=1 buildspec=2 row=1` |
| 8 | changed-blocks-verbatim-and-harness-copies-in-step (REGRESSION) | five `verbatim` lines, then `spec_writer-diff=6 critic-diff=2 implementer-diff=5 reviewer-diff=2` | the same |
| 9 | records-name-the-coding-standard (NEW) | `changelog=0 design=0 buildspec=0 row=0` | `changelog=1 design=3 buildspec=1 row=1` |
| 10 | gates-pass (REGRESSION) | `check=0`, `126 passed in 101.27s` | `check=0`, `131 passed in 83.81s` |
| 11 | the new test file on its own (NEW) | see below | `5 passed in 0.36s` |

What each result means:
- Row 5 shows that both live prompts carry the absolute path of the checkout they ran from, with no placeholder left.
- Row 8 shows that every changed design block still equals its `docs/prompts/` copy byte for byte. Each `factory/prompts/` copy still differs from it only in the placeholders the harness already fills.
- Row 10: the suite count rose from 126 to 131, which is exactly the five new tests.

Criterion 11 also asks that the new tests fail where the change is missing. I ran them in two states:
- **Pages and pointer lines in place, harness fill not yet written** (parts A and B, without C). This was the real red step of this ticket, and the failure is the one the spec names. The two prompt-path tests failed because the prompt still held `{coding standard}`, so `Follow the coding standard at <checkout>/docs/coding.md.` was not in the implementer's prompt (`2 failed, 3 passed`).
- **`main`'s files.** I made a scratch clone of `main` at `61d92be` in my scratchpad, outside the repo, and copied in only the new test file. The two prompt-path tests failed on `assert (True and False)`, because `docs/coding.md` does not exist there (`2 failed, 3 passed`). I deleted the clone afterwards.

Both gate commands, run exactly as written from the worktree: `git diff --check main...HEAD` exited 0, and `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `131 passed`.

## Tests added/changed

- Added `tests/factory/test_coding_standard.py`, a new file. It drives `bin/factory` in a scratch target repository on a throwaway store, as `test_writing_standard.py` does.
  - `test_run_prompt_names_the_running_checkouts_coding_standard[implementer|reviewer]` (2 tests). These check the spec's first bullet. Each run's system prompt contains the filled pointer line with the absolute path of the running checkout's `docs/coding.md`, the file exists and is not empty, and no `{coding standard}` is left. The ticket's status is set with `ticket set` so that each role can start, as in scenario 5.
  - `test_changed_design_block_equals_its_prompt_copy[2. Spec writer|5. Implementer|8. Retro]` (3 tests). These check the spec's second bullet: the three changed design blocks that `test_writing_standard.py` does not already cover equal their `docs/prompts/` copies.
- Changed: none. No existing test file was touched (`git diff --stat main...HEAD -- tests/` lists only the new file). `test_design_block_equals_its_prompt_copy` and `test_system_prompt_is_the_design_preamble_filled_from_the_instance` pass unchanged.

## Known gaps and uncertainties

- **The three block-equality tests pass on `main`.** They are regression guards, like the existing `test_design_block_equals_its_prompt_copy`. Each one fails only if a future edit changes a design block without re-copying it. Criterion 11 requires only the prompt-path tests to fail on `main`, and they do. A strict reading of "a test that passes on `main` checks nothing" would flag these three. The spec's part F asks for them anyway, so I kept them and am saying so here.
- **The new README row describes the system before it runs.** The row says the two prompts "name the runtime's copy". The runtime is the pinned checkout that runs every ticket, and that statement holds only after the operator moves it to this merge and accepts it (the parent's Operator step 1). The README's "Ground truth only" rule says a thing appears above "Where this can go" only after it has run on a real ticket. The existing `docs/writing.md` row has the same timing. The spec asks for this row in this ticket, so I added it as specified. The README's status date is already 2026-10-03, so no date bump was needed.
- **Backticks in the Routing table's Retro row.** The spec quoted the appended text inside backticks that also contain backticked `factory:` and `no-trigger`. I read the outer backticks as quotation marks and kept the inner ones as code formatting. Scenario 7 does not depend on this choice.
- **Changelog entry 44's wording is mine.** The spec lists what the entry must say, not its text. It names `docs/coding.md`, the precedence rule, the five rules, the tags and their severities, both pointer lines, the `{coding standard}` fill, the removal of check 7's old text, the cut rule and the critic's probe, the marker ledger as design only, and ponytail (DietrichGebert/ponytail, MIT).
- **Not verified here: live behaviour.** The parent leaves two questions to the operator: whether a live reviewer tags its findings, and whether a live implementer guards a shared function (Operator steps 0 and 2). No running agent sees this change until the runtime moves (Operator step 1).
- factory: markers added: none.

## Out-of-scope observations

- None beyond the parent's own list: the drifted `agents/` templates, the unbuilt `render` command described at `dev/build-harness.spec.md:158`, the `ensure_gitignore` duplication in `factory/store.py`, and changelog entry 43's "eight rules". This change adds the two further `agents/` drifts the parent predicted: the spec writer's cut rule and the critic's probe.
- This repository has no `AGENTS.md` at its root, so step 1 of my process had none to read. That is consistent with the briefing, which names `README.md` as the current-state page.

## Responses to findings

Round 1: none.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. All 11 acceptance criteria and both gates were run on the committed head and printed the expected results. The new prompt-path tests were seen to fail both without the harness fill and on `main`.
ESCALATIONS: none
