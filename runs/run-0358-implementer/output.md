Sub-ticket: T-0038.1 (parent T-0038, approved spec v2, `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0038/v2.md`)
Branch: `factory/T-0038.1` in `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0038.1`, commit `9aa97bf` on base `f4ea041` (= `main`).

## What changed

Some background first. In the factory, a planner agent splits an approved spec (a numbered version: v1, v2, ...) into sub-tickets under a parent ticket. When the operator sends a planned parent back to the spec gate and approves a new version, the planner splits it again under the same parent. Before this change, the old plan's sub-tickets still counted. One the operator had closed parked the parent for good, and the final check and close waited on old sub-tickets that would never merge. This change makes those old unmerged sub-tickets "superseded": they keep their records and ids, but they no longer count.

- **A. Record the plan.** `factory/cli.py` `_create_subtickets` sets `st["planned_from"] = parent["spec"]["approved_version"]` next to `st["spec"]`. Both `subticket add` and `plan whole-spec` create sub-tickets through it, and nothing else writes the field.
- **B. One rule** in `factory/subtickets.py`:
  - `planned_from(sub)`: the record's `planned_from`, else its `spec.approved_version`, else None.
  - `split_plan(subs) -> (current, superseded)`, in input order. A sub-ticket is superseded when it has not merged, its `planned_from` is set, and that value is lower than the highest one among the parent's sub-tickets.
  - `superseded_by_plan(subs, version)`: the ids `split_plan` would mark once a plan at `version` is added. It is D's `after` set, and E uses it too, so the rule exists once.
- **C. Count only the current plan** (`factory/cli.py`):
  - `ticket_ready_implementers` computes `ready`, the waiting-sibling release, `remaining`, `in_flight`, `parked`, `resumable` and `closed` from the current sub-tickets. It keeps `subtickets` as every id and adds `superseded`.
  - `ticket_parent_check` still refuses a parent with no sub-tickets at all. It runs the all-merged test and builds its `subtickets` map on the current ones, and adds `superseded`.
  - `_reused_subticket_run`, `_parent_close_verified` and `resolve --replan`'s all-merged test use the current sub-tickets. The "has any sub-tickets" tests in `ticket_transition` and `archive_cmd` are unchanged and still look at every sub-ticket.
- **D. Re-planning** (`subticket_add`). Before anything is written, it computes `before` (superseded now) and `after` (superseded once this plan is added). A `Depends on:` naming an id in `after` is refused with exit 2: `<id> (<label>) depends on <dep>, which this plan supersedes`. After the sub-tickets are created, a non-empty `after - before` is logged as `subtickets.superseded` (`ticket`, `subtickets` in id order, `approved_version`). The JSON output gains `superseded`, which is `[]` when there are none.
- **E. Planner input** (`factory/compose.py`). After the `## Sub-tickets already under <id>` list, when D's `after` set is non-empty, there is one blank line and then `Not merged and planned from an earlier approved version, so a new plan supersedes them and may not depend on them: <ids>`. With none, the section is byte-identical: `tests/factory/test_replan.py` still passes unchanged.
- **F. Tests.** New file `tests/factory/test_superseded_plan.py` (see below).
- **G. Documents.**
  - `docs/design.md` gets the bullet "...or a sub-ticket closed by the human, parks the parent..." with the supersede sentence appended.
  - `dev/build-harness.spec.md`'s `ready-implementers` JSON description gains the `superseded` list.
  - `README.md` gets a new "Re-plan after a re-spec." bullet after "Sibling tests check". It ends "It is tested, and has not yet fired on a real ticket."
  - `docs/changelog.md` gets entry 62, "After issue #77 (2026-10-08), ...". It names `planned_from`, superseded sub-tickets and the `Depends on` refusal.

