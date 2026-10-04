Commit: 7090d9d21f17688df45fd3701dc5ee26f01452c4 (branch `factory/T-0012.5`; base and `main` = bed7e2883d86583731c111036fde925fa513d34d)

Clean environment: two fresh `git clone --no-local` copies of `~/dev/spec-factory` in my scratchpad, one left on `main` (= base `bed7e28`) and one checked out at `factory/T-0012.5` (`7090d9d`). In both, `main` = `bed7e28`, so `git show main:` and `main...HEAD` resolve the same as in the worktree. The parent-scenario `BASE` is the parent's recorded base, `parent_base: cdb1c6769ecc39208e62edc65578f62f5a23908f` (`intake/state/tickets/T-0012.yaml:74`), exported before every run. Every command was copied verbatim from the sub-ticket, the parent spec v3, or T-0012.2's subticket (`intake/state/specs/T-0012.2/subticket.md:19`, for no-old-paths documents-only), and run from a single script on both trees.

Per criterion: NEW/REGRESSION | command | base (bed7e28) | PR (7090d9d) | PASS/FAIL
- NEW | design-doc-instance-text | `kept=0 open=1 piece8=0 logged=0` | `kept=1 open=0 piece8=1 logged=1` | PASS
- NEW | build-spec-render-paths | `stale=3 new=0 d8=0` | `stale=0 new=3 d8=1` (N=3 ≥ 3) | PASS. On base, the stale hits are lines 145, 158 and 456, as the sub-ticket says. On the PR, the only `factory/prompts/design-doc.md` left is line 537, after `## Responses` (line 523).
- NEW (intermediate, F.3) | changelog-entry-appended | `0` | `1` | PASS
- NEW (intermediate, F.4) | responses-unchanged | `exit=0` | `exit=0` | **SPEC-DEFECT**. It passes on base as well as on the PR. The command diffs `main`'s `## Responses` section against the working tree's, so on base it compares the file with itself and passes before any edit. It is an invariant (a REGRESSION check) labelled NEW, so it cannot show that the change did anything. It does what it is meant to: the section is unchanged on the PR. The fix is to relabel it, the same as T-0012.2's records-untouched after run-0057. The implementer flagged the same point in the PR description.
- REGRESSION | changelog-moved-verbatim | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` | PASS
- REGRESSION | design-text-kept | `0` | `0` | PASS
- REGRESSION | prompt-copies-moved-unchanged | `changed=0 of 10 VERBATIM` | `changed=0 of 10 VERBATIM` | PASS
- REGRESSION | no-old-paths, documents only (T-0012.2 command) | `exit=1` | `exit=1` | PASS
- REGRESSION | whitespace, `git diff --check main...HEAD; echo "exit=$?"` | `exit=0` | `exit=0` | PASS

Gate suite: PASS. Both commands were run from the worktree `/Users/dphang/dev/spec-factory/intake/state/runs/run-0071-verifier/wt`, exactly as written:
- `git diff --check main...HEAD` printed nothing, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `92 passed in 102.79s` on the first run. A second run, to capture the exit code, printed `92 passed in 96.34s (0:01:36)` and exit 0.
- `git status --short` in the worktree is empty afterwards.

Text checks, independent of the acceptance greps (Python substring match of the parent v3 quoted text against the PR files):
- F.1 replacement text is in `docs/design.md` verbatim and ends the `**Role-context block.**` paragraph. A word diff shows that only the old sentence was removed.
- F.2 sentence is in the piece 8 row verbatim. The only change outside it is a full stop added after "itself", which the PR description discloses.
- F.3 entry `42. After issue #19 (2026-10-02): …` is in `docs/changelog.md` verbatim.
- F.4: the D8 Value cell and the layout row match the parent's text character for character, as read from the diff. The render bullet now says it reads `docs/design.md`, has no `--doc`, writes `docs/prompts/` and the `agents/` templates, fills placeholders per instance from `.factory/instance.yaml` at run start, and that `render --check` diffs against `docs/design.md`. Item 82 has all three paths replaced.
- `git diff --name-only main...HEAD` lists only `dev/build-harness.spec.md`, `docs/changelog.md` and `docs/design.md` (+7 −6).

Probes:
- Every tracked file, searched for the removed sentence fragment `not fixed here` (`git grep`) → hits only under `intake/state/**` and `intake/answers/**`, which are records; none in `docs/`, `dev/` or `README.md` → OK.
- Boundary of the Responses cut (could a second `## Responses` heading, or a stale path just before it, hide a hit?) → exactly one `## Responses` heading (line 523), and the whole file has one `factory/prompts/design-doc.md` hit (line 537, inside Responses). `new=3` is exactly lines 145, 158 and 456, the three rewritten lines, so the counts are not inflated by anything else → OK.
- Uniqueness of the matched lines (could `kept=1` and `piece8=1` come from a stray duplicate line?) → `docs/design.md` has one `**Role-context block.**` paragraph and one `| 8 |` row. The only other line that mentions a role-context block (line 84, the routing table) does not contradict the new text → OK.
- Changelog structure → entry 42 sits between entry 41 and the `Declined:` line, which is still the last line of the file. Numbering is contiguous 1–42, and the diff adds 1 line and removes none, so no other entry changed → OK.

None of the probes shows special-casing: the edits are the parent's prose, inserted verbatim at the places the spec names.

Out-of-scope observations (not criteria, not blocking):
- After this change, `dev/build-harness.spec.md` contradicts itself. The render bullet (line 158) says render writes the `agents/` templates, but item 82 (line 456) still checks `git status --porcelain .claude factory/prompts` and edits `.claude/agents/factory-verifier.md`. The layout row `factory/prompts/preamble.md` (around line 140), D6's `factory/config.yaml` and the `AGENTS.md` guardrail bullet also still describe the old layout. F.4 does not name any of these, and the implementer already listed them for a later build-spec pass.

STATUS: SPEC-DEFECT
CONFIDENCE: high. I ran every command on fresh clones of base and PR, and both gates in the worktree. The only defect is a labelling one: NEW criterion responses-unchanged passes on base by construction. The change itself meets every other criterion, and its text is verbatim from the parent.
ESCALATIONS:
- responses-unchanged is labelled NEW but cannot fail on base (it diffs `main` against an unchanged tree). It should be relabelled REGRESSION or invariant, as was done for T-0012.2's records-untouched after run-0057. The operator then decides whether to re-verify or accept. Apart from this label, I found nothing that would block merging this PR.
