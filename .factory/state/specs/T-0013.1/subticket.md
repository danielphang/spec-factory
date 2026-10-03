### ST-1 / Writing standard, the preamble line that points every role to it, critic rubric 6 widened, reviewer check 8, briefing reader line

Parent: `.factory/state/specs/T-0013/v1.md` (T-0013, issue #23). Read it for context. Do NOT implement parts outside this sub-ticket.

Depends on: none

Parallel-safe: yes. It is the only sub-ticket. It does edit `docs/design.md`, `docs/changelog.md`, `README.md`, `factory/prompts/*` and `tests/factory/test_instance.py`. Any other ticket in flight on those files has to re-verify after this one merges, and this one after it.

Scope: parts A, B (B.1 to B.5), C, D, E and F. That is all of the parent's Proposed change:
- A: new `docs/writing.md`. It has eight rules in the request's order. Each rule has one sourced Before and one After, taken from real factory text. Where the `checks-in-flight` escalation example could not be found, use another real one and name its source.
- B: the preamble line with `{writing standard}`, written in `docs/design.md` §Shared preamble and re-copied to `docs/prompts/00-preamble.md` and `factory/prompts/preamble.md`. `fill_preamble` in `factory/instance.py` (function at line 160; `HARNESS` at line 28) fills the placeholder and its docstring is updated. Also two edits to the role-context paragraph in `docs/design.md` (line 54), and `{writing standard}` added to the placeholder list in `dev/build-harness.spec.md` line 158.
- C: critic rubric item 6 (`docs/design.md:381-393`) replaced with the parent's exact text. Re-copy it to `docs/prompts/03-spec-critic.md` and apply it to `factory/prompts/critic.md`, which keeps its literal `2`.
- D: code-reviewer CHECK item 8 added after item 7 (`docs/design.md:530-545`). Re-copy it to `docs/prompts/06-code-reviewer.md` and apply it to `factory/prompts/reviewer.md`.
- E: the reader bullet in `factory/context.template.md`, after the "What kind of request to expect" bullet (line 13).
- F: changelog entry 43, or the next free number. Two README edits: the line at 392-393 and a new row after `docs/prompts/` at line 348; bump the status-header date if the day has changed. The one changed test. A new `tests/factory/test_writing_standard.py`.

Acceptance (every WHEN runs from `~/dev/spec-factory`, exactly as the parent writes it):
- **standard-is-one-page-with-a-pair-per-rule**, NEW.
  - WHEN: `if [ -f docs/writing.md ]; then echo "lines=$(grep -c '' docs/writing.md) rules=$(grep -c '^## [0-9]' docs/writing.md) before=$(grep -c '^Before (' docs/writing.md) after=$(grep -c '^After:' docs/writing.md)"; else echo missing; fi`
  - THEN: one line with `lines` below 120, `rules` at least 8, and `rules`, `before` and `after` equal.
- **preamble-names-the-standard**, NEW.
  - WHEN: the parent's bash one-liner, which starts at `H=$(pwd -P); T=$(mktemp -d); …`, copied verbatim. It sets up a scratch target and a throwaway store, starts one triage run, and greps that run's `system-prompt.txt`.
  - THEN: `standard=[<checkout>/docs/writing.md] unfilled=0 file=present`.
- **preamble-line-in-every-copy**, NEW.
  - WHEN: `grep -c 'the writing standard at {writing standard}' docs/design.md docs/prompts/00-preamble.md factory/prompts/preamble.md`
  - THEN: `:1` for each of the three files.
- **briefing-template-has-reader-line**, NEW.
  - WHEN: `grep -c '^- Who reads what the roles write' factory/context.template.md`
  - THEN: `1`.
- **rubric-6-widened-in-every-copy**, NEW.
  - WHEN: `grep -c 'could read the Problem section' docs/design.md docs/prompts/03-spec-critic.md factory/prompts/critic.md; grep -c 'every human-facing section' docs/design.md docs/prompts/03-spec-critic.md factory/prompts/critic.md`
  - THEN: the first three lines each end `:0` and the last three each end `:1`.
- **reviewer-check-in-every-copy**, NEW.
  - WHEN: `grep -c 'SHOULD-FIX, never BLOCKING' docs/design.md docs/prompts/06-code-reviewer.md factory/prompts/reviewer.md`
  - THEN: `:1` for each of the three files.
- **prompt-copies-verbatim**, REGRESSION.
  - WHEN: the parent's `q=$(printf '\140\140\140'); for s in …` one-liner, copied verbatim.
  - THEN: `00-preamble verbatim`, `03-spec-critic verbatim`, `06-code-reviewer verbatim`, `preamble copies equal`, `critic-diff=2 reviewer-diff=2`.
- **records-name-the-standard**, NEW.
  - WHEN: `echo "changelog=$(grep -E '^[0-9]+\. ' docs/changelog.md | grep -c 'docs/writing.md') design=$(grep -c '{writing standard}' docs/design.md) buildspec=$(grep -c '{writing standard}' dev/build-harness.spec.md) stale=$(grep -c 'this list is the standard' README.md) row=$(grep -c '^| .docs/writing.md. |' README.md)"`
  - THEN: `changelog` 1 or more, `design` 2 or more, `buildspec` 1 or more, `stale=0`, `row=1`.
- **gates-pass**, REGRESSION.
  - WHEN: `git diff --check main...HEAD; echo "check=$?"; uv run --frozen pytest -q -p no:cacheprovider tests/factory`
  - THEN: `check=0`, and pytest ends with `N passed` and no failures or errors. N is the baseline plus the new file's tests; the parent recorded 121 at `4d0de52`.

No intermediate checks are needed, because this is the only sub-ticket.

Tests to change: `tests/factory/test_instance.py`, `test_system_prompt_is_the_design_preamble_filled_from_the_instance` (line 274). Exactly the change the parent describes:
- Exclude the index of the `{writing standard}` line from the comparison of unchanged lines.
- Assert that this filled line holds the absolute path of `docs/writing.md` in the harness checkout.
- Extend the final check with `"{writing standard}" not in` the prompt.
- Remove or loosen no assertion.

Protected paths, all declared in the parent's Risk section and authorised by the operator's answer:
- **harness:** `factory/instance.py`, `factory/prompts/preamble.md`, `factory/prompts/critic.md`, `factory/prompts/reviewer.md`, `factory/context.template.md`.
- **generated:** `docs/prompts/00-preamble.md`, `docs/prompts/03-spec-critic.md`, `docs/prompts/06-code-reviewer.md`.
- **guardrail, agent prompts:** the preamble, critic and code-reviewer blocks in `docs/design.md`.
- **guardrail, existing tests:** `tests/factory/test_instance.py`, the one test above.

Out of scope:
- `agents/**` and any installed `.claude/agents/` copies. In particular, do not run `factory render` to re-copy the blocks. Per `dev/build-harness.spec.md:158`, it also rewrites the `agents/` templates, which the parent's Decisions leave untouched. Re-copy the three blocks by hand.
- `.factory/**`, including this instance's `.factory/context.md` reader line (Operator step 2).
- Every other prompt block: spec writer, implementer PR DESCRIPTION format, verifier, planner, triage, retro.
- Routing, STATUS values, round limits.
- Adding `docs/writing.md` or `docs/` to the paths the harness revision is computed over (a parent Decision).
- Any README edit beyond the two lines and the date bump.
- The documentation-review checker role (Operator step 4).
- Green (`~/dev/nanobot-upstream/**`) and `~/.nanobot/**`.

---

## Shared plan context (from the plan; applies to every sub-ticket)

## Plan for T-0013 (issue #23): a writing standard for the sections people read

This spec fits one PR, so the plan is one sub-ticket. The case against splitting:
- **The parts form a chain.** Part B fills the preamble with the path of `docs/writing.md`. Its scenario and its new test both require that file to exist, so B cannot merge before A. The text added by parts C and D refers to "the writing standard the preamble names", so it means nothing until B lands. A split would give two or three PRs that must merge strictly in order. None of them could run in parallel.
- **They share files.** Parts B, C and D each edit `docs/design.md`. Part F asks for one changelog entry (43) that covers everything. The new test file checks the preamble, critic and reviewer blocks together.
- **Splitting does not make rollback easier.** No agent sees any of this until the operator moves the runtime to the merged revision and accepts it (Operator step 1). Reverting one PR is as easy as reverting part of a chain.
- **It is small.** The change is one new page under 120 lines, three prompt blocks with their copies, one `replace` call in `fill_preamble`, one template bullet, one changed test, one new test file, and four record edits.

---
