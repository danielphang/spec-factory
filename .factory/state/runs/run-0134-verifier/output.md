Commit: 530c9ef3b8a557b5a340b3662cd610eb4f2d0a41 (parent-close run: head is the current main; base is 61d92bef32d05c89bb9187f8455f4eb298b2a99f)

Environment: each scenario ran exactly as written, in the run worktree at the head (`.../run-0134-verifier/wt`, `git status --short` empty before and after). It also ran in two fresh `git clone`s of that worktree, made in my scratchpad: `run0134/head` at 530c9ef and `run0134/base` at 61d92be, each with `uv sync --frozen` and an empty `git status`. Head results were the same in the worktree and the head clone. The one difference is the absolute path in S5, which follows the checkout, as the scenario intends.

Per criterion: NEW/REGRESSION | command | base | PR | PASS/FAIL
- coding-page-has-five-checkable-rules | NEW | spec WHEN as written | `missing` | `rules=1,2,3,4,5 check=5 principle=5 before=5 after=5 precedence=first` | PASS
- coding-page-has-every-requested-phrase | NEW | spec WHEN as written | 13 `missing: …` lines, `found=0 of 13` | only `found=13 of 13` | PASS
- tag-table-severities | NEW | spec WHEN as written | `reuse= stdlib= native= yagni= delete= ` | `reuse=BLOCKING stdlib=SHOULD-FIX native=SHOULD-FIX yagni=SHOULD-FIX delete=SHOULD-FIX ` | PASS
- pointer-line-in-every-copy | NEW | spec WHEN as written | six `:0`, then three `:1` | six `:1` (design.md, 05-implementer.md, implementer.md, design.md, 06-code-reviewer.md, reviewer.md), then three `:0` | PASS
- implementer-and-reviewer-prompts-name-the-page | NEW | spec WHEN as written | `implementer standard=[] unfilled=0`, `reviewer standard=[] unfilled=0`, `file=absent` | `implementer standard=[/Users/dphang/dev/spec-factory/.factory/state/runs/run-0134-verifier/wt/docs/coding.md] unfilled=0`, the same for reviewer, `file=present` | PASS
- cut-rule-and-probe-in-every-copy | NEW | spec WHEN as written | six `:0` | six `:1` | PASS
- marker-ledger-named-in-design-and-build-spec | NEW | spec WHEN as written | `design=0 retro=0 buildspec=0 row=0` | `design=2 retro=1 buildspec=2 row=1` | PASS
- changed-blocks-verbatim-and-harness-copies-in-step | REGRESSION | spec WHEN as written | five `verbatim`, `spec_writer-diff=6 critic-diff=2 implementer-diff=5 reviewer-diff=2 ` | identical | PASS
- records-name-the-coding-standard | NEW | spec WHEN as written | `changelog=0 design=0 buildspec=0 row=0` | `changelog=1 design=3 buildspec=1 row=1` | PASS
- gates-pass | REGRESSION | `git diff --check main...HEAD; echo "check=$?"; uv run --frozen pytest -q -p no:cacheprovider tests/factory` | `126 passed in 85.29s` (clean base clone) | `check=0`, `131 passed in 81.77s` | PASS

Every base result matches the "today" result stated in verification.md. Every NEW criterion fails on base for the reason the spec gives. In S5 on base, both runs start (the system prompts exist, `unfilled=0`), and the failure is the missing path and file.

Text checks beyond the scenarios:
- `docs/coding.md` matches design.md part A word for word. I normalised whitespace on both and ran `diff`: no difference. It has no line over 100 characters outside table rows.
- The diffs to `docs/design.md`, `docs/prompts/08-retro.md`, `dev/build-harness.spec.md` (lines 158, 323, 435), `docs/changelog.md` (entry 44, after 43 and before "Declined:"), `README.md` (one row after `docs/writing.md`) and the four `factory/prompts/` files each match parts B, D, E and F.
- `factory/instance.py` adds `fill_standards`, which `fill_preamble` now calls. `factory/cli.py:219` passes the role prompt through `instance.fill_standards`. This is part C, with no second `.replace` in `cli.py`.
- The 17 changed files touch no path under `.factory/`, `agents/`, `bin/factory`, `pyproject.toml`, `uv.lock` or existing tests. One file is new: `tests/factory/test_coding_standard.py`.
- That new test file, copied into the base clone: its 2 prompt tests fail and its 3 block-verbatim tests pass. So the 3 verbatim tests are regression guards, and the 2 prompt tests fail without the change.

Gate suite: PASS
- `git diff --check main...HEAD` → exit 0 (`check=0`). Main equals HEAD in a parent close, so this diff is empty. I also ran `git diff --check 61d92be HEAD`, which exits 0 too.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` → `131 passed in 81.77s`. That is 126 on base plus the 5 new tests.

Probes:
- Harness run from a different checkout (the clean head clone in my scratchpad) → both prompts name `<that clone>/docs/coding.md` with `unfilled=0` → OK. The path comes from the running checkout, not a hard-coded value.
- Harness run through a symlink to the head clone (`headlink/bin/factory`) → the implementer and reviewer prompts name the resolved path `.../run0134/head/docs/coding.md`, which is what the scenario's `pwd -P` expects (`HARNESS = Path(__file__).resolve()...`, `instance.py:28`). → OK.
- Other roles and leftover placeholders → a triage run's system prompt has no coding-standard line and no `{…}` placeholder, and it still names `<checkout>/docs/writing.md` once. The implementer and reviewer prompts also name `writing.md` once each, with no `{…}` left (`grep -oE '\{[a-z][a-z ,-]*\}'` prints nothing). So moving the writing-standard fill into the shared helper did not break the preamble. → OK.

STATUS: VERIFIED
CONFIDENCE: high. Every scenario ran verbatim on the head and on a clean base clone, and each matched its stated before-state and after-state. The gates pass, and the probes show the path is filled from whichever checkout runs.
ESCALATIONS:
- The scratchpad was not clean. My first base checkout extracted `git archive 61d92be` over a `scratchpad/base` directory that already existed. It held an older git checkout (HEAD f4be7ec, with `.factory/` and `intake/`), probably left by another run sharing this scratchpad. Its files got mixed with the base files, and pytest there printed `23 failed, 103 passed`. I discarded those results and redid every base check in fresh clones under `scratchpad/run0134/`. Every base result above comes from those clones. The older directory is now partly overwritten. If another run relies on `scratchpad/base`, it should rebuild it.
- Not verified here, by design: whether a live reviewer tags its findings, and whether a live implementer follows the page. Those are Operator steps 0 and 2. The change has no effect until the runtime moves and the operator accepts it with `--accept-harness` (Operator step 1).
