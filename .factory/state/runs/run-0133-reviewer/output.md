## Code review: T-0015.1, round 1

Commit: 27d6d63fcb2f5c03d64696f6769abf871e4f2bc0 (branch `factory/T-0015.1`, base 61d92bef32d05c89bb9187f8455f4eb298b2a99f, one commit, 17 files, +235/-15)

### What I checked and how

Every command below ran in the review worktree
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0133-reviewer/wt` at the head above.

1. Test integrity. `git diff --stat main...HEAD -- tests/ agents/ bin/ pyproject.toml uv.lock .factory/` lists only the new file `tests/factory/test_coding_standard.py` (+86). No existing test, CI config or template changed. The new tests assert exact lines and a non-empty file; nothing is skipped, swallowed or hard-coded to output.
2. Correctness. I ran every parent scenario verbatim:
   - 1 `rules=1,2,3,4,5 check=5 principle=5 before=5 after=5 precedence=first`; 2 `found=13 of 13` with no `missing:` line; 3 `reuse=BLOCKING stdlib=SHOULD-FIX native=SHOULD-FIX yagni=SHOULD-FIX delete=SHOULD-FIX`.
   - 4: the six pointer-line greps end `:1`, the three "Maintainability, only where" greps end `:0`.
   - 5: `implementer standard=[<wt>/docs/coding.md] unfilled=0`, the same for `reviewer`, `file=present`, where `<wt>` is the worktree's absolute path. I also checked `{writing standard}` stays filled in both prompts (`writing_unfilled=0`).
   - 6: six lines `:1`. 7: `design=2 retro=1 buildspec=2 row=1`. 9: `changelog=1 design=3 buildspec=1 row=1`.
   - 8: five `verbatim` lines and `spec_writer-diff=6 critic-diff=2 implementer-diff=5 reviewer-diff=2`, unchanged from main. Every `factory/prompts/` copy still differs from its `docs/prompts/` twin only in the placeholders it already fills.
   - 10: `git diff --check main...HEAD` exited 0; `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `131 passed in 111.80s`. Main had 126; the five new tests account for the rise.
   - 11: I cloned `main` (61d92be) into my scratchpad, copied in only the new test file and ran it: `2 failed, 3 passed`, the two failures being the prompt-path tests on `is_file()` of the missing `docs/coding.md`. The test checks something.
   - `docs/coding.md` is byte-identical to the parent's part A block (`diff` of the extracted block against the file printed nothing).
   - `fill_standards` has the two callers the spec names (`factory/instance.py:173` in `fill_preamble`, `factory/cli.py:219` on the role prompt); `grep -rn 'fill_preamble\|fill_standards' --include='*.py' --include='*.js' .` shows no other caller and no leftover `.replace("{writing standard}"` in `cli.py`.
3. Scope. Every hunk maps to a lettered part A to F. The `docs/design.md` diff touches only line 54, the Retro routing row, and the spec writer, critic, implementer, reviewer and retro blocks. Nothing under Out of scope (preamble, verifier, triage, planner, `agents/`, `store.py`) changed.
4. Silent behaviour changes. One, and the spec asks for it: every role prompt now passes through `fill_standards`. `grep -n '{[a-z ]*}' factory/prompts/*.md` shows the only placeholders that match are the two new `{coding standard}` lines and the preamble's `{repo name}` and `{writing standard}`, so no other role prompt's text changes.
5. Security and data safety. No new input, no secrets, no destructive operation. The helper only substitutes two constant paths.
6. Protected paths. All touched paths are declared in the sub-ticket; listed under ESCALATIONS.
7. Maintainability. `fill_standards` is six lines next to its one sibling; the test file copies `test_writing_standard.py`'s `cli` helper, which is the existing pattern in `tests/factory/` and the way the spec asked for it. Not a real problem.
8. PR description. What changed glosses implementer, code reviewer, retro and placeholder on first use and says what changed in words. Known gaps names the three regression-guard tests that pass on `main`, the README timing, the backtick reading in the Routing row, and the marker line. Readable by the operator at the gate.

### Findings

- [NIT] PR description: What changed, part C: "After the change the only placeholders in `factory/prompts/` are the two coding-standard lines and the preamble's writing-standard line" omits the preamble's `{repo name}` (`factory/prompts/preamble.md:1`), which `fill_preamble` still fills → a reader auditing placeholders from the description would count one too few. No code effect.

Prior findings: none (round 1).

STATUS: APPROVE
CONFIDENCE: high. All eleven acceptance scenarios and both gates were re-run here and printed the THEN values; the new prompt-path tests were seen to fail on a scratch clone of `main`; `docs/coding.md` is byte-identical to the approved block.
ESCALATIONS: protected paths touched, all declared in the sub-ticket (merge gate needs the human approval): harness `factory/instance.py`, `factory/cli.py`, `factory/prompts/implementer.md`, `factory/prompts/reviewer.md`, `factory/prompts/spec_writer.md`, `factory/prompts/critic.md`; generated `docs/prompts/02-spec-writer.md`, `03-spec-critic.md`, `05-implementer.md`, `06-code-reviewer.md`, `08-retro.md`, each verbatim to its design block (scenario 8); guardrail agent-prompt blocks in `docs/design.md` (spec writer, spec critic, implementer, code reviewer, retro).
