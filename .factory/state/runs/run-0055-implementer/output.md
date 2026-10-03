Sub-ticket: T-0012.2, Document re-layout (parent `intake/state/specs/T-0012/v3.md`, part D, D.1–D.4)
Branch: `factory/T-0012.2` in `/Users/dphang/dev/spec-factory/intake/state/worktrees/T-0012.2`, base `cdb1c6769ecc39208e62edc65578f62f5a23908f` (still `main`), head `c367bef72e2ed70a4417e98de907c91dbbe31320` (one commit).

What changed:
- D.1:
  - `git mv docs/spec-factory.md docs/design.md`.
  - The `## Changelog` section (old lines 678–725, from the heading to the line before `## Appendix`) is cut out of `docs/design.md` and becomes the new `docs/changelog.md`. That file is a `# Changelog` title followed by old lines 679–724 verbatim: the intro paragraph, entries 1–41 and the `Declined:` line. Old line 725, the blank separator before `## Appendix`, is dropped so the file does not end in a blank line.
  - At the end of "How to use this" (after the last wiring-rule bullet, before `## Harness: functional pieces`) there is one new paragraph line: "This document's changelog is `docs/changelog.md`, and `docs/prompts/` holds a verbatim copy of each prompt block in it, changed only by re-copying that block." A blank line separates it from the bullet list.
  - Every other line of `docs/design.md` is unchanged. Checked with `diff <(sed -n '1,29p;32,$p' docs/design.md) <(old lines 1–677 + 726–759)`, which printed nothing.
- D.2: `git mv prompts docs/prompts`. All 10 files are renamed at 100% similarity.
- D.3: `specs/build-harness.md` → `dev/build-harness.spec.md`, `plans/build-harness.md` → `dev/build-harness.plan.md`, `plans/P0-intake-skeleton.md` → `dev/P0-intake-skeleton.md`, `issues/README.md` → `dev/issues.md` (all `git mv`). The spec and the issues index are 100% renames.
- D.4: reference updates.
  - `README.md`, lines 5–11:
    - `docs/spec-factory.md` → `docs/design.md`, and the changelog is now named as `docs/changelog.md`;
    - `prompts/` → `docs/prompts/` (lines 6 and 11);
    - `plans/P0-intake-skeleton.md` → `dev/P0-intake-skeleton.md`;
    - the `specs/<ticket>.md` and `plans/<ticket>.md` bullets now name `dev/build-harness.spec.md` and `dev/build-harness.plan.md`, because the directories they described no longer exist here (see Known gaps);
    - added one bullet for `dev/issues.md`.
  - `dev/build-harness.plan.md`: the 9 `Parent:` lines now read `dev/build-harness.spec.md`. Line 3's GitHub URL now ends `/blob/main/dev/build-harness.spec.md`.
  - `dev/P0-intake-skeleton.md:3`: `specs/build-harness.md` → `dev/build-harness.spec.md`, `plans/build-harness.md` → `dev/build-harness.plan.md`.
  - `intake/README.md`: line 4 `../issues/README.md` → `../dev/issues.md`; line 42 `issues/README.md` → `dev/issues.md`. `HARNESS_PIN` and `intake/setup.sh` are left alone: D does not move them, and E removes them.
  - `intake/instance/context.md`, lines 3–20: the design doc, changelog, build spec, build plan, P0 skeleton and prompt-copy paths now point to the new homes. "the Changelog section at its end" now reads "its changelog entry in `docs/changelog.md`", because the changelog no longer sits at the end of the design doc.
- Records are untouched: `intake/state/`, `intake/answers/`, `intake/green-pilot/`, `intake/.gitignore` and the changelog entries.

Acceptance results (run from the worktree with bash; `BASE=$(git rev-parse main)` = `cdb1c67…`):

| Criterion | Before (at base) | After (at `c367bef`) |
|---|---|---|
| docs-moved-and-split | seven `missing …` lines, `old_tracked=15` | `old_tracked=0` |
| changelog-moved-verbatim | `DIFFERENT` / `declined= numbering=NONE in_design=` | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` |
| design-text-kept | `570` | `0` |
| prompt-copies-moved-unchanged | `changed=10 of 10 DRIFT` | `changed=0 of 10 VERBATIM` |
| no-old-paths, documents only | `exit=0` | `exit=1` |
| how-to-use-names-new-homes | `awk: can't open file docs/design.md` then `0` | `1` |
| records-untouched | `0` (vacuous: the branch had no commits yet) | `0` |
| green-harness-still-present (REGRESSION) | `green keeps its harness` | `green keeps its harness` |
| whitespace (REGRESSION) | `exit=0` | `exit=0` |

Gate, as written: `git diff --check main...HEAD` printed nothing, exit 0.

Extra checks:
- `diff <(tail -n +2 docs/changelog.md) <(sed -n '679,724p' <base design doc>)` matched, so the whole changelog body is byte-identical, not only the numbered lines.
- `git diff --name-status -M main...HEAD` touches only `docs/**`, `dev/**`, `README.md`, `intake/README.md` and `intake/instance/context.md`.
- `git status --short` is empty after the commit.

Tests added/changed: none. This repo has no tests, and part D is a document move whose checks are the acceptance commands above. "Tests to change: none" is respected.

Known gaps and uncertainties:
- **Reviewers should compare the README hunk, not only the path tokens.** D.4 says "only references are updated" in `README.md`, but lines 7–8 described `specs/<ticket>.md` and `plans/<ticket>.md` as this repo's directories, and both directories are gone. I reworded them to name the two moved files (`dev/build-harness.spec.md`, `dev/build-harness.plan.md`) and added one `dev/issues.md` bullet. That is slightly more than a token swap. E.6 rewrites README in full anyway.
- `README.md:11` still says `docs/prompts/` "is regenerated from" the design doc. The parent Evidence says nothing regenerates the copies. I kept the claim because only the path is in D's scope, and E.6 rewrites it.
- One unintended edit happened during the work and was reverted. An Edit call replaced part of `docs/design.md` line 29 with `x`. I did not patch it by hand: I regenerated `docs/design.md` from `git show HEAD:docs/spec-factory.md` with the same split, then re-applied the insertion with a scripted line-29 insert. The full-file `diff` against the base (above) and `design-text-kept` = `0` show no trace of it in the commit.
- The "one added line" sits in its own paragraph, so it brings one blank separator line with it.
- Process note: the session scratchpad is shared with the parallel T-0012.1 run. My first acceptance script there (`acc.sh`) was overwritten mid-run with T-0012.1's checks. I re-ran everything from a uniquely named `T-0012.2-acc.sh`. All "after" results above come from that file, run against the committed head.

Out-of-scope observations:
- `intake/instance/config.yaml:9` (`generated: ["prompts/**"]`) and `intake/instance/preamble.md:38` (`generated (prompts/**, …)`) still name the old prompt-copy path. Both files are outside this sub-ticket's file list, which allows only `intake/README.md` and `intake/instance/context.md` under `intake/`. E.5 deletes them. Until then, the running copy's protected-paths line names `prompts/**` rather than `docs/prompts/**`. The live harness under `intake/harness/` changes only when `setup.sh` is re-run, so editing `context.md` here does not change the briefing the running copy uses either.
- The changelog's intro paragraph (kept verbatim) says the review rounds used "the reviewer prompt in the appendix". That appendix is now in `docs/design.md`, not in `docs/changelog.md`. Part F, or a later doc pass, may want a cross-reference. I did not add one, because records are left as written.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance criterion and the gate were run on the committed head and gave the expected output; the changelog body and the rest of the design doc were checked byte for byte against the base.
ESCALATIONS: none
