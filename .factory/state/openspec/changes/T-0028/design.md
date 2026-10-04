## Proposed change

Run every command from the root of `~/dev/spec-factory`. The parts are about 380 changed lines in all, about half of them tests. They fit one reviewable merge.

**A. Gate commands may declare the paths they cover.**

A.1 `factory/compose.py`: add `gate_entries(cfg) -> list[tuple[str, list[str] | None]]`. It reads `cfg.get("gate_commands")`, treating absent or null as an empty list. A string entry gives `(command, None)`. A mapping gives `(command, paths)`, or `(command, None)` when it has no `paths`. Raise `store.Refused` naming `gate_commands` and the entry's index in each of these cases:
- the entry is neither a string nor a mapping;
- the mapping has a key other than `command` or `paths`;
- `command` is missing, is not a string, or is empty;
- `paths` is present but is not a list, is empty, or holds an item that is not a non-empty string.

The refusal text says to omit `paths` for a command that always runs. `gate_commands(cfg)` keeps its signature and its `{integration}` substitution, and returns the command strings of `gate_entries(cfg)`.

A.2 `factory/compose.py`: add `gate_skips(cfg, repo, base, head) -> list[dict]`. For each entry with `paths`, run `gitops.git(repo, "diff", "--name-only", f"{base}...{head}", "--", *paths)`. When it prints nothing, append `{"command": <command as written>, "status": "SKIPPED", "reason": f"the diff {base[:9]}...{head[:9]} touches none of its paths: {', '.join(paths)}"}`. A git error propagates as the `Refused` that `gitops.git` raises.

A.3 `factory/cli.py` `run_start`: for a role in `BUILD_ROLES`, call `compose.gate_entries(cfg)` before `tripwire.baseline`, so a malformed entry refuses with exit 2 before a run id is reserved. In `_start_build_run`, for a reviewer or verifier run that is not a parent close, set `meta["gate_skipped"] = compose.gate_skips(cfg, repo, base, head)` before the detached worktree is added. Every other build run gets `meta["gate_skipped"] = []`.

A.4 `factory/compose.py` "Where you work": a reviewer or verifier run on a sub-ticket lists only the commands not in `meta.get("gate_skipped") or []` in the `Gate commands (run each from your worktree, exactly as written; each is already wrapped): …` sentence, each wrapped as today. If every command is skipped, that sentence ends `none (every gate command is skipped below)`. After that line comes one line per skipped command, each starting at column 0 exactly as `SKIPPED by the harness for this diff, do not run: `<command>`: <reason>`. The implementer and the parent-close verifier get every command, as today, and no `SKIPPED` line. The block's text for an instance with no `paths` is byte-identical to today's, which `tests/factory/test_run_isolation.py` checks.

A.5 `factory/cli.py` `results_record`: when `--role verifier` is not `--killed` and `runs/<--run>/meta.yaml` exists with a non-empty `gate_skipped`, the `ci` row also gets `skipped:` holding that list. `store.record_result` gains an optional `extra: dict | None = None` merged into the row. The `ci` status is still parsed from the `Gate suite:` line.

A.6 `factory/instance.template.yaml`: above `gate_commands: []`, a comment gives the two entry forms. It says `paths` are git pathspecs, that a sub-ticket's checkers skip a command whose paths its diff touches none of, and that the exclude form (`:(exclude)dev/`) keeps a new file running the command. The value stays `[]`.

A.7 New test file `tests/factory/test_gate_paths.py`. It covers the scenarios of `specs/gate-commands/spec.md`, run through the CLI on a scratch instance and target, plus the `gate_entries` refusals one by one.

**B. A spec that needs one sub-ticket skips the planner.**

B.1 `factory/cli.py`: add `plan_whole_spec(a, root, cfg)`, registered as `factory plan whole-spec PARENT` in the existing `plan` subparser. The order:
1. Load the parent. Refuse with exit 2, writing nothing:
   - when its status is not `ready-for-planner`: `<id> is <status>, not ready-for-planner`, as `run_start` words it;
   - when it has a run in flight;
   - when it has no approved spec: `<id> has no approved spec`.
2. Find the first reason the planner is needed:
   - the parent has sub-tickets (`store.subtickets_of`);
   - a planner run of the parent exists (`compose._runs_for(root, id, "planner", "")`);
   - its latest finished spec-writer run's `meta.yaml` status is `NEEDS-SPLIT`;
   - the approved spec `specs/<id>/v<approved>.md` has, outside code fences (`specstore.lines_outside_fences`), a line matching `^#{2,3}\s` that is not a `### Requirement:` line and contains `\bseams?\b`, ignoring case.

   If one holds, print `{"ok": true, "id", "planner": "needed", "reason"}` and write nothing.
3. If the spec store is active (`specstore.is_active`) and the change folder is missing, refuse exactly as `spec tasks` does: `<id> has no change folder (no pinned version)`.
4. Otherwise build the text below, then:
   - create sub-ticket `<id>.1` the way `subticket_add` creates one: `type: sub-ticket`, `parent`, `label: whole-spec`, `depends_on: []`, `parallel_safe: true`, `status: ready-for-implementer`, source `plan:whole-spec`, the parent's spec versions, and its text at `specs/<id>.1/subticket.md`;
   - write the same text to `plans/<id>.md` and set the parent's `plan`;
   - write it to the change folder's `tasks.md` when the spec store is active, logging `tasks.written`;
   - log `ticket.created`, then `plan.skipped` with `ticket`, `subticket` and `reason` (`one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run`);
   - print `{"ok": true, "id", "planner": "skipped", "reason", "subtickets": [<as subticket_add prints them>]}`.

   Factor the record-writing loop out of `subticket_add` so both commands use it; `subticket_add`'s behaviour does not change.

