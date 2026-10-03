Commit: c367bef72e2ed70a4417e98de907c91dbbe31320 (branch `factory/T-0012.2`, base `cdb1c6769ecc39208e62edc65578f62f5a23908f` = `main`, one commit)

## What I checked, in order

1. **Test integrity.** `git ls-files tests | wc -l` → `0`; the repo has no tests, and `git diff --name-status -M main...HEAD` touches no test, CI, AGENTS.md, skill or agent-prompt file. "Tests to change: none" is respected. Nothing to block on.

2. **Correctness against D.1–D.4.** I re-ran every acceptance command from the sub-ticket on the head, from the worktree with bash, `BASE=$(git rev-parse main)`:
   - docs-moved-and-split → `old_tracked=0`, no `missing` lines.
   - changelog-moved-verbatim → `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0`.
   - design-text-kept → `0`.
   - prompt-copies-moved-unchanged → `changed=0 of 10 VERBATIM`.
   - no-old-paths, documents only → `exit=1`.
   - how-to-use-names-new-homes → `1`.
   - records-untouched → `0`.
   - green-harness-still-present → `green keeps its harness`.
   - whitespace → `exit=0` (gate `git diff --check main...HEAD` printed nothing).

   Byte-level checks beyond the acceptance lines:
   - `docs/design.md` with its inserted paragraph removed (`sed -n '1,29p;32,$p'`) is identical to the base `docs/spec-factory.md` with lines 678–725 removed (`diff` printed nothing). So the reverted `x` edit on line 29 that the PR description discloses left no trace; the whole file, not only the line set, matches.
   - `tail -n +2 docs/changelog.md` is identical to base lines 679–724 (`diff` printed nothing): intro paragraph, entries 1–41 and the `Declined:` line, verbatim. The file ends in exactly one `\n` (`od -c`), no trailing blank line.
   - `docs/design.md:680` `## Appendix: reviewer prompt` is preceded by the closing fence and one blank line, so the cut left no double blank.
   - `docs/design.md` has no other mention of "changelog" than the added line 31 (`grep -n -i changelog`), so removing the section left no dangling in-document cross-reference.
   - `git diff --stat -M100% main...HEAD -- prompts docs/prompts` → 10 files, `0 insertions(+), 0 deletions(-)`: D.2's "bytes do not change" holds.
   - `dev/build-harness.plan.md`: 9 `Parent:` lines, 0 of them still naming the old path; `dev/build-harness.spec.md` and `dev/issues.md` are R100 renames.
   - `intake/README.md`: exactly the two reference lines changed (lines 4 and 42, `../issues/README.md` → `../dev/issues.md`, `issues/README.md` → `dev/issues.md`).
   - Remaining `specs/` / `plans/` tokens in `dev/*.md` and `docs/design.md` (e.g. `docs/design.md:78`, `dev/build-harness.plan.md:61,65,…`) are the store's own subdirectory names (`specs/<ID>/v<N>.md`, `plans/T-0001.md` as an output path), not this repo's moved directories. Correctly left alone.

3. **Scope.** Changed set is exactly `README.md`, `docs/**`, `dev/**`, `intake/README.md`, `intake/instance/context.md`; all inside the sub-ticket's file list. `intake/state`, `intake/answers`, `intake/green-pilot`, `intake/.gitignore` untouched (records-untouched = 0). The README hunk the implementer asked reviewers to read: the two bullets that described `specs/<ticket>.md` and `plans/<ticket>.md` as directories of this repo now name the two moved files, and one `dev/issues.md` bullet is added. Those directories no longer exist here, so a pure token swap would have produced a false description; the reword is the smallest change that keeps the references true, and E.6 rewrites the file anyway. I accept it as D.4 reference work, not scope creep.

4. **Silent behavior changes.** None a reader of the live documents would not expect. `intake/instance/context.md` is the source `setup.sh` copies into the running harness's `context.md`; this change does not alter the running copy until `setup.sh` is re-run (this very run's input still carries the old block), which is the intended state for D.

5. **Security / data safety.** Documents only; no secrets, no destructive operations, nothing under `~/.nanobot/` or `~/dev/nanobot-upstream/` read beyond the two `cat-file -e` of the REGRESSION check.

6. **Protected paths.** Two touched, both declared in the sub-ticket: generated `prompts/**` (moved to `docs/prompts/`, byte-identical, verified above) and infra `intake/**` (only `intake/README.md` and `intake/instance/context.md`, verified by `git diff --name-only main...HEAD -- intake`). Listed under ESCALATIONS for the gate; STATUS is the one the code earns.

7. **Maintainability.** Nothing that will cause real problems.

## Findings

None.

## Prior findings

None (round 1).

## Out-of-scope observations

- `README.md:11` still asserts `docs/prompts/` "is regenerated from" the design doc. Parent Evidence says nothing regenerates them. Only the path was in D's scope; E.6's rewrite should drop or correct the claim.
- `docs/changelog.md:3` (kept verbatim) says "the reviewer prompt in the appendix", which now lives in `docs/design.md`. Records are left as written per the sub-ticket; a later doc pass (F or after) may add the cross-reference.
- `intake/instance/config.yaml:9` and `intake/instance/preamble.md:38` still name `prompts/**` as the generated class. Outside this sub-ticket's file list; E.5 deletes both files.

STATUS: APPROVE
CONFIDENCE: high. Every acceptance command and the gate were re-run by me on the committed head with the expected output, and the design doc, changelog body and prompt copies were byte-compared against the base rather than taken from the PR description.
ESCALATIONS: protected paths touched, both declared in the sub-ticket: generated `prompts/**` (moved to `docs/prompts/`, byte-identical); infra `intake/**` (`intake/README.md`, `intake/instance/context.md` only, reference updates). Merge gate needs the human approval the declaration provides for.
