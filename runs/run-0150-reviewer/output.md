Commit: 6db43bf1ea50df49b0e56476f66a4ff7be6b69fc (branch `factory/T-0017.1`, base `0d1cef4a8b6b534e177f16f779a1c6161f69c853`, one commit)

## What I checked, in the role's order

1. **Test integrity.** `git diff --stat main...HEAD` lists twelve files; the only one under `tests/` is the new `tests/factory/test_decision_log.py`. No existing test file changed, no assertion weakened, no skip or xfail added. The sub-ticket's "Tests to change" is none, and that holds.

2. **Correctness.** Read `factory/cli.py` `resolve()` and `decision_add()` (worktree lines 675-750), `factory/specstore.py` `decision_text` / `record_decision` / `archive` (lines 239-262, 337-356) and `factory/compose.py` `add_decisions()` (lines 73-77) against the parent's part A and B text.
   - `resolve`: the `--decision` mode check and `decision_text()` run before `store.load_ticket` and before `_approval_dir()` creates `approvals/<id>/`, so a refused flag writes nothing. `decided()` is called inside the `--answer` and `--close` branches only after those branches' own refusals (`--answer applies to …`, `is already closed`), and its return is spread into `move()`'s `extra`, so the line reaches the history entry, the `resolve-<n>.yaml` record and the printed JSON. I confirmed this on a throwaway store: `approvals/T-0001/resolve-1.yaml` carries `decision: 2026-10-04 T-0001 Closed with a rule`, and `log tail --event decision.recorded` shows one event with `via: "resolve --close"`, `by: dphang`.
   - The extra refusal of `--ruling F --close --decision x` is correct: `resolve`'s `elif` chain runs `--ruling` ahead of `--close`, so without it the decision would have been dropped. It follows the parent's Decision "a decision is never silently dropped" and expands no scope.
   - `archive()` now feeds `record_decision(root, tid, ln, date)` the same `date` and lines it wrote before, so the log line format is unchanged. `decisions_of()` (lines 306-320) emits stripped, non-blank, single-line strings, so `decision_text`'s refusal cannot fire from archive; the implementer says the same under Known gaps.
   - `add_decisions()` tests `p.exists() and p.read_text().strip()`, which covers absent, empty and whitespace-only logs, and sits right after `add_truth()` for spec writer and critic and right after the approved spec for the planner, before the rulings loop. Triage and the build roles are untouched.
   - Acceptance I re-ran from the worktree root, each printing its THEN exactly: "Decision refused alone, with a ruling, and on a second close" (`alone=2 ruling=2 state=parked rulings=0 lines=0` / `close=0 state=closed lines=1` / `again=2 lines=1`); "Spec writer, critic and planner receive the decision log" (all eight lines); "Documents describe the new writers" (`old_design=no old_build=no design=yes build=yes readme=yes changelog=yes`); "Triage and spec-writer design blocks equal their copies" (`1. Triage SAME` / `2. Spec writer SAME`). The other five scenarios are covered one-for-one by tests in the new file, which the suite ran.
   - Part C wording: the `docs/design.md` diff hunks match the parent's two blocks character for character. `diff docs/prompts/01-triage.md factory/prompts/triage.md` and the spec-writer pair show only the differences that already existed on base (I diffed `main:` copies against `main:` harness prompts): the "Acceptance items describe behaviour" rule in both, and `400` for `{400}` in the spec writer.

3. **Scope.** Every changed file is named in the sub-ticket's parts A-E. `dev/build-harness.spec.md` line 207 (the `FACTORY_KEY` command list) is unchanged, as Out of scope requires. The one addition the sub-ticket did not name by number, a `factory decision add ID TEXT` bullet in `dev/build-harness.spec.md` (new line 585), is inside part D.2's intent: line 193 now names the command, and the operator-command list is where that document defines each command.

4. **Silent behaviour changes.** One, disclosed in Known gaps: `archive()` no longer opens `decisions.md` in append mode when the proposal has no Decisions lines, so it no longer creates an empty file in that case. Reachable only in a store where `factory init` ran and `decisions.md` was then deleted, since archive refuses without `openspec/` and `init` creates both. Recorded as a NIT below, not a defect.

5. **Security and data safety.** Appends only; no deletes, no shell, no secrets. `record_decision` creates the parent directory with `exist_ok=True` under the store root, which the CLI already owns.

6. **Protected paths.** `factory/cli.py`, `factory/compose.py`, `factory/specstore.py`, `factory/prompts/triage.md`, `factory/prompts/spec_writer.md` (harness) and `docs/prompts/01-triage.md`, `docs/prompts/02-spec-writer.md` (generated). All are declared in the sub-ticket and the parent's Risk section. Listed under ESCALATIONS for the gate's human approval.

7. **Coding standard.** Rule 1: `_utc_date()` replaces a duplicated expression; `decision_text` is split from `record_decision` because `resolve` must validate before any write, a real second caller. Rule 2: the PR description names every caller of `archive`, `compose` and `resolve`, found by grep. Rule 5: one name, `decision`, from spec to command, flag, event and function. Lean already.

8. **PR description.** What changed leads with the problem and glosses `decisions.md` and archive. See the SHOULD-FIX below for terms it leaves unglossed.

Gates, run from the worktree on `6db43bf`: `git diff --check main...HEAD` printed nothing, exit 0; `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `157 passed in 147.78s`, the 136 on base plus the 21 new tests.

## Findings

- [SHOULD-FIX] PR description: What changed: "parked" (first paragraph), "current truth" (part D, first bullet) and "the runtime" (Known gaps, prompt-edit item) are factory terms used without a gloss → the operator at the gate, held to the writing standard's rule 2, has to know the design document to read why archive and `resolve` differ and what must happen before the prompt change takes effect. One clause each would do: a parked ticket is one stopped on a human question; current truth is the store's record of how the system behaves now; the runtime is the separate pinned checkout that runs tickets.
- [NIT] factory/specstore.py:355: `archive()` writes nothing to `decisions.md` when the proposal has no Decisions lines, where before it created an empty file → observable only in a store whose `decisions.md` was deleted after `factory init`; no test or document depends on the empty file. Disclosed by the implementer. No change asked.
- [NIT] factory/cli.py:1105: `decision add` takes `text` as a positional, so a line that starts with `-` (a pasted bullet, say `"- Lionbot code lives under lionbot/"`) is read by argparse as an option and refused with `the following arguments are required: text`, exit 2 → nothing is written, which keeps the refusal contract, but the message does not say to put `--` before the text. Standard argparse behaviour; a help-text note would be enough, and nothing in the spec asks for it.

net: 0 lines possible. Lean already.

Prior findings: none (round 1).

STATUS: APPROVE
CONFIDENCE: high, I re-ran both gates and four of the nine acceptance commands from the worktree and read the three changed harness functions against the parent's text; the remaining scenarios are covered by tests the suite ran.
ESCALATIONS:
- Protected paths touched, all declared in the sub-ticket and the parent's Risk section: harness `factory/cli.py`, `factory/compose.py`, `factory/specstore.py`, `factory/prompts/triage.md`, `factory/prompts/spec_writer.md`; generated `docs/prompts/01-triage.md`, `docs/prompts/02-spec-writer.md` (verified equal to their `docs/design.md` blocks). The merge gate needs a human approval for these, and parent Operator step 1 (the operator's read of the new NEEDS-HUMAN wording before the runtime moves) is still owed.
