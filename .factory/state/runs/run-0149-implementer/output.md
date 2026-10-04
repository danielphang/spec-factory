Sub-ticket: T-0017.1 (parent T-0017, approved spec v2, `.factory/state/specs/T-0017/v2.md`). Branch `factory/T-0017.1`, commit `6db43bf` on base `0d1cef4`, worktree `/Users/dphang/dev/spec-factory/.factory/state/worktrees/T-0017.1`.

## What changed

Before this change, the factory lost a standing decision when a human answered a parked ticket's question and then closed the ticket without a build. The decision log, `decisions.md`, is one file per target repository with one dated line per decision. Only archive wrote it, and archive runs only when a built ticket closes. No agent received the log in its input either. Now a human can log a decision at any point in a ticket's life. The spec writer, critic and planner receive the log. Questions to a human ask whether the answer is a standing decision.

**A. Logging a decision** (`factory/specstore.py`, `factory/cli.py`)
- `specstore.decision_text(text)` strips the text. It refuses (exit 2) when the result is blank or spans more than one line. It uses `str.splitlines`, so `\r` and other line breaks count too.
- `specstore.record_decision(root, tid, text, today=None)` appends `<UTC YYYY-MM-DD> <tid> <text>` to `decisions.md` and returns the line. It creates the file and its parent when they are absent, so a store where `factory init` never ran can still log decisions.
- `archive()` now writes each Decisions line through `record_decision`, with the same date and format. A small helper, `_utc_date()`, holds the date expression that `archive` and `record_decision` share. The module docstring (line 6) now names the three writers.
- New command `factory decision add ID TEXT`. It loads the ticket, so an unknown id refuses with `no ticket ID`. It does not check the ticket's state. It logs the event `decision.recorded` with `ticket`, `by`, `line` and `via: "decision add"`, and prints `{"ok": true, "id", "decision": <line>}`.
- `resolve --decision TEXT`. Both checks below run at the top of `resolve()`, before the ticket loads and before any write, including the empty `approvals/<id>/` directory that `resolve` creates:
  - the flag must go with a mode that carries it. Otherwise `resolve` refuses with `--decision applies only with --answer or --close`.
  - the text must be one non-blank line.

  The `--answer` and `--close` branches log the decision only after their own refusals pass. They then log `decision.recorded` (`via: "resolve --answer"` or `"resolve --close"`) and pass `{"decision": <line>}` to `move()`. That puts the line in the ticket history, in the `resolve-<n>.yaml` record and in the printed result. Without `--decision`, every branch behaves as before.

  One case the spec did not spell out: `resolve` runs `--ruling`, `--to` and `--redispatch` ahead of `--close`. So `--ruling F --close --decision x` would have run the ruling and silently dropped the decision. The check refuses that combination too. This follows the spec's rule that a decision is never silently dropped.

**B. The log as input** (`factory/compose.py`)
- `add_decisions()` sits beside `add_truth()`. When `decisions.md` holds any non-whitespace text, it adds the file under the heading `Decision log (decisions.md): standing decisions, read-only`, with source `decisions.md`. Otherwise it adds nothing.
- The spec writer and critic branches call it right after `add_truth()`. The planner branch calls it right after the approved spec, before the rulings loop.
- Triage and the build roles are unchanged.

**C. Prompts**
- In `docs/design.md`, the NEEDS-HUMAN item of §1 Triage and the "Open questions stay open" rule of §2 Spec writer now use the exact wording the parent spec gives.
- `docs/prompts/01-triage.md` and `02-spec-writer.md` were re-copied by a script that extracts each fenced `text` block, not edited by hand.
- `factory/prompts/triage.md` and `spec_writer.md` got the same edit. A `diff` against the copies shows only the two differences they had before: the "Acceptance items describe behaviour" rule, and `400` in place of `{400}`.

**D. Documents**
- `docs/design.md`:
  - line 82 now says only archive writes current truth. It names the three writers of `decisions.md` and their line format. It adds that the spec writer, critic and planner receive a non-empty log.
  - line 97: archive appends nothing for a parent closed as applied. The human logs any decision with `factory decision add`.
  - the resolution item "A question returns to the role that asked" now says the human passes `--decision` when the answer is a standing decision.
  - the routing table's "Receives" column gains the decision log in three rows: Triage ACCEPT, Spec writer READY-FOR-CRITIC, and Human spec gate Approved.
