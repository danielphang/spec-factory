# Plan for T-0027: spec amendment, spec drift and the critic's cross-ticket check

The parent spec is NEEDS-SPLIT and names its seams: A stands alone; B and C go together; D needs A; E lands with each part or last. This plan follows them. The three code parts come first, each with its own new tests. The documents (E) come last in one sub-ticket, so the changelog gets one entry written once against what was built, and the first two code sub-tickets share no file and can run side by side. Splitting further would add merges, and every merge makes in-flight siblings re-verify, without making any part easier to review or roll back.

What I checked on `~/dev/spec-factory` `main` (8929054) before planning:
- Every helper the design names exists: `factory/cli.py` `run_start` (198), `_check_sibling_tests` (242), `_add_spec_version(root, t, text, source)` (395, four arguments today), `approve_spec` (843), the `spec` subparser (1564); `factory/specstore.py` `is_active`, `lines_outside_fences`, `_heading`, `split_parts`, `parse_delta`, `validate`, `applies`, `change_dir`, `pin`, `decisions_of`, `archive`, `delta_ops_of_change`, `DELTA_RE`, `SCEN_RE`; `factory/subtickets.py` `PLAN_FIELDS`, `sibling_tests`, `planned_from`, `split_plan`; `factory/gitops.py` `rev`; `factory/compose.py` `_runs_for` and the critic branch (265) with `add_decisions()`.
- `factory/workflows/build.js:81-83` already parks an implementer run start refused with an error that starts `BLOCKED `.
- `t0022-build.mjs`, which a drift scenario reuses, is written by a GIVEN block in current truth (`.factory/store/openspec/specs/build-dispatch/spec.md:82`) and reads only `FACTORY_STATE` and `FACTORY_REPO`.
- The critic rubric item 5 line is at `docs/design.md:462`, `docs/prompts/03-spec-critic.md:21` and `factory/prompts/critic.md:21`.
- The last changelog entry is 64, followed by the closing `Declined:` line, so this change's entry is 65.

One sequencing detail the design leaves implicit: part A calls `_add_spec_version(..., cfg)`, but the `cfg` parameter belongs to part D.1. ST-1 calls `_add_spec_version` with its current four arguments. ST-3 adds `cfg` and passes it from all three callers, `spec_amend` included. Nothing the spec asks for changes.

---

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

### ST-2 / The critic sees approved changes not yet archived, and its rubric asks about them (parts B and C)
Depends on: none
Parallel-safe: yes

Parent: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0027/v3.md`. Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part B, the `## Approved changes not yet archived` section in the critic branch of `factory/compose.py`, after `add_decisions()`, with its skip rules, entry format, `none` body, omission without `openspec/changes/`, and each listed `proposal.md` added to `sources`. Part C: the four rubric lines under item 5 in the design doc's critic block (`docs/design.md`, around line 462), re-copied into `docs/prompts/03-spec-critic.md`, and the runtime copy `factory/prompts/critic.md` with `2` where the others have `{2}`. Edit only the critic block of `docs/design.md`; part E's other design-doc edits are ST-4's. Add new tests in a new file under `tests/factory/` covering B's section with and without other changes.

