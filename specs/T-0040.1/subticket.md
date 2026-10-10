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
