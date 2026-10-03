Sub-ticket: T-0012.5, "Design-doc and build-spec text for `.factory/` instances" (`intake/state/specs/T-0012.5/subticket.md`; parent `intake/state/specs/T-0012/v3.md`, part F)
Branch: `factory/T-0012.5` in `/Users/dphang/dev/spec-factory/intake/state/worktrees/T-0012.5`, base `bed7e2883d86583731c111036fde925fa513d34d`, head `7090d9d21f17688df45fd3701dc5ee26f01452c4` (one commit). `git diff --stat main...HEAD`: `dev/build-harness.spec.md | 8`, `docs/changelog.md | 1`, `docs/design.md | 4`; 3 files, 7 insertions, 6 deletions.

## What changed

- **F.1, `docs/design.md` "Role-context block" paragraph (line 54).** I replaced the last sentence, "Where the block is kept, and how a harness serving more than one repo picks the right one, are not fixed here.", with the parent's F.1 text word for word: the block lives at `.factory/context.md`, what the instance holds, how the harness finds the instance by walking up or by override with no fallback, and the composer and preamble filling.
- **F.2, `docs/design.md` piece 8 row (line 46), "What it must do" cell.** I appended "The harness code (its package, entry point, agent templates and dependency lock) is itself a protected path in the repo that holds it." The cell used to end "…needs a human approval on the PR itself" with no full stop, so I added one before the new sentence. That full stop is the only character I changed outside the parent's text, and it is on the line that design-text-kept excludes.
- **F.3, `docs/changelog.md`.** I added entry `42. After issue #19 (2026-10-02): …`, using the parent's F.3 text word for word. It sits right after entry 41 and before the `Declined:` line, so the numbered list stays together. 42 is one past main's last entry: `git show main:docs/changelog.md | grep -c '^[0-9][0-9]*\. '` printed 41.
- **F.4, `dev/build-harness.spec.md`:**
  - **D8 row, Value column.** It now reads "per instance: `repo_name` and `protected_paths` in the target repo's `.factory/instance.yaml` (doc §Harness, role-context block); for nanobot: `nanobot`; protected: `infra`, `dependencies`, `credentials`, `public API` (globs in F)".
  - **Layout row (line 145).** It is now `docs/design.md (spec-factory, beside the harness)  the design doc; the only doc `factory render` reads (A)`, exactly as F.4 gives it.
  - **Part A `factory render` bullet (line 158):**
    - It now says that render reads `docs/design.md`, which is in the same repo as the harness, reads no other path and still has no `--doc` option.
    - It writes `docs/prompts/` and the `agents/` templates from the prompt blocks.
    - The addendum-2 added rule is kept as it was.
    - New sentence: the placeholders (`{repo name}`, protected paths, `{2}`, `{400}`, `{gate commands}`, `{3}`, `{5}`, `{force-push allowed}`) are filled per instance from `.factory/instance.yaml` when a run starts.
    - `render --check` now diffs against `docs/design.md`.
    - Removed: "writes `factory/prompts/preamble.md` and the eight `.claude/agents/factory-<role>.md` bodies", "under the guardrail glob `factory/prompts/**`" and "filled from `config.yaml`". F.4 replaces each of them.
  - **Item 82 (line 456).** All three `factory/prompts/design-doc.md` there became `docs/design.md`. Nothing else on that line changed.
  - **`## Responses`.** Not touched. Its line 537 still says `factory/prompts/design-doc.md`, as the ticket requires.

No `docs/prompts/` file changed: neither line I rewrote in `docs/design.md` is inside a prompt block.

## Acceptance results

Every command below was run from the worktree with `BASE=cdb1c6769ecc39208e62edc65578f62f5a23908f`, the parent's recorded base (`parent_base` in `intake/state/tickets/T-0012.yaml`). The commands are the parent spec's WHEN lines and the sub-ticket's intermediates, copied verbatim.

| Criterion | Before (base `bed7e28`) | After (`7090d9d`) |
|---|---|---|
| design-doc-instance-text (NEW) | `kept=0 open=1 piece8=0 logged=0` | `kept=1 open=0 piece8=1 logged=1` |
| build-spec-render-paths (NEW) | `stale=3 new=0 d8=0` | `stale=0 new=3 d8=1` (N=3 ≥ 3) |
| changelog-entry-appended (NEW, F.3) | `0` | `1` |
| responses-unchanged (NEW, F.4) | `exit=0` | `exit=0` |
| changelog-moved-verbatim (REGRESSION) | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` |
| design-text-kept (REGRESSION) | `0` | `0` |
| prompt-copies-moved-unchanged (REGRESSION) | `changed=0 of 10 VERBATIM` | `changed=0 of 10 VERBATIM` |
| no-old-paths, documents only (REGRESSION; T-0012.2's command) | `exit=1` | `exit=1` |
| whitespace, `git diff --check main...HEAD` (REGRESSION) | `exit=0` | `exit=0` |

Notes on the results:
- **responses-unchanged already printed `exit=0` before the change.** It is labelled NEW but it is a preservation check: it compares the section against `main`, so it passes trivially before any edit. Its value is that it still passes after the edit, and it does.
- **The three stale hits before the change were lines 145, 158 and 456**, the ones the sub-ticket names. After the change, `grep -n 'factory/prompts/design-doc\.md' dev/build-harness.spec.md` finds only line 537, which is inside `## Responses`.
- **Extra check.** `diff <(git show main:docs/design.md) docs/design.md | grep -c '^[<>]'` printed `4`: two lines out, two lines in. Those are the only two lines this sub-ticket rewrites.

