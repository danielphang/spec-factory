Commit: 7090d9d21f17688df45fd3701dc5ee26f01452c4 (branch `factory/T-0012.5`, worktree `/Users/dphang/dev/spec-factory/intake/state/runs/run-0073-verifier/wt`, clean `git status`)

Base: f809c694fed21286bd2c1c234943c3dd96656db3 (= `main`), checked out as a detached scratch worktree, which I removed afterwards. `main` is one store-only commit (`intake(T-0012): ...`) on top of bed7e28, which is the PR's merge-base and the base the PR description cites. `git diff --name-only bed7e28 main | grep -v '^intake/state/'` prints nothing, so the two bases give the same results for these documents. `git merge-tree --write-tree main HEAD` exits 0, so the branch merges without conflict. `BASE=cdb1c6769ecc39208e62edc65578f62f5a23908f` is the parent's recorded base (`parent_base` in `intake/state/tickets/T-0012.yaml:74`), and I used it for the parent scenarios. I ran every command below verbatim with bash.

## Per criterion

| Criterion | Kind | Command | Base (f809c69) | PR (7090d9d) | Result |
|---|---|---|---|---|---|
| design-doc-instance-text | NEW | parent WHEN (specs/repo-layout) | `kept=0 open=1 piece8=0 logged=0` | `kept=1 open=0 piece8=1 logged=1` | PASS |
| build-spec-render-paths | NEW | parent WHEN (specs/repo-layout) | `stale=3 new=0 d8=0` | `stale=0 new=3 d8=1` (N=3 ≥ 3) | PASS |
| changelog-entry-appended | NEW | sub-ticket WHEN (`grep ... tail -1 ... grep -c "^$((41+1))\. After issue #19 (2026-10-02):"`) | `0` (last entry is 41) | `1` | PASS |
| responses-unchanged | REGRESSION | sub-ticket WHEN (`diff <(git show main:... awk '/^## Responses/...') ...; echo "exit=$?"`) | `exit=0` | `exit=0` | PASS |
| changelog-moved-verbatim | REGRESSION | parent WHEN, BASE=cdb1c67 | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` | PASS |
| design-text-kept | REGRESSION | parent WHEN, BASE=cdb1c67 | `0` | `0` | PASS |
| prompt-copies-moved-unchanged | REGRESSION | parent WHEN, BASE=cdb1c67 | `changed=0 of 10 VERBATIM` | `changed=0 of 10 VERBATIM` | PASS |
| no-old-paths, documents only | REGRESSION | T-0012.2 intermediate (`git grep -n -e ... -- README.md docs dev >/dev/null; echo "exit=$?"`, read from `intake/state/specs/T-0012.2/subticket.md:19`) | `exit=1` | `exit=1` | PASS |
| whitespace (sub-ticket diff) | REGRESSION | `git diff --check main...HEAD; echo "exit=$?"` | `exit=0` (empty range) | `exit=0` | PASS |

Every NEW criterion fails on base for the reason the spec gives: the old sentence is still present, the build spec still has 3 stale hits on lines 145, 158 and 456 before `## Responses` (line 523), and changelog entry 42 does not exist yet. Each passes on the PR. Every REGRESSION criterion passes on both.

## Gate suite: PASS

- `git diff --check main...HEAD`: printed nothing, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: on the first run uv created the worktree's `.venv` and printed `92 passed in 94.18s (0:01:34)`. A second run printed `92 passed in 88.83s (0:01:28)` and exited 0. `git status --short` was still empty afterwards.

## Probes

I compared the text against the parent spec's F.1–F.4 exactly, instead of relying on the acceptance greps.

- F.1 verbatim: I took main's Role-context paragraph, removed the old last sentence and appended the parent's F.1 text. The result equals the PR's line byte for byte (`F1 EXACT`). OK.
- F.2 placement: I split the `| 8 |` row on ` | `. Only cell 2 ("What it must do") changed, and it equals main's cell + `. ` + the F.2 sentence. That full stop is the one non-spec character, and the PR description discloses it. The `harness code` match is in the right column, not somewhere else on the row. OK.
- F.3 verbatim and position: `grep -qxF` finds the parent's full entry-42 text as an exact line (`F3 EXACT`). It sits right after entry 41 and before `Declined:`, so the numbering check reads `CONTIGUOUS` and the `Declined:` line is intact. The entry-number check computes the number from `main` (41+1), not from a hard-coded 42, so it is not special-cased. OK.
- F.4 D8 / layout / render / item 82:
  - There is exactly 1 `| D8 |` row, and it contains the parent's Value text as a whole cell.
  - Line 145 is exactly F.4's layout text.
  - The render bullet on line 158 names `docs/prompts/`, `agents/` and `.factory/instance.yaml`, and says ``render --check` diffs the rendered bodies back against `docs/design.md``.
  - `grep -n 'factory/prompts/design-doc\.md'` now hits only line 537, which is inside `## Responses`.

  OK.
- Diff scope: `git diff --stat main...HEAD` shows only `dev/build-harness.spec.md`, `docs/changelog.md` and `docs/design.md` (7 insertions, 6 deletions). No `docs/prompts/` file changed. `docs/design.md` has exactly 4 changed lines (2 out, 2 in), and both are the lines design-text-kept excludes. OK.
- Residual old-path text the checks cannot see: `dev/build-harness.spec.md:335` (before `## Responses`) still says "`render` from `design-doc.md`" without the `factory/prompts/` prefix. F.4 does not list that line and the stale grep does not match it, so this is not a criterion failure. CONCERN (minor, out of scope; see below).
- Parent-range whitespace (an extra check, not this sub-ticket's criterion): `git diff --check cdb1c67 HEAD` exits 2. All the hits are trailing whitespace in store records `intake/state/runs/run-0057-verifier/{diff.patch,input.md}` and `run-0058-reviewer/{diff.patch,input.md}`, which store commit 20849b6 added. The same range excluding `intake/state` exits 0. This PR adds no whitespace errors. CONCERN for parent close (see ESCALATIONS).

## Out-of-scope observations

- `dev/build-harness.spec.md:335` still says "`render` from `design-doc.md`". This joins the implementer's list of old-layout text that F.4 does not cover (the layout row for `factory/prompts/preamble.md`, item 82's `git status --porcelain .claude factory/prompts`, the `AGENTS.md` bullet, D6's `factory/config.yaml`). A later build-spec pass should reconcile them.

STATUS: VERIFIED
CONFIDENCE: high. I ran every acceptance command verbatim on base and head and got the expected base-to-PR transitions, both gates exit 0, and the inserted text matches the parent spec's F.1–F.4 byte for byte.
ESCALATIONS:
- Parent-close risk, outside this sub-ticket: the parent's whitespace-clean scenario (`git diff --check "$BASE" HEAD`, BASE=cdb1c67) already exits 2 on this branch. The cause is trailing whitespace inside committed store run records (`intake/state/runs/run-0057-verifier/*`, `run-0058-reviewer/*`, added by store commit 20849b6), not any sub-ticket's diff. Unless the operator or planner rules on how that scenario treats `intake/state/**`, it will fail at parent close. Records may not be rewritten.