The sub-ticket text, with `<names>` as one `- <name>` line per `specstore.scenario_names` of the approved spec, in order:

```text
<id>.1 / <parent title>
Depends on: none
Parallel-safe: yes

Parent: <id>, approved spec v<N>. This sub-ticket is the whole of it; read it in full. The planner was skipped: <reason>.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
<names>
Tests to change: the parent's list.
Protected paths: the parent's Risk list.
```

B.2 `factory/workflows/build.js` phase 1, when the parent is `ready-for-planner`:
- First clerk `${BIN} plan whole-spec ${TICKET}`.
- If it is not ok, park the parent with `harness-bug: plan whole-spec: ${whole.stderr || ''}` and return `parked`.
- If `whole.planner === 'skipped'`, log `${TICKET}: planner skipped (${whole.reason}); one sub-ticket from the whole spec` and run no planner.
- Any other success runs today's planner block unchanged (`runRole('planner')`, `spec tasks`, `plan add`, `subticket add`). A stub that returns `{"ok": true}` gets the planner too.
- Both paths then `transition(TICKET, 'planned')` and go to phase 2.

Nothing else in the script changes. The new clerk command carries `FACTORY_DISPATCH=1` through `BIN`, like every other.

B.3 Where each refusal the plan step gives today fires when the planner is skipped:

| Refusal today | With the planner skipped |
|---|---|
| Planner ESCALATE: the spec is already applied on `main` (`run-0030`, `run-0032`) | The implementer's step 2 runs the NEW checks first and stops with BLOCKED when one already passes. The verifier's step 3 runs the NEW checks on the base and returns SPEC-DEFECT when one passes there. Either parks the sub-ticket for the operator. |
| Planner ESCALATE: acceptance contradicts `main` (`run-0031`) | The implementer escalates on a NEW check that behaves otherwise, and on a REGRESSION check that fails on the base. The verifier reports SPEC-DEFECT or FAILED. |
| Planner ESCALATE: the spec cannot be split without redesign | Cannot arise: nothing is split. |
| `spec tasks`: no change folder while the spec store is active | `plan whole-spec` refuses with the same text, and the build parks it as a harness bug. |
| `spec tasks`, `subticket add`: the run is not a PLANNED planner run | Cannot arise: there is no planner run. `plan whole-spec` checks the parent's state, in-flight runs and approved spec instead. |
| `subticket add`: no approved spec | `plan whole-spec` refuses with the same condition. |
| `subticket add`: plan format (no `Depends on:`, a repeated id, an unknown dependency) | Cannot arise: the harness writes the sub-ticket and there is no plan text to check. |
| `subticket add`: the id already exists | A parent with any sub-ticket goes to the planner. |
| The planner's coverage map: every parent scenario has a sub-ticket | Holds by construction: the one sub-ticket names every scenario. |

The checkers, the merge gate and protected-path review are untouched, and none of their inputs changes except A.4's SKIPPED lines.

B.4 New test file `tests/factory/test_whole_spec_plan.py`. It covers the scenarios of `specs/sub-ticket-planning/spec.md` through the CLI. It also checks that a parent with one whole-spec sub-ticket, merged with a VERIFIED run on the parent's base, gets `reuse` from `ticket parent-check`, using the existing helpers in `tests/factory/test_parent_close_reuse.py` as the model. The build-script scenarios stay acceptance-only under node, as T-0023 decided for the suite.

**C. Documents.**

C.1 `docs/design.md`:
- Routing table, row "Human spec gate | Approved | Planner": the next-role cell adds that when the spec needs one sub-ticket, the harness creates it from the whole spec and the build goes to that sub-ticket's Implementer, logging `plan.skipped`. It names the four conditions of B.1 and the `plan whole-spec` command.
- Row 11 (Gate runner): add that a gate command may name the paths it covers, as git pathspecs. For a sub-ticket whose diff touches none of them, the harness marks it SKIPPED for the checkers, with the reason, and records it on the `ci` row. A command without paths always runs.
- The spec-store table row for `tasks.md`: "Planner, or the harness when it skips the planner".

Prompt blocks do not change.

C.2 `docs/changelog.md`: one entry, numbered after the last entry at merge, covering parts A and B. It names `paths`, SKIPPED, `plan whole-spec`, NEEDS-SPLIT and seams, and records that part A overturns T-0016's cut.

C.3 `dev/build-harness.spec.md`:
- Line 206's command list adds `factory plan whole-spec PARENT`.
- Phase 1 of the workflow (line 284) starts with that clerk command and its three outcomes.
- The `ci` row paragraph (line 320) adds the `skipped:` list.

C.4 `README.md`:
- "How a ticket moves" (line 88): the build creates the one sub-ticket itself when the spec needs only one (`factory plan whole-spec`), and runs the planner otherwise. The sentence "The build workflow runs the planner, which …" no longer stands alone.
- Step 3 of setting up a target (line 260): `gate_commands` entries may declare `paths`.
- The "Build, local-only" bullet (line 361): a skipped command is recorded as SKIPPED with its reason.
- Bump the status date.

## Tests to change

none. `tests/factory/test_run_isolation.py::test_implementer_gate_commands_come_wrapped` checks the implementer's "Where you work" text. A.4 keeps that text byte-identical when no command has `paths`, so the test stays as it is. `tests/factory/test_instance.py` checks the template's `gate_commands == []`, and A.6 keeps that value.