Callers of each existing function changed (coding standard rule 2, from `grep -rn` over `factory/`):
- `_create_subtickets` has two callers, `subticket_add` and `plan_whole_spec`. The fix goes in the shared function so that both paths record `planned_from`.
- `_parent_close_verified` has two callers: `ticket_transition --to closed` (`cli.py:164`) and `archive_cmd` (`cli.py:1382`).
- `_reused_subticket_run` has two callers: `ticket_parent_check` and `_parent_close_verified`. The change sits in each helper, so every one of these paths counts only the current plan.
- `store.subtickets_of` is unchanged. Its other callers are the merge release of waiting siblings, the sibling-tests check and `_planner_needed`. All three still see every sub-ticket, as the spec's Out of scope requires.

## Acceptance results

Each command ran from the worktree root under `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; ...)`. `TMPDIR` pointed at this run's scratch directory. The fixtures `t0023-parent.sh`, `t0023-closed.sh`, `t0023-wf.mjs`, `t0022-build.mjs` and `t0038-respec.sh` were written there from the GIVEN blocks in the T-0023 v2, T-0022 v1 and T-0038 v2 specs. Before = base `f4ea041`, after = `9aa97bf`.

| Scenario | Label | Before | After |
|---|---|---|---|
| After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept | NEW | `add: ` / `ready: "ready": ["T-0001.4"]` / `closed: "closed": ["T-0001.2"]` / `superseded: ` / `kept=T-0001.1.yaml T-0001.2.yaml T-0001.3.yaml T-0001.4.yaml T-0001.yaml logged=0` | `add: "superseded": ["T-0001.2", "T-0001.3"]` / `ready: "ready": ["T-0001.4"]` / `closed: "closed": []` / `superseded: "superseded": ["T-0001.2", "T-0001.3"]` / `kept=T-0001.1.yaml T-0001.2.yaml T-0001.3.yaml T-0001.4.yaml T-0001.yaml logged=1` |
| The plan a sub-ticket belongs to does not move with its spec record, and a record without it falls back to its creation version | NEW | `moved: ` / `unrecorded: ` | `moved: "superseded": ["T-0001.2", "T-0001.3"]` / `unrecorded: "superseded": ["T-0001.2", "T-0001.3"]` |
| A second plan at the same approved version supersedes nothing | REGRESSION | (`exit=0` / `"ready": ["T-0001.2"]` / `"remaining": ["T-0001.2", "T-0001.3"]`) | `exit=0` / `"ready": ["T-0001.2"]` / `"remaining": ["T-0001.2", "T-0001.3"]` |
| A plan that depends on an old unmerged sub-ticket is refused and writes nothing | NEW | `exit=0 names=0 T-0001.1.yaml T-0001.2.yaml T-0001.3.yaml T-0001.4.yaml T-0001.yaml ` | `exit=2 names=1 T-0001.1.yaml T-0001.2.yaml T-0001.3.yaml T-0001.yaml ` |
| A re-specced parent's planner input names the sub-tickets its plan supersedes | NEW | `said=0 listed=3` | `said=1 listed=3` |
| The build of a re-planned parent dispatches the new sub-ticket instead of parking on the old one | NEW | `park T-0001: sub-ticket closed by a human: T-0001.2` | `park T-0001.4: EMPTY-OUTPUT from implementer` |
| A sub-ticket of the current plan that a human closed still parks the parent | REGRESSION | (`park T-0001: sub-ticket closed by a human: T-0001.2`) | `park T-0001: sub-ticket closed by a human: T-0001.2` |
| With the new plan merged, the re-planned parent reaches its final check and closes | NEW | `check: "state": "planned"` / `close=2 planned` | `check: "state": "ready-for-parent-verify"` / `close=0 closed` |
| A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list | REGRESSION | (`exit=0 ready-for-planner` / `in_input=1 listed=2`) | `exit=0 ready-for-planner` / `in_input=1 listed=2` |
| A re-plan is refused while a sub-ticket is not merged | REGRESSION | (`names=1` / `parked spec-v1.yaml `) | `names=1` / `parked spec-v1.yaml ` |
| A re-planned parent whose final check failed can be re-planned again past its superseded sub-tickets | NEW | `exit=2 parked` | `exit=0 ready-for-planner` |
| The design doc, build spec, README and changelog record superseded plans | NEW | `design=0 build-spec=0 readme=0 changelog=0 CONTIGUOUS` | `design=1 build-spec=1 readme=1 changelog=3 CONTIGUOUS` |
| The superseded-plan change leaves prompts, workflows and agents alone and adds no whitespace errors | REGRESSION | (`whitespace=ok untouched=0`) | `whitespace=ok untouched=0` |

