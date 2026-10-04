Commit: 771ee0ec14ec755265f969c709ee3a4099d5160d (branch `factory/T-0022.1`, base `c2750bf9c18ca6e37e4cfec439a0a9ef42f318d6`; `main` in the worktree resolves to that base)

## What I checked, in the role's order

1. **Test integrity.** `git diff --name-only --diff-filter=MD c2750bf...HEAD -- tests/` prints nothing: no existing test file is modified or deleted. The only test change is the new file `tests/factory/test_sibling_tests.py` (231 lines added). Its 10 cases assert exact exit codes, the `BLOCKED from harness: ` prefix, the named path, no run directory, no branch, unchanged status and an empty `in_flight`; nothing is skipped or swallowed. The build-dispatch case asserts `node` is present instead of skipping, as the PR description says.

2. **Correctness.** Read `_check_sibling_tests` (`factory/cli.py:240-265`), `sibling_tests` (`factory/subtickets.py:40-55`) and `first_added` (`factory/gitops.py:83-89`) against Decisions 1-4 of the pinned spec.
   - The check sits after the in-flight guards and before `tripwire.baseline` (`cli.py:214-216`), so a refusal reserves no run id and writes nothing. Confirmed by running the spec's refused scenario on the head: three lines of `exit=2 blocked=1 names=1 runs=0 branch=0 ready-for-implementer`, meaning the run was refused, the error carries the prefix and the file, and no run, branch or status change exists. The merged-sibling scenario printed `exit=0 ready-for-implementer runs=1`: a file a sibling's merge added passes and the Scope-line mention is ignored.
   - `first_added` returns None when `git cat-file -e <base>:<path>` succeeds, otherwise the oldest `--diff-filter=A` commit in `base..tip`, as B.2 asks. The sibling test uses `head_contains(repo, main_after, added) and not head_contains(repo, base_before, added)`, which is `git merge-base --is-ancestor added main_after` and its negation on `base_before`: Decision 2 exactly.
   - `sibling_tests` opens a field on a `FIELD_RE` match whose key is in `PLAN_FIELDS`, or on a heading, and reads entries only while inside `tests to change`. A bullet line that starts with a backtick does not match `FIELD_RE` (its key must start with a capital letter), so entries never close the field by accident. The stored sub-ticket text gains a `## Shared plan context` heading, which closes the field; the new test `test_the_field_ends_at_the_next_plan_field_or_heading...` covers that.
   - Deviations the PR description declares: `is_ancestor` not added (`head_contains` reused, which is the coding standard's rule 1), and a merge record is used only when `base_before` is also set. Both are safe; the second is stricter than the spec in a direction that cannot admit a wrong file.
   - Silent-behaviour risk: for a sub-ticket with no `(added by …)` line the function returns before touching git (`cli.py:246-248`). `grep -ln "(added by" .factory/state/specs/*/subticket.md` on this repo's store prints nothing, so no existing sub-ticket here changes behaviour. I did not read the Nanobot store.

3. **Scope.** All 19 changed files are inside parts A-E of the sub-ticket. No file outside them.

4. **Silent behaviour changes.** None beyond the spec's: `run start` for an implementer on a sub-ticket now reads `specs/<id>/subticket.md`; `runRole` parks a `BLOCKED ` refusal verbatim (`build.js:71-72`), every other refusal unchanged. `clerk()` (`build.js:41-57`) puts the CLI's JSON `error` on the parsed result, so `start.error` is the string the check raised.

5. **Security and data safety.** One finding below (SHOULD-FIX). No secrets, no destructive operations, no writes outside the throwaway store in the tests.

6. **Protected paths.** Touched, all declared in the parent's Risk list and the sub-ticket: `factory/cli.py`, `factory/subtickets.py`, `factory/gitops.py`, `factory/workflows/build.js`, `factory/prompts/{preamble,planner,spec_writer,critic,reviewer}.md`, `docs/prompts/{00-preamble,02-spec-writer,03-spec-critic,04-planner,06-code-reviewer}.md`. Listed under ESCALATIONS; the merge gate needs the operator's approval.

7. **Coding standard.** `first_added` sits on rung 2/4 (git via `subprocess`); nothing it does exists in the repo. `head_contains` reused rather than duplicated. The test file's `Fixture` class repeats the per-file scaffolding that `test_resolve_rulings.py` and `test_run_isolation.py` also carry; there is no shared helper module to reuse, so this is the suite's existing pattern, not a `reuse:` finding. No `factory:` markers needed; the PR description says "markers added: none". Lean already.

8. **Prompt copies.** The planner and preamble blocks are byte-identical across `docs/design.md`, `docs/prompts/` and `factory/prompts/` (planner scenario printed `verbatim`; `cmp` on the preamble copies: same). The spec writer, critic and reviewer copies differ between `docs/prompts/` and `factory/prompts/` only in lines that already differed on the base (`{400}`/`400`, `{2}`/`2` placeholders, and the spec writer's FORMAT and acceptance bullets): I diffed each pair on `c2750bf` and on `HEAD` and the differences are the same lines, shifted. This change adds no drift.

9. **Documents.** Design-doc scenario `piece8=1 gate=1 stale=0 check=1 build=1`; changelog `CONTIGUOUS` then `5` (entry 54 carries all five phrases and ends with the Rejected sentence); README `built=1 ruling=1`. The README status date is already 2026-10-04 (`README.md:9`). The `**Tests a sibling added.**` paragraph covers every item E.3 lists.

10. **Gates**, run from the worktree with a fresh HOME:
   - `git diff --check main...HEAD` → exit 0, no output.
   - `uv run --frozen pytest -q -p no:cacheprovider tests/factory` with `TMPDIR` under `/tmp` → `310 passed in 341.88s`, exit 0. That is the 300 the base had plus the 10 new cases.

## Findings

- [SHOULD-FIX] `factory/workflows/build.js:62`: `park()` places the reason inside a double-quoted `sh -c` string and escapes only `"`. With this change the reason can carry a planner-written path, and `SIBLING_TEST_RE` (`factory/subtickets.py:34`) admits `$`, `(` and `)` as long as there is no whitespace or backtick, so a listed file such as `` `$(id)` (added by ST-1) `` is expanded by the clerk's shell when the park command runs → text a planner wrote, which came from an untrusted request, reaches a shell. Today's `harness-bug:` parks pass stderr through the same string, so the hole is older than this change, but this is the first time planner-controlled text is routed into it on purpose. `park()` is outside parts A-E and the regex is the spec's own, so this belongs in a follow-up issue (single-quote the reason, or have `sibling_tests` refuse a path with `$`), not in this PR.

- [NIT] PR description: What changed → the acceptance table says "Before = base `c2750bf`" for the REGRESSION row "no whitespace errors", where the range on the base is empty; it is a true result but a vacuous one. No change needed to merge.

No BLOCKING finding. The `is_ancestor` omission and the `base_before` requirement are disclosed in Known gaps and are the right calls.

Prior findings: none (round 1).

## Out-of-scope observations

- The planner text "This one must depend on that sibling" is not enforced by the harness, as the PR description and the critic both say. If it matters, it is a planner-prompt or a `subticket add` check in a later ticket.
- `head_contains` (`factory/gitops.py:80`) does not capture git's stderr, so a malformed SHA in a merge record prints a git error on the CLI's stderr before the JSON refusal. Disclosed in Known gaps; harmless to the refusal itself.

STATUS: APPROVE
CONFIDENCE: high. I re-ran the merged, refused, planner-copy, design-doc, changelog and README scenarios on the head and saw each THEN; both gates passed on `771ee0e` in a fresh HOME; the diff touches no existing test; the prompt-copy differences that remain all predate the base.
ESCALATIONS:
- Protected paths touched, all declared in the sub-ticket's list: `factory/cli.py`, `factory/subtickets.py`, `factory/gitops.py`, `factory/workflows/build.js`, `factory/prompts/preamble.md`, `factory/prompts/planner.md`, `factory/prompts/spec_writer.md`, `factory/prompts/critic.md`, `factory/prompts/reviewer.md`, `docs/prompts/00-preamble.md`, `docs/prompts/02-spec-writer.md`, `docs/prompts/03-spec-critic.md`, `docs/prompts/04-planner.md`, `docs/prompts/06-code-reviewer.md`. The merge gate needs the operator's protected-path approval on `771ee0e`.
