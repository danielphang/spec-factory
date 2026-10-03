Commit: c367bef72e2ed70a4417e98de907c91dbbe31320 (branch `factory/T-0012.2`, one commit on `cdb1c6769ecc39208e62edc65578f62f5a23908f`; `main` is `20849b63a3a632cd43724819d860f71717dc8a53`, so `main...HEAD` uses merge-base `cdb1c67`)

Review of T-0012.2 (part D, D.1–D.4), round 1.

What I checked, in the role's order, with what I ran from the worktree:

1. Test integrity. `git diff --name-status -M main...HEAD` touches `README.md`, `docs/**` (1 rename-with-edit, 1 new file, 10 pure renames), `dev/**` (4 renames, 2 with reference edits), `intake/README.md`, `intake/instance/context.md`. No test file is in the diff. The branch itself has no `tests/` (it predates T-0012.1's merge); `main` has `tests/factory/**` and the diff leaves it alone. Nothing weakened, skipped or deleted.

2. Correctness against D.1–D.4. Every parent scenario this sub-ticket cites passes on the head, run as written with `BASE=$(git rev-parse main)`:
   - docs-moved-and-split → `old_tracked=0`, no `missing` lines.
   - changelog-moved-verbatim → `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0`.
   - design-text-kept → `0`.
   - prompt-copies-moved-unchanged → `changed=0 of 10 VERBATIM`.
   - no-old-paths, documents only → `exit=1`.
   - how-to-use-names-new-homes → `1`.
   - records-untouched → `0`.
   - green-harness-still-present → `green keeps its harness`.
   - whitespace → `git diff --check main...HEAD` exit 0.
   Beyond the scenarios, I reproduced the implementer's byte-level claims independently: `diff <(tail -n +2 docs/changelog.md) <(git show main:docs/spec-factory.md | sed -n '679,724p')` is empty (changelog body byte-identical, not only the numbered lines); `diff <(sed -n '1,29p;32,$p' docs/design.md) <(git show main:docs/spec-factory.md | sed -n '1,677p;726,$p')` is empty (every other line of the design doc unchanged). Line arithmetic agrees: 759 old = 713 (`design.md`) + 47 (`changelog.md`) − 1 (title) − 2 (added line + blank). `## Appendix` at `docs/design.md:680` is preceded by exactly one blank line (`678` is the closing fence). `docs/changelog.md` ends with a single `\n`. The added line sits at `docs/design.md:31`, the last line of "How to use this" before `## Harness: functional pieces`, and names both `docs/changelog.md` and `docs/prompts/`. `dev/build-harness.plan.md` has 9 `Parent: \`dev/build-harness.spec.md\`` lines; `dev/P0-intake-skeleton.md:3`, `intake/README.md:4,42` and `intake/instance/context.md:3-20` point at the new homes. The remaining `specs/`/`plans/` tokens in `dev/build-harness.plan.md` and `dev/P0-intake-skeleton.md` are store-layout paths (`specs/<ID>/v<N>.md`, `plans/T-0001.md`, `knowledge_vault/specs/`), not this repo's moved directories; D.4 does not ask for them and the scenario's patterns exclude them.

3. Scope. All touched files are in the sub-ticket's file list. See the NIT on README below.

4. Silent behaviour changes. None for a reader of the documents. The live harness under `intake/harness/` reads `intake/instance/*` only when `setup.sh` re-runs, so the `context.md` edit changes no running briefing (the implementer says the same).

5. Security and data safety. Nothing applicable: document moves, no secrets, no deletions of records (`intake/state`, `intake/answers`, `intake/green-pilot`, `intake/.gitignore` untouched per records-untouched).

6. Protected paths: both declared by the sub-ticket; listed under ESCALATIONS.

7. Maintainability: no concerns.

Findings:

- [SHOULD-FIX] branch `factory/T-0012.2` @ `c367bef`, base `cdb1c67`: the head does not contain current `main` (`20849b6`, which merged T-0012.1). The run's second gate command, `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, exits 4 on this head with `no tests ran in 0.00s`, because `pyproject.toml` and `tests/` do not exist at `cdb1c67` → as it stands the declared gate cannot pass on this branch, and the merge gate (design, changelog 17: the head must contain current main) would refuse it. Rebase or merge `main` into the branch and re-run both gate commands. Evidence this is mechanical: `git merge-tree --write-tree main HEAD` exits 0 with no conflicts (tree `62e84c1`), and in a scratch extraction of that tree `uv sync --frozen` then `PYTHONDONTWRITEBYTECODE=1 uv run --frozen pytest -q -p no:cacheprovider tests/factory` gave `70 passed in 121.80s`; the documents-only no-old-paths grep on the merged tree also gives `exit=1`. This is a dispatch/sequencing gap, not a defect in the diff; I rate it SHOULD-FIX rather than BLOCKING because the change itself is correct and the fix is a no-conflict rebase.

- [NIT] `README.md:7-10`: the two `specs/<ticket>.md` / `plans/<ticket>.md` bullets are reworded to name `dev/build-harness.spec.md` and `dev/build-harness.plan.md`, and a `dev/issues.md` bullet is added. That is one line of new content beyond D.4's "update the references" → slightly outside the letter of "content is unchanged apart from the path updates". It is truthful (a token swap would have described a `dev/<ticket>.md` convention that does not exist), the implementer disclosed it under Known gaps, and E.6 replaces the file. No change requested.

Prior findings: none (round 1).

Out-of-scope observations:
- `README.md:11` still says `docs/prompts/` "is regenerated from" the design doc; the parent's Evidence says nothing regenerates it. Pre-existing claim, E.6's to fix.
- `docs/changelog.md:3` says "the reviewer prompt in the appendix"; the appendix now lives in `docs/design.md`. Records are left as written; part F or a later doc pass could add the cross-reference.
- `intake/instance/config.yaml:9` (`generated: ["prompts/**"]`) and `intake/instance/preamble.md:38` still name `prompts/**`. Outside this sub-ticket's `intake/` allowance; E.5 removes both files. Until then the running copy's protected-paths line is stale by one path.
- The sub-ticket header gives base `20849b6` while the implementer's PR description gives `cdb1c67` "(still `main`)". Both are consistent with `main` having advanced after the branch was cut (the T-0012.1 merge plus store commits); see the SHOULD-FIX.

STATUS: APPROVE
CONFIDENCE: high. Every cited acceptance scenario and both byte-identity claims were re-run by me on `c367bef` and matched; the only open item is the missing rebase, which I verified merges without conflict and keeps the suite at 70 passed.
ESCALATIONS:
- Protected path touched, declared in the sub-ticket: generated `prompts/**` moved to `docs/prompts/` byte-identical (`changed=0 of 10 VERBATIM`; 10 × `R100`).
- Protected path touched, declared in the sub-ticket: infra `intake/**`, only `intake/README.md` (lines 4, 42) and `intake/instance/context.md` (lines 3–20), reference updates per D.4. The merge gate requires a human approval for these.
