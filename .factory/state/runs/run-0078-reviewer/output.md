Commit: 7090d9d21f17688df45fd3701dc5ee26f01452c4 (branch `factory/T-0012.5`; merge-base with `main` is `bed7e28`, `main` is `68e8945`)

## Checks, in order

1. **Test integrity.** `git diff --name-status main...HEAD` lists exactly `M dev/build-harness.spec.md`, `M docs/changelog.md`, `M docs/design.md`. No file under `tests/`, no agent prompt, no `docs/prompts/` file (`git diff --stat main...HEAD -- docs/prompts` is empty). Nothing to weaken; "Tests to change: none" holds.

2. **Correctness against F.1–F.4** (compared programmatically against `intake/state/specs/T-0012/v3.md`, the pinned parent, and against `main`'s copy of each file):
   - F.1 `docs/design.md:54`: the "Role-context block" paragraph equals `main`'s line with only its last sentence ("Where the block is kept … are not fixed here.") replaced by the parent's F.1 text, byte for byte. `grep -c 'are not fixed here' docs/design.md` → 0.
   - F.2 `docs/design.md:46`: the piece 8 row equals `main`'s row with `…on the PR itself |` → `…on the PR itself. <F.2 sentence> |`. The added full stop is the one character outside the parent's text; without it the cell would read "…itself The harness code…", so it is the right call, and the line is one of the two design-text-kept excludes.
   - F.3 `docs/changelog.md:46`: entry 42 is the parent's text verbatim, follows 41 directly, and the next non-empty line is `Declined: …`. Numbered list stays contiguous. 42 = `git show main:docs/changelog.md | grep -c '^[0-9][0-9]*\. '` (41) + 1.
   - F.4 `dev/build-harness.spec.md`: D8 row (line 127) carries the parent's Value text verbatim; layout row (line 145) is the parent's string verbatim; item 82 (line 456) equals `main`'s line with every `factory/prompts/design-doc.md` → `docs/design.md` and nothing else changed; the render bullet (line 158) states each of the parent's four points (reads `docs/design.md` in the same repo as the harness, no `--doc`; writes `docs/prompts/` and the `agents/` templates; placeholders filled per instance from `.factory/instance.yaml` at run start; `render --check` diffs against `docs/design.md`) and keeps the addendum-2 rule. `## Responses` (from line 523) is byte-identical to `main`; its line 537 still names `factory/prompts/design-doc.md`, as required.
   - Whole-file diff counts: `docs/design.md` 4 changed lines (2 out, 2 in), `dev/build-harness.spec.md` 8 (4 out, 4 in), `docs/changelog.md` +1. No other line moved.

3. **Scope.** Only the three files the sub-ticket names. `README.md`, `docs/prompts/`, `.factory/`, harness paths untouched.

4. **Silent behavior changes.** None; prose only. No prompt block changed (prompt-copies-moved-unchanged → `changed=0 of 10 VERBATIM`), so no agent's instructions move.

5. **Security / data safety.** Not applicable; no code, no secrets, no destructive ops.

6. **Protected paths.** None touched. `docs/` and `dev/` are not in any class; `generated` (`docs/prompts/**`) unchanged.

7. **Maintainability.** Nothing that will cause real problems. The build spec is now internally inconsistent in places F.4 does not cover (see Out-of-scope), but that was declared out of scope by the parent and is noted by the implementer.

## Acceptance re-run (from the worktree, `BASE=cdb1c6769ecc39208e62edc65578f62f5a23908f` from `parent_base` in `intake/state/tickets/T-0012.yaml`)

| Criterion | Observed |
|---|---|
| design-doc-instance-text (NEW) | `kept=1 open=0 piece8=1 logged=1` |
| build-spec-render-paths (NEW) | `stale=0 new=3 d8=1` (N=3 ≥ 3) |
| changelog-entry-appended (NEW) | `1` |
| responses-unchanged (REGRESSION) | `exit=0` |
| changelog-moved-verbatim (REGRESSION) | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` |
| design-text-kept (REGRESSION) | `0` |
| prompt-copies-moved-unchanged (REGRESSION) | `changed=0 of 10 VERBATIM` |
| no-old-paths, documents only (REGRESSION; T-0012.2's command, `-- README.md docs dev`) | `exit=1` |
| whitespace `git diff --check main...HEAD` | `exit=0`, no output |

Gates: `git diff --check main...HEAD` → exit 0, no output. `PYTHONDONTWRITEBYTECODE=1 uv run --frozen pytest -q -p no:cacheprovider tests/factory` → `92 passed in 134.14s`. `git status --short` in the worktree is empty afterwards.

## Findings

None.

## Prior findings

None (round 1).

## Out-of-scope observations

- `HEAD` does not contain current `main` (`git merge-base --is-ancestor main HEAD` → no). The three commits on `bed7e28..main` (`f809c69`, `e725a5c`, `68e8945`) are intake-store commits; `git diff --stat bed7e28 main -- docs/design.md docs/changelog.md dev/build-harness.spec.md` is empty, so the merge is conflict-free. The merge gate's "head contains main" condition is the harness's to enforce, not a defect in this PR.
- `dev/build-harness.spec.md` still describes the old layout where F.4 did not reach: layout row `factory/prompts/preamble.md … (A)` (line ~140), item 82's `git status --porcelain .claude factory/prompts` and `.claude/agents/factory-verifier.md`, the `AGENTS.md` bullet naming `factory/prompts/**` as a guardrail path (line 160), D6's `factory/config.yaml`, and the bare-repo `factory init` bullet. The parent's Out of scope and the implementer's PR description both name these; a later build-spec pass should reconcile them. Not a finding against this sub-ticket.
- The render bullet now says `render` writes `docs/prompts/`, while the parent's own Decisions keep `docs/prompts/` as hand re-copied verbatim copies until `render` exists. That is what F.4 asked for and `render` is not built, so no action here.

STATUS: APPROVE
CONFIDENCE: high. Every rewritten line was checked byte for byte against the pinned parent text and against `main`; all nine acceptance commands and both gates were run in the worktree and matched the sub-ticket's THEN values.
ESCALATIONS: none
