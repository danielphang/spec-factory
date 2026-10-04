## Findings

[BLOCKING] 6 Decisions, first bullet; Operator steps, step 1
Problem: The first bullet of Decisions and the first Operator step use names specific to this system that no earlier human-facing section has glossed: `decision add`, `--decision`, `factory init` and `resolve` (Decisions), and "the runtime" and "the pre-approval policy" (Operator steps); the Problem says what the change does but never names the command or the flag, so the operator reading Decisions has to infer that `decision add` is the new command and `--decision` the new flag on `resolve`.
Evidence: Read Problem, Evidence, Decisions and Operator steps in order as the gate operator. `resolve` first appears in Evidence ("Who runs `resolve`") with no statement of what it does; `factory init` appears nowhere before Decisions; `decision add` and `--decision` first appear in Out of scope and Decisions; "runtime" and "pre-approval policy" appear only in Operator steps. The writing standard (rule 2) asks for a gloss at first use.
Suggested fix: End the Problem's last paragraph with one sentence naming the pieces, for example "It adds a command, `factory decision add <ticket> "<line>"`, and a `--decision "<line>"` flag on `resolve`, the command a human runs to answer or close a ticket; `factory init`, which creates a store's spec tree, is not needed first", and open Operator step 1 with a clause saying what the runtime is (the pinned harness checkout that runs tickets) and that the pre-approval policy requires the operator to read every prompt change before it runs.

[SHOULD-FIX] 1 Evidence, "The real case" bullet; Risk, first paragraph
Problem: The Nanobot store's `decisions.md` is no longer 0 bytes, so the Risk claim "no run changes until someone logs a decision" is false for that target.
Evidence: `wc -c ~/dev/nanobot-upstream/.factory/state/decisions.md` printed `695` today; the file holds four `2026-10-04 T-0012 …` lines written by archive when T-0012 closed (commit `8d2f0e07c` in that repo). T-0003's decision is still absent, so the Problem and the T-0003 evidence stand. After the runtime moves, every Nanobot spec writer, critic and planner run gains those four lines at once.
Suggested fix: Date the `0` observation ("at the time of T-0003's close") and restate the blast radius: the Nanobot target's three roles receive four lines from the first run after the upgrade; this repo's runs change only once a decision is logged here.

[NIT] 6 Proposed change, D.4 (README)
Problem: The README's "Maintaining this page" table row for "Where a human decides" lists the parser arguments that section is derived from (`approve-spec`, `request-changes`, `resolve`, `--accept-harness`) and D.4 adds a Record row without adding `decision` to that derivation row.
Evidence: `README.md` line 446: "| Where a human decides | `factory/cli.py` `build_parser()`: the `approve-spec`, `request-changes`, `resolve`, `--accept-harness` arguments | …".
Suggested fix: Add "the `decision` subparser" to that row in D.4.

## Spot-checks

- Cited paths and lines are real: `factory/specstore.py` docstring line 6, `init()` lines 55-71 (decisions.md at 67-70), `archive()` lines 310-336 (append at 328-333); `factory/compose.py` `compose()` from line 52, `add_truth()` lines 68-70 called at 81 and 98, planner branch 106-112; `factory/cli.py` `resolve()` 675-742 and parser 1075-1082, with `Refused` exiting 2 at line 1116; `docs/design.md` line 82 and line 97 text as quoted; `dev/build-harness.spec.md` line 193 and the `resolve` synopsis as quoted; the three routing rows (design.md lines 103, 107, 114) exist under the names the spec uses; the "Tests to change" line citations (test_shepherd 48/54/69, test_spec_store 60/66/71, test_p0_cli 108/153/172) are exact-sources assertions on stores with no or an empty `decisions.md`, so Decision B leaves them green.
- Acceptance "Spec writer, critic and planner receive the decision log" ran today: printed the four source lists without `'decisions.md'` and `in_input=0` for every role, as verification.md states. It fails for the stated reason and cannot pass against a stub that adds the file without reading it (`in_input` counts the sentinel in the composed input).
- Acceptance "Decision refused alone, with a ruling, and on a second close" ran today: `alone=2 ruling=2 state=parked rulings=0 lines=0` / `close=2 state=parked lines=0` / `again=2 lines=0`, matching the today description (first line matches only because the flag is unknown; the valid close fails).
- Acceptance "Documents describe the new writers" printed `old_design=yes old_build=yes design=no build=no readme=no changelog=no`; "design blocks equal their copies" printed `1. Triage SAME` / `2. Spec writer SAME`. `factory log tail --event E` prints one JSON line per event, so the `events=2` count in scenario 1 is well-formed.
- Part C's replacement text matches the current blocks: triage.md lines 12-13 and spec_writer.md lines 34-35 read as the spec quotes them; the harness copies differ from `docs/prompts/` only by the "Acceptance items describe behaviour" rule and `400` for `{400}`, as part C.3 says.
- Archive through `record_decision` (A.1) cannot newly refuse: `decisions_of()` (specstore.py line 280) drops blank lines and joins wrapped continuations, so every line it returns is one non-blank line.
- Open-ticket consistency: `dev/issues.md` lists this as #32 and names #24 and #27 as the other `compose()` changes; the spec's Out-of-scope observation records the conflict.

Prior findings: none (round 1)

STATUS: REVISE
CONFIDENCE: high; every cited path and three acceptance commands checked on `main` at `9a48194`, and the one blocking finding is a gloss gap, not a design defect.
ESCALATIONS: none