Every "Before" output matches the "today" output in the spec's verification.md, so the spec matched this checkout. Every "After" output is exactly the scenario's THEN. The REGRESSION rows were also run on the base, as part of the same before pass, and printed their THENs there too.

What the key NEW outputs mean:
- In the first scenario, `closed: []` together with `superseded: [T-0001.2, T-0001.3]` means the closed old sub-ticket no longer parks the parent. `kept=...` shows that no record was deleted.
- The build scenario's park line is on `T-0001.4`, not on the parent. The build dispatched the new plan's sub-ticket, and the stub agent's empty output stopped it there.
- `close=0 closed` means the VERIFIED final check closed the parent, although T-0001.2 is closed and T-0001.3 never started.

Gate commands, run from the worktree on `9aa97bf`, each exactly as written:
- `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`: no output, exit 0. The change adds no whitespace errors.
- `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`: `391 passed in 318.04s (0:05:18)`. That is the whole suite with the 9 new tests and no failures.

## Tests added/changed

Added: `tests/factory/test_superseded_plan.py`, 9 tests. Like `test_replan.py`, they run black-box through `bin/factory` on throwaway stores. Before the code change, all 9 failed (`9 failed in 17.79s`). After it, all 9 pass. They cover:
- `planned_from` recorded at creation (v1, v1, v1, v2);
- a re-spec plus re-plan with one sub-ticket merged, one closed and one never started: `superseded` reported and logged once, `closed` empty, `ready`/`remaining` only the new sub-ticket, and old records kept with their states unchanged;
- parent-check counts only the current plan and reaches `ready-for-parent-verify`;
- `resolve --replan` is accepted past superseded sub-tickets;
- the `Depends on` refusal (exit 2, the exact message, no ticket written);
- the planner-input line, placed right after the list;
- a second plan at the same version supersedes nothing and logs nothing;
- a moved `spec` record does not change the split;
- the null-`planned_from` fallback.

Changed: none. The spec's "Tests to change" is none.

## Known gaps and uncertainties

- README status date: part G says to bump it. The header already reads `Current state as of 2026-10-09`, which is today's UTC date (`date -u` printed `Fri Oct  9 06:02:18 UTC 2026`), so it was left as is. Local time is still 2026-10-08 PDT. The changelog entry uses the spec's `2026-10-08`, the date of issue #77.
- The only scenario that covers `archive` passing over superseded sub-tickets is the close scenario, and it runs without a spec store. The fixture has no `factory init`, so `archive` itself is not exercised. `archive_cmd` reaches the change through `_parent_close_verified`, the same function the close path uses.
- `split_plan` ranks versions with `<` on whatever is stored. A hand-written non-integer `planned_from`, such as `ticket set planned_from=abc`, would raise a TypeError. No harness path writes one. I added no guard, because the spec does not ask for one.
- `factory:` markers added: none.

## Out-of-scope observations

- `resolve --replan`'s refusal still reads "--replan needs every sub-ticket merged". It now lists only current sub-tickets, so "every current sub-ticket" would be more exact. The spec does not change the message, and an existing test pins its prefix.
- The planner input's existing sentence "A `Depends on:` line may name any of these ids." stays byte-identical, as E requires. When a plan supersedes sub-tickets, the new line after it narrows that sentence.

## Responses to findings

None. This is round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance scenario printed its THEN verbatim after the change, every NEW scenario printed the spec's "today" output before it, and the full suite passed (391).
ESCALATIONS: none. The protected paths touched are `factory/cli.py`, `factory/subtickets.py` and `factory/compose.py`, all under harness `factory/**`, and the spec's Risk section declares all three.
