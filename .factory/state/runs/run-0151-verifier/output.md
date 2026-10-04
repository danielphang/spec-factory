Commit: 6db43bf1ea50df49b0e56476f66a4ff7be6b69fc (branch `factory/T-0017.1`, worktree `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0151-verifier/wt`, clean before and after). Base: 0d1cef4a8b6b534e177f16f779a1c6161f69c853, which is also `main` and the merge base. I ran the base in a separate detached worktree in my scratchpad and removed it afterwards.

How I ran it: I saved each WHEN command verbatim into one bash script, then ran that script with bash from the root of each checkout. The PR run was at `date -u` = `Sun Oct  4 07:01:12 UTC 2026`, so no run straddled UTC midnight.

Per criterion: label | command | base | PR | result

1. NEW | Decision logged against a closed ticket | `first=2 state=closed` / `second=2` / `events=0` | `first=0 state=closed` / `second=0` / `TODAY T-0001 Lionbot code lives under lionbot/` / `TODAY T-0001 Second rule` / `events=2` | PASS
2. NEW | Unknown ticket, blank text and multi-line text are refused | `unknown=2 blank=2 multiline=2 lines=0` / `valid=2 lines=0` | `unknown=2 blank=2 multiline=2 lines=0` / `valid=0 lines=1` | PASS
3. NEW | Answer and close each log a decision | `answer=2 state=parked answers=0` / `close=2 state=parked` | `answer=0 state=ready-for-triage answers=1` / `close=0 state=closed` / `TODAY T-0001 Option B is the standing rule` / `TODAY T-0001 Closed as a recorded decision` | PASS
4. NEW | Decision refused alone, with a ruling, and on a second close | `alone=2 ruling=2 state=parked rulings=0 lines=0` / `close=2 state=parked lines=0` / `again=2 lines=0` | `alone=2 ruling=2 state=parked rulings=0 lines=0` / `close=0 state=closed lines=1` / `again=2 lines=1` | PASS. The first line also matches on base, but only because the flag does not exist there. The parent's `verification.md` predicts exactly that, and lines 2 and 3 fail on base as it says.
5. NEW | Documents describe the new writers | `old_design=yes old_build=yes design=no build=no readme=no changelog=no` | `old_design=no old_build=no design=yes build=yes readme=yes changelog=yes` | PASS
6. NEW | Spec writer, critic and planner receive the decision log | triage `['requests/T-0001.md']`; spec_writer `['requests/T-0001.md', 'openspec/specs/thing/spec.md']`; critic `['specs/T-0001/v1.md', 'openspec/specs/thing/spec.md']`; planner `['specs/T-0001/v1.md']`; every role `in_input=0` | the expected eight lines exactly: triage unchanged with `in_input=0`; spec_writer, critic and planner each end with `'decisions.md'` and print `in_input=1` | PASS
7. REGRESSION | Empty and absent decision logs add no input source | the expected five lines | the expected five lines | PASS
8. NEW | Triage and spec-writer prompts ask about standing decisions | all four lines `no` | `triage prompt=yes` / `spec_writer prompt=yes` / `01-triage copy=yes` / `02-spec-writer copy=yes` | PASS
9. REGRESSION | Triage and spec-writer design blocks equal their copies | `1. Triage SAME` / `2. Spec writer SAME` | `1. Triage SAME` / `2. Spec writer SAME` | PASS

Every base output matches the "Today" column of the parent's `verification.md`. Every NEW criterion fails on base for the reason the spec states: no `decision` command, no `--decision` flag, no `decisions.md` source, no prompt wording, or the old document text.

Gate suite: PASS. I ran both commands from the worktree on 6db43bf.
- `git diff --check main...HEAD` printed nothing and exited 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `157 passed in 150.70s (0:02:30)` and exited 0. That is 136 on base plus the 21 tests in the new file `tests/factory/test_decision_log.py`. No existing test file changed: the diff stat touches only that new file under `tests/`.

