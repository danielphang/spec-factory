Commit: a922a4426c6b6a5416fbb2305e72abbc726451cb (parent close of T-0027; the worktree head equals `main`)

This was a parent-close run. Every scenario of the pinned spec (`specs/T-0027/v3.md`; its build-dispatch part is byte-identical to `openspec/changes/T-0027/`) ran on the head. Each NEW scenario also ran on base 89290547a33a6091860c850fdda7ff285b409fa0, the `main` commit before T-0027.2's first commit (d085ca0). That base was a local clone in the run's scratch directory. Each WHEN command was extracted verbatim from v3.md with `awk -F'`'` (all 18 lines have exactly two backticks). Each ran under `bash` from the checkout root after `uv sync --frozen`, with a fresh HOME and `TMPDIR` set to the scratch `tmp/` directory. The GIVEN blocks were also extracted verbatim and run once: `t0027-amend.sh` from v3.md lines 207-229, and `t0022-sib.sh` / `t0022-build.mjs` from current truth `openspec/specs/build-dispatch/spec.md` lines 53-100. Node v24.14.0 was used.

Per criterion:
- NEW | An intent-unchanged amendment re-pins the change and keeps the plan's tasks | base: `exit=2 "approved_version": 1 pinned=0 tasks=1 first=merged` (as the spec states) | PR: `exit=0 "approved_version": 2 pinned=1 tasks=1 first=merged` | PASS
- NEW | A later implementer run receives the amended spec, and the record lists what changed | base: `changed=0 merged=0 reason=0 logged=0` / `amended=0 old=1 run_version=1` | PR: `changed=1 merged=1 reason=1 logged=1` / `amended=1 old=0 run_version=2` | PASS
- NEW | Archive after an amendment writes the amended scenario | base: `archive=0 hello=0 hi=1` | PR: `archive=0 hello=1 hi=0` | PASS
- NEW | An amendment declared or found to change intent is refused, naming what a restart keeps and discards | base: both lines all zeros, then `"approved_version": 1 versions=1 records=0` | PR: `intent=changed exit_json=1 restart=1 decision=0 merged=1 pending=1 paths=1` / `intent=unchanged exit_json=1 restart=1 decision=1 merged=1 pending=1 paths=1` / `"approved_version": 1 versions=1 records=0` | PASS
- NEW | An amendment after archive is refused | base: `late=0 changes=archive hello=0` | PR: `late=1 changes=archive hello=1` | PASS
- NEW | A malformed amendment, a sub-ticket target and a two-line reason are refused and write nothing | base: `malformed=0 subticket=0 reason=0 "approved_version": 1 v2=0 records=0` | PR: `malformed=1 subticket=1 reason=1 "approved_version": 1 v2=0 records=0` | PASS
- NEW | An amendment is refused while a sub-ticket's run is in flight, naming the run | base: `exit=2 names_run=0 "approved_version": 1 v2=0 pinned_old=1 records=0` | PR: `exit=2 names_run=1 "approved_version": 1 v2=0 pinned_old=1 records=0` | PASS
- NEW | A sub-ticket whose Acceptance names an unmerged sibling it does not depend on is refused until that sibling merges | base: `unmerged: blocked=0 names=0 runs=1 ready-for-implementer` / `merged: exit=2 runs=1` | PR: `unmerged: blocked=1 names=1 runs=0 ready-for-implementer` / `merged: exit=0 runs=1` | PASS
- NEW | A test changed beside a file the spec names parks the sub-ticket, and a ruling lets it start | base: `park T-0001.1: EMPTY-OUTPUT from implementer` / `greet=0 other=0 runs=2` / `ruled: exit=2 runs=2` | PR: `park T-0001.1: BLOCKED from harness: spec drift:` / `greet=1 other=0 runs=0` / `ruled: exit=0 runs=1` | PASS
- REGRESSION | Unrelated changes, a listed test and an amendment written after the change let the implementer start | base: not run | PR: `other: exit=0 runs=1` / `listed: exit=0 runs=1` / `amended: exit=0 runs=1` | PASS
- NEW | The critic's input lists approved changes not yet archived, other than its own | base: `listed=0 self=0 decision=0 requirement=0` / `after_archive: heading=0 listed=0` | PR: `listed=1 self=0 decision=1 requirement=1` / `after_archive: heading=1 listed=0` | PASS
- NEW | A change sent back to the spec writer leaves the critic's list | base: `listed=0 self=0 decision=0 requirement=0` / `respec: heading=0 listed=0` | PR: `listed=1 self=0 decision=1 requirement=1` / `respec: heading=1 listed=0` | PASS
- NEW | A critic run's system prompt carries the cross-ticket rule | base: `rule=0` | PR: `rule=1` | PASS
- REGRESSION | The runtime critic prompt stays a copy of the documented one | base: not run | PR: `copies=same` | PASS
- NEW | The changelog records the change in one contiguous entry | base: `CONTIGUOUS`, `0`, `0` | PR: `CONTIGUOUS`, `1`, `6` | PASS
- NEW | The design doc and build spec name the amend command, its intent flag, spec drift and the critic's new input | base: `amend=0 intent=0 drift=0 row=0 build=0 build_drift=0` | PR: `amend=1 intent=1 drift=1 row=1 build=1 build_drift=1` | PASS
- NEW | README lists the amend command and the drift check | base: `amend=0 intent=0 built=0` | PR: `amend=1 intent=1 built=1` | PASS
- REGRESSION | The change adds no whitespace errors | base: not run | PR: `exit=0` | PASS

