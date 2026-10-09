Sub-ticket: T-0027.1 (ST-1, part A of `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0027/v3.md`). Branch `factory/T-0027.1`, head `9a99851`, base `8929054`.

## What changed

The factory had no way to correct a spec after the human gate had approved and pinned it. This PR adds that command for a human operator: `factory spec amend PARENT --file F --reason "<one line>" --intent unchanged`. It works only when the correction keeps what the ticket is for. A pinned spec is the frozen, approved version that every later agent run reads. When this repo's store has a spec store, the pinned version is also written out as the ticket's change folder, `openspec/changes/<id>/`.

**Part A, `factory/cli.py`.**
- New `spec amend` subparser: positional `id`, plus `--file`, `--reason` and `--intent` (`unchanged` or `changed`), all three required.
- New `spec_amend(a, root, cfg)`. It runs the seven refusals in the spec's order. Each one raises `Refused`, so the command exits 2, prints `{"ok": false, "error": ...}` and writes nothing:
  1. The ticket is a sub-ticket. The error names its parent.
  2. The ticket is at `awaiting-spec-gate`, and the error points to `approve-spec <id> --edit F`. Or it has no approved version, or it is `closed`.
  3. `--reason`, stripped, is blank or more than one line.
  4. A run is in flight on the parent or on one of its sub-tickets. The error names each run id.
  5. `--intent changed` was given. The error starts `intent changed: ` and carries the restart note.
  6. `specstore.intent_changes` finds a change of intent. The error reads `intent changed (<each change>; ...)`, says what `--intent unchanged` keeps, and carries the restart note.
  7. With a spec store, the change folder is gone because the ticket was archived. Or the gate's own `validate` and `applies` checks fail, and the error reads `spec not amended: <errors>`.
