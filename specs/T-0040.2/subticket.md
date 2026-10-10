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
