# Plan for T-0040: `factory drive`, the external dispatcher

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

### T-0040.A / The driver core and the intake phase
Depends on: none
Parallel-safe: no (B and C build on it, and B edits the same `factory/drive.py`)

Parent: T-0040 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0040/v3.md`). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part A, items 1 to 10 of design.md:
- the `drive` subparser, with `--phase`, `--parallel` and `--prompt-mode`;
- `call()` through `factory.cli.main`;
- `run_role()` and the `claude -p` argv;
- `run finish --reply`;
- the intake routing ported from `intake.js`;
- phase selection from the stored state;
- progress lines, `drive/<parent id>.yaml`, and `drive/` added to `STORE_GITIGNORE`;
- the SIGINT/SIGTERM stop sequence;
- the commented `effort:` example in `factory/instance.template.yaml`;
- `tests/factory/test_drive.py`, plus the three tests listed under Tests to change.

Interim behaviour: until B lands, the build phase does not exist. If `--phase build` is given, or the stored state selects build, the driver must refuse with a non-zero exit and an error saying the build phase is not built yet, and it must write nothing to the store. It must not try to route those states. Do not add a suite test that pins this refusal, because B replaces it.

Acceptance:
- NEW. "The driver takes the intake fixtures through the same routes as the intake script".
  - WHEN `(for P in '{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "REVISE"}, {"write": "APPROVE"}]}' '{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "REVISE"}]}' '{"triage": [{"say": "still waiting on my commands"}]}' '{"triage": [{"fail": "usage limit reached"}]}'; do (PHASE=intake; . ${TMPDIR:-/tmp}/t0040-parity.sh); done)`
  - THEN it prints exactly these four lines: `awaiting-spec-gate script=5/5 drive=5/5 same`, `parked script=5/5 drive=5/5 same`, `parked script=2/2 drive=2/2 same`, `parked script=1/1 drive=1/1 same`.
- NEW. "Each role run records its process's reply".
  - WHEN the parent's command for that scenario is run (an intake parity run, then the inline Python check of `claude:` in `meta.yaml` and of `reply.json`).
  - THEN it prints exactly `triage=ok spec_writer=ok critic=ok`.
- NEW. "Every intake step line names its ticket and title, and the status file shows the end".
  - WHEN the parent's command for that scenario is run.
  - THEN it prints exactly `steps=yes untagged=0 last=1 status=T-0001 Fixture awaiting-spec-gate 0 ignored=1`.
- NEW. "A stopped driver ends its role process, records the run as killed and resumes from the stored state". It runs with no `--phase`, so it also checks that a `ready-for-triage` state selects intake.
  - WHEN the parent's command for that scenario is run.
  - THEN it prints exactly `stop: exit=143 running=1 run=KILLED ready-for-triage in_flight: [] child=gone last=1`, then `resumed: exit=0 closed calls=2`.
- NEW. "The driver marks its own store calls, never its roles', and passes a configured effort".
  - WHEN the parent's command for that scenario is run, after the `t0024-inflight.sh` GIVEN block.
  - THEN it prints exactly `unmarked=2 marked=0 closed calls=1 effort=1 dispatch=1 inside=2`.
- NEW, an intermediate check: the intake half of "Each role runs as one claude process with its prompt, model and tool limits". This checks the argv, the prompt, the tool lists, the `Edit` rules and the dropped marker for the three intake roles. The full scenario needs B.
  - WHEN `(P='{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "APPROVE"}]}'; PHASE=intake; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; .venv/bin/python ${TMPDIR:-/tmp}/t0040-calls.py $D/drive.log)`
  - THEN it prints exactly `critic ok`, `spec_writer ok`, `triage ok`, one per line.
- REGRESSION. "The Workflow scripts still take both fixtures to the end of their routes".
  - WHEN the parent's command for that scenario is run.
  - THEN it prints exactly `T-0001.1 merged T-0001 parked`, then `T-0001 awaiting-spec-gate`.
- Intermediate check: the harness suite passes, including the new `tests/factory/test_drive.py` and the three changed `test_run_scratch.py` tests.
  - WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, run through the running-code wrapper.
  - THEN it exits 0.

Before any of these scenarios, run their GIVEN blocks once: the six fixture files written by the first scenario's block, `t0023-parent.sh` (from the human-resolution scenario of current truth), and `t0024-inflight.sh` (from live-store-guard).

Interim tests: none. A must not pin the interim build-phase refusal in a test.

Tests to change:
- `tests/factory/test_run_scratch.py::test_a_new_store_gitignore_is_the_full_commented_block_once`: the block now has 4 comment lines, not 3, and the loop over entries also counts `drive/` once.
- `tests/factory/test_run_scratch.py::test_an_existing_store_gitignore_gains_only_the_missing_lines`: the expected line list now ends `"runs/*/scratch/", "drive/"`.
- `tests/factory/test_run_scratch.py::test_an_existing_store_gitignore_without_a_final_newline_keeps_its_last_line`: the same change, so its list now ends with `"drive/"`.

Protected paths: `factory/**` (`factory/drive.py`, `factory/cli.py`, `factory/store.py`, `factory/instance.template.yaml`)

Out of scope:
- part B: build routing, the checkers' concurrency, the `--parallel` semaphore, and sub-ticket progress lines;
- part C: README, `docs/design.md`, `dev/build-harness.spec.md` and `docs/changelog.md`;
- everything under the parent's Out of scope, including any change to `factory/workflows/*.js`, `agents/`, `docs/prompts/` or either instance's `.factory/` files.

---

### T-0040.B / The build phase
Depends on: T-0040.A
Parallel-safe: no (it edits `factory/drive.py`, which A creates, and C depends on it)

Parent: T-0040 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0040/v3.md`). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part B, items 1 to 4 of design.md:
- `build.js` ported from `// --- start` to its end, with `buildOne`, branch for branch;
- the two checkers run with `asyncio.gather`;
- ready sub-tickets run under a semaphore of `--parallel N`;
- progress lines and status-file `running` entries for sub-tickets;
- the build-route suite cases.

This sub-ticket also replaces A's interim build-phase refusal.

Put the new suite cases in a new file, `tests/factory/test_drive_build.py`. The file may import A's stand-in `claude` helper from `tests/factory/test_drive.py`, or copy it. The spec says these cases go in `test_drive.py`, but the guardrail allows new tests only in new files, and A's file is not on the parent's Tests to change list. This changes where the tests live, not what they check.

Acceptance:
- NEW. "The driver takes the build fixtures through the same routes as the build script".
  - WHEN `(for P in '{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"write": "APPROVE"}], "verifier": [{"write": "VERIFIED"}]}' '{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"write": "REQUEST-CHANGES"}], "verifier": [{"write": "VERIFIED"}]}' '{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"say": ""}], "verifier": [{"write": "SPEC-DEFECT"}]}' '{"implementer": [{"write": "BLOCKED"}]}'; do (PHASE=build; . ${TMPDIR:-/tmp}/t0040-parity.sh); done)`
  - THEN it prints exactly these four lines: `parked script=4/4 drive=4/4 same`, `planned script=6/6 drive=6/6 same`, `planned script=4/4 drive=4/4 same`, `planned script=1/1 drive=1/1 same`.
- NEW. "Each role runs as one claude process with its prompt, model and tool limits", in full. The intake half already passes after A; the build half does not.
  - WHEN the parent's command for that scenario is run (an intake parity run, then a build parity run, each followed by `t0040-calls.py`).
  - THEN it prints exactly `critic ok`, `spec_writer ok`, `triage ok`, `implementer ok`, `reviewer ok`, `verifier ok`, `verifier ok`, one per line.
- NEW. "The checkers run at once, and sub-tickets up to the parallel limit".
  - WHEN the parent's command for that scenario is run.
  - THEN it prints exactly `parallel=1: calls=4 max=2 parked parked`, then `parallel=default: calls=4 max=4 parked parked`.
- NEW. "Build step lines name the sub-ticket they concern".
  - WHEN the parent's command for that scenario is run.
  - THEN it prints exactly `untagged=0 sub=yes last=1`.
- REGRESSION. These parent scenarios already pass after A, and each must print exactly what A's Acceptance lists:
  - "The driver takes the intake fixtures through the same routes as the intake script";
  - "Each role run records its process's reply";
  - "Every intake step line names its ticket and title, and the status file shows the end";
  - "A stopped driver ends its role process, records the run as killed and resumes from the stored state";
  - "The driver marks its own store calls, never its roles', and passes a configured effort".
- REGRESSION. "The Workflow scripts still take both fixtures to the end of their routes".
  - THEN it prints exactly `T-0001.1 merged T-0001 parked`, then `T-0001 awaiting-spec-gate`.
- Intermediate check: the harness suite passes, including `tests/factory/test_drive_build.py`.
  - WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, run through the running-code wrapper.
  - THEN it exits 0.

Before these scenarios, run the same GIVEN blocks as A.

Interim tests: none

Tests to change: none

Protected paths: `factory/**` (`factory/drive.py`)

Out of scope:
- part A's core, except where the build phase plugs into it. Do not change A's intake routing, `call()`, the argv, `run finish --reply` or the stop sequence, beyond what is needed to run them for build roles and sub-tickets;
- part C's documents;
- the parent's Out of scope, including any change to `factory/workflows/build.js`.

---

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

Coverage map:
- The driver takes the intake fixtures through the same routes as the intake script → T-0040.A
- Each role run records its process's reply → T-0040.A
- Every intake step line names its ticket and title, and the status file shows the end → T-0040.A
- A stopped driver ends its role process, records the run as killed and resumes from the stored state → T-0040.A
- The driver marks its own store calls, never its roles', and passes a configured effort → T-0040.A
- The driver takes the build fixtures through the same routes as the build script → T-0040.B
- Each role runs as one claude process with its prompt, model and tool limits → T-0040.B (intake half checked early in T-0040.A)
- The checkers run at once, and sub-tickets up to the parallel limit → T-0040.B
- Build step lines name the sub-ticket they concern → T-0040.B
- The documents describe the driver → T-0040.C
- The Workflow scripts still take both fixtures to the end of their routes → REGRESSION in T-0040.A, T-0040.B and T-0040.C

STATUS: PLANNED
CONFIDENCE: high. The approved spec names these three parts, their order and which part owns each scenario, and I confirmed on `main` that every file, test, anchor and line the plan relies on exists and that the change is not yet applied.
ESCALATIONS: none