- New `_restart_note(root, t)`. It is one paragraph starting `Restart instead of amending.`. It lists the merged sub-tickets as `<id> / <title> (merge <main_after, 9 chars>)`. It lists the others that are not closed as `<id> / <title>: <status>[, branch <branch>]`, or `none`. It names both restart routes with the ticket id: re-spec and re-plan with `ticket park`, `resolve --to spec-gate` and `approve-spec --edit F`; or close and re-file with `resolve --close` and `ticket new`.
- The writes, in the spec's order:
  - `_add_spec_version(root, t, text, f"amend {a.file}")`, with its current four arguments. ST-3 adds `cfg`.
  - With a spec store: read `tasks.md` (the planner's task list), call `specstore.pin`, then write `tasks.md` back.
  - Set `spec.approved_version = n`.
  - Move the `spec` record of each sub-ticket that is neither merged nor closed to `{version: n, approved_version: n}`. Its `planned_from` is left alone.
  - Write `approvals/<id>/amendment-<k>.md`, where `k` comes from `_next_n`.
  - Log the `spec.amended` event with `ticket`, `by`, `previous`, `version`, `reason` and `record`.
  - Print `{"ok": true, "id", "version", "record"}`.
- `import difflib` (standard library, already used by `factory/compose.py`).

**Part A, `factory/specstore.py`.**
- `scenario_blocks(text)` maps each scenario name to its block. It covers every delta part (the spec's `specs/<capability>/spec.md` sections) and ignores headings inside code fences.
- `intent_of(text)` returns the intent as three things: the `## Problem` body; the `decisions_of` lines; and, for each capability, operation and requirement, the requirement's text before its first scenario. Whitespace runs are collapsed in all three.
- `intent_changes(old, new)` names each difference: `the Problem section`, `Decisions line removed/added: ...`, or `requirement removed/added/restated: <cap> <OP> <name>`.

Reuse: `_approval_dir`, `_next_n`, `_by`, `_rel`, `store.write_text`, `specstore.pin/validate/applies/change_dir/is_active`, `lines_outside_fences`, `_heading`, `split_parts`, `parse_delta`, `decisions_of`, `DELTA_RE` and `SCEN_RE`. No existing function was changed, so there are no callers to re-check. `_add_spec_version` keeps its signature and its two existing callers, `spec_add` and `approve_spec`. I did not reuse `specstore.decision_text` for the reason check, because its refusal message says "a decision".

## Acceptance results

All commands ran from the worktree root through the running-code wrapper, with `TMPDIR` set to this run's scratch directory, after the first scenario's GIVEN block had been run once. The outputs below were captured before the change on base `8929054` and after it on head `9a99851`.

| Scenario | Before (base) | After (head) |
|---|---|---|
| NEW: an intent-unchanged amendment re-pins and keeps tasks | `exit=2 "approved_version": 1 pinned=0 tasks=1 first=merged` | `exit=0 "approved_version": 2 pinned=1 tasks=1 first=merged` |
| NEW: a later implementer run receives the amended spec; the record lists what changed | `changed=0 merged=0 reason=0 logged=0` / `amended=0 old=1 run_version=1` | `changed=1 merged=1 reason=1 logged=1` / `amended=1 old=0 run_version=2` |
| NEW: archive after an amendment | `archive=0 hello=0 hi=1` | `archive=0 hello=1 hi=0` |
| NEW: intent declared or found changed | `intent=changed exit_json=0 restart=0 decision=0 merged=0 pending=0 paths=0` / the same for `intent=unchanged` / `"approved_version": 1 versions=1 records=0` | `intent=changed exit_json=1 restart=1 decision=0 merged=1 pending=1 paths=1` / `intent=unchanged exit_json=1 restart=1 decision=1 merged=1 pending=1 paths=1` / `"approved_version": 1 versions=1 records=0` |
| NEW: amendment after archive | `late=0 changes=archive hello=0` | `late=1 changes=archive hello=1` |
| NEW: malformed, sub-ticket target, two-line reason | `malformed=0 subticket=0 reason=0 "approved_version": 1 v2=0 records=0` | `malformed=1 subticket=1 reason=1 "approved_version": 1 v2=0 records=0` |
| NEW: run in flight | `exit=2 names_run=0 "approved_version": 1 v2=0 pinned_old=1 records=0` | `exit=2 names_run=1 "approved_version": 1 v2=0 pinned_old=1 records=0` |

Every "before" output matches the "today" output in the spec's `verification.md`, so each command failed for the reason the spec describes. Every "after" output is exactly the line the spec expects.

REGRESSION, the harness suite: `uv sync --frozen && uv run --frozen pytest -q -p no:cacheprovider tests/factory` ended with `446 passed in 372.40s`. `main`'s count is 418: `pytest --collect-only tests/factory --ignore tests/factory/test_spec_amend.py` printed `418 tests collected`, and the new file is the only test change. 418 + 28 new tests = 446, with no failures.

REGRESSION, whitespace: `(git diff --check main...HEAD; echo "exit=$?")` printed only `exit=0`.

The two gate commands, run exactly as written: `git diff --check main...HEAD` exited 0. The pytest gate is the 446-passed run above.

## Tests added/changed

New file `tests/factory/test_spec_amend.py`, with 28 tests. Like `test_sibling_tests.py`, it drives `bin/factory` on a throwaway `FACTORY_STATE` with a scratch target repository. Its fixture is built the same way as the spec's GIVEN block.
- **Writes.** Re-pin, `tasks.md` kept, a missing `tasks.md` not created, and the ticket state unchanged. Sub-ticket `spec` records move to v2 while `planned_from` stays 1. No gate approval file is written. The JSON result is checked.
- **The amendment record.** It has the heading, `By`, `Reason` and `Intent` lines. Its scenario lines cover `changed`, `added` and `removed`. Its merged lines appear, or `none`. The record is numbered after a hand-written `amendment-1.md`. The diff is fenced, and the fence is lengthened when the spec itself holds a fence.
- **The `spec.amended` event and its fields.**
- **Later runs.** A later implementer run composes v2 and records `spec_version: 2`. Archive writes the amended scenario into current truth.
- **Each refusal.** Every case asserts exit 2, `ok: false` and a byte-identical store before and after:
  - a sub-ticket target;
  - no approved version;
  - at the gate, pointing to `approve-spec --edit`;
  - a closed ticket;
  - a blank, whitespace-only or two-line reason;
  - a run in flight on a sub-ticket, and one on the parent;
  - `--intent changed`, checked for the restart note's merge sha, branch, `none` lists, a closed sub-ticket left out and all five commands;
  - an intent found changed: a Decisions line, the Problem section, a restated requirement, a renamed requirement and a changed operation;
  - an archived change;
  - a malformed version, which passes the validator's own error through;
  - a delta that does not apply to current truth.
- **The intent check.** Changes to scenarios, whitespace, design text and Tests to change are all accepted. A `#### Scenario:` heading inside a fence is not counted as a scenario.

With `factory/cli.py` and `factory/specstore.py` stashed back to base, all 28 failed (`28 failed in 19.98s`). With the change, all 28 passed. No existing test changed.

## Known gaps and uncertainties

- A `--file` path that does not exist raises `FileNotFoundError`. The command then exits 1 with nothing written, not a `Refused` with exit 2. This matches `approve-spec --edit`, which reads its file the same way. With `--intent changed`, the file is never read, because refusal 5 comes first.
- A merged sub-ticket with no recorded `merge.main_after` appears in the restart note as `(merge not recorded)`. The spec does not cover this case; the acceptance fixture's merged sub-ticket is one, since it is merged with `ticket set`.
- Decisions lines are compared as sets. Reordering or duplicating a Decisions line is not reported as a change of intent.
- An amendment identical to the approved version is accepted. It writes a new version, its scenario list reads `none`, and its diff block is empty. The spec does not ask for a refusal here.
- Without a spec store, the amendment writes the version and `approved_version` but pins nothing. That case has no archived-change check, because there is no change folder. This is as the spec states.
- Within step 2, the gate check comes first, then the missing-approved-version check, then the closed check. A ticket at the gate with no approved version therefore gets the `approve-spec --edit` pointer.
- `factory:` markers added: none.

## Out-of-scope observations

- None of the documents mention the command yet: `docs/design.md`, `docs/changelog.md`, `dev/build-harness.spec.md` and `README.md`. That work is ST-4, as the plan sets out.
- The test package is named `factory` (`tests/factory/__init__.py`), so a test cannot `from factory import specstore`. I tested the helpers through the CLI instead.

## Responses to findings

None. This is round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. All seven NEW acceptance commands print exactly the expected lines on the committed head, both regressions pass (446 = 418 + 28), and the new tests fail on base.
ESCALATIONS: none
