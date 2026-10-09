### ST-1 / `factory spec amend`: amend a pinned spec whose intent is unchanged (part A)
Depends on: none
Parallel-safe: yes

Parent: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0027/v3.md`. Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part A in full: the `amend` subcommand under `spec`, `spec_amend` with its seven refusals in order, the restart note, the writes (new version, re-pin that keeps `tasks.md`, `approved_version`, the `spec` records of sub-tickets that are neither merged nor closed with `planned_from` left alone, `approvals/<id>/amendment-<k>.md`, the `spec.amended` event, the JSON result), and the `specstore.py` helpers `scenario_blocks`, `intent_of` and `intent_changes`. Call `_add_spec_version(root, t, text, f"amend {file}")` with its current signature: ST-3 adds `cfg`. Add new tests in a new file under `tests/factory/` covering A's writes, each refusal and the intent check, driving `bin/factory` as `tests/factory/test_sibling_tests.py` does.

Acceptance (all from `~/dev/spec-factory`, through the running-code wrapper, after the GIVEN block of the first scenario has been run once):
- NEW. An intent-unchanged amendment re-pins the change and keeps the plan's tasks. WHEN the parent's command for this scenario. THEN it prints exactly `exit=0 "approved_version": 2 pinned=1 tasks=1 first=merged`.
- NEW. A later implementer run receives the amended spec, and the record lists what changed. THEN `changed=1 merged=1 reason=1 logged=1`, then `amended=1 old=0 run_version=2`.
- NEW. Archive after an amendment writes the amended scenario. THEN `archive=0 hello=1 hi=0`.
- NEW. An amendment declared or found to change intent is refused, naming what a restart keeps and discards. THEN `intent=changed exit_json=1 restart=1 decision=0 merged=1 pending=1 paths=1`, then `intent=unchanged exit_json=1 restart=1 decision=1 merged=1 pending=1 paths=1`, then `"approved_version": 1 versions=1 records=0`.
- NEW. An amendment after archive is refused. THEN `late=1 changes=archive hello=1`.
- NEW. A malformed amendment, a sub-ticket target and a two-line reason are refused and write nothing. THEN `malformed=1 subticket=1 reason=1 "approved_version": 1 v2=0 records=0`.
- NEW. An amendment is refused while a sub-ticket's run is in flight, naming the run. THEN `exit=2 names_run=1 "approved_version": 1 v2=0 pinned_old=1 records=0`.
- REGRESSION (intermediate). The harness suite passes: WHEN `uv sync --frozen && uv run --frozen pytest -q -p no:cacheprovider tests/factory`. THEN it ends with `N passed`, no failures, N being `main`'s count plus this sub-ticket's new tests.
- REGRESSION (intermediate). WHEN `(git diff --check main...HEAD; echo "exit=$?")`. THEN only `exit=0`.

Interim tests: none
Tests to change: none
Protected paths: `factory/cli.py`, `factory/specstore.py`
Out of scope: the `v<n>.yaml` record and the `cfg` parameter (ST-3); the drift check (ST-3); the critic's input and prompt (ST-2); every document: `docs/design.md`, `docs/changelog.md`, `dev/build-harness.spec.md`, `README.md` (ST-4).

---

## Shared plan context (from the plan; applies to every sub-ticket)

The parent spec is NEEDS-SPLIT and names its seams: A stands alone; B and C go together; D needs A; E lands with each part or last. This plan follows them. The three code parts come first, each with its own new tests. The documents (E) come last in one sub-ticket, so the changelog gets one entry written once against what was built, and the first two code sub-tickets share no file and can run side by side. Splitting further would add merges, and every merge makes in-flight siblings re-verify, without making any part easier to review or roll back.

What I checked on `~/dev/spec-factory` `main` (8929054) before planning:
- Every helper the design names exists: `factory/cli.py` `run_start` (198), `_check_sibling_tests` (242), `_add_spec_version(root, t, text, source)` (395, four arguments today), `approve_spec` (843), the `spec` subparser (1564); `factory/specstore.py` `is_active`, `lines_outside_fences`, `_heading`, `split_parts`, `parse_delta`, `validate`, `applies`, `change_dir`, `pin`, `decisions_of`, `archive`, `delta_ops_of_change`, `DELTA_RE`, `SCEN_RE`; `factory/subtickets.py` `PLAN_FIELDS`, `sibling_tests`, `planned_from`, `split_plan`; `factory/gitops.py` `rev`; `factory/compose.py` `_runs_for` and the critic branch (265) with `add_decisions()`.
- `factory/workflows/build.js:81-83` already parks an implementer run start refused with an error that starts `BLOCKED `.
- `t0022-build.mjs`, which a drift scenario reuses, is written by a GIVEN block in current truth (`.factory/store/openspec/specs/build-dispatch/spec.md:82`) and reads only `FACTORY_STATE` and `FACTORY_REPO`.
- The critic rubric item 5 line is at `docs/design.md:462`, `docs/prompts/03-spec-critic.md:21` and `factory/prompts/critic.md:21`.
- The last changelog entry is 64, followed by the closing `Declined:` line, so this change's entry is 65.

One sequencing detail the design leaves implicit: part A calls `_add_spec_version(..., cfg)`, but the `cfg` parameter belongs to part D.1. ST-1 calls `_add_spec_version` with its current four arguments. ST-3 adds `cfg` and passes it from all three callers, `spec_amend` included. Nothing the spec asks for changes.

---
