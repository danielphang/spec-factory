Commit: ebe9baf0843c3421585aa37a03e835617e652f59

All nine acceptance criteria pass on the head, and so do both gates. The round-1 failure is fixed: the pytest gate now gives `70 passed` with exit 0, because the head now contains `main` (`20849b6`). The merge leaves this PR's content byte-for-byte as it was at `c367bef`.

Environment:
- Head: the given worktree `…/run-0064-verifier/wt`. `git rev-parse HEAD` = `ebe9baf`, `main` = `20849b6`, `git merge-base HEAD main` = `20849b6`, and the parents of `ebe9baf` are `c367bef 20849b6`.
- Base: a scratch clone checked out at `20849b63a3a632cd43724819d860f71717dc8a53`.
- `BASE` is the parent's recorded base, `cdb1c6769ecc39208e62edc65578f62f5a23908f` (`parent_base`, `intake/state/tickets/T-0012.yaml:74`). `docs/spec-factory.md` (blob `f7d825a…`) and `prompts/` (tree `29610d6…`) are identical at `cdb1c67` and at `main`. On the head, the full output with `BASE=cdb1c67` and with `BASE=$(git rev-parse main)` is identical (`diff` of the two captures is empty).
- Every command ran with bash, verbatim from the sub-ticket and the parent spec, from one script.

Per criterion: NEW/REGRESSION | command | base (20849b6) | PR (ebe9baf) | PASS/FAIL
- docs-moved-and-split | NEW | parent scenario, as written | 7 `missing …` lines, then `old_tracked=15` | `old_tracked=0` only | PASS
- changelog-moved-verbatim | NEW | parent scenario, as written | `DIFFERENT` / `declined= numbering=NONE in_design=` | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` | PASS
- design-text-kept | NEW | parent scenario, as written | `570` | `0` | PASS
- prompt-copies-moved-unchanged | NEW | parent scenario, as written | `changed=10 of 10 DRIFT` | `changed=0 of 10 VERBATIM` | PASS
- no-old-paths, documents only | NEW | `git grep -n … -- README.md docs dev >/dev/null; echo "exit=$?"` | `exit=0` | `exit=1` | PASS
- how-to-use-names-new-homes | NEW | `awk '/^## How to use this/…' docs/design.md | grep … | grep -c 'docs/prompts/'` | `awk: can't open file docs/design.md`, then `0` | `1` | PASS
- records-untouched | REGRESSION | `git diff --name-only main...HEAD -- intake/state intake/answers intake/green-pilot intake/.gitignore | wc -l | tr -d ' '` | `0` | `0` | PASS
- green-harness-still-present | REGRESSION | parent scenario, as written | `green keeps its harness` | `green keeps its harness` | PASS
- whitespace (sub-ticket diff) | REGRESSION | `git diff --check main...HEAD; echo "exit=$?"` | `exit=0` | `exit=0` | PASS

Every NEW criterion fails on base for the reason the spec states: the moved files do not exist there yet. The base outputs match verification.md's "today" values. Both REGRESSION criteria pass on base and on the PR.

Gate suite: PASS
- `git diff --check main...HEAD`: no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, run in the worktree:
  - First run: `Creating virtual environment at: .venv` (the worktree's own `.venv`), then `70 passed in 94.61s (0:01:34)`.
  - Second run, under `bash -c` to capture the exit code: `gate2 exit=0`, `70 passed in 95.23s (0:01:35)`.
  - `git status --short --untracked-files=all` printed nothing afterwards (`.venv/` is ignored by `.gitignore`).
  - An intermediate attempt printed `exit=1`. That was a typo in my own redirect path (`No such file or directory`), not pytest, and pytest did not run. The corrected run is the one above.

Probes:
- Did the merge change any PR content? `git diff --stat c367bef HEAD -- README.md docs dev intake/README.md intake/instance` is empty. → OK
- Did the merge bring in anything beyond `main`? `diff <(git diff --name-only main HEAD) <(git diff --name-only main...HEAD)` is empty, and both list 19 paths. So the head equals `main` plus exactly this PR's files, and T-0012.1's tree is carried unchanged. → OK
- Is the whole changelog body verbatim? The scenario compares only numbered lines. `diff <(tail -n +2 docs/changelog.md) <(git show main:docs/spec-factory.md | sed -n '679,724p')` is empty, and line 1 is `# Changelog`. → OK
- Was any line added to the design doc? design-text-kept cannot detect additions. `diff <(old doc with its Changelog section removed) docs/design.md` shows only `30a31,32`: the allowed "How to use this" line (it names `docs/changelog.md` and `docs/prompts/`) plus a blank separator. Line counts are 713 + 47. → OK
- Are the renames clean? `git diff -M --name-status main...HEAD` shows:
  - R100 for the 10 prompt copies, `dev/build-harness.spec.md` and `dev/issues.md`;
  - R097 for the plan and R096 for P0;
  - R085 for `docs/design.md`, with `docs/changelog.md` added;
  - M for `README.md`, `intake/README.md` and `intake/instance/context.md`.
  All are within the sub-ticket's file list. → OK
- Reading the reference edits line by line:
  - the 9 `Parent:` lines, plus the GitHub URL on the plan's line 3;
  - P0 line 3;
  - `intake/README.md` (2 lines);
  - `intake/instance/context.md` (2 hunks);
  - `README.md` lines 5–11.
  All are path updates. The README rewords its `specs/<ticket>.md` and `plans/<ticket>.md` bullets and adds a `dev/issues.md` bullet, as the PR discloses. E.6 rewrites the README. → OK
- The old-path grep widened to the whole tree outside the records (`intake/state`, `intake/answers`, `intake/green-pilot`, `docs/changelog.md`). It still matches in:
  - `factory/config.yaml` (3), `factory/prompts/context.md` (6) and `factory/prompts/preamble.md` (1): T-0012.1's interim overlay, already on `main`;
  - `intake/README.md` (2: `HARNESS_PIN`, `intake/setup.sh`), `intake/instance/config.yaml` (3), `intake/instance/preamble.md` (1) and `intake/setup.sh` (1);
  - `tests/factory/test_shepherd.py:3`, a docstring naming `docs/spec-factory.md`.

  None of these is in this sub-ticket's pathspec or file list. → CONCERN, out of scope. The overlay files (`factory/**`) fall inside the parent's no-old-paths-in-live-files pathspec, and B/E have to clear them. Until then, the live `generated` protected class names `prompts/**`, which is no longer tracked.

STATUS: VERIFIED
CONFIDENCE: high. I ran all nine acceptance commands verbatim on base and head, ran both gates as written in the given worktree (`70 passed`, exit 0), and confirmed byte-level that the merge left the PR content unchanged and added nothing beyond `main`.
ESCALATIONS:
- Protected paths touched, both declared in the sub-ticket:
  - generated `prompts/**` → `docs/prompts/`, byte-identical (10 × R100, `changed=0 of 10 VERBATIM`);
  - infra `intake/**`, only `intake/README.md` and `intake/instance/context.md`, for D.4 reference updates.
  The merge gate needs human approval for these.
- Out of scope, for B and E: these files still name old paths. B must replace the interim overlay `factory/config.yaml`, `factory/prompts/context.md` and `factory/prompts/preamble.md` (`generated: ["prompts/**"]`, the old `docs/spec-factory.md`/`plans/`/`specs/` text), or the parent's no-old-paths-in-live-files will fail at close. `tests/factory/test_shepherd.py:3` (docstring) names `docs/spec-factory.md`; it is outside that scenario's pathspec, and the spec forbids changing existing tests.
