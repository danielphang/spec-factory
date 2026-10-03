Commit: aeb684d96544915c57435bd904959b3af45999ce

Setup:
- Head: the given worktree `/Users/dphang/dev/spec-factory/intake/state/runs/run-0084-verifier/wt`. `git rev-parse HEAD` printed `aeb684d…`, `git status --short` was empty, and `main` = merge-base = `68e89456939ac7939ef659975dfbb37812bd6f83`.
- Base: a scratch `git clone` of `~/dev/spec-factory`, detached at `68e8945`, with local `main` at `68e8945`. Nothing in the real repo was touched for this.
- `BASE` for the parent scenarios is the parent's recorded base, `cdb1c6769ecc39208e62edc65578f62f5a23908f` (`parent_base` in `intake/state/tickets/T-0012.yaml`), as the plan's readings require.
- Each command was copied verbatim from the parent spec (v3) or from the sub-ticket intermediates. The no-old-paths command comes from `intake/state/specs/T-0012.2/subticket.md:19`, and the whitespace command from `T-0012.2/subticket.md:28`. All of them ran from one script against both trees.
- `git diff --stat main...HEAD`: 3 files (`dev/build-harness.spec.md`, `docs/changelog.md`, `docs/design.md`), 7 insertions and 6 deletions. `docs/prompts/` is untouched.

Per criterion: NEW/REGRESSION | command | base | PR | PASS/FAIL
- NEW | design-doc-instance-text | `kept=0 open=1 piece8=0 logged=0` | `kept=1 open=0 piece8=1 logged=1` | PASS
- NEW | build-spec-render-paths | `stale=3 new=0 d8=0` | `stale=0 new=3 d8=1` (N=3 ≥ 3; lines 145, 158, 456) | PASS
- NEW | changelog-entry-appended | `0` | `1` | PASS
- REGRESSION | responses-unchanged | `exit=0` | `exit=0` | PASS
- REGRESSION | changelog-moved-verbatim | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` | PASS
- REGRESSION | design-text-kept | `0` | `0` | PASS
- REGRESSION | prompt-copies-moved-unchanged | `changed=0 of 10 VERBATIM` | `changed=0 of 10 VERBATIM` | PASS
- REGRESSION | no-old-paths, documents only | `exit=1` | `exit=1` | PASS
- REGRESSION | whitespace (sub-ticket diff), `git diff --check main...HEAD; echo "exit=$?"` | `exit=0` | `exit=0` | PASS

Each NEW criterion fails on base for the reason the spec gives (the text is absent, and the base has the three stale hits) and passes on the PR.

Gate suite: PASS
- `git diff --check main...HEAD`: printed nothing, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `92 passed in 98.51s (0:01:38)`, exit 0. An earlier run printed `92 passed in 101.01s`. The worktree was clean afterwards: only ignored `.venv/` and `__pycache__/` were added.

Probes: input → result → OK / CONCERN
- F.1 sentence from `intake/state/specs/T-0012/v3.md`, taken as a fixed string (861 chars) and checked against the `**Role-context block.**` line, preceded by the paragraph's unchanged prior sentence → 1 match. The paragraph text before the replaced sentence is byte-equal to `main` → OK. The text is verbatim, not a paraphrase that only satisfies the `.factory/context.md` grep.
- Piece 8 row: rebuilt `main`'s row with ". " + the F.2 sentence after "on the PR itself" and compared it to the PR's row → identical (`piece8_exact`). The only extra character is the full stop the implementer disclosed. The sentence sits in column 3, "What it must do" → OK.
- Changelog entry 42 vs the F.3 text (625 chars), whole-line fixed-string match `42. <F.3>` → 1. The entry sits after 41 and before `Declined:`, and numbering stays contiguous → OK.
- D8 Value cell and layout row vs the F.4 strings, whole-field fixed-string match → 1 and 1 → OK.
- Boundary of the stale check (it matches only `factory/prompts/design-doc.md`): looked for any `design-doc` before `## Responses` (line 523) → line 335 still says "`render` from `design-doc.md`" (Round-4 seam summary). F.4 and the sub-ticket name only lines 145, 158 and 456, so this does not break a stated criterion → CONCERN (out of scope, noted below).

Out-of-scope observations:
- `dev/build-harness.spec.md:335` (before `## Responses`) still names `design-doc.md` as render's source. The stale criterion does not catch it because it lacks the `factory/prompts/` prefix. The implementer's list of other old-layout leftovers (layout row `factory/prompts/preamble.md`, item 82's `git status --porcelain .claude factory/prompts`, the `AGENTS.md` guardrail bullet, D6's `factory/config.yaml`, the bare-repo `factory init`) is also accurate as far as I read. All of these are for a later build-spec pass.

STATUS: VERIFIED
CONFIDENCE: high. Every acceptance command and both gates ran on the exact head, and the base comparison ran in a separate clone. The inserted prose was fixed-string matched against the parent's F.1–F.4 text.
ESCALATIONS: none