Part C side check. The spec requires the harness prompts to keep their existing differences from the `docs/prompts/` copies. `diff docs/prompts/0{1-triage,2-spec-writer}.md factory/prompts/{triage,spec_writer}.md` shows the same two differences on base and on the PR: the "Acceptance items describe behaviour" rule, and `400` in place of `{400}`. The only change is that their line offsets shifted.

Probes. Each ran on a throwaway `FACTORY_STATE` from the PR worktree.
- `decision add T-0001 ""` → exit 2, no file written → OK
- text containing `\r` → exit 2; text containing U+2028 (a Unicode line separator) → exit 2. Neither writes anything. The one-line check is not limited to `\n` → OK
- text wrapped in tabs and spaces → exit 0, line `2026-10-04 T-0001 tabbed rule`, stripped → OK
- 20,000-character text → exit 0, one line written, file is 20049 bytes → OK
- text starting with `-` (`"-leading dash"`) → exit 0, logged as given; same with `--` before it → OK
- `resolve --answer F --decision "nope"` on an unparked ticket → exit 2, no decision line, no answer appended → OK (the decision is not logged when the answer itself is refused)
- `resolve --answer F --decision "   "` on a NEEDS-HUMAN park → exit 2, no answer appended, ticket still `parked`, no decision line → OK (the text check runs before any write)
- `resolve --ruling F --close --decision x` → exit 2, ticket still `parked`, no line → OK. The implementer's extra guard works: without it, the ruling would run and the decision would be silently dropped.
- `resolve --to spec-gate --decision x` → exit 2; `resolve --redispatch --decision x` → exit 2. No line written by either → OK
- `resolve --answer F --decision "real rule"` → exit 0. The decision line appears in `approvals/T-0001/resolve-1.yaml`, in the ticket history (`decision:` key), in the printed result, and in a `decision.recorded` event with `via: resolve --answer` and `by: dphang` → OK. This covers the part the sub-ticket left to the reviewer.
- Compose with a whitespace-only `decisions.md` (`"  \t\n \n\n"`) in a store where `factory init` never ran → no `decisions.md` source for the critic or the planner → OK
- Compose for the planner with a non-empty log and a ruling present → sources `['specs/T-0001/v1.md', 'decisions.md', 'approvals/T-0001/ruling-1.md']`, so the log comes before the ruling → OK. With the same store, the implementer gets no `decisions.md` source → OK
- An existing `decisions.md` with no trailing newline (for example a hand-edited file), then `decision add` → the new line is joined onto the last line: `legacy line no newline2026-10-04 T-0001 after legacy`. → CONCERN, outside this sub-ticket's criteria. Archive's old code appended the same way, so this is not a regression and not special-casing. But the new command makes hand-maintained logs more likely, and this breaks "one line per decision". See ESCALATIONS.

Code read. The diff matches the parent's design A and B:
- `record_decision`, `decision_text` and `_utc_date` are in `factory/specstore.py`, and `archive()` writes its Decisions lines through `record_decision`.
- `resolve()` in `factory/cli.py` runs the `--decision` check and the text check before `load_ticket` and before any write. It logs the decision only inside the `--answer` and `--close` branches, after their own refusals.
- In `factory/compose.py`, `add_decisions()` is called right after `add_truth()` for the spec writer and the critic, and right after the approved spec for the planner, before its rulings loop.

Nothing in the code special-cases the acceptance inputs.

STATUS: VERIFIED
CONFIDENCE: high. I ran all nine acceptance commands verbatim on base and on the PR; every PR output matches its THEN exactly, and every NEW criterion fails on base for the reason the spec states. Both gates pass (157 passed). Thirteen probes behaved correctly; the one concern is pre-existing behaviour outside the criteria.
ESCALATIONS:
- A `decisions.md` with no trailing newline corrupts the next entry. `record_decision` opens the file in append mode and writes `line + "\n"`. If the file's last byte is not a newline, as happens after a hand edit or a truncated write, the new decision is joined onto the previous line. I reproduced this with `decision add`. Archive behaved the same way before this change, so it is not a regression. But the new command invites hand-maintained logs, and the parent spec promises one line per decision. A follow-up could add a newline first whenever the file is non-empty and does not end with one. This needs an owner's call, not a fix in this ticket.
