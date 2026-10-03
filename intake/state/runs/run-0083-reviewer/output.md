Commit: aeb684d96544915c57435bd904959b3af45999ce (branch `factory/T-0012.5`; merge of `main` 68e89456939ac7939ef659975dfbb37812bd6f83 onto 7090d9d2; `git merge-base --is-ancestor main HEAD` succeeds)

## What I checked, in the role's order

1. **Test integrity.** `git diff --name-status main...HEAD` lists exactly `M dev/build-harness.spec.md`, `M docs/changelog.md`, `M docs/design.md` (3 files, +7/-6). No file under `tests/`, `factory/`, `bin/`, `agents/`, `pyproject.toml`, `uv.lock`, `AGENTS.md` or `.claude/` is touched. "Tests to change: none" holds.

2. **Correctness against F.1–F.4.** I extracted the quoted text from the parent spec file `intake/state/specs/T-0012/v3.md` and compared it with the worktree files by exact string match (Python, not eyeballing):
   - F.1: `docs/design.md:54` (the one `**Role-context block.**` line) contains the parent's F.1 sentence verbatim as its tail; the old "are not fixed here" sentence is gone; the text before it is unchanged ("…share the error instead of catching it. ").
   - F.2: `docs/design.md:46` (the one `| 8 |` row) contains the parent's F.2 sentence verbatim in the "What it must do" cell, preceded by "…an approval on the PR itself. " (a full stop added to a cell that had none, so the appended sentence reads as a sentence) and followed by ` | CO…` (the next cell, untouched).
   - F.3: `docs/changelog.md:46` is exactly `42. ` + the parent's F.3 text. It sits after entry 41 (line 45) and before `Declined:` (line 48). `main` has 41 numbered entries, head has 42, numbering CONTIGUOUS.
   - F.4: the D8 row's Value cell equals the parent's quoted text exactly. The layout row equals the parent's quoted text exactly (`dev/build-harness.spec.md:145`). Item 82 has zero `factory/prompts/design-doc.md` and three `docs/design.md`; nothing else on that line changed (confirmed from the diff hunk). The `factory render` bullet (line 158) says it reads `docs/design.md`, same repo as the harness, no other path, still no `--doc`; writes `docs/prompts/` and the `agents/` templates; placeholders filled per instance from `.factory/instance.yaml` when a run starts; `render --check` diffs against `docs/design.md`. That covers every clause F.4 gives for the bullet. The addendum-2 rule is retained verbatim. `## Responses` is byte-identical to `main` (responses-unchanged `exit=0`); its line 537 keeps `factory/prompts/design-doc.md`, as the ticket requires.
   - Both rewritten `docs/design.md` lines (46, 54) are in §Harness, above the first fence in the file (line 166, ```` ```text ````), so no prompt block changed. prompt-copies-moved-unchanged confirms: `changed=0 of 10 VERBATIM`. The design doc's "How to use this" (line 31) already points at `docs/changelog.md`, so the changelog convention is met by the entry in that file.

3. **Scope.** Only the three files the sub-ticket names. The merge commit brought in `main`'s store-only commits; the sub-ticket diff (`main...HEAD`) is the same three hunks the PR description shows (diff md5 `16c3c44ebd688bfeded91661867b2589` in the worktree; the input's diff has the same 3 `diff --git` headers and content).

4. **Silent behaviour changes.** None possible: prose only, no harness path.

5. **Security / data safety.** Nothing applicable. The `-c core.hooksPath=/dev/null` commit the implementer disclosed skipped nothing: `git config core.hooksPath` is unset and `/Users/dphang/dev/spec-factory/.git/hooks` holds only `.sample` files (checked).

6. **Protected paths.** None touched. `docs/prompts/**` (generated) unchanged; `intake/**`, `.factory/**`, `~/dev/nanobot-upstream`, `~/.nanobot` untouched by the diff.

7. **Maintainability.** Nothing that will cause a real problem.

## Acceptance, re-run by me from the worktree (`BASE=cdb1c6769ecc39208e62edc65578f62f5a23908f`, a commit in this repo)

| Criterion | My result | Expected |
|---|---|---|
| design-doc-instance-text | `kept=1 open=0 piece8=1 logged=1` | same |
| build-spec-render-paths | `stale=0 new=3 d8=1` | `stale=0 new=N d8=1`, N ≥ 3 |
| changelog-entry-appended | `1` | `1` |
| responses-unchanged | `exit=0` | `exit=0` |
| changelog-moved-verbatim | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` | same |
| design-text-kept | `0` | `0` |
| prompt-copies-moved-unchanged | `changed=0 of 10 VERBATIM` | same |
| no-old-paths, documents only | `exit=1` | `exit=1` |
| whitespace `git diff --check main...HEAD` | `exit=0`, no output | `exit=0` |

Gates: `git diff --check main...HEAD` printed nothing, exit 0. `PYTHONDONTWRITEBYTECODE=1 uv run --frozen pytest -q -p no:cacheprovider tests/factory` → `92 passed in 125.79s (0:02:05)`, no `failed`/`error`. `git status --short` in the worktree is empty after both.

## Findings

None.

Two implementer-disclosed choices I accept rather than flag: the full stop added before the F.2 sentence (the cell otherwise reads "…PR itself The harness code…"; the line is one of the two design-text-kept excludes, so no scenario is affected), and placing entry 42 before `Declined:` rather than after it (keeps the numbered list contiguous; the scenario's `declined=1 numbering=CONTIGUOUS` both hold).

Prior findings: none (round 1).

## Out-of-scope observations

- The implementer's list of stale build-spec text F.4 does not cover is accurate on this head: `dev/build-harness.spec.md:140` layout row `factory/prompts/preamble.md`; item 82's `git status --porcelain .claude factory/prompts` and `.claude/agents/factory-verifier.md`; the `AGENTS.md` bullet naming `factory/prompts/**`; D6's `factory/config.yaml`; the bare-repo `factory init` bullet (line 160). The parent itself defers these to a later build-spec pass.
- `changelog-entry-appended` hard-codes the main-count+1 numbering; if any other branch appended an entry to `docs/changelog.md` before this merges, the number would be wrong and the check would catch it. No sibling edits that file per the plan.

STATUS: APPROVE
CONFIDENCE: high. Every inserted sentence was matched byte-for-byte against the parent's quoted text, all nine acceptance commands and both gates were re-run by me on head aeb684d with the stated results, and the diff touches only the three permitted prose files.
ESCALATIONS: none
