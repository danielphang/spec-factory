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