- `dev/build-harness.spec.md`:
  - line 193 states the three-writer rule and what `run compose` gives.
  - line 211 adds `decision.recorded` to the event list.
  - line 314 adds `[--decision TEXT]` to the `resolve` synopsis, with its effect and refusals.
  - a new bullet follows it for `factory decision add ID TEXT`. Line 193 names this command, so its section needs a definition there; the parent did not name the bullet explicitly.
  - the archive bullet (old line 315, now 316) takes the same closed-as-applied change as design.md line 97.
- `docs/changelog.md` gains entry `46.` before `Declined:`.
- `README.md`, "Where a human decides": the Unstick row gains `--decision "<line>"`, valid with `--answer` or `--close`, and there is a new **Record** row. The source-of-truth row for that section names the `decision` subparser and `… decision add --help`. The status-header date stays `2026-10-04`, because that is already today's UTC date (`date -u` printed `Sun Oct  4 06:55:05 UTC 2026`).

**E. Tests**: one new file, `tests/factory/test_decision_log.py`, with 21 tests (described below).

Callers of the changed functions, found by `grep -rn` over `factory/` and `tests/`:
- `specstore.archive` has one caller, `cli.archive_cmd`, at `factory/cli.py:948`.
- `compose.compose` has one caller, `cli.run_compose`, at line 274.
- `resolve` is reached only through its parser, at line 1103.
- `record_decision` is called from `archive` and from the two CLI paths. `decision_text` is called from `record_decision` and from the up-front check in `resolve`.

## Acceptance results

Each WHEN command ran with bash from the worktree root, exactly as written. Before = base `0d1cef4`; after = `6db43bf`.

| Scenario | Label | Before (base) | After |
|---|---|---|---|
| Decision logged against a closed ticket | NEW | `first=2 state=closed` / `second=2` / `events=0` | `first=0 state=closed` / `second=0` / `TODAY T-0001 Lionbot code lives under lionbot/` / `TODAY T-0001 Second rule` / `events=2` |
| Unknown ticket, blank text and multi-line text are refused | NEW | `unknown=2 blank=2 multiline=2 lines=0` / `valid=2 lines=0` | `unknown=2 blank=2 multiline=2 lines=0` / `valid=0 lines=1` |
| Answer and close each log a decision | NEW | `answer=2 state=parked answers=0` / `close=2 state=parked` | `answer=0 state=ready-for-triage answers=1` / `close=0 state=closed` / `TODAY T-0001 Option B is the standing rule` / `TODAY T-0001 Closed as a recorded decision` |
| Decision refused alone, with a ruling, and on a second close | NEW | `alone=2 ruling=2 state=parked rulings=0 lines=0` / `close=2 state=parked lines=0` / `again=2 lines=0` | `alone=2 ruling=2 state=parked rulings=0 lines=0` / `close=0 state=closed lines=1` / `again=2 lines=1` |
| Documents describe the new writers | NEW | `old_design=yes old_build=yes design=no build=no readme=no changelog=no` | `old_design=no old_build=no design=yes build=yes readme=yes changelog=yes` |
| Spec writer, critic and planner receive the decision log | NEW | triage `['requests/T-0001.md']`, spec_writer `[…, 'openspec/specs/thing/spec.md']`, critic `[…, 'openspec/specs/thing/spec.md']`, planner `['specs/T-0001/v1.md']`, each `in_input=0` | the expected eight lines exactly: triage unchanged with `in_input=0`; spec_writer, critic and planner each end with `'decisions.md'` and print `in_input=1` |
| Empty and absent decision logs add no input source | REGRESSION | the expected five lines | the expected five lines (unchanged) |
| Triage and spec-writer prompts ask about standing decisions | NEW | all four lines `no` | `triage prompt=yes` / `spec_writer prompt=yes` / `01-triage copy=yes` / `02-spec-writer copy=yes` |
| Triage and spec-writer design blocks equal their copies | REGRESSION | `1. Triage SAME` / `2. Spec writer SAME` | `1. Triage SAME` / `2. Spec writer SAME` |

Every "before" output matches the "today" column of the parent's `verification.md`. Every "after" output matches its THEN exactly.

In the refusal scenario, the first line already matched on base, only because the flag did not exist. The parent spec says so, and the second and third lines still differ on base.

Gates, run from the worktree on `6db43bf`:
- `git diff --check main...HEAD` printed nothing and exited 0 (`main` = `0d1cef4`).
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `157 passed in 133.79s`. That is the 136 on base plus the 21 new tests.
- Not a gate: `uv run --frozen ruff check factory tests/factory/test_decision_log.py` printed `All checks passed!`.