Acceptance (the first two after the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" has been run once; that block uses only commands that exist on `main`):
- NEW. The critic's input lists approved changes not yet archived, other than its own. THEN `listed=1 self=0 decision=1 requirement=1`, then `after_archive: heading=1 listed=0`.
- NEW. A change sent back to the spec writer leaves the critic's list. THEN `listed=1 self=0 decision=1 requirement=1`, then `respec: heading=1 listed=0`.
- NEW. A critic run's system prompt carries the cross-ticket rule. THEN `rule=1`.
- REGRESSION. The runtime critic prompt stays a copy of the documented one: WHEN `(diff <(sed 's/{2}/2/' docs/prompts/03-spec-critic.md) factory/prompts/critic.md >/dev/null && echo copies=same || echo copies=differ)`. THEN `copies=same`.
- REGRESSION (intermediate). The design doc's critic block and `docs/prompts/03-spec-critic.md` both carry the new lines: WHEN `grep -c 'whichever of the two merges first' docs/design.md docs/prompts/03-spec-critic.md factory/prompts/critic.md`. THEN each file reports `1`.
- REGRESSION (intermediate). The harness suite passes, as in ST-1.
- REGRESSION (intermediate). `git diff --check main...HEAD` exits 0, as in ST-1.

Interim tests: none
Tests to change: none
Protected paths: `factory/compose.py`, `factory/prompts/critic.md`, `docs/prompts/03-spec-critic.md`
Out of scope: `spec amend` (ST-1); the drift check (ST-3); the design doc's Spec store, Spec drift, line-113 and routing-row edits, the changelog, the build spec and README (ST-4).

---

### ST-3 / Spec drift parks a sub-ticket before its first implementer run (part D)
Depends on: ST-1
Parallel-safe: yes

Parent: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0027/v3.md`. Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part D in full. D.1: `_add_spec_version` takes `cfg` and writes `specs/<id>/v<n>.yaml` with `integration_head` (null when the repo or branch does not resolve); `spec_add`, `approve_spec --edit` and ST-1's `spec_amend` all pass `cfg`. D.2: `subtickets.field_text`. D.3: `_check_drift` called in `run_start` for the implementer on a sub-ticket, before `_check_sibling_tests`, skipped when an implementer run has finished or a ruling is on file, with the sibling rule, the test rule and the `BLOCKED from harness: spec drift: ...` refusal, raised before a run id is reserved. A `factory/gitops.py` helper only if one is needed. D.4: no workflow change. Add new tests in a new file under `tests/factory/` covering both rules, the ruling skip and the amendment that clears drift.

Depends on ST-1 because the "amended" case of the third scenario needs `spec amend` and its `v<n>.yaml` record, and because this sub-ticket edits `spec_amend`'s call. It also edits `run_start` in `factory/cli.py`, the file ST-1 edits.

Acceptance (after the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" has been run once; the second also needs the current-truth GIVEN block that writes `t0022-build.mjs`):
- NEW. A sub-ticket whose Acceptance names an unmerged sibling it does not depend on is refused until that sibling merges. THEN `unmerged: blocked=1 names=1 runs=0 ready-for-implementer`, then `merged: exit=0 runs=1`.
- NEW. A test changed beside a file the spec names parks the sub-ticket, and a ruling lets it start. THEN `park T-0001.1: BLOCKED from harness: spec drift:`, then `greet=1 other=0 runs=0`, then `ruled: exit=0 runs=1`.
- REGRESSION (it already passes with ST-1 merged, because no drift check exists yet). Unrelated changes, a listed test and an amendment written after the change let the implementer start. THEN `other: exit=0 runs=1`, then `listed: exit=0 runs=1`, then `amended: exit=0 runs=1`.
- REGRESSION (made true by ST-1; this sub-ticket changes `spec_amend`'s call). An intent-unchanged amendment re-pins the change and keeps the plan's tasks: `exit=0 "approved_version": 2 pinned=1 tasks=1 first=merged`.
- REGRESSION (made true by ST-1; its implementer start now passes through the drift check). A later implementer run receives the amended spec, and the record lists what changed: `changed=1 merged=1 reason=1 logged=1`, then `amended=1 old=0 run_version=2`.
- NEW (intermediate). `spec add` writes the record: after the GIVEN block, WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && sed -n 's/^integration_head: //p' $FACTORY_STATE/specs/T-0001/v1.yaml | grep -cx "$(git -C $T27/t rev-parse main)")`. THEN `1`.
- REGRESSION (intermediate). The harness suite passes, as in ST-1. The current-truth sibling-tests scenarios in `build-dispatch` print the same lines as on this sub-ticket's base.
- REGRESSION (intermediate). `git diff --check main...HEAD` exits 0, as in ST-1.

Interim tests: none
Tests to change: none. The parent lists none. If an existing test fails because the drift check now parks it, do not edit it: escalate.
Protected paths: `factory/cli.py`, `factory/subtickets.py`, `factory/gitops.py` (only if a helper is added)
Out of scope: changes to `spec_amend` other than passing `cfg`; any change to `factory/workflows/build.js` or `resolve`; a new park status; the critic (ST-2); every document (ST-4).

---

### ST-4 / The documents record spec amendment, spec drift and the cross-ticket check (part E)
Depends on: ST-1, ST-2, ST-3
Parallel-safe: yes

Parent: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0027/v3.md`. Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part E, except item 1 (the critic rubric block), which ST-2 landed. In `docs/design.md`: E items 2 (the `**Spec drift.**` paragraph after `**Tests a sibling added.**`), 3 (the Spec store sentence on `factory spec amend ... --intent unchanged`), 4 (line 113) and 5 (the `| Spec writer | READY-FOR-CRITIC / NEEDS-SPLIT | Critic |` row). In `docs/changelog.md`: one new entry, 65, after 64 and before the closing `Declined:` line, covering all of A, B, C and D as part E lists. In `dev/build-harness.spec.md`: the `factory resolve` bullet (line 315) and the Spec store paragraph (line 193). In `README.md`: the Amend row, the Unstick row's `--ruling F` list, the `**Spec amendment and drift.**` Built bullet, and the status date. Describe what ST-1 to ST-3 built, read from the merged code. Read README's "Maintaining this page" section first.

Acceptance:
- NEW. The changelog records the change in one contiguous entry. THEN `CONTIGUOUS`, then `1`, then `6`.
- NEW. The design doc and build spec name the amend command, its intent flag, spec drift and the critic's new input. THEN `amend=1 intent=1 drift=1 row=1 build=1 build_drift=1`.
- NEW. README lists the amend command and the drift check. THEN `amend=1 intent=1 built=1`.
- REGRESSION. The change adds no whitespace errors: WHEN `(git diff --check main...HEAD; echo "exit=$?")`. THEN only `exit=0`.
- REGRESSION (intermediate). The runtime critic prompt stays a copy of the documented one: `copies=same`. ST-4 must not touch the critic block.
- REGRESSION (intermediate). The harness suite passes, as in ST-1. `tests/factory/test_writing_standard.py` and the other document checks are in it.

Interim tests: none
Tests to change: none
Protected paths: none
Out of scope: any code or prompt file; the critic block of `docs/design.md` and its `docs/prompts/` copy (ST-2).

---

## Coverage map

| Parent scenario | Sub-ticket |
|---|---|
| An intent-unchanged amendment re-pins the change and keeps the plan's tasks | ST-1 (NEW), ST-3 (REGRESSION) |
| A later implementer run receives the amended spec, and the record lists what changed | ST-1 (NEW), ST-3 (REGRESSION) |
| Archive after an amendment writes the amended scenario | ST-1 |
| An amendment declared or found to change intent is refused, naming what a restart keeps and discards | ST-1 |
| An amendment after archive is refused | ST-1 |
| A malformed amendment, a sub-ticket target and a two-line reason are refused and write nothing | ST-1 |
| An amendment is refused while a sub-ticket's run is in flight, naming the run | ST-1 |
| A sub-ticket whose Acceptance names an unmerged sibling it does not depend on is refused until that sibling merges | ST-3 |
| A test changed beside a file the spec names parks the sub-ticket, and a ruling lets it start | ST-3 |
| Unrelated changes, a listed test and an amendment written after the change let the implementer start | ST-3 |
| The critic's input lists approved changes not yet archived, other than its own | ST-2 |
| A change sent back to the spec writer leaves the critic's list | ST-2 |
| A critic run's system prompt carries the cross-ticket rule | ST-2 |
| The runtime critic prompt stays a copy of the documented one | ST-2 (and ST-4 as an intermediate check) |
| The changelog records the change in one contiguous entry | ST-4 |
| The design doc and build spec name the amend command, its intent flag, spec drift and the critic's new input | ST-4 |
| README lists the amend command and the drift check | ST-4 |
| The change adds no whitespace errors | ST-4 (and each earlier sub-ticket as an intermediate check) |

Order: ST-1 and ST-2 can run side by side, because they share no file. ST-3 follows ST-1, and can run alongside ST-2. ST-4 runs last.

## Out-of-scope observations

- The spec's Risk section says T-0031 is approved and `planned`. In the store, `.factory/store/tickets/T-0031.yaml` now reads `status: ready-for-spec-writer` (an untracked `.factory/answers/T-0031-changes-2026-10-09.md` is beside it). Under part B, a critic run would therefore leave T-0031 out of the list. The scenarios use their own throwaway store, so this does not affect them.
- Some line numbers in the spec's Root cause section have moved: `_check_sibling_tests` is at `factory/cli.py:242`, not 213, and the critic's item 5 is at `docs/design.md:462`, not 456. The symbols are the same.

STATUS: PLANNED
CONFIDENCE: medium. The split follows the spec's own seams and every named helper exists on `main`. ST-3's "no existing test breaks" rests on the spec's prototype suite run, which predates T-0033, T-0038 and T-0039 landing on `main`, and I did not re-run the suite.
ESCALATIONS: none
