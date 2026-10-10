### T-0040.C / Documents
Depends on: T-0040.A, T-0040.B
Parallel-safe: no (it documents what A and B build, so it runs after both)

Parent: T-0040 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0040/v3.md`). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part C, items 1 to 4 of design.md:
- README:
  - a how-to for `factory drive` under "Starting a run";
  - a row for the role processes under "What depends on Claude Code";
  - a bullet for the driver under **Built**, ending "It is tested, and has not yet run a real ticket";
  - the **Not built** "Per-role effort settings" bullet removed, with its replacement under **Built**;
  - a `drive/<ticket>.yaml` row in the store's file table;
  - the "Store records" row updated;
  - the status date bumped, and any quoted figure re-derived, as "Maintaining this page" requires.
- `docs/design.md`: piece 2, the fence paragraph, and "Running on another agent host".
- `dev/build-harness.spec.md`: R3, R6 (keep "nor `dontAsk`"), part H and I.4.
- `docs/changelog.md`: one entry at the next free number, which is 67 today, placed before "Declined:".

Do not change any prompt block in `docs/design.md`. Its `docs/prompts/` copy is protected and the parent does not declare it. If a needed edit falls inside a prompt block, escalate.

Acceptance:
- NEW. "The documents describe the driver".
  - WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; r=README.md; echo "starting=$(y $(sed -n '/^## Starting a run/,/^### Filing a request/p' $r | grep -c 'factory drive')) depends=$(y $(sed -n '/^### What depends on Claude Code/,/^## Terms used/p' $r | grep -c 'claude -p')) built=$(y $(sed -n '/^\*\*Built\*\*/,/^\*\*Not built\*\*/p' $r | grep -c 'factory drive')) effort-gap=$(y $(grep -c 'none has an effort level' $r)) drive-row=$(y $(grep -cE '^\| `drive/' $r)) design=$(y $(grep -c 'factory drive' docs/design.md)) changelog=$(y $(grep -cE '^[0-9]+\. After issues? [^(]*#65' docs/changelog.md)) buildspec=$(y $(grep -c 'factory drive' dev/build-harness.spec.md)) dontask-ban=$(y $(grep -c 'nor `dontAsk`' dev/build-harness.spec.md)) whitespace=$(git diff --check main -- README.md docs dev >/dev/null && echo clean || echo dirty)")`
  - THEN it prints exactly `starting=yes depends=yes built=yes effort-gap=no drive-row=yes design=yes changelog=yes buildspec=yes dontask-ban=yes whitespace=clean`.
- REGRESSION. All nine driver and script scenarios of `specs/build-dispatch/spec.md` must print exactly what A's and B's Acceptance list. That covers intake parity, build parity, role argv, the reply record, concurrency, intake step lines, build step lines, stop and resume, marker and effort, and the Workflow scripts.
- Intermediate check: the harness suite passes.
  - WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, run through the running-code wrapper.
  - THEN it exits 0.

Interim tests: none

Tests to change: none

Protected paths: none

Out of scope:
- any code under `factory/`, `bin/` or `tests/`;
- `docs/prompts/`, `agents/` and `.factory/`;
- the retirement of the Workflow scripts, which is Operator step 5's later ticket.

---

Notes:
- README lags the code from A's merge until C's merge. The briefing expects a new command to update README in the same ticket, but the approved spec puts all the documents in part C. This plan follows the spec. If the operator wants each part to update README, that is a gate edit, not something the planner should decide.
- B's suite cases go in a new test file rather than the `test_drive.py` the spec names (see B's Scope). This keeps the guardrail without listing a sibling's file under Tests to change. The behaviour checked is unchanged.

## Shared plan context (from the plan; applies to every sub-ticket)

The approved spec (v3) already divides the change into three lettered parts, A, B and C, and states their order: B depends on A, and C depends on A and B (design.md, "Size and seams"). It also maps each scenario to a part. This plan keeps that split. Nothing smaller is worth splitting: A and B both edit `factory/drive.py`, and C documents what A and B build. Each of the three runs alone, one after another.

What I checked on `main` at `37848db`: `factory/drive.py` and `tests/factory/test_drive.py` do not exist, and `factory/cli.py` has no `drive`. So the change is not already applied. These things the spec names do exist:
- `STORE_GITIGNORE` at `factory/store.py:49`;
- the three tests to change, at `tests/factory/test_run_scratch.py:121`, `:132` and `:142`;
- the `// --- start` markers at `factory/workflows/intake.js:138` and `factory/workflows/build.js:217`;
- `run_finish` at `factory/cli.py:446`;
- the README anchors the documents scenario reads: "What depends on Claude Code" (line 97), "Terms used on this page" (117), "Starting a run" (690), "Filing a request from an issue tracker" (712), **Built** (828), **Not built** (904), and the "Per-role effort settings" bullet (913);
- R6's "nor `dontAsk`" at `dev/build-harness.spec.md:118`;
- `docs/changelog.md` entries up to 66, then "Declined:" at line 72.

---
