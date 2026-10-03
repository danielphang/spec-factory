Sub-ticket: T-0012.2, Document re-layout (parent `intake/state/specs/T-0012/v3.md`, part D, D.1–D.4). Round 2 (fix round).
Branch: `factory/T-0012.2` in `/Users/dphang/dev/spec-factory/intake/state/worktrees/T-0012.2`. `main` is `20849b63a3a632cd43724819d860f71717dc8a53`. The new head is `ebe9baf0843c3421585aa37a03e835617e652f59`, and `git merge-base HEAD main` is now `20849b6`.

Commits on the branch over main:
- `c367bef`: T-0012.2 (#19 part D), the document re-layout. Unchanged since round 1.
- `ebe9baf`: merge of `main` (`20849b6`, which includes T-0012.1's merge `02e8c8d`) into the branch. I used `git merge --no-ff main`, with no rebase and no force-push. It had no conflicts.

## What changed

Round 2:
- The only change is the merge of `main`. It does not change any file in this PR:
  - `git diff --stat c367bef HEAD -- README.md docs dev intake/README.md intake/instance` is empty.
  - `git diff --name-only main HEAD` lists the same 19 paths as `git diff --name-only main...HEAD`.
- The head now has `pyproject.toml`, `uv.lock` and `tests/factory/` from T-0012.1, so the run's second gate can run.

The content is the same as round 1, per lettered part:
- D.1:
  - `git mv docs/spec-factory.md docs/design.md`.
  - The `## Changelog` section (old lines 678–725, from the heading to the line before `## Appendix`) is cut out into the new `docs/changelog.md`. That file is a `# Changelog` title followed by old lines 679–724 verbatim: the intro paragraph, entries 1–41 and the `Declined:` line. Old line 725, the blank separator before `## Appendix`, is dropped.
  - One line is added at the end of "How to use this", in its own paragraph (`docs/design.md:31`): "This document's changelog is `docs/changelog.md`, and `docs/prompts/` holds a verbatim copy of each prompt block in it, changed only by re-copying that block."
  - Every other line is unchanged.
- D.2: `git mv prompts docs/prompts`. All 10 files are R100.
- D.3: four `git mv` renames:
  - `specs/build-harness.md` → `dev/build-harness.spec.md` (R100);
  - `plans/build-harness.md` → `dev/build-harness.plan.md` (R097);
  - `plans/P0-intake-skeleton.md` → `dev/P0-intake-skeleton.md` (R096);
  - `issues/README.md` → `dev/issues.md` (R100).
- D.4: reference updates in:
  - `README.md` lines 5–11;
  - the 9 `Parent:` lines in `dev/build-harness.plan.md`, plus the GitHub URL on line 3;
  - `dev/P0-intake-skeleton.md:3`;
  - `intake/README.md` lines 4 and 42;
  - `intake/instance/context.md` lines 3–20.

  Records are untouched.

## Acceptance results

All commands ran with bash from the worktree, exactly as written (script: `…/scratchpad/t122/acc.sh`), with `BASE=$(git rev-parse main)` = `20849b6`. Today's "before" values are the round-1 base values. The verifier re-ran them on `20849b6` and got the same results.

| Criterion | Before (base) | Round-1 head `c367bef` (re-run today) | After (`ebe9baf`) |
|---|---|---|---|
| docs-moved-and-split | seven `missing …`, `old_tracked=15` | `old_tracked=0` | `old_tracked=0` |
| changelog-moved-verbatim | `DIFFERENT` / `declined= numbering=NONE in_design=` | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` |
| design-text-kept | `570` | `0` | `0` |
| prompt-copies-moved-unchanged | `changed=10 of 10 DRIFT` | `changed=0 of 10 VERBATIM` | `changed=0 of 10 VERBATIM` |
| no-old-paths, documents only | `exit=0` | `exit=1` | `exit=1` |
| how-to-use-names-new-homes | `awk: can't open file docs/design.md`, then `0` | `1` | `1` |
| records-untouched (REGRESSION) | `0` | `0` | `0` |
| green-harness-still-present (REGRESSION) | `green keeps its harness` | `green keeps its harness` | `green keeps its harness` |
| whitespace, `git diff --check main...HEAD; echo "exit=$?"` (REGRESSION) | `exit=0` | `exit=0` | `exit=0` |

Gates, run from the worktree exactly as written:
- `git diff --check main...HEAD`
  - Round-1 head: exit 0.
  - After: no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`
  - Round-1 head: exit 4, `no tests ran in 0.00s`. This is the verifier's run-0062 result. I did not re-run it, because on that tree uv walks up to the dev checkout's project and would touch `~/dev/spec-factory/.venv`.
  - After, first run: uv printed `Creating virtual environment at: .venv` (the worktree's own, fresh), then `70 passed in 90.10s (0:01:30)`.
  - After, second run under `bash -c` to capture the exit code: `gate2 exit=0`, `70 passed in 88.93s (0:01:28)`.
  - `git status --short --untracked-files=all` was empty afterwards. `.venv/` is ignored by `main`'s `.gitignore`.

## Tests added/changed

None. Part D is a document move, and the acceptance commands above are its checks. The merge brings in `tests/factory/**` from `main` unchanged. It is not part of this PR's `main...HEAD` diff.

## Known gaps and uncertainties

- **README hunk is more than a token swap** (same as round 1, and the reviewer's NIT):
  - `README.md:7-10` rewords the `specs/<ticket>.md` / `plans/<ticket>.md` bullets to name `dev/build-harness.spec.md` / `dev/build-harness.plan.md`, because those directories no longer exist.
  - It adds one `dev/issues.md` bullet.
  - E.6 rewrites the file.
- **`README.md:11` still says `docs/prompts/` "is regenerated from" the design doc.** That claim was already there. Only the path is in D's scope.
- **The added "How to use this" line brings one blank separator line with it.**
- **The fix is a merge commit, not a rebase.** I chose it because the role forbids force-push. So `main...HEAD` shows only this PR's 19 paths, but `git log main..HEAD` lists two commits.

## Out-of-scope observations

- **The `generated` protected class still names the old path.** `intake/instance/config.yaml:9` (`generated: ["prompts/**"]`) and `intake/instance/preamble.md:38` still say `prompts/**`. Both files are outside D's `intake/` allowance, and E.5 deletes them. Until then, the live instance's `generated` class names a path that no longer exists.
- **`docs/changelog.md:3` points to an appendix that is no longer in that file.** It says "the reviewer prompt in the appendix", and the appendix is now in `docs/design.md`. Records are left as written.
- **The verifier's run-0062 left `/Users/dphang/dev/spec-factory/.venv` in place** (gitignored). It was created when uv walked up from the old head's worktree. I did not touch it.
- **Empty untracked directories `issues/`, `plans/` and `specs/` remain in this worktree** after the `git mv`s. Git does not track empty directories, so they are not in the branch, and I left them alone.

## Responses to findings

- **Reviewer [SHOULD-FIX] (head does not contain current `main`, so the pytest gate cannot pass): FIXED in `ebe9baf`.**
  - I merged `main` (`20849b6`) into `factory/T-0012.2` with no conflicts.
  - `git merge-base HEAD main` is now `20849b6`.
  - `uv run --frozen pytest -q -p no:cacheprovider tests/factory` now gives `70 passed`, exit 0.
  - Every acceptance criterion gives the same output as before the merge.
- **Reviewer [NIT] (`README.md:7-10` slightly beyond a reference update): no change.** The reviewer requested none, and it is disclosed under Known gaps. E.6 rewrites the file.
- **Verifier FAILED (gate suite FAIL, branch predates T-0012.1): FIXED in `ebe9baf`.**
  - The fix is the same merge as for the reviewer's SHOULD-FIX.
  - Both gates now pass on the head itself, not only on a trial merge.
  - No content change.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Both gates and all nine acceptance commands were run as written on `ebe9baf` and printed the expected output. The merge leaves this PR's files byte-for-byte as on `c367bef`.
ESCALATIONS:
- Protected path touched, declared in the sub-ticket: generated `prompts/**` moved to `docs/prompts/` byte-identical (`changed=0 of 10 VERBATIM`; 10 × R100).
- Protected path touched, declared in the sub-ticket: infra `intake/**`, only `intake/README.md` (lines 4, 42) and `intake/instance/context.md` (lines 3–20), for reference updates per D.4. The merge gate needs human approval for these.
