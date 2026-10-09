## Problem

When the operator, the person who runs the factory and approves its work, sends an already-planned ticket back for a new spec, the ticket's build stops for good on work left over from the old plan. The operator can get past it only by hand-editing the files where the factory keeps each ticket's state. It happened on 2026-10-08 to ticket T-0024 on Nanobot, one of the repositories the factory builds in, and that ticket now runs on a hand-made workaround.

Some terms first. The factory builds a ticket from a spec the operator approves at the spec gate, the one point where a human signs off a design before code is written. Each approval is numbered: approved spec v1, v2 and so on. The planner, an agent, splits the approved spec into sub-tickets. Each sub-ticket is one piece of the work, built on its own branch and merged on its own; together they make up the plan. The build loop dispatches each sub-ticket that is ready. When every sub-ticket has merged, one final check runs the whole spec against the merged result and then closes the parent ticket. To park a ticket is to stop it and hand it to the operator with a reason.

The design already provides for a change of plan (`docs/design.md:109`). The operator may send a planned ticket back, approve a new spec version and have the planner split it again. The new sub-tickets take the next free numbers under the same parent. But the old plan's sub-tickets stay attached, and the build still counts all of them:

- An old sub-ticket the operator closed parks the parent at once, with "sub-ticket closed by a human". No command resumes the build from that park. The re-plan command refuses too, because it needs every sub-ticket merged.
- An old sub-ticket that never started is still treated as current work. The build would dispatch it against the new spec, and the parent cannot close until it merges.
- The final check and the close refuse while any old sub-ticket is unmerged.

