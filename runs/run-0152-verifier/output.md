Commit: 6cfd43c98c32404a6e332a9cbbc842fb16350233 (main; merge of factory/T-0017.1, task commit 6db43bf). Base: 0d1cef4a8b6b534e177f16f779a1c6161f69c853.

How it ran: head is the verifier worktree `.factory/state/runs/run-0152-verifier/wt`, clean, detached at 6cfd43c. Base is a throwaway detached worktree at 0d1cef4 in my scratchpad, removed afterwards. Each tree got its own `.venv` from `uv sync --frozen`, so `bin/factory` used that tree's code. Each acceptance command was saved to a file and checked by a script to be byte-equal to its block in the spec (9 of 9 equal). Each ran with `bash` from the tree root. Today's UTC date is 2026-10-04, and no run crossed UTC midnight.

Per criterion: NEW/REGRESSION | command | base | PR | PASS/FAIL
- NEW | Decision logged against a closed ticket | `first=2 state=closed` / `second=2` / no decision lines / `events=0` (matches the spec's "today") | `first=0 state=closed` / `second=0` / `TODAY T-0001 Lionbot code lives under lionbot/` / `TODAY T-0001 Second rule` / `events=2`, exact | PASS
- NEW | Unknown ticket, blank text and multi-line text are refused | `unknown=2 blank=2 multiline=2 lines=0` / `valid=2 lines=0` (matches) | `unknown=2 blank=2 multiline=2 lines=0` / `valid=0 lines=1`, exact | PASS
- NEW | Answer and close each log a decision | `answer=2 state=parked answers=0` / `close=2 state=parked` / no lines (matches) | `answer=0 state=ready-for-triage answers=1` / `close=0 state=closed` / both `TODAY T-0001 …` lines, exact | PASS
- NEW | Decision refused alone, with a ruling, and on a second close | `alone=2 ruling=2 state=parked rulings=0 lines=0` / `close=2 state=parked lines=0` / `again=2 lines=0` (matches; first line passes on base only because the flag is unknown, as the spec says) | `alone=2 ruling=2 state=parked rulings=0 lines=0` / `close=0 state=closed lines=1` / `again=2 lines=1`, exact | PASS
- NEW | Documents describe the new writers | `old_design=yes old_build=yes design=no build=no readme=no changelog=no` (matches) | `old_design=no old_build=no design=yes build=yes readme=yes changelog=yes`, exact | PASS
- NEW | Spec writer, critic and planner receive the decision log | triage line matches; spec_writer/critic/planner lack `'decisions.md'`, each `in_input=0` (matches) | all 8 expected lines exact: `decisions.md` is last source for spec_writer and critic (after current truth) and for planner (after approved spec); triage unchanged, `in_input=0` | PASS
- REGRESSION | Empty and absent decision logs add no input source | 5 expected lines, exact | 5 expected lines, exact | PASS
- NEW | Triage and spec-writer prompts ask about standing decisions | all four `no` (matches) | `triage prompt=yes`, `spec_writer prompt=yes`, `01-triage copy=yes`, `02-spec-writer copy=yes` | PASS
- REGRESSION | Triage and spec-writer design blocks equal their copies | `1. Triage SAME` / `2. Spec writer SAME` | `1. Triage SAME` / `2. Spec writer SAME` | PASS

Every NEW criterion fails on base for the reason the spec gives (no `decision` command, no `--decision` flag, old document text, no compose source, old prompt text), and passes on the PR. No criterion is a SPEC-DEFECT.

Gate suite: PASS
- `git diff --check main...HEAD`: exit 0, no output. Note: `main` is HEAD here (parent-close run on main), so this range is empty and checks nothing. I also ran `git diff --check 0d1cef4...HEAD` over the real change: exit 0, no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `157 passed in 141.74s`. The spec gives 136 on base; the 21 more are the new file `tests/factory/test_decision_log.py`. No other test file changed (`git diff 0d1cef4 HEAD --stat -- tests/` lists only that file). Existing archive tests in `tests/factory/test_spec_store.py` that read `decisions.md` (lines 250, 278, 321, 365) still pass now that archive appends through `record_decision`.

Probes: input → result → OK / CONCERN (all on head, throwaway `FACTORY_STATE` under `mktemp -d`)
- `resolve --answer F --decision "$(printf 'one\ntwo')"` on a NEEDS-HUMAN park → exit 2, `a decision is one non-blank line of text`; state `parked`, `answers=0`, no `decisions.md` lines. The answer is not appended before the text is refused. → OK
- `resolve --answer F --decision "$(printf 'one\rtwo')"` (carriage return only) → exit 2, same refusal, nothing written. → OK
- `resolve --to spec-gate --decision x`, `resolve --redispatch --decision x`, `resolve --close --ruling F --decision x` → each exit 2, `--decision applies only with --answer or --close`; state `parked`, 0 lines. → OK
- `resolve --answer F --decision "should not log"` on a `ready-for-triage` ticket, so the answer itself is refused → exit 2, `--answer applies to waiting-requester or a NEEDS-HUMAN park`; 0 answers, 0 lines. → OK
- Valid `resolve --answer F --decision "  Rule with   inner  spaces and unicode é  "` → exit 0. The text is trimmed at both ends and inner spaces are kept. The same line appears in `decisions.md`, in the printed result (`"decision": …`), in the ticket history (`tickets/T-0001.yaml` line 29), in `approvals/T-0001/resolve-1.yaml` line 7, and in a `decision.recorded` event with `"via": "resolve --answer"` and `"by": "dphang"`. → OK
- `decision add T-0001 "-x leading dash"` → exit 0, line `2026-10-04 T-0001 -x leading dash`. → OK
- `decision add` with a 20000-character single-line text → exit 0, line written whole (20019 bytes). → OK
- `decision add T-0001 x` against a store path that does not exist → exit 2, `no ticket T-0001`, and no store directory is created. → OK
- A `decisions.md` whose last line has no trailing newline (a hand edit), then `decision add T-0001 "after"` → the new line is glued onto the old one: `old line no newline2026-10-04 T-0001 after`. → CONCERN, minor. Archive behaved the same before this change, no criterion covers it, and no file the harness writes ends without a newline. It matters only if an operator edits the log by hand, for example while backfilling.

Code read (diff 0d1cef4..HEAD, `factory/`): `specstore.decision_text` / `record_decision` exist and match design A.1, and `archive()` now appends through `record_decision`. `cli.resolve` checks `--decision` and its text before loading the ticket, and calls `decided()` only after each branch's own refusals have passed. `decision_add` loads the ticket without a state check. `compose.add_decisions` adds the log only when the file has non-whitespace text, and is called where design B says. None of this is special-cased to the scenario inputs.

Out-of-scope observations
- `archive()` now runs every Decisions line through `decision_text`, which can raise `Refused`. The `archive` docstring still says "nothing here refuses". `decisions_of` already strips lines and drops blank ones. So a refusal needs a Decisions line holding a character that Python's `splitlines` treats as a line break but a `\n` split does not (for example `\x0c` or ` `). If that happened, archive would stop after it had already applied the deltas to current truth. This is unlikely, and it is not one of this ticket's criteria.

STATUS: VERIFIED
CONFIDENCE: high. All 9 acceptance commands are byte-equal to the spec and printed the exact expected output on head; base printed the spec's stated "today" output for each; both gates pass; probes found no special-casing.
ESCALATIONS: none