Gates (run from the worktree, exactly as written):
- `git diff --check main...HEAD` printed nothing (exit 0).
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `92 passed in 93.75s (0:01:33)`.
  - The first `uv run` created the worktree's `.venv`, which `.gitignore` ignores (`git status --short` is empty).
  - uv warned that the inherited `VIRTUAL_ENV` (`/Users/dphang/dev/nanobot/.venv-test`) does not match the project environment and would be ignored. So the suite ran with the worktree's own `.venv`.

## Tests added/changed

None. This sub-ticket changes prose only, and "Tests to change" is none. The acceptance commands above are the checks for it.

## Known gaps and uncertainties

- **Full stop added to the piece 8 cell.** "itself" became "itself." so that the appended sentence reads as a separate sentence. F.2 says only "Append". If the gate wants the cell otherwise byte-identical, the alternative is "…on the PR itself; the harness code…", but that departs from F.2's wording instead.
- **Placement of changelog entry 42.** I put it after entry 41 and before the `Declined:` line, not after `Declined:` at the end of the file. "Append one entry" leaves this open. This placement keeps the numbered list together, and changelog-moved-verbatim still passes.
- **What the render bullet dropped.** It no longer says that render writes `factory/prompts/preamble.md` or fills placeholders from `config.yaml`, because F.4 says render writes `docs/prompts/` and the `agents/` templates and that placeholders are filled when a run starts. I did not keep the old "guardrail glob `factory/prompts/**`" wording, and I did not claim that `docs/design.md` is a guardrail path, because nothing in the parent says it is.
- **The commit was made with `git -c core.hooksPath=/dev/null`.** No hook was skipped: `core.hooksPath` is unset and the repo's hooks directory holds only `.sample` files. I checked this after the commit.
- **Not done by me:** a fresh reviewer's reading of the prose. I checked it only with the acceptance commands and by reading the word diff.

## Out-of-scope observations

- **The build spec still describes the old layout in places this ticket does not cover:**
  - The layout row `factory/prompts/preamble.md  doc §Shared preamble, placeholders filled (A)` (around line 140).
  - Item 82's `git status --porcelain .claude factory/prompts` and `.claude/agents/factory-verifier.md`.
  - The `AGENTS.md` bullet naming `factory/prompts/**` as a guardrail path.
  - D6's `factory/config.yaml`.
  - The bare-repo `factory init` (the parent's own out-of-scope observation).
  F.4 does not list any of these. A later build-spec pass should reconcile them.
- **Possible ambiguity on the input's single-output-file rule.** The context block says the output file is "the only file you may create or modify". As Implementer, I also edited the three files in my worktree and committed on `factory/T-0012.5`, which is what the role and "Where you work" require. I have not listed this under ESCALATIONS. I read that line as covering files outside my assigned worktree and branch.


## Conflict resolution (run-0082)

The merge gate refused head `7090d9d` because it did not contain `main`. I merged `main` (`68e89456939ac7939ef659975dfbb37812bd6f83`) into `factory/T-0012.5` with `git merge --no-ff --no-edit main`. The new head is `aeb684d96544915c57435bd904959b3af45999ce`, "Merge main (68e8945, intake-store commits only) into factory/T-0012.5 so the head contains main". There were no conflicts: `git diff --name-only bed7e28 main | grep -v '^intake/state/' | wc -l` printed `0`, so `main` had moved only in store records (`f809c69`, `e725a5c`, `68e8945`). The sub-ticket diff is unchanged. `git diff --name-status main...HEAD` still lists only `M dev/build-harness.spec.md`, `M docs/changelog.md` and `M docs/design.md`, and `git merge-base --is-ancestor main HEAD` succeeds. I re-ran all nine acceptance commands on the merged head, with `BASE=cdb1c6769ecc39208e62edc65578f62f5a23908f`. Each printed the same output as in the After column above: `kept=1 open=0 piece8=1 logged=1`; `stale=0 new=3 d8=1`; `1`; `exit=0`; `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0`; `0`; `changed=0 of 10 VERBATIM`; `exit=1`; `exit=0`. Both gates pass. `git diff --check main...HEAD` printed nothing and exited 0. `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `92 passed in 95.11s (0:01:35)`, exit 0. `git status --short` in the worktree is empty.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every NEW criterion moved from failing to its target, every REGRESSION criterion and both gates pass, and the diff is limited to the 3 permitted files.
ESCALATIONS: none
