## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`, the working documents for building the factory itself: `dev/build-harness.spec.md` (the
  spec for building the harness), `dev/build-harness.plan.md` (the Planner's decomposition of it),
  `dev/P0-intake-skeleton.md` (the walking skeleton) and `dev/issues.md` (this repo's issue index);
- the harness, as code in this repo: `factory/` (the package, its role prompts and its workflow
  scripts), `bin/factory` (the entry point), `agents/` (the agent definition templates) and
  `tests/factory/` (its suite). Install with `uv sync --frozen`; test with
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`;
- `.factory/`, this repo's own instance of the factory: `instance.yaml`, this briefing,
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `store/`.
  The store is a checkout of its own branch, `factory-store`; the operator commits it there, so a
  store commit never moves `main`.

Two checkouts. Tickets are built and merged in the dev checkout, `~/dev/spec-factory` on `main`.
The factory runs from the runtime checkout, `~/dev/spec-factory-harness`, a detached worktree of
this repo at the harness revision `.factory/harness.lock` has accepted. A merge into `main` never
changes the running code; only the upgrade step moves the runtime, after which the instance
refuses its store until `--accept-harness`. Your shell may start in another directory: use
absolute paths, or `cd ~/dev/spec-factory && <cmd>`.

The Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3.5`) is instance A: a target
with only `.factory/`, run from the same runtime by its own Driver session. This repo's harness was
imported from its retired `feat/lionbot-v3` branch. Read it only to observe what a fix does there; never write there, and never copy its test names,
line numbers or commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents, the harness suite). A change to the design doc keeps its
own conventions: its changelog entry in `docs/changelog.md`, `dev/build-harness.spec.md`
consistent with the new text, and any `docs/prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. For
every role but the implementer that is the only file you may create or modify. The implementer
also changes files in its own worktree and commits there, and nowhere else. Then return the same
text as your final message.

This repo's current-state page is the top-level `README.md`. A change to a command, state, stop or
path updates it in the same ticket; read its "Maintaining this page" section before editing it.

Who reads what the roles write here: the operator at the spec gate, and a technical reader new to this project reading the README or a PR description. Gloss every term specific to the factory at first use (docs/writing.md).
## Output file
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0358-implementer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0358-implementer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0038.1` (branch `factory/T-0038.1`, base `f4ea04193e829219b592f44c3fc55d9e42e768d9`, head `f4ea04193e829219b592f44c3fc55d9e42e768d9`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0038.1

T-0038.1 / After a re-spec and re-plan, a sub-ticket from the old plan keeps parking the parent: sub-tickets should record which plan they belong to, and only the current plan's sub-tickets should count
Depends on: none
Parallel-safe: yes

Parent: T-0038, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept
- The plan a sub-ticket belongs to does not move with its spec record, and a record without it falls back to its creation version
- A second plan at the same approved version supersedes nothing
- A plan that depends on an old unmerged sub-ticket is refused and writes nothing
- A re-specced parent's planner input names the sub-tickets its plan supersedes
- The build of a re-planned parent dispatches the new sub-ticket instead of parking on the old one
- A sub-ticket of the current plan that a human closed still parks the parent
- With the new plan merged, the re-planned parent reaches its final check and closes
- A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list
- A re-plan is refused while a sub-ticket is not merged
- A re-planned parent whose final check failed can be re-planned again past its superseded sub-tickets
- The design doc, build spec, README and changelog record superseded plans
- The superseded-plan change leaves prompts, workflows and agents alone and adds no whitespace errors
Tests to change: the parent's list.
Protected paths: the parent's Risk list.

## Parent spec (v2, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0038/v2.md`

=== proposal.md
## Problem

When the operator, the person who runs the factory and approves its work, sends an already-planned ticket back for a new spec, the ticket's build stops for good on work left over from the old plan. The operator can get past it only by hand-editing the files where the factory keeps each ticket's state. It happened on 2026-10-08 to ticket T-0024 on Nanobot, one of the repositories the factory builds in, and that ticket now runs on a hand-made workaround.

Some terms first. The factory builds a ticket from a spec the operator approves at the spec gate, the one point where a human signs off a design before code is written. Each approval is numbered: approved spec v1, v2 and so on. The planner, an agent, splits the approved spec into sub-tickets. Each sub-ticket is one piece of the work, built on its own branch and merged on its own; together they make up the plan. The build loop dispatches each sub-ticket that is ready. When every sub-ticket has merged, one final check runs the whole spec against the merged result and then closes the parent ticket. To park a ticket is to stop it and hand it to the operator with a reason.

The design already provides for a change of plan (`docs/design.md:109`). The operator may send a planned ticket back, approve a new spec version and have the planner split it again. The new sub-tickets take the next free numbers under the same parent. But the old plan's sub-tickets stay attached, and the build still counts all of them:

- An old sub-ticket the operator closed parks the parent at once, with "sub-ticket closed by a human". No command resumes the build from that park. The re-plan command refuses too, because it needs every sub-ticket merged.
- An old sub-ticket that never started is still treated as current work. The build would dispatch it against the new spec, and the parent cannot close until it merges.
- The final check and the close refuse while any old sub-ticket is unmerged.

The people affected are the operator, who must hand-edit ticket state files to get past the park, and any ticket whose spec changes after planning. Ticket T-0027 (issue #44), approved but not yet built, adds a command that amends an approved spec after planning, which leads into the same situation.

The fix records on each sub-ticket the approved version it was planned from. When a newer plan exists, an old sub-ticket that never merged is superseded: it is kept with its id and record, but it no longer dispatches, parks the parent or holds back the close. Old sub-tickets that merged stay merged and count as done work. "Superseded" is used in the same sense as the check results a re-check already sets aside: an earlier record that is kept but no longer counted.

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

=== design.md
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

=== specs/sub-ticket-planning/spec.md
## ADDED Requirements

### Requirement: A plan made from a later approved version supersedes the earlier plan's unmerged sub-tickets
A sub-ticket SHALL record the parent's approved version it was planned from, and that record MUST NOT follow later changes to its `spec` record. Once a parent has a sub-ticket planned from a later version, each of its sub-tickets that is not merged and was planned from an earlier version MUST be listed as superseded and left out of every other list `ticket ready-implementers` returns except `subtickets`. Its record SHALL be kept. `subticket add` SHALL report and log the sub-tickets it supersedes. A record with no plan version SHALL fall back to its `spec.approved_version`.

#### Scenario: After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell. This scenario needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0038-respec.sh <<'EOF'
# Sourced from the repo root after t0023-parent.sh. T-0001 was planned at approved spec v1 as
# T-0001.1 (merged), T-0001.2 (closed by a human with no commits) and T-0001.3 (waiting on
# T-0001.2, never started). The human parked the parent, sent it back to the spec gate and approved
# an edited spec, v2, so T-0001 is ready for its planner again, as Nanobot T-0024 was.
printf 'ST-1 / Base\nDepends on: none\nParallel-safe: yes\n\nST-2 / Dropped\nDepends on: none\nParallel-safe: yes\n\nST-3 / Unstarted\nDepends on: ST-2\nParallel-safe: yes\n' > $T23/plan1.md
bin/factory subticket add T-0001 --file $T23/plan1.md >/dev/null
bin/factory ticket transition T-0001 --to planned --by t >/dev/null
bin/factory ticket set T-0001.1 status=merged >/dev/null
bin/factory ticket transition T-0001.2 --to closed --by t >/dev/null
bin/factory ticket park T-0001 --reason "sub-ticket closed by a human: T-0001.2" >/dev/null
bin/factory resolve T-0001 --to spec-gate >/dev/null
printf '## Problem\nx, amended\n' > $T23/spec2.md
bin/factory approve-spec T-0001 --edit $T23/spec2.md >/dev/null
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && printf 'ST-1 / Redo\nDepends on: T-0001.1\nParallel-safe: yes\n' > $T23/plan2.md && A=$(bin/factory subticket add T-0001 --file $T23/plan2.md 2>/dev/null | tail -1) && bin/factory ticket transition T-0001 --to planned --by t >/dev/null; R=$(bin/factory ticket ready-implementers T-0001 | tail -1); echo "add: $(echo "$A" | grep -o '"superseded": \[[^]]*\]')"; for k in ready closed superseded; do echo "$k: $(echo "$R" | grep -o "\"$k\": \[[^]]*\]")"; done; echo "kept=$(ls $FACTORY_STATE/tickets | tr '\n' ' ')logged=$(cat $FACTORY_STATE/log/*.jsonl | grep '"event": "subtickets.superseded"' | grep -c '"T-0001.2", "T-0001.3"')")`
- THEN it prints exactly `add: "superseded": ["T-0001.2", "T-0001.3"]`, `ready: "ready": ["T-0001.4"]`, `closed: "closed": []`, `superseded: "superseded": ["T-0001.2", "T-0001.3"]`, `kept=T-0001.1.yaml T-0001.2.yaml T-0001.3.yaml T-0001.4.yaml T-0001.yaml logged=1`, one per line

#### Scenario: The plan a sub-ticket belongs to does not move with its spec record, and a record without it falls back to its creation version
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept" run once. The first part moves T-0001.3's `spec` record to v2, as an amendment under approved T-0027 would. The second part clears `planned_from` on every record, as on a record made before this change.
- WHEN `( (. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && bin/factory ticket set T-0001.3 spec.version=2 spec.approved_version=2 >/dev/null && printf 'ST-1 / Redo\nDepends on: T-0001.1\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md >/dev/null 2>&1; echo "moved: $(bin/factory ticket ready-implementers T-0001 | tail -1 | grep -o '"superseded": \[[^]]*\]')"); (. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && printf 'ST-1 / Redo\nDepends on: T-0001.1\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md >/dev/null 2>&1; for i in 1 2 3 4; do bin/factory ticket set T-0001.$i planned_from= >/dev/null 2>&1; done; echo "unrecorded: $(bin/factory ticket ready-implementers T-0001 | tail -1 | grep -o '"superseded": \[[^]]*\]')"))`
- THEN it prints exactly `moved: "superseded": ["T-0001.2", "T-0001.3"]`, then `unrecorded: "superseded": ["T-0001.2", "T-0001.3"]`

#### Scenario: A second plan at the same approved version supersedes nothing
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: none\nParallel-safe: yes\n' > $T23/plan1.md && bin/factory subticket add T-0001 --file $T23/plan1.md >/dev/null && bin/factory ticket set T-0001.1 status=merged >/dev/null && printf 'ST-1 / Extra\nDepends on: T-0001.2\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md >/dev/null 2>&1; echo "exit=$?"; bin/factory ticket ready-implementers T-0001 | tail -1 | grep -o '"ready": \[[^]]*\]\|"remaining": \[[^]]*\]')`
- THEN it prints exactly `exit=0`, then `"ready": ["T-0001.2"]`, then `"remaining": ["T-0001.2", "T-0001.3"]`

### Requirement: A new plan may not depend on a sub-ticket it supersedes
`factory subticket add` MUST refuse with exit 2, writing no sub-ticket, a plan whose `Depends on:` line names a sub-ticket that the plan supersedes, and the refusal SHALL name that sub-ticket.

#### Scenario: A plan that depends on an old unmerged sub-ticket is refused and writes nothing
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && printf 'ST-1 / Redo\nDepends on: T-0001.3\nParallel-safe: yes\n' > $T23/plan3.md; bin/factory subticket add T-0001 --file $T23/plan3.md >/dev/null 2>$T23/err; echo "exit=$? names=$(grep -c 'T-0001.3' $T23/err) $(ls $FACTORY_STATE/tickets | tr '\n' ' ')")`
- THEN it prints exactly `exit=2 names=1 T-0001.1.yaml T-0001.2.yaml T-0001.3.yaml T-0001.yaml `

### Requirement: The planner is told which sub-tickets its plan will supersede
When a plan made at the parent's approved version would supersede existing sub-tickets, the planner's input SHALL name them on one line after the existing sub-ticket list, and that list SHALL be unchanged.

#### Scenario: A re-specced parent's planner input names the sub-tickets its plan supersedes
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && R=$(bin/factory run start --role planner --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; I=$FACTORY_STATE/runs/${R:-none}/input.md; echo "said=$(cat $I 2>/dev/null | grep -cxF 'Not merged and planned from an earlier approved version, so a new plan supersedes them and may not depend on them: T-0001.2, T-0001.3') listed=$(cat $I 2>/dev/null | grep -cxF -e '- T-0001.1 / Base: merged' -e '- T-0001.2 / Dropped: closed' -e '- T-0001.3 / Unstarted: waiting-dependencies')")`
- THEN it prints exactly `said=1 listed=3`

=== specs/build-dispatch/spec.md
## ADDED Requirements

### Requirement: The build counts only the current plan's sub-tickets
The build MUST NOT park a parent for a superseded sub-ticket the human closed, and SHALL dispatch the current plan's ready sub-tickets. A closed sub-ticket of the current plan MUST still park the parent with `sub-ticket closed by a human: <id>`.

#### Scenario: The build of a re-planned parent dispatches the new sub-ticket instead of parking on the old one
Needs the GIVEN blocks of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored", "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept" run once. In `t0022-build.mjs` every role run returns an empty string, so the implementer of the dispatched sub-ticket ends EMPTY-OUTPUT twice.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && printf 'ST-1 / Redo\nDepends on: T-0001.1\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null; node ${TMPDIR:-/tmp}/t0022-build.mjs)`
- THEN it prints exactly `park T-0001.4: EMPTY-OUTPUT from implementer`

#### Scenario: A sub-ticket of the current plan that a human closed still parks the parent
Needs the GIVEN blocks of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" and "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: none\nParallel-safe: yes\n' > $T23/plan1.md && bin/factory subticket add T-0001 --file $T23/plan1.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null && bin/factory ticket transition T-0001.2 --to closed --by t >/dev/null; node ${TMPDIR:-/tmp}/t0022-build.mjs)`
- THEN it prints exactly `park T-0001: sub-ticket closed by a human: T-0001.2`

### Requirement: A parent's final check and close count only the current plan's sub-tickets
`factory ticket parent-check` SHALL move a planned parent to `ready-for-parent-verify` when every current sub-ticket has merged, and `ticket transition <parent> --to closed` MUST accept a VERIFIED final check whatever its superseded sub-tickets' states.

#### Scenario: With the new plan merged, the re-planned parent reaches its final check and closes
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && printf 'ST-1 / Redo\nDepends on: T-0001.1\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null && bin/factory ticket set T-0001.4 status=merged >/dev/null; echo "check: $(bin/factory ticket parent-check T-0001 | tail -1 | grep -o '"state": "[^"]*"')"; R=$(bin/factory run start --role verifier --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); if [ -n "$R" ]; then H=$(sed -n "s/^head: '*\([0-9a-f]*\).*/\1/p" $FACTORY_STATE/runs/$R/meta.yaml); printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $FACTORY_STATE/runs/$R/output.md; bin/factory run finish $R >/dev/null 2>&1; fi; bin/factory ticket transition T-0001 --to closed --by t >/dev/null 2>&1; echo "close=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints exactly `check: "state": "ready-for-parent-verify"`, then `close=0 closed`

=== specs/human-resolution/spec.md
## MODIFIED Requirements

### Requirement: A re-plan returns a fully merged parent to its planner
`factory resolve <parent> --replan F` on a parked parent whose current sub-tickets have all merged MUST move it to `ready-for-planner` with F as its next ruling, and the next planner input SHALL contain F and list each existing sub-ticket with its title and state; a sub-ticket that a later plan superseded SHALL NOT count, and with any current sub-ticket not merged it MUST refuse, naming that sub-ticket, and write nothing.

#### Scenario: A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'Re-plan: add one fix for the case-insensitive path.\n' > $T23/note.md; bin/factory resolve T-0001 --replan $T23/note.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')"; R=$(bin/factory run start --role planner --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; I=$FACTORY_STATE/runs/${R:-none}/input.md; echo "in_input=$(cat $I 2>/dev/null | grep -c 'Re-plan: add one fix') listed=$(cat $I 2>/dev/null | grep -cxF -e '- T-0001.1 / First: merged' -e '- T-0001.2 / Second: merged')")`
- THEN it prints `exit=0 ready-for-planner`, then `in_input=1 listed=2`

#### Scenario: A re-plan is refused while a sub-ticket is not merged
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && bin/factory ticket set T-0001.2 status=closed >/dev/null && echo n > $T23/note.md; echo "names=$(bin/factory resolve T-0001 --replan $T23/note.md 2>&1 >/dev/null | grep -c 'T-0001.2')"; echo "$(bin/factory ticket show T-0001 | sed -n 's/^status: //p') $(ls $FACTORY_STATE/approvals/T-0001 | tr '\n' ' ')")`
- THEN it prints `names=1`, then `parked spec-v1.yaml ` (still parked, and no ruling file written)

#### Scenario: A re-planned parent whose final check failed can be re-planned again past its superseded sub-tickets
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && printf 'ST-1 / Redo\nDepends on: T-0001.1\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null && bin/factory ticket set T-0001.4 status=merged >/dev/null && bin/factory ticket set T-0001 status=ready-for-parent-verify >/dev/null && bin/factory ticket park T-0001 --reason "FAILED from parent-close verifier" >/dev/null && echo 'Re-plan: one more fix.' > $T23/note.md; bin/factory resolve T-0001 --replan $T23/note.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints exactly `exit=0 ready-for-planner`

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The documents record superseded plans
`docs/design.md` SHALL say, in its rule for a sub-ticket closed by the human, that a new plan from a later approved version supersedes the earlier plan's unmerged sub-tickets. `dev/build-harness.spec.md` SHALL describe the `superseded` list of `ready-implementers`. `README.md` SHALL carry a "Re-plan after a re-spec" bullet. `docs/changelog.md` SHALL hold one entry for issue #77, numbered without a gap. The change MUST NOT touch any prompt copy, workflow script or agent template, and MUST add no whitespace errors.

#### Scenario: The design doc, build spec, README and changelog record superseded plans
- WHEN `(echo "design=$(grep 'sub-ticket closed by the human' docs/design.md | grep -c supersede) build-spec=$(grep 'ready-implementers PARENT' dev/build-harness.spec.md | grep -c superseded) readme=$(grep -c '^- \*\*Re-plan after a re-spec\.\*\*' README.md) changelog=$(grep '^[0-9]*\. After issue #77 ' docs/changelog.md | grep -oF -e superseded -e planned_from -e 'Depends on' | sort -u | grep -c .) $(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md)")`
- THEN it prints exactly `design=1 build-spec=1 readme=1 changelog=3 CONTIGUOUS`

#### Scenario: The superseded-plan change leaves prompts, workflows and agents alone and adds no whitespace errors
- WHEN `(echo "whitespace=$(git diff --check main...HEAD >/dev/null && echo ok || echo bad) untouched=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts factory/workflows agents | grep -c .)")`
- THEN it prints exactly `whitespace=ok untouched=0`

=== verification.md
## Acceptance

Each NEW item below was run on this checkout (`main` at `51e2af7`) and printed the "today" output shown. Each item except the documents scenario was also run, verbatim under bash, on a scratch prototype of design.md A-E and printed its THEN. The prototype changed no documents, so the documents scenario printed its "today" line there too. Those runs are from round 1 (run-0346). In round 2, `main` is still at `51e2af7`, and three NEW items were run again verbatim under the HOME wrapper, with the fixtures written to this run's scratch directory. "After a re-spec and a re-plan...", "The build of a re-planned parent..." and "A plan that depends on an old unmerged sub-ticket..." printed exactly the "today" output below. The prototype was not rebuilt in round 2, because this round changes only the wording of proposal.md.

- After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept → NEW. Today it prints `add: ` (no `superseded` in the output), `ready: "ready": ["T-0001.4"]`, `closed: "closed": ["T-0001.2"]`, `superseded: ` (no such list), `kept=T-0001.1.yaml T-0001.2.yaml T-0001.3.yaml T-0001.4.yaml T-0001.yaml logged=0`.
- The plan a sub-ticket belongs to does not move with its spec record, and a record without it falls back to its creation version → NEW. Today it prints `moved: `, then `unrecorded: `: there is no `superseded` list, and `ticket set ... planned_from=` is refused as an unknown key. An implementation that read `spec.approved_version` instead would leave `T-0001.3` out of the `moved` list (worked from the rule in design.md B; not run).
- A second plan at the same approved version supersedes nothing → REGRESSION (prints its THEN today).
- A plan that depends on an old unmerged sub-ticket is refused and writes nothing → NEW. Today it prints `exit=0 names=0 T-0001.1.yaml T-0001.2.yaml T-0001.3.yaml T-0001.4.yaml T-0001.yaml `: the plan is accepted.
- A re-specced parent's planner input names the sub-tickets its plan supersedes → NEW. Today it prints `said=0 listed=3`.
- The build of a re-planned parent dispatches the new sub-ticket instead of parking on the old one → NEW. Today it prints `park T-0001: sub-ticket closed by a human: T-0001.2`, the Nanobot T-0024 park.
- A sub-ticket of the current plan that a human closed still parks the parent → REGRESSION (prints its THEN today).
- With the new plan merged, the re-planned parent reaches its final check and closes → NEW. Today it prints `check: "state": "planned"`, then `close=2 planned`.
- A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list → REGRESSION (current truth, unchanged).
- A re-plan is refused while a sub-ticket is not merged → REGRESSION (current truth, unchanged).
- A re-planned parent whose final check failed can be re-planned again past its superseded sub-tickets → NEW. Today it prints `exit=2 parked`. The refusal is `--replan needs every sub-ticket merged: T-0001.2 is closed, T-0001.3 is waiting-dependencies`.
- The design doc, build spec, README and changelog record superseded plans → NEW. Today it prints `design=0 build-spec=0 readme=0 changelog=0 CONTIGUOUS`.
- The superseded-plan change leaves prompts, workflows and agents alone and adds no whitespace errors → REGRESSION (prints `whitespace=ok untouched=0` on `main`).