The people affected are the operator, who must hand-edit ticket state files to get past the park, and any ticket whose spec changes after planning. Ticket T-0027 (issue #44), approved but not yet built, adds a command that amends an approved spec after planning, which leads into the same situation.

The fix records on each sub-ticket the approved version it was planned from. When a newer plan exists, an old sub-ticket that never merged is superseded: it is kept with its id and record, but it no longer dispatches, parks the parent or holds back the close. Old sub-tickets that merged stay merged and count as done work. "Superseded" is used in the same sense as the check results a re-check already sets aside: an earlier record that is kept but no longer counted.

## Evidence

On Nanobot, read-only (`~/dev/nanobot-upstream/.factory/store/log/2026-10.jsonl`):
- Line 1392: T-0024.1 created from the plan of approved v2. Line 1396: closed by hand. Lines 1397-1398: the parent was parked and sent to the spec gate.
- Lines 1730-1732: the parent was approved at v4. Line 1751: the new planner run created T-0024.2.
- Line 1753: `"event": "ticket.parked", "ticket": "T-0024", "from": "planned", "reason": "sub-ticket closed by a human: T-0024.1"`.
- Lines 1780-1781: the hand-made workaround. The record `tickets/T-0024.1.yaml` was moved to `tickets/superseded/`, and the parent was set back to `planned`. It works only because the sub-ticket lookup does not read subdirectories.
- Every sub-ticket record on both stores carries `spec.approved_version`, the version it was created with. Within each parent all share one version, except Nanobot T-0024 (T-0024.1 at v2, T-0024.2 at v4).

Reproduced on this checkout (`main` at `51e2af7`). The fixture `t0038-respec.sh` (GIVEN block in the first scenario below) plans T-0001 at v1 as T-0001.1 (merged), T-0001.2 (closed by hand) and T-0001.3 (never started). It then sends the parent back and approves v2. A second plan adds T-0001.4, which depends on the merged T-0001.1:

| Command (after the re-plan) | Output today |
|---|---|
| `ticket ready-implementers T-0001` | `"ready": ["T-0001.4"]`, `"closed": ["T-0001.2"]`, no `superseded` list |
| `build.js` on T-0001, real store commands | `park T-0001: sub-ticket closed by a human: T-0001.2` |
| `ticket parent-check T-0001` with T-0001.4 merged | `"state": "planned"`, so the final check never starts |
| `ticket transition T-0001 --to closed` after a VERIFIED final check | exit 2, `T-0001 has sub-tickets: it closes after a VERIFIED parent-close run` |
| `resolve T-0001 --replan F` after a failed final check | exit 2, `--replan needs every sub-ticket merged: T-0001.2 is closed, T-0001.3 is waiting-dependencies` |
| `subticket add` of a plan whose `Depends on:` names T-0001.3 | exit 0: T-0001.4 is created waiting on a sub-ticket that should not be built |

A prototype of the change below, in a scratch clone, printed each NEW scenario's expected output. On that prototype the harness suite gave `384 passed in 198.34s`.

## Root cause

- `factory/store.py:228-235` `subtickets_of` globs `tickets/<parent>.*.yaml` and returns every match. No record says which plan a sub-ticket belongs to.
- `factory/cli.py:549-566` `ticket_ready_implementers` builds `ready`, `remaining` and `closed` from every sub-ticket. `factory/workflows/build.js:264` parks the parent whenever `closed` is non-empty.
- `factory/cli.py:738-751` `ticket_parent_check` needs every sub-ticket merged.
- `factory/cli.py:1335-1341` `_parent_close_verified` needs every sub-ticket merged. It guards `ticket transition --to closed` (`cli.py:161-167`) and `archive` (`cli.py:1365`). `_reused_subticket_run` (`cli.py:1302-1306`) counts every sub-ticket.
- `factory/cli.py:912-917`, `resolve --replan`, refuses unless every sub-ticket merged.
- `factory/cli.py:478`: a sub-ticket's `spec` record is the only trace of its plan. Approved T-0027 (its spec v2, Decisions line 66) moves that record forward on every unmerged, unclosed sub-ticket when a spec is amended. After T-0027 it no longer shows which plan a sub-ticket came from.

## Out of scope

- `factory/workflows/build.js` and every other workflow script: unchanged. They read the lists the store commands return.
- No new state or routing edge. In particular there is no `parked` → `planned` edge.
- A superseded sub-ticket's status, branch and record are never changed or moved by the harness.
- A run or merge a human starts by hand on a superseded sub-ticket is not refused.
- `merge`'s release of waiting siblings (`cli.py:680-688`) and its sibling-tests check (`cli.py:255`), which reads only merged sub-tickets: unchanged.
- The whole-spec step's planner decision (`_planner_needed`, `cli.py:492-495`) still counts every sub-ticket. A re-specced parent therefore always gets a planner run, and the one-sub-ticket path never recreates `<parent>.1`.
- The planner input's per-sub-ticket lines (`- <id> / <title>: <state>`): unchanged.
- T-0027's `spec amend` command.
- The Nanobot store, which holds the hand-made workaround (Operator steps).

## Open questions

none

## Decisions

- Each sub-ticket records `planned_from`, the parent's approved version when the sub-ticket was created. Nothing changes it afterwards. Rejected: reading `spec.approved_version`, which approved T-0027 moves forward on amendment.
- Superseded is computed whenever sub-tickets are read, not stored. A sub-ticket is superseded when it has not merged and its `planned_from` is lower than the highest `planned_from` among its parent's sub-tickets. Rejected: the request's mark written at re-plan time. That needs a write on every path that adds a plan and a migration for stores that already hold such sub-tickets, such as Nanobot T-0024. Also rejected: comparing with the parent's current approved version. That would supersede the live plan after a T-0027 amendment that keeps it.
- A record without `planned_from`, or with it null, falls back to its `spec.approved_version`. With neither, the sub-ticket counts as current.
- A plan made from the same approved version supersedes nothing. This covers `resolve --replan` after a failed final check, and a second plan added by hand. The design ties a new plan to an amended spec (`docs/design.md:109`). To replace a plan without changing intent, the operator approves with `approve-spec --edit`, which always makes a new version. This is a standing decision.
- Merged sub-tickets are never superseded. They count toward the close, the final check must contain their merges, and a new plan may depend on them.
- `subticket add` refuses, writing nothing, a plan whose `Depends on:` names a sub-ticket that the plan supersedes. Rejected: accepting it. The dependant would wait forever, because a superseded sub-ticket is never dispatched.
- `subticket add` reports the sub-ticket ids it newly supersedes under `superseded` and logs a `subtickets.superseded` event. Nothing is deleted, and every id stays taken.
- `ticket ready-implementers` keeps `subtickets` as every sub-ticket id. `build.js` reads an empty list as "planned with none", and `dev/build-harness.spec.md:286` documents it that way. Every other list there leaves superseded sub-tickets out, and the new `superseded` list names them.
- The planner is told which sub-tickets its plan will supersede, on one line after the existing list. With none, its input is byte-identical to today.
- The name is "superseded", as the request and triage use it, and in the same sense as `results/<head>/superseded-<n>/`: a record kept but no longer counted.

## Risk

Blast radius: every parent with sub-tickets, through `ready-implementers`, `parent-check`, the close and archive guards, `resolve --replan`, `subticket add` and the planner's input. On a parent whose sub-tickets were all planned from one approved version, the split marks nothing superseded and nothing changes. That is every parent on both stores today, counting Nanobot T-0024 as it stands after the hand-made workaround. On a parent re-planned from a newer version, its unmerged older sub-tickets stop counting. That is the intended change.

Protected paths touched: harness, `factory/**`: `factory/cli.py`, `factory/subtickets.py`, `factory/compose.py`. No file under `factory/workflows/`, `factory/prompts/`, `docs/prompts/`, `agents/`, `bin/factory`, `pyproject.toml`, `uv.lock` or `.factory/` changes.

The change reaches a target only after the runtime is moved to a revision that contains it and the instance accepts that harness.

Sequencing with T-0027 (#44): build this first, as the request asks. If T-0027 merges first, it moves the `spec` record on any sub-ticket created before this change, still unmerged and still open. The fallback above would then read that moved version for those records.

## Operator steps

Optional. Once Nanobot runs a harness revision that contains this change (the operator moves it there with `--accept-harness`), the hand-made workaround can be undone. On `factory-store`, the branch that holds Nanobot's ticket state, run `git mv tickets/superseded/T-0024.1.yaml tickets/` and commit. Then `factory ticket ready-implementers T-0024` should list `T-0024.1` under `superseded` and not under `closed`: the old sub-ticket is kept but no longer counted. Leaving the workaround in place also works, because the sub-ticket lookup never reads that subdirectory.