Every NEW scenario's base output matches, line for line, the "today" output in verification.md.

Gate suite: PASS
  `git diff --check main...HEAD`: exit 0. This is vacuous on a parent close, because `main` is HEAD. The probe below runs the same check over the whole parent change.
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `486 passed in 309.35s`, no failures.

Probes:
- `git diff --check 8929054 HEAD` (the whole parent change, 13 files, +1154/-22) → exit 0 → OK
- Amendment that restates the requirement (`SHALL greet` → `MUST greet`) with `--intent unchanged` → `"ok": false`, `intent changed (requirement restated: demo ADDED Greets)` followed by the restart note → OK
- Amendment that renames the requirement → refused: `requirement removed: demo ADDED Greets; requirement added: demo ADDED Greets loudly` → OK
- Amendment with whitespace-only edits to the Problem and Decisions lines and a changed scenario, with a hand-written `approvals/T-0001/amendment-1.md` already present → accepted, record `amendment-2.md`; `specs/T-0001/v2.yaml` written beside `v1.yaml` → OK (the whitespace rule and the `_next_n` numbering both hold)
- `--reason "   "` → `"ok": false, "error": "--reason is one non-blank line of text"` → OK
- Sibling rule, a near-miss on the token boundary: Acceptance `see T-0001.10 and ST-1.2 and ST-12` while ST-1 is unmerged → run starts (`"ok": true`); none of these tokens counts as naming ST-1 → OK
- Sibling rule with a dependency: ST-2 `Depends on: ST-1` names ST-1 in Acceptance, with its status set to ready-for-implementer by hand → run starts, no drift finding → OK (the dependency closure excludes it)
- Test rule with the other two test-name forms: `pkg/greet_test.go` and `web/greet.test.ts` landed beside `src/greet.py` → each refused with `spec drift: <file> changed by <sha> since spec v1 was written at <sha>` → OK. A non-test file (`docs/testing_notes.md`) beside it → run starts → OK
- Human-only check: `grep -rn "spec amend" factory/workflows factory/prompts agents docs/prompts` → no matches → OK

Protected paths changed between base and head: `factory/cli.py`, `factory/compose.py`, `factory/specstore.py`, `factory/subtickets.py`, `factory/prompts/critic.md` and `docs/prompts/03-spec-critic.md`. The spec's Risk section declares all of them. `factory/gitops.py`, `factory/workflows/`, `bin/`, `agents/`, `pyproject.toml` and `uv.lock` are unchanged.

STATUS: VERIFIED
CONFIDENCE: high. All 18 scenarios gave their exact expected output on the head, every NEW scenario failed on base exactly as the spec states, the full suite passed (486), and the boundary probes show the logic is general, not fitted to the tested inputs.
ESCALATIONS: none
