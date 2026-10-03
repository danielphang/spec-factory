Commit: ebe9baf0843c3421585aa37a03e835617e652f59 (branch `factory/T-0012.2`; `main` = `20849b63a3a632cd43724819d860f71717dc8a53`; `git merge-base HEAD main` = `20849b6`)

Review of T-0012.2 (part D, D.1–D.4), round 2. Per the convergence rule I checked the prior findings and the changed lines only. The only change since round 1 is the merge commit `ebe9baf` (parents `c367bef`, `20849b6`), so "changed lines" is the merge itself.

What I ran from the worktree `intake/state/runs/run-0065-reviewer/wt`:

1. Test integrity. `git diff --name-status -M main...HEAD` lists the same 19 paths as round 1 (README.md, 1 rename-with-edit + 1 new file + 10 R100 renames under `docs/`, 4 renames under `dev/`, `intake/README.md`, `intake/instance/context.md`). `git diff --name-only main HEAD -- tests pyproject.toml uv.lock factory bin agents .gitignore | wc -l` → `0`: the merge carries T-0012.1's suite and project files from `main` untouched. No test weakened, skipped, deleted or added.

2. The merge is mechanical, not an evil merge. `git merge-tree --write-tree 20849b6 c367bef` → tree `62e84c107cd6efc1baf8d047d1d2b6f019b49f4a`, exit 0 (the same tree I computed in round 1); `git rev-parse HEAD^{tree}` → `62e84c107cd6efc1baf8d047d1d2b6f019b49f4a`. Identical, so the head is exactly what git produces by merging the two parents with no hand edits. `git diff --stat c367bef HEAD -- README.md docs dev intake/README.md intake/instance` is empty: the PR's files are byte-for-byte as reviewed in round 1. `git diff --name-only main...HEAD` and `git diff --name-only main HEAD` list the same 19 paths.

3. Correctness. All nine acceptance commands re-run as written on `ebe9baf` with `BASE=$(git rev-parse main)` = `20849b6`:
   - docs-moved-and-split → `old_tracked=0`, no `missing` lines.
   - changelog-moved-verbatim → `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0`.
   - design-text-kept → `0`.
   - prompt-copies-moved-unchanged → `changed=0 of 10 VERBATIM`.
   - no-old-paths, documents only → `exit=1`.
   - how-to-use-names-new-homes → `1`.
   - records-untouched → `0`.
   - green-harness-still-present → `green keeps its harness`.
   - whitespace → `git diff --check main...HEAD; echo "exit=$?"` → `exit=0`.
   Round-1 byte-identity probes still hold: `diff <(tail -n +2 docs/changelog.md) <(git show main:docs/spec-factory.md | sed -n '679,724p')` empty; `diff <(sed -n '1,29p;32,$p' docs/design.md) <(git show main:docs/spec-factory.md | sed -n '1,677p;726,$p')` empty.

4. Gates, exactly as written from the worktree:
   - `git diff --check main...HEAD` → no output, exit 0.
   - `uv run --frozen pytest -q -p no:cacheprovider tests/factory` → uv created the worktree's own `.venv` (`Creating virtual environment at: .venv`, `Installed 6 packages`), then `70 passed in 97.63s`; a second run with stdout to a file for the exit code gave `70 passed in 93.23s`, exit 0. `git status --short --untracked-files=all` afterwards prints nothing (`.venv/` is ignored by `main`'s `.gitignore`). The worktree now has `pyproject.toml`, so uv did not walk up to the dev checkout this time.

5. Scope, silent behaviour changes, security, maintainability: unchanged from round 1 (no new content). Protected paths: both declared by the sub-ticket; listed under ESCALATIONS.

Findings: none new.

Prior findings:
- [SHOULD-FIX] head does not contain current `main`, so the pytest gate cannot pass → RESOLVED. `git merge-base HEAD main` is now `20849b6`; the merge tree equals `git merge-tree` of the two parents; both gates pass on the head itself (`70 passed`, exit 0), not only on a trial merge. A merge rather than a rebase is acceptable: the role forbids force-push, and `main...HEAD` is still exactly this PR's 19 paths.
- [NIT] `README.md:7-10` slightly beyond a token swap → WITHDRAWN as an open item (no change was requested; it stands as disclosed under Known gaps, and E.6 rewrites the file).

Out-of-scope observations (unchanged from round 1; none new):
- `README.md:11` still claims `docs/prompts/` "is regenerated from" the design doc. Pre-existing; E.6's to fix.
- `docs/changelog.md:3` says "the reviewer prompt in the appendix", which now lives in `docs/design.md`. Records are left as written.
- `intake/instance/config.yaml:9` and `intake/instance/preamble.md:38` still name `prompts/**` as the `generated` class; E.5 removes both files.

STATUS: APPROVE
CONFIDENCE: high. The only delta since round 1 is a merge whose tree I matched byte-for-byte against `git merge-tree` of its parents; every acceptance command and both gates were re-run by me on `ebe9baf` and printed the expected output, including `70 passed` with exit 0.
ESCALATIONS:
- Protected path touched, declared in the sub-ticket: generated `prompts/**` moved to `docs/prompts/` byte-identical (`changed=0 of 10 VERBATIM`; 10 × `R100`).
- Protected path touched, declared in the sub-ticket: infra `intake/**`, only `intake/README.md` (lines 4, 42) and `intake/instance/context.md` (lines 3–20), reference updates per D.4. The merge gate requires a human approval for these.
