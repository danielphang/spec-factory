Commit: 7090d9d21f17688df45fd3701dc5ee26f01452c4 (branch `factory/T-0012.5`, worktree `intake/state/runs/run-0072-reviewer/wt`; `main` = `bed7e2883d86583731c111036fde925fa513d34d` = merge base, one commit ahead)

## What I checked, in the role's order

1. **Test integrity.** `git diff --stat main...HEAD`: `dev/build-harness.spec.md | 8`, `docs/changelog.md | 1`, `docs/design.md | 4`; 3 files, 7 insertions, 6 deletions. No file under `tests/`, no agent prompt, no `docs/prompts/` file. `prompt-copies-moved-unchanged` → `changed=0 of 10 VERBATIM`. Nothing to block on.

2. **Correctness against F.1–F.4.** I extracted each quoted string from the pinned parent (`intake/state/specs/T-0012/v3.md`) and matched it with `grep -F` against the worktree:
   - F.1 (861 chars) → 1 match on the `**Role-context block.**` line of `docs/design.md` (line 54). The old closing sentence is gone (`open=0`).
   - F.2 (134 chars) → 1 match inside the `| 8 |` row (line 46). Joined as `…on the PR itself. The harness code…`; on `main` the cell ended `…on the PR itself |`. The added full stop is the only non-spec character, it is on a line `design-text-kept` already excludes, and without it the cell would read as one run-on sentence. Fine.
   - F.3 (625 chars) → 1 match as `42. …` at `docs/changelog.md:46`, before `Declined:` at line 48. `main` has 41 numbered entries; 42 is one past. Placement before `Declined:` keeps the numbered list contiguous and `changelog-moved-verbatim` compares only the first 41, so it is the right spot.
   - F.4 D8 value (231 chars) → 1 match on the `| D8 |` row. Layout row → the exact string from the spec, 1 match. Item 82: all three `factory/prompts/design-doc.md` replaced; the only remaining hit is line 537, inside `## Responses` (heading at line 523), which F.4 says to leave. Render bullet: reads `docs/design.md`, same repo as the harness, no `--doc`, writes `docs/prompts/` and the `agents/` templates, placeholders filled per instance from `.factory/instance.yaml` at run start, `render --check` diffs against `docs/design.md`; the addendum-2 rule is kept verbatim. That is every clause F.4 asks for.
   - The two rewritten `docs/design.md` lines are 46 and 54 (`git diff -U0`); the first prompt block starts at line 167. So no `docs/prompts/` copy could have drifted, and the regression scenario confirms it.

   Acceptance, all run by me from the worktree with `BASE=cdb1c6769ecc39208e62edc65578f62f5a23908f` (`parent_base` in `intake/state/tickets/T-0012.yaml`):

   | Criterion | Result |
   |---|---|
   | design-doc-instance-text | `kept=1 open=0 piece8=1 logged=1` |
   | build-spec-render-paths | `stale=0 new=3 d8=1` (N=3 ≥ 3) |
   | changelog-entry-appended | `1` |
   | responses-unchanged | `exit=0` |
   | changelog-moved-verbatim | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` |
   | design-text-kept | `0` |
   | prompt-copies-moved-unchanged | `changed=0 of 10 VERBATIM` |
   | no-old-paths, documents only (`-- README.md docs dev`) | `exit=1` |
   | `git diff --check main...HEAD` | `exit=0` |
   | `uv run --frozen pytest -q -p no:cacheprovider tests/factory` | `92 passed in 127.80s` |

   The PR description's numbers match mine. Its honesty note is right: `responses-unchanged` is a preservation check that passes trivially before the edit; its value is passing after.

3. **Scope.** Only the three files the sub-ticket allows. No `README.md`, no harness path, no `docs/prompts/`.

4. **Silent behaviour changes.** None possible; prose only, and no prompt copy or agent template changed.

5. **Security and data safety.** Nothing applicable. The commit was made with `core.hooksPath=/dev/null`; I did not re-verify the implementer's claim that the hooks dir holds only samples, but no hook enforces anything for this repo's documents, and the gates were run directly.

6. **Protected paths.** None touched. `docs/prompts/**` (generated) is byte-identical to `main`; nothing under `intake/**`; nothing read from `~/.nanobot/`; `~/dev/nanobot-upstream` not needed for this sub-ticket.

7. **Maintainability.** The new layout row (`docs/design.md (spec-factory, beside the harness)  the design doc; …`) breaks the two-column alignment of that ASCII table because the left cell is longer than the column. It is the spec's exact text, so not a finding.

## Findings

None.

## Prior findings

None (round 1).

## Out-of-scope observations

- The build spec still describes the old layout where F.4 did not reach: layout row `factory/prompts/preamble.md … (A)`, item 82's `git status --porcelain .claude factory/prompts` (line 456) and `.claude/agents/factory-verifier.md` (lines 417, 419, 456), the `AGENTS.md` bullet naming `factory/prompts/**` as a guardrail path, D6's `factory/config.yaml`, and the bare-repo `factory init`. The implementer listed the same set. A later build-spec pass should take them together.
- The render bullet now says `factory render` writes `docs/prompts/`, while the parent's Out of scope says `docs/prompts/` stays a set of hand-copied verbatim files until render exists. Both are true at once (render is not built), but the build spec should say so when render is specified.

STATUS: APPROVE
CONFIDENCE: high. Every acceptance command and both gates were re-run by me on head 7090d9d and gave the sub-ticket's targets; every inserted string matches the pinned spec byte-for-byte; the diff is confined to the three permitted files.
ESCALATIONS: none
