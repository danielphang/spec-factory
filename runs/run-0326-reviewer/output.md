Commit: f25dffed5f970142f9da01b0ed24f8e8deaac40a (branch `factory/T-0034.1`, base `2e73dbb8c997a4284649dcc25f5e9fbba8b65fea`; `main` in the worktree is the base, so the scenarios' `main...HEAD` comparisons measure this one commit)

Round 1.

What I checked, in the prescribed order:

1. Test integrity: no file under `tests/` changed (`git diff --name-only 2e73dbb...HEAD -- tests` is empty). The spec's "Tests to change" is none. Nothing weakened, skipped or deleted.
2. Correctness, part by part:
   - A. The seven turn-economy lines sit directly after `  wrong just to get approved.` in `docs/design.md:372-378`, `docs/prompts/02-spec-writer.md:59-65` and `factory/prompts/spec_writer.md:59-65`, before the blank line and the run copy's extra "Acceptance items describe behaviour" bullet. The text matches the spec's block word for word.
   - B. The twelve critic lines sit directly after `Spot-check at least 2 cited paths and 1 acceptance command yourself.` (`factory/prompts/critic.md:42`, confirmed as line 42 on `main`) in all three copies, before the blank line that precedes `ANTI-GOODHARTING (REVIEWER SIDE)`. The minimum spot-check line is kept. Text matches the spec.
   - C. The diff for the four prompt files is additions only: the whole diff removes 3 lines, all in `docs/principles.md` (the three lines the spec's D.2 says to change). No file under `agents/` changed.
   - D.1 Entry 58 is one line, after 57, before `Declined:`, verbatim from the spec.
   - D.2 Principle 2's "Implemented by" ending and status line are exactly the spec's text, rewrapped. Lines 44 and 46 are 102 and 101 columns; the file already carries 101- to 112-column lines (lines 4, 5, 12, 26 among others), so this stays within "the file's existing width".
   - Confirming commands I ran (narrow, under a fresh HOME):
     - The first scenario as written printed `spec_writer copy=SAME doc=4/4 run=4/4 fill=unchanged` then `critic copy=SAME doc=6/6 run=6/6 fill=unchanged`: each design block equals its documented copy, every rule phrase is present in both copies, and each run copy differs from its documented copy only as it did on `main` (the `{400}`/`{2}` fill-ins and the writer's extra bullet).
     - The documents scenario printed `CONTIGUOUS`, `5`, `implemented=1 status=1`: the changelog numbering has no gap, entry 58 holds all five phrases, and principle 2 carries both new sentences.
     - `diff factory/prompts/critic.md docs/prompts/03-spec-critic.md` on head shows only the `{2}` line; the spec writer pair shows only the `{400}` line and the extra bullet with its blank line, the same set of lines as on `main`.
3. Scope: every change is inside parts A to D. Nothing else.
4. Silent behaviour changes: none that run today. The runtime is pinned; the prompts change what a spec writer or critic receives only after the harness upgrade, which the spec's Operator steps gate on a replay.
5. Security and data safety: prose only; no code, no secrets, no destructive operation.
6. Protected paths: all four declared in the spec's Risk list, listed under ESCALATIONS below. The two `factory/prompts/` files are also agent prompts (a guardrail path); the sub-ticket asks for them.
7. Coding standard: no code added. Lean already.
8. PR description: What changed says in words what each role is, what a "copy" is and where each insertion sits; Known gaps names the untested claim (whether turns halve), the two over-width lines, the `factory:` marker count and the declared paths; each output in Acceptance results is followed by what it shows. Meets the writing standard.

Findings: none.

Prior findings: none (round 1).

Out-of-scope observations:
- `dev/issues.md` has no row for #73 (`grep -n '#73' dev/issues.md` prints nothing). The spec's part D does not ask for one, and the previous issue's row landed in its own commit (`6038510`), so this is not a gap in this PR; the operator may want the row added when the ticket closes.
- The `agents/factory-spec-writer.md` and `agents/factory-spec-critic.md` bodies stay stale, as the spec and the PR description already note; T-0030 owns that.

STATUS: APPROVE
CONFIDENCE: high — the diff is additions only in the four prompt files and matches the spec's blocks verbatim; I re-ran the copy-equality scenario and the documents scenario on the head and both printed their expected output.
ESCALATIONS: declared protected paths touched, as the spec's Risk section lists: harness `factory/prompts/spec_writer.md`, `factory/prompts/critic.md` (also agent prompts); generated `docs/prompts/02-spec-writer.md`, `docs/prompts/03-spec-critic.md`. Human approval at the merge gate.
