Commit: c367bef72e2ed70a4417e98de907c91dbbe31320

The document re-layout is correct, and every acceptance criterion passes on the head. The verdict is FAILED for one reason only: the second gate command exits 4 on this head, because the branch was cut from `cdb1c67`, which is before T-0012.1 merged. The branch does not contain `tests/factory/` or `pyproject.toml`. On a trial merge of the head into `main` (`20849b6`), both gates pass (`70 passed`) and so does every criterion. The fix is to bring the branch up to `main`, with no change to its content. Details follow.

Environment:
- Head: a scratch clone with `factory/T-0012.2` fetched at `c367bef` (`main` = `20849b6`).
- Base: a scratch clone at `20849b6`, the base I was given.
- Trial merge: `c367bef` merged with `main` `20849b6`, no conflicts.
- `BASE` was the parent's recorded base, `cdb1c6769ecc39208e62edc65578f62f5a23908f` (`parent_base` in `intake/state/tickets/T-0012.yaml:74`). `docs/spec-factory.md` and `prompts/` have the same blobs at `f082708`, `cdb1c67` and `20849b6` (`f7d825a…` and `29610d6…`), so using `$(git rev-parse main)` gives the same results.
- Topology: `git merge-base HEAD main` = `cdb1c67`, so the head does not descend from the given base `20849b6` (T-0012.1's merge `02e8c8d` plus the intake commit `20849b6`). `main...HEAD` is still exactly this PR's single commit.

Per criterion: NEW/REGRESSION | command | base (20849b6) | PR (c367bef) | PASS/FAIL
- docs-moved-and-split | NEW | as written | 7 `missing …` lines, then `old_tracked=15` | `old_tracked=0` only | PASS
- changelog-moved-verbatim | NEW | as written | `DIFFERENT` / `declined= numbering=NONE in_design=` | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` | PASS
- design-text-kept | NEW | as written | `570` | `0` | PASS
- prompt-copies-moved-unchanged | NEW | as written | `changed=10 of 10 DRIFT` | `changed=0 of 10 VERBATIM` | PASS
- no-old-paths, documents only | NEW | as written | `exit=0` | `exit=1` | PASS
- how-to-use-names-new-homes | NEW | as written | `awk: can't open file docs/design.md` then `0` | `1` | PASS
- records-untouched | REGRESSION | as written | `0` | `0` | PASS
- green-harness-still-present | REGRESSION | as written | `green keeps its harness` | `green keeps its harness` | PASS
- whitespace (sub-ticket diff) | REGRESSION | `git diff --check main...HEAD; echo "exit=$?"` | `exit=0` | `exit=0` | PASS

Every NEW criterion fails on base for the reason the spec states (the files are not there yet) and passes on the PR. The base outputs match the verification.md "today" values. The trial merge (`c367bef` + `20849b6`) gives the same PASS outputs for all nine.

Gate suite: FAIL
- `git diff --check main...HEAD`: no output, exit 0 (in the given worktree, the head clone and the trial merge).
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`:
  - In the given worktree `…/run-0062-verifier/wt`, run under bash, it printed `ERROR: file or directory not found: tests/factory` / `no tests ran in 0.00s`, exit 4. The head's tree is only `README.md dev docs intake` (`git ls-tree HEAD --name-only`). Because the worktree has no `pyproject.toml`, uv walked up to the dev checkout's project, `/Users/dphang/dev/spec-factory/.venv`.
  - In the head scratch clone: `no tests ran in 0.00s`, exit 4.
  - In the trial merge with `main` (`unset VIRTUAL_ENV`, `PYTHONDONTWRITEBYTECODE=1`): `70 passed in 121.91s (0:02:01)`, exit 0.
  - Cause: the gate command was added after T-0012.1 merged, and this branch predates that merge. It is not a defect in D's content. Remedy: merge or rebase `main` into `factory/T-0012.2`, or gate on the merge result. No content change is needed.

Probes:
- Full changelog body (the scenario only compares numbered lines). Command: `diff <(base Changelog section) docs/changelog.md`. Result: only `## Changelog` became `# Changelog`, and the trailing blank line before `## Appendix` was dropped. The intro paragraph, the 41 entries and the `Declined:` line are byte-identical. Numbered lines: 41 in `docs/changelog.md` + 45 in `docs/design.md` = 86 in the base doc. → OK
- Full `docs/design.md` against the base doc minus its Changelog. Result: the only difference is lines 31–32, the new "How to use this" line plus a blank separator, sitting before `## Harness: functional pieces`. Line counts: 713 + 47 = 759 − 1 + 2. → OK. The design-text-kept check could not detect added lines; this diff does, and there are none besides the allowed line.
- Renames. Command: `git diff -M --name-status cdb1c67 HEAD`. Result: all 10 prompt copies, `dev/build-harness.spec.md` and `dev/issues.md` are R100. The plan is R097 and P0 is R096 (path edits only). `docs/design.md` is R085, with `docs/changelog.md` added. The other changed files are `README.md`, `intake/README.md` and `intake/instance/context.md`, all within the sub-ticket's file list. → OK
- Reference edits read line by line:
  - all 9 `Parent:` lines in the plan, plus line 3's GitHub URL;
  - P0 line 3;
  - `intake/README.md` lines 4 and 42;
  - `intake/instance/context.md` lines 3–20;
  - `README.md` lines 5–11.
  All are path swaps. The README's `specs/<ticket>.md` / `plans/<ticket>.md` bullets are reworded to name the moved files, and one `dev/issues.md` bullet is added, as the PR discloses; E.6 rewrites the README anyway. → OK
- Old-path grep widened to the whole tree outside records. Result: matches remain only in `intake/README.md` (2: `HARNESS_PIN`, `intake/setup.sh`), `intake/instance/config.yaml` (3, including `generated: ["prompts/**"]`), `intake/instance/preamble.md` (1, `generated (prompts/**, …)`) and `intake/setup.sh` (1). All of them are either removed by E.5 or outside D's file list. → CONCERN, out of scope: until E lands, the live instance's `generated` protected class names `prompts/**`, which no longer exists, so the moved copies under `docs/prompts/` are not covered by that class's text.
- Relative markdown links in `README.md`, `docs` and `dev`: none, so the moves cannot break any. → OK

STATUS: FAILED
CONFIDENCE: high. Every acceptance command and both gates were run as written on base, head and a trial merge. The only failure is the pytest gate on the head, which has an unambiguous cause (branch predates T-0012.1), and the gate passes once the branch includes `main`.
ESCALATIONS:
- Stale branch base, which is a harness/process issue. The verifier was given base `20849b6`, but the head forks at `cdb1c67` and does not contain T-0012.1, so the instance's second gate (`uv run --frozen pytest … tests/factory`) cannot pass on this head as built. The content is verified correct on both the head and the merge result. Operator decision: update the branch onto `main` and re-verify, or accept on the trial-merge evidence above.
- Side effect of running the gate as written. In the given worktree, which has no `pyproject.toml`, `uv run` discovered the parent dev checkout's project and created `/Users/dphang/dev/spec-factory/.venv` (birth `Oct 3 01:12:15 2026`, during this run; it is gitignored by `main`'s `.gitignore:1`). I left it in place rather than delete it, in case a concurrent run is now using it. Remove it if it is unwanted.
- Out of scope, already noted by the implementer: `intake/instance/config.yaml:9` and `intake/instance/preamble.md:38` still name `prompts/**` as the `generated` class. E.5 deletes both files.
