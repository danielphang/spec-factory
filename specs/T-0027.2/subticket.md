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
