Commit: 27d6d63fcb2f5c03d64696f6769abf871e4f2bc0 (branch `factory/T-0015.1`; worktree clean, `git status --short` empty)
Base: 61d92bef32d05c89bb9187f8455f4eb298b2a99f (a scratch clone checked out at that SHA, with `main` pointed at it)

How run: each acceptance command was saved verbatim to a script and run with `bash` from the PR worktree and from the base clone. Criterion 5 ran on the PR before any `.venv` existed (so `bin/factory` fell back to `python3`), and again in a second clone at the PR head (Probes A and B).

Per criterion: NEW/REGRESSION | command | base | PR | PASS/FAIL
1. NEW | coding-page-has-five-checkable-rules | `missing` | `rules=1,2,3,4,5 check=5 principle=5 before=5 after=5 precedence=first` | PASS
2. NEW | coding-page-has-every-requested-phrase | 13 `missing: …` lines, `found=0 of 13` | only `found=13 of 13` | PASS
3. NEW | tag-table-severities | `reuse= stdlib= native= yagni= delete= ` | `reuse=BLOCKING stdlib=SHOULD-FIX native=SHOULD-FIX yagni=SHOULD-FIX delete=SHOULD-FIX ` | PASS
4. NEW | pointer-line-in-every-copy | six `:0`, then three `:1` | six `:1` (design.md, 05-implementer.md, implementer.md, design.md, 06-code-reviewer.md, reviewer.md), then three `:0` | PASS
5. NEW | implementer-and-reviewer-prompts-name-the-page | `implementer standard=[] unfilled=0`, `reviewer standard=[] unfilled=0`, `file=absent` (both runs started; their system-prompt.txt files existed) | `implementer standard=[/Users/dphang/dev/spec-factory/.factory/state/runs/run-0132-verifier/wt/docs/coding.md] unfilled=0`, the same for `reviewer`, `file=present` | PASS
6. NEW | cut-rule-and-probe-in-every-copy | six `:0` | six `:1` | PASS
7. NEW | marker-ledger-named-in-design-and-build-spec | `design=0 retro=0 buildspec=0 row=0` | `design=2 retro=1 buildspec=2 row=1` | PASS
8. REGRESSION | changed-blocks-verbatim-and-harness-copies-in-step | five `verbatim` lines, then `spec_writer-diff=6 critic-diff=2 implementer-diff=5 reviewer-diff=2 ` | identical | PASS
9. NEW | records-name-the-coding-standard | `changelog=0 design=0 buildspec=0 row=0` | `changelog=1 design=3 buildspec=1 row=1` | PASS
10. REGRESSION | gates-pass | `check=0`, `126 passed in 108.52s` | `check=0`, `131 passed in 112.14s` | PASS (the count rose by 5, the new file's 5 tests)
11. NEW | `uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_coding_standard.py` | the new file copied into the base clone: `2 failed, 3 passed`. The two prompt-path tests fail on `AssertionError: assert (True and False)`, because `docs/coding.md` is absent. The three block-equality tests pass. | `5 passed in 1.56s` | PASS (the criterion requires that the prompt-path test fail on `main`, and it does)

Other checks:
- `docs/coding.md` matches part A of the parent's design.md byte for byte. I compared it with `diff` against the block extracted from the input (input.md lines 408–505), and diff printed nothing.
- Scope: `git diff --name-only 61d92be HEAD` lists 17 files. Each is named in the sub-ticket's scope or its declared protected paths. Nothing changed under `.factory/**`, `agents/**`, `bin/factory`, `pyproject.toml` or `uv.lock`. The only change under `tests/` is the new file `tests/factory/test_coding_standard.py`.

Gate suite: PASS
- `git diff --check main...HEAD` exited 0 (`check=0`)
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` → `131 passed in 112.14s`

Probes:
- A. Criterion 5 run from a second clone at the PR head whose path contains a space (`…/v0132/pr head`) → both prompts name `…/v0132/pr head/docs/coding.md`, `unfilled=0`, `file=present` → OK. The path follows the running checkout and is not hard-coded.
- B. The same clone entered through the `/tmp` symlink (`/tmp` is a symlink to `/private/tmp` on macOS) → both prompts name the resolved `/private/tmp/…/pr head/docs/coding.md`, which matches `pwd -P`. `HARNESS` is `Path(__file__).resolve().parent.parent` (`factory/instance.py:28`) → OK.
- C. Half of part C removed: `factory/cli.py` restored to its base version (no role-prompt fill), with the PR's prompts and page kept → criterion 5 prints `standard=[] unfilled=1` for both roles, and the new test file prints `2 failed, 3 passed` → OK. The test and the scenario both catch the failure the spec names. File restored afterwards.
- D. `fill_standards` applied to every `factory/prompts/*.md`, and `fill_preamble` to the preamble → only `implementer.md` and `reviewer.md` change, and no `{writing standard}` or `{coding standard}` remains in any prompt. The preamble still gets the `docs/writing.md` path and has no `{repo name}` left. The fill is idempotent, and empty input returns `''` → OK. The fill has two callers, both changed: `fill_preamble` and `run_start` (`factory/cli.py:218-219`).

Out-of-scope observations:
- The three `test_changed_design_block_equals_its_prompt_copy` tests pass on `main`. They guard against future drift: each fails only if someone edits a design block without re-copying it. Part F asks for them explicitly, and criterion 11 requires only the prompt-path tests to fail on `main`. The implementer disclosed this under Known gaps. Under a strict reading of "a test that passes on `main` checks nothing", the spec's part F and criterion 11 pull against each other slightly. That tension is in the spec, not in this PR.
- `uv run` created an untracked, gitignored `.venv` in the verifier worktree. `git status` is still clean.

STATUS: VERIFIED
CONFIDENCE: high. All 11 criteria and both gate commands were run as written on the head and on the base, and each printed its expected result. The probes show the path fill tracks the running checkout and fails as the spec says when the fill is missing.
ESCALATIONS: none