## Tests added/changed

Added: `tests/factory/test_decision_log.py`, 21 tests. Like `test_spec_store.py`, they run black-box through `bin/factory` on a throwaway `FACTORY_STATE` store.
- `decision add`:
  - logs against a closed ticket, prints the line and logs two `decision.recorded` events with `via` and a non-empty `by`.
  - appends to an existing log without a spec store.
  - refuses an unknown ticket, and text that is blank, empty, or has `\n` or `\r` (five cases), writing no file and no event.
- `resolve --decision`:
  - `--answer` and `--close` each log a decision. The line appears in `resolve-1.yaml` and `resolve-2.yaml`, in the ticket history and in the events.
  - without the flag, `resolve` writes no `decision` key and no log.
  - the flag is refused alone, and with `--ruling`, `--to spec-gate`, `--redispatch`, or `--ruling` plus `--close`. The ticket file stays byte-for-byte the same, and no ruling or log is written.
  - no decision is logged when the answer or close is itself refused.
  - blank or multi-line text refuses before the answer is appended.
- compose:
  - the spec writer, critic and planner get the log as a source and in their input, under the new heading; triage gets neither.
  - the planner gets the log before a ruling.
  - an absent, empty, `\n`-only or whitespace-only log adds no source for any of the three roles.
- prompts:
  - the triage and spec-writer system prompts of a started run contain "standing decision".
  - the §1 and §2 design blocks contain the phrase and equal their `docs/prompts/` copies.

Before the code for parts A and B, 12 of these failed for the expected reason: `decision` was an invalid argparse choice, `--decision` was not recognised, or `decisions.md` was missing from the sources. Part C was already applied when the tests first ran, so its tests passed on that first run.

Changed: none. The exact-source assertions the parent names stay green because their stores have no `decisions.md`, or only the empty one `factory init` creates. The full suite passes unchanged.

## Known gaps and uncertainties

- **Archive no longer creates an empty log.** Before, archive opened `decisions.md` in append mode even when the proposal had no Decisions lines, which created an empty file. Through `record_decision` it now writes nothing in that case. This shows only in a store where `factory init` ran and `decisions.md` was then deleted. Line format, refusals and current truth are unchanged, and the existing archive tests pass.
- **Archive's "nothing here refuses" still holds, but by argument, not by a test.** `record_decision` can refuse. Archive feeds it lines from `decisions_of()`, which are already stripped, non-blank and single-line: they come out of `splitlines()`, and wrapped lines are joined with a space. So the refusal cannot fire from archive, but no test covers that path.
- **The README describes a command no real ticket has run yet.** Its "Ground truth only" rule says a thing appears only after it has run on a real ticket. The parent spec's part D.4 and its acceptance (`readme=yes`) require the new rows anyway, so I followed the spec.
- **The README Record row is written to the spec, not to its own source-of-truth rule.** The "Where a human decides" row now names `… decision add --help` as the way to re-derive it. That help text exists only in this dev checkout until the runtime moves.
- **The changelog date is the UTC date of this change.** Entry 46 is dated 2026-10-04, the UTC date of this change. The Nanobot ticket it cites closed earlier.
- **The prompt edit still needs your acceptance test.** Before the runtime checkout moves to this revision, read the new NEEDS-HUMAN wording in `factory/prompts/triage.md` and `spec_writer.md`. This is parent Operator step 1, and this ticket cannot do it.
- factory: markers added: none.

## Out-of-scope observations

- Combining `resolve` modes is otherwise unguarded. For example, `--answer F --ruling R` runs only the answer and ignores the ruling, with no refusal. This change guards that only where `--decision` is involved.
- `resolve` creates `approvals/<id>/` before its own refusals run, so a refused `resolve` leaves an empty directory behind. Many refusals predate this ticket. The new `--decision` refusals run before that point and do not add to it.
- The parent's Out-of-scope observations still apply. Triage does not receive the log. Queued requests #24 and #27 also change `compose()`, so building them close to this one may conflict there.

## Responses to findings

None (round 1).

STATUS: READY-FOR-REVIEW
CONFIDENCE: high, every acceptance command prints its THEN exactly and both gates pass (157 passed); the only behaviour beyond the spec's text is refusing `--ruling … --close --decision`, which its never-drop rule implies.
ESCALATIONS: none
