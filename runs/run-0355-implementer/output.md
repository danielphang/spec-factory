Sub-ticket: T-0037.1 (parent T-0037, approved spec v2, `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0037/v2.md`). Branch `factory/T-0037.1`, one commit `2f3fcef` on base `51e2af7`, worktree `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0037.1`.

## What changed
Three agent roles were missing standing rules. Since #75, the spec writer (writes a ticket's spec), the critic (reviews that spec) and the planner (splits an approved spec into pieces of work) received only some lines of the decision log, `decisions.md`, in full. The decision log holds one line per standing decision. A line counted only if it was logged against their own ticket or named a capability they received in full. A capability is one current-truth spec, the store's record of how one part of the system behaves today. No decision line names a capability, so every other ticket's decision reached these roles only as a line in a "decision index". This change sends them the whole log again.

- **A. `factory/compose.py`.**
  - `add_decisions` now takes no argument. It adds `decisions.md` whole under `## Decision log (decisions.md): standing decisions, read-only` when the file holds any text, and adds nothing otherwise, as before. The line filter, the trimmed-log block and the "Decision index" section, with its `title()` helper and `grep` instruction, are removed.
  - Callers: `add_decisions` is a closure inside `compose()`. `git grep -n add_decisions` finds only its three calls, for the spec writer (`:250`), the critic (`:269`) and the planner (`:292`). All three are now `add_decisions()`. The writer and critic calls still follow `add_truth(sel)`. The planner no longer calls `selected()`.
  - `CAPABILITY_INDEX_NOTE` (`:138-142`) loses the clause ", and the decisions that name it to the critic and the planner,". It now matches the spec's text word for word. Its only use is in `add_truth` (`:223`).
  - `selected()`, `add_truth()`, the capability index and the triage branch are unchanged.
- **B. `tests/factory/test_capability_index.py`.** The decision-filter tests are replaced by one parametrized test, `test_each_role_gets_the_whole_decision_log_and_no_decision_index`. It runs with `Capabilities: beta` and with `Capabilities: none`. For each of the spec writer, critic and planner it checks three things: the input holds the whole-log heading followed by every fixture line; it holds no `Decision index` and no `<ticket id>` grep instruction; and `decisions.md` is in its `input_sources`. The module docstring and the note text in the writer test are updated. `test_a_whitespace_only_log_still_adds_nothing` and the part-B4 test are unchanged.
- **C. Documents.**
  - `docs/design.md:94`: the last two sentences of the "Spec store" paragraph are replaced with the spec's text.
  - `README.md`: the Spec writer, Spec critic and Planner rows of the role table now say "the whole decision log". The Status date moves to 2026-10-09, the store's UTC date for this change.
  - `docs/changelog.md`: entry 61, "After issue #78 (2026-10-09)". It gives what went wrong, what changed, the measured size change (under 3 kB to about 36 kB here; about 5 kB to about 80 kB on Nanobot) and the rejected alternative.

Protected paths touched: `factory/compose.py`, part of the harness. The spec's Risk section declares it. No `docs/prompts/` file and no other protected path changed.

## Acceptance results
The role-input scenarios depend on a GIVEN fixture. It was written from the current-truth `role-inputs` spec (`openspec/specs/role-inputs/spec.md:13-48`) with `TMPDIR` set to this run's scratch directory, and run from the worktree after `uv sync --frozen`. Every command ran inside the throwaway-HOME wrapper.

- **With a Capabilities line every decision line reaches the writer, critic and planner, and no decision index does (NEW).**
  - Before, on `51e2af7`:
    ```
    W: own=1 beta-line=1 gamma-line=0 other=0 whole=0 index=1 grep-cmd=1 note-decisions=1 source=1
    C: own=1 beta-line=1 gamma-line=1 other=0 whole=0 index=1 grep-cmd=1 note-decisions=1 source=1
    P: own=1 beta-line=1 gamma-line=1 other=0 whole=0 index=1 grep-cmd=1 note-decisions=0 source=1
    ```
    This is the failure the spec describes. OTHER-LINE, a decision logged against another ticket that names no capability, reaches no role, and each role gets a decision index.
  - After, on `2f3fcef`:
    ```
    W: own=1 beta-line=1 gamma-line=1 other=1 whole=1 index=0 grep-cmd=0 note-decisions=0 source=1
    C: own=1 beta-line=1 gamma-line=1 other=1 whole=1 index=0 grep-cmd=0 note-decisions=0 source=1
    P: own=1 beta-line=1 gamma-line=1 other=1 whole=1 index=0 grep-cmd=0 note-decisions=0 source=1
    ```
    This matches the THEN exactly. Every decision line reaches all three roles. No role gets a decision index or its `grep` instruction, and the capability index note no longer mentions decisions.
