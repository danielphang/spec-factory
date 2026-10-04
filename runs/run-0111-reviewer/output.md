Commit: e703c1bfb1216079f802ba25e3d3a218246f385d (branch `factory/T-0013.1`, one commit on base `0759162e`; worktree `.factory/state/runs/run-0111-reviewer/wt`)

## What I checked, in the role's order

1. **Test integrity.** One existing test file changed, `tests/factory/test_instance.py`, and only the test the spec lists under "Tests to change" (`test_system_prompt_is_the_design_preamble_filled_from_the_instance`, diff lines 278-289). The change: finds the index `w` of the `{writing standard}` line, excludes it from the unchanged-lines comparison alongside indexes `0` and `i`, adds an exact-equality assertion on that line (`got[w] == block[w].replace("{writing standard}", str(REPO.resolve() / "docs" / "writing.md"))`, which is stricter than the spec's "contains the path"), and extends the final `not in` check with `"{writing standard}"`. No assertion removed, weakened, skipped or hard-coded. `REPO` in that test is `Path(__file__).resolve().parents[2]` (test_instance.py:17) and `HARNESS` is `Path(__file__).resolve().parent.parent` (factory/instance.py:28), so both sides are resolved paths and the equality is not symlink-fragile. No other test file was touched; `tests/factory/test_writing_standard.py` is new.

2. **Correctness against the spec.**
   - The three inserted prompt texts match the parent spec byte for byte. I extracted the rubric-6 and check-8 fenced blocks from `.factory/state/specs/T-0013/v1.md` and tested substring presence in all three copies of each: `rubric6 ... EXACT` x3, `check8 ... EXACT` x3. The six preamble lines (v1.md:127-132) match `factory/prompts/preamble.md:52-57` line for line (compared by eye after my script mis-parsed the indented fence; the diff hunks for `docs/design.md` and `docs/prompts/00-preamble.md` show the same six lines).
   - `fill_preamble` (factory/instance.py:160-166) replaces `{writing standard}` with `str(HARNESS / "docs" / "writing.md")`; docstring updated; its one caller is `factory/cli.py:218`, so every started run gets the filled line. It does not refuse on a missing file, as the spec says.
   - Role-context paragraph (`docs/design.md:54`) carries both of the spec's B.4 sentences. `dev/build-harness.spec.md:158` names `{writing standard}` and says it is filled from the running checkout, not `instance.yaml`.
   - `docs/writing.md`: 86 lines, 8 rules in the request's order, each with one `Before (` and one `After:`. I verified the four run-sourced Befores against the store (read only): run-0054-planner `output.md` has the uncaptioned "Order and parallelism:" graph (rules 4 and 8), run-0052-spec_writer line 55 has the `old_tracked=0` / `numbering=CONTIGUOUS` outputs quoted bare (rule 5), run-0014-triage line 68 has the `A3: Answer 1's "whole word none"` escalation (rule 6), run-0062-verifier line 50 has the "Stale branch base, which is a harness/process issue" escalation (rule 7). The substituted rule-7 example is real and its source is named, as the parent's Decisions require.
   - Acceptance, every WHEN run from the worktree exactly as written:
     - standard-is-one-page-with-a-pair-per-rule → `lines=86 rules=8 before=8 after=8`
     - preamble-names-the-standard → `standard=[/Users/dphang/dev/spec-factory/.factory/state/runs/run-0111-reviewer/wt/docs/writing.md] unfilled=0 file=present` (the worktree is `pwd -P`); the run's OUTPUT block shows the five new lines with the path filled
     - preamble-line-in-every-copy → `:1` for all three files
     - briefing-template-has-reader-line → `1`
     - rubric-6-widened-in-every-copy → `:0 :0 :0` then `:1 :1 :1`
     - reviewer-check-in-every-copy → `:1` for all three files
     - prompt-copies-verbatim → `00-preamble verbatim`, `03-spec-critic verbatim`, `06-code-reviewer verbatim`, `preamble copies equal`, `critic-diff=2 reviewer-diff=2`; the two differing lines in each are the `{2}` round-limit line only
     - records-name-the-standard → `changelog=1 design=2 buildspec=1 stale=0 row=1`
     - gates-pass → `check=0`; `uv run --frozen pytest -q -p no:cacheprovider tests/factory` → `126 passed in 116.06s`. 126 = the parent's 121 baseline + 5 new tests.

3. **Scope.** Fifteen files changed, all named in the sub-ticket's parts A-F. No edit to `agents/**`, `.factory/**`, `bin/factory`, `pyproject.toml`, `uv.lock`, other prompt blocks, routing or STATUS values. README edits are the two named lines plus the table row; the status-header date already reads 2026-10-03 (README.md:9), so no bump was due. Changelog entry 43 is the next free number (42 was last).

4. **Silent behavior changes.** Every started run's system prompt now carries five more preamble lines and one absolute path into the harness checkout. That is what the spec asks for and the Risk section declares it. Nothing else a caller or service would notice; `fill_preamble` has one caller.

5. **Security and data safety.** None: text and one string replacement; no secrets, no destructive operations, no new inputs.

6. **Protected paths.** All touched paths are declared in the parent's Risk section and the sub-ticket, and authorised by the operator's answer. Listed under ESCALATIONS; the merge gate needs the human approval it already provides for them.

7. **Maintainability.** `tests/factory/test_writing_standard.py::_design_block` (line 61-66) finds the first ```` ```text ```` fence after the heading with a non-greedy `.*?`; it would silently pick up a later section's fence if a heading's section ever lost its own, but all three sections have one and the matching copy check would then fail loudly. Not a problem today.

## Findings

- [NIT] docs/writing.md:751-752 (rule 4, After): the rewrite says ".6 merges last", but its source (run-0054-planner `output.md`, line 18) says .6 is "the last sub-ticket that may touch harness paths", and line 17 says .5 may run in parallel with .6. The caption on the next line ("Part E (.6) is the last change to harness code") is the accurate claim. → A reader of the example could take "merges last" literally and conclude .5 had to precede .6, which the plan does not require. Consequence is confined to an illustrative example in a style page; "merges last among the harness changes" or dropping the clause fixes it.

No BLOCKING or SHOULD-FIX findings.

Prior findings: n/a, round 1.

STATUS: APPROVE
CONFIDENCE: high. Every acceptance command and both gate commands were run on the committed head in the worktree and gave the spec's expected output; the three prompt insertions were compared to the approved spec text byte for byte; the four run-sourced Before examples were located in the store.
ESCALATIONS:
- Protected and guardrail paths touched, every one declared in the parent's Risk section and the sub-ticket (operator-authorised; merge gate requires the human approval): harness `factory/instance.py`, `factory/prompts/preamble.md`, `factory/prompts/critic.md`, `factory/prompts/reviewer.md`, `factory/context.template.md`; generated `docs/prompts/00-preamble.md`, `docs/prompts/03-spec-critic.md`, `docs/prompts/06-code-reviewer.md`; guardrail agent prompts, the preamble, critic and code-reviewer blocks in `docs/design.md`; guardrail existing test, the one listed test in `tests/factory/test_instance.py`.
- No undeclared protected path touched. No prompt-injection content in the input.
