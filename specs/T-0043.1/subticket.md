## ST-1 / Count each transcript message once, and add the transcript readers that `factory stats` needs
Depends on: none
Parallel-safe: no (ST-2 builds on the functions this adds, and ST-3 on ST-2)

Parent: T-0043, spec v2 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0043/v2.md`). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part A (all of it: `transcript_usage()`, the once-per-message-id fix in `tally()` and in `calls`, the docstring, `match_transcripts()`, `gate_failures()`, and the unchanged `python -m factory.cost` interface and table), and part D's `tests/factory/test_cost_once.py`.

Acceptance:
- NEW. "The transcript cost report counts each message once". First run the fixture GIVEN block from "Runs and verdicts are counted per role and model, with kills, outcome changes, BLOCKING findings and fixed gate failures" once, as written in the spec. WHEN `(. ${TMPDIR:-/tmp}/t0043-fixture.sh && .venv/bin/python -m factory.cost $F/tx/a | grep '^| critic |')` THEN it prints exactly `| critic | fable-5 | 1 | 2 | 310 | 17 |`. On `main` it prints `| critic | fable-5 | 1 | 5 | 725 | 33 |`.
- NEW (intermediate check). WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_cost_once.py` THEN it passes. The file covers what part D lists for it: `tally()` on repeated message ids; the matching rule (S's own path preferred, the `[Workflow harness — user request]` message skipped, another given store's path ruled out, the started/finished window, a single remaining candidate taken); and `gate_failures()` for a failure fixed later, a failure never fixed, and an input with no "Gate commands" line (returns None).
- REGRESSION (intermediate check). WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory` THEN the whole suite passes.

Interim tests: none
Tests to change: none
Protected paths: `factory/cost.py`
Out of scope: `factory/stats.py`, the `stats` subcommand and every `factory/cli.py` change (ST-2); every document, including the changelog entry that names #61 (ST-3). Do not change the `python -m factory.cost` header or columns.

---

## Shared plan context (from the plan; applies to every sub-ticket)

The approved spec (v2) already names its three seams (design.md, "Proposed change": ST-1 is part A, ST-2 is parts B and C, ST-3 is part E, with part D's tests split between them). This plan follows those seams and does not split further: each one is a single reviewable change, and a fourth would only add a re-verify cycle. The three run in a chain, because each needs the previous one's code or output.

Checked on this checkout (`main` at `5215c5f`, the revision verification.md was captured on): `factory/cost.py` exists and has `tally()` at line 47 and no `transcript_usage`, `match_transcripts` or `gate_failures`; `factory/cli.py` has `build_parser()` at line 1753, `READ_ONLY` at line 1939, `main()` at line 1969 and no `"stats"`; `factory/stats.py`, `tests/factory/test_cost_once.py` and `tests/factory/test_stats.py` do not exist; `tests/factory/test_live_store_guard.py` exists; no file under `tests/factory/` mentions `factory.cost`, `tally` or `READ_ONLY`; and the log shows no earlier plan or sub-ticket for T-0043.

---