- **The capabilities each role receives and triage's input are unchanged by the whole log (REGRESSION).** After, on `2f3fcef`:
  ```
  W: alpha=0 beta=1 gamma=0 alpha-index=y gamma-index=y cites=1
  C: alpha=0 beta=1 gamma=1 alpha-index=y gamma-index=n cites=1
  P: alpha=0 beta=0 gamma=0 alpha-index=n gamma-index=n cites=0
  triage: alpha-index=y beta-index=y gamma-index=y bodies=0 decisions=0
  ```
  This matches the THEN exactly, and the base printed the same four lines: #75's capability half is intact, and triage still gets no decision line.
- **The harness suite passes with the whole decision log (REGRESSION).** After, on `2f3fcef`, with the default macOS `TMPDIR` (`/var/folders/...`, outside every instance), it printed `suite=0`.
- **The design, README and changelog describe the whole decision log and no decision index (NEW).**
  - Before, on `51e2af7`: `design-index=1 design-whole=0 readme-index=3 readme-whole=0 changelog=0`, then `whitespace=ok`.
  - After, on `2f3fcef`: `design-index=0 design-whole=1 readme-index=0 readme-whole=3 changelog=1`, then `whitespace=ok`. This matches the THEN exactly.
- **Gates, each run exactly as written, from the worktree, on `2f3fcef`.**
  - `git diff --check main...HEAD` exited 0.
  - `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `382 passed in 292.40s`. The base had 384. The net -2 is this change: it removes four tests and adds one test with two parameter cases.

## Tests added/changed
All in `tests/factory/test_capability_index.py`, and every change is on the spec's Tests to change list. Because this edits an existing test file, the PR goes to a human gate.

| Change | Lines on base | Why |
|---|---|---|
| Module docstring rewritten | `:1-9` | It described the decision filter and index (Decision 1) |
| `CITES` constant removed; the writer test's note text drops the clause | `:22`, `:122-126` | They pinned the note clause that Decision 2 removes |
| Helpers `decision_block` and `decision_index` removed | `:194-203` | They built the trimmed-log heading and the decision index (Decision 1) |
| `test_each_role_gets_its_ticket_s_and_its_capabilities_decisions_and_an_index_of_the_rest` removed | `:206-217` | It expected OTHER-LINE left out and an index (Decisions 1 and 3) |
| `test_a_decision_index_line_carries_the_ticket_s_title` removed | `:220-224` | The index no longer exists (Decision 1) |
| `test_no_kept_line_leaves_only_the_index_and_no_decisions_source` removed | `:227-232` | With `Capabilities: none` the log and its source now appear (Decision 1) |
| `test_every_line_kept_leaves_no_decision_index` removed | `:235-238` | It expected the trimmed-log heading (Decision 1) |
| Added `test_each_role_gets_the_whole_decision_log_and_no_decision_index`, parametrized with `Capabilities: beta` and `Capabilities: none` | new, in place of the removed block | Part B: each role holds the whole log, no index, and the `decisions.md` source |

The new test failed on the base code: 3 failed and 15 passed in the file, the writer-note test plus both parameter cases. It passed after the code change: 39 passed together with `tests/factory/test_decision_log.py`, whose whole-log test at `:205-215` passes before and after, as the spec says.

## Known gaps and uncertainties
- The `others` parameter of the test helpers `setup` and `build` (`test_capability_index.py:71-96`) now has no caller. Only the removed title test used it. The helpers are not on the Tests to change list, so they are left as they are. Likewise, the fifth fixture line `OTHER2-LINE` was written for the removed word-boundary test. It is still checked, as one of the lines the whole log must carry.
- The README Status date is 2026-10-09, the UTC date the store and the spec use. The operator's local date was still 2026-10-08 (PDT) when this ran.
- factory: markers added: none.
- The Operator steps are not done here: moving the runtime and running `--accept-harness` in each target.

## Out-of-scope observations
- To keep step 2's NEW-before output, the fixture's throwaway stores were created under this run's scratch directory, which is inside `.factory/`. This worked because the fixture sets `FACTORY_INSTANCE` itself. The suite itself was run with `TMPDIR` outside every instance, as its scenario requires.

## Responses to findings
n/a (round 1)

STATUS: READY-FOR-REVIEW
CONFIDENCE: high, every acceptance command printed its THEN exactly on `2f3fcef`, both NEW commands printed the spec's "before" output on `51e2af7`, and both gates passed.
ESCALATIONS: none
