## Proposed change

A. Record the plan (`factory/cli.py` `_create_subtickets`, lines 471-484). Beside `st["spec"]`, set `st["planned_from"] = parent["spec"]["approved_version"]`. Both `subticket add` and `plan whole-spec` create sub-tickets here. Nothing else writes the field.

B. One rule, in `factory/subtickets.py` (pure functions, next to `ready_implementers`):
- `planned_from(sub)` returns the record's `planned_from` when present and not null. Otherwise it returns `spec.approved_version`, and otherwise None.
- `split_plan(subs) -> (current, superseded)` keeps the input order. A sub-ticket is superseded when its status is not `merged`, its `planned_from` is not None, and that value is lower than the highest non-None `planned_from` in `subs`. All others are current.

C. Count only the current plan (`factory/cli.py`):
- `ticket_ready_implementers` (549-566) computes `ready`, the waiting-sibling release, `remaining`, `in_flight`, `parked`, `resumable` and `closed` from the current sub-tickets only. It keeps `subtickets` as every id and adds `"superseded": [ids]`.
- `ticket_parent_check` (738-751) keeps refusing a parent with no sub-tickets at all. It applies the all-merged test and builds its `subtickets` map from the current sub-tickets, and it adds `"superseded": [ids]`.
- `_reused_subticket_run` (1302-1306) and `_parent_close_verified` (1335-1341) use the current sub-tickets. This covers `ticket transition --to closed`, `archive` and parent-check's `reuse`. The guards' "has any sub-tickets" tests (161, 1365) stay on every sub-ticket.
- `resolve --replan` (912-917) applies its "every sub-ticket merged" test to the current sub-tickets.

D. Re-planning (`subticket_add`, 438-468). Before writing anything:
- Compute `after`, the ids `split_plan` would mark superseded once sub-tickets planned from the parent's current `approved_version` are added. Compute `before`, the ids it marks superseded now.
- A `Depends on:` that names an id in `after` is refused with exit 2 and nothing written. The error is `<id> (<label>) depends on <dep>, which this plan supersedes`.

After creating, when `after - before` is non-empty, log `subtickets.superseded` with `ticket=<parent>`, `subtickets=[ids in id order]` and `approved_version=<n>`. The JSON output gains `"superseded": [those ids]`, which is `[]` when there are none.

E. Planner input (`factory/compose.py` 318-322). After the existing `## Sub-tickets already under <id>` list, when D's `after` set for the parent is non-empty, append the line `Not merged and planned from an earlier approved version, so a new plan supersedes them and may not depend on them: <ids joined by ", ">`, preceded by a blank line. With none, the section stays byte-identical. `tests/factory/test_replan.py:108` pins it.

F. Tests: a new file `tests/factory/test_superseded_plan.py`, black-box through `bin/factory` on throwaway stores. It covers re-spec after planning with one sub-ticket closed, one merged and one never started. In that case the new plan's sub-ticket is ready, `closed` is empty and parent-check reaches `ready-for-parent-verify`. It also covers the dependency refusal, a same-version second plan superseding nothing, the null-`planned_from` fallback, and a moved `spec` record not changing the split.

G. Documents:
- `docs/design.md:109`: append to the bullet that a new plan made from a later approved version supersedes the earlier plan's sub-tickets that have not merged. They keep their records and ids, are no longer dispatched, and neither park the parent nor hold back its close. Merged ones stay merged and count toward the close.
- `dev/build-harness.spec.md:286`: in the `ready-implementers` JSON description, add that sub-tickets a later plan superseded are listed under `superseded` and left out of every other list except `subtickets`.
- `README.md`: add a bullet `- **Re-plan after a re-spec.**` to the list of what runs, after "Sibling tests check". It should say what superseded means and that merged work stays. Like its neighbours, it should end by saying it is tested and has not yet fired on a real ticket. Bump the status date.
- `docs/changelog.md`: one entry, `<n>. After issue #77 (2026-10-08), ...`, numbered after the last. It names `planned_from`, superseded sub-tickets, and the `Depends on` refusal.

Size: about 60 changed lines of harness code, a test file of about 150 lines and about 15 lines of documents.

## Tests to change

none. No decision overturns behaviour an existing test pins. The prototype of A-E passed the whole suite unchanged: `384 passed`.

