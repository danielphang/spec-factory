Sub-ticket: T-0041.1 (parent T-0041, approved spec v2), branch `factory/T-0041.1`, head `654f523`, base `cce3d6f`

## What changed

The spec drift check runs before a sub-ticket's first implementer run. It no longer parks a sub-ticket because one of its own siblings has merged. A sibling is another sub-ticket of the same parent ticket. Separately, the operator can now use a ruling to send a sub-ticket back to its implementer after the harness failed to start that implementer's run. Before this change, that park could only be cleared by editing the ticket file by hand.

**A. The test rule skips merged siblings' merges** (`factory/cli.py`, `_test_drift`, lines 341-348). Before the first-parent walk, the rule collects `merge.main_after` from every sub-ticket of the parent (`store.subtickets_of`) that has status `merged` and a recorded `main_after`. Sub-tickets from earlier plans are included. Any commit in that set is skipped (`continue`) before it is diffed. Merge commits in general are still checked. The docstrings of `_test_drift` and `_check_drift` now say that a merged sibling's merge is not drift.

**B. A ruling on a failed implementer run start** (`factory/cli.py`, `resolve`, `--ruling` branch, lines 1188-1206). `start_bug` is true when two things hold: the park reason starts with `harness-bug: run start implementer:`, and `parked["from"]` is `ready-for-implementer`. `--ruling` accepts a park that starts with `ESCALATE`, a park that starts with `BLOCKED`, or a park where `start_bug` is true. A `start_bug` park is routed the same way as `BLOCKED`. F becomes the next `approvals/<id>/ruling-<n>.md`, and the ticket moves to `ready-for-implementer` without changing its round. The refusal text is now Decision 4's: `--ruling applies to an ESCALATE or BLOCKED park, or a harness-bug park from an implementer's run start; <id> is <state> (<reason or 'no park'>)`. The `use --answer` refusal is unchanged.

**C. Suite cases** are in the new file `tests/factory/test_drift_siblings.py`, which reuses the fixture and helpers from `test_spec_amend` and `test_spec_drift`.

**D. Documents.**
- `docs/design.md`:
  - The Spec drift paragraph now says that a merged sub-ticket's recorded merge (`main_after`) does not count, from any plan of the parent, and that every other commit and merge does.
  - The routing rules' resolution bullet now covers the `harness-bug: run start implementer:` ruling and says that every other harness-bug park is refused.
- `dev/build-harness.spec.md`:
  - The `factory resolve` entry gains the new `--ruling` case.
  - The spec-store drift sentence gains the `merge.main_after` exception.
- `README.md`:
  - The Unstick row gains "the harness failed to start an implementer run, a `harness-bug: run start implementer:` park".
  - The Spec amendment and drift bullet says that another sub-ticket's merge is not drift.
  - "has not yet fired on a real ticket" is replaced: the check has fired on real sub-tickets, and the new exception is tested but has not yet run on a real ticket.
  - The status date is already 2026-10-10, today's date, so it is unchanged.
- `docs/changelog.md`: new entry 68, "After issue #85 (2026-10-10), …". It names the two false parks of T-0040.2 and T-0040.3, the `main_after` skip, the `harness-bug: run start implementer:` ruling route, and the rejected options. I checked its facts with `git show --stat 2ad4d8c52` (changes `factory/cli.py` and `tests/factory/test_drive.py`) and `git show --stat 18fbe88ba` (adds `tests/factory/test_drive_build.py`).
- No file under `docs/prompts/` or `factory/prompts/` changed.

## Acceptance results

I ran each WHEN through the running-code wrapper, from the worktree, after `uv sync --frozen`. The GIVEN blocks come from current truth (`openspec/specs/{spec-amendment,build-dispatch,human-resolution}/spec.md`). I extracted them verbatim and ran them once, with `TMPDIR` set to this run's scratch directory (`scratch/acc.sh`). The outputs are in `scratch/acc-before.txt` (at `cce3d6f`) and `scratch/acc-after.txt` (at `654f523`).

- **NEW: "A merged sibling's merge is not drift, and a later commit or merge from elsewhere still is"**
  - Before: `none: drift=1 greet=1 named=0 runs=0` / `other: drift=1 greet=1 named=1 runs=0` / `greet: drift=1 greet=1 named=1 runs=0` / `merge: drift=1 greet=1 named=1 runs=0`. This matches verification.md's "today".
  - After: `none: drift=0 greet=0 named=0 runs=1` / `other: drift=1 greet=0 named=1 runs=0` / `greet: drift=1 greet=1 named=1 runs=0` / `merge: drift=1 greet=0 named=1 runs=0`. This is exactly what the scenario expects.
- **NEW: "A ruling on a harness-bug park from an implementer's run start returns the sub-ticket, and its implementer then starts"**
  - Before: `ruling=2 parked kept=no drift=1` / `start=2 runs=0`.
  - After: `ruling=0 ready-for-implementer kept=yes drift=1` / `start=0 runs=1`. Expected.
- **NEW: "The design doc, build spec, README and changelog record both changes, and no prompt copy changes"**
  - Before: `design-drift=no design-ruling=no buildspec=no unstick=no bullet-sibling=no bullet-stale=yes prompts=0` / `CONTIGUOUS` / `0`.
  - After: `design-drift=yes design-ruling=yes buildspec=yes unstick=yes bullet-sibling=yes bullet-stale=no prompts=0` / `CONTIGUOUS` / `3`. Expected.
- **REGRESSION: "A sub-ticket whose Acceptance names an unmerged sibling it does not depend on is refused until that sibling merges"**. After: `unmerged: blocked=1 names=1 runs=0 ready-for-implementer` / `merged: exit=0 runs=1`. Expected.
- **REGRESSION: "A test changed beside a file the spec names parks the sub-ticket, and a ruling lets it start"**. After: `park T-0001.1: BLOCKED from harness: spec drift:` / `greet=1 other=0 runs=0` / `ruled: exit=0 runs=1`. Expected.
- **REGRESSION: "A ruling on a checker's or a compose step's harness-bug park is still refused"**. After: two lines, each `exit=2 refused=1 parked rulings=0`. Expected.
- **REGRESSION: "The sibling-merge change adds no whitespace errors"**. After: `exit=0`. `main` is `cce3d6f`, the branch base.

Gates, each run from the worktree exactly as written, at `654f523`:
- `git diff --check main...HEAD`: exit 0, no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `530 passed in 349.49s`. The full log is in `scratch/suite.log`.

## Tests added/changed

- Added `tests/factory/test_drift_siblings.py`, 10 cases. Before the `factory/cli.py` change, 8 failed for the intended reason: a drift refusal naming the sibling's `tests/test_greet.py`, or the old refusal text. The other 2 passed, as they should: they pin behaviour that must not change.
  - A merged sibling's `--no-ff` recorded merge is not drift, and part B starts.
  - A later direct commit beside a design-named file is refused. The refusal names only `tests/test_other.py` and that commit.
  - A later direct commit to the sibling's own test is refused. The refusal names the later commit, not the sibling's merge. This passed before the change.
  - A `--no-ff` merge of a branch that belongs to no sub-ticket is refused. The refusal names `tests/test_merge.py` and that merge commit, not `test_greet.py`.
  - A sub-ticket that is not merged but has a stale `main_after` still counts as drift. This passed before the change. It guards against a skip that is too broad.
  - A merged sub-ticket of an earlier plan (`planned_from` 1, re-planned at v2) is not drift. The re-spec was a real park, `resolve --to spec-gate`, then `approve-spec --edit`. `v2.yaml`'s `integration_head` was then reset to the head before the merge, so the walk passes over the merge.
  - `--ruling` on a `harness-bug: run start implementer:` park from `ready-for-implementer`:
    - It returns the sub-ticket to `ready-for-implementer` with `parked` cleared and the round unchanged.
    - `ruling-1.md` equals F.
    - The implementer then starts, although the drift is still present.
  - `--ruling` is refused, with exit 2, the new refusal text and an unchanged store snapshot, in three cases:
    - `harness-bug: run start reviewer:` from `checks-in-flight`;
    - `harness-bug: run compose implementer:` from `ready-for-implementer`;
    - `harness-bug: run start implementer:` parked from `checks-in-flight`. Decision 3 accepts the prefix only from `ready-for-implementer`.
- Changed `tests/factory/test_resolve_rulings.py::test_a_ruling_on_any_other_state_is_refused_and_names_both_park_kinds`. This test is listed under the parent's Tests to change. Only the refusal-text assertion changed, to Decision 4's text. Its parametrized cases (`budget kill: reviewer`, no park) and its other assertions are unchanged.

## Known gaps and uncertainties

- The skip compares full commit ids exactly. `factory merge` records `main_after` as a full id. A value set by hand with `ticket set` as an abbreviated id would not be skipped, and the merge would still be reported as drift. This fails safe, by parking. The spec asks for an exact match on the recorded merge.
- The spec's Out of scope already says this: a sibling merged by hand as a fast-forward is not covered. Only its last commit would equal `main_after`.
- README's Built section now describes the sibling-merge exception and the new ruling route in the present tense. Neither has run on a real ticket yet, and the bullet says so. The design requires the sentence. "Maintaining this page" would otherwise keep untried behaviour out of that section, so a reviewer may prefer different wording.
- The acceptance runs set `TMPDIR` to this run's scratch directory, which is inside the store's git checkout. All outputs matched. The gate suite ran with the default `TMPDIR`: the spec's Evidence notes that some suite cases fail when the temporary directory is inside a git checkout.

## Out-of-scope observations

- README's previous bullet, about tests that a sibling added, still ends "It is tested, and has not yet fired on a real ticket." I did not check whether that is still true, and I left it unchanged.

## Operator steps

None beyond the spec's. After merge, move the runtime checkout to the new harness revision. Then run `--accept-harness <commit>` on each instance. Until both steps are done, the running factory still parks a sub-ticket when its sibling merges.

Protected paths changed, all declared in the spec's Risk section: `factory/cli.py`.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command printed its expected output, the full suite passed (530 tests), and the new tests failed before the change for the intended reason.
ESCALATIONS: none
