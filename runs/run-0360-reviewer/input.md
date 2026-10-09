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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0360-reviewer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0360-reviewer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0360-reviewer/wt` (branch `factory/T-0038.1`, base `f4ea04193e829219b592f44c3fc55d9e42e768d9`, head `9aa97bf43d815b288ca4dd1cf89cbde4dac55103`). There is no remote: commit on the branch; the PR is the branch plus the description you return. The verifier runs the gate commands on this head; you do not run them.

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

## PR description (the implementer's output)

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

## Diff `f4ea04193e829219b592f44c3fc55d9e42e768d9...9aa97bf43d815b288ca4dd1cf89cbde4dac55103`

diff --git a/README.md b/README.md
index 322d463..f6eddcc 100644
--- a/README.md
+++ b/README.md
@@ -857,6 +857,13 @@ path above is relative to the store.
   sub-ticket added the file. If none did, the sub-ticket parks as blocked, and the human rules on it
   as on any blocked build ("Where a human decides"). Any other existing test still changes only if
   the approved spec lists it. It is tested, and has not yet fired on a real ticket.
+- **Re-plan after a re-spec.** When the human sends a planned parent back to the spec gate and
+  approves a new spec version, the planner splits it again under the same parent. Each sub-ticket
+  records the approved version it was planned from. The new plan supersedes the old plan's
+  sub-tickets that have not merged: they keep their records and ids, but are no longer dispatched,
+  no longer park the parent, and no longer hold back its final check or close. Old sub-tickets that
+  merged stay merged and count as done work. A new plan may not depend on a sub-ticket it
+  supersedes. It is tested, and has not yet fired on a real ticket.
 - **Empty output.** A role run that ends without writing its output file is run once more on the
   same inputs, and the harness keeps the agent's last message with the run. A second run in a row
   that ends the same way parks the ticket. The harness enforces no time or token budget and cannot
diff --git a/dev/build-harness.spec.md b/dev/build-harness.spec.md
index 000f7de..1fd6fa9 100644
--- a/dev/build-harness.spec.md
+++ b/dev/build-harness.spec.md
@@ -283,7 +283,7 @@ Common step `runRole(role, ticket, head)` in both scripts: clerk `factory run st
 
 `build.js` (`args: {ticket}`), run after `factory approve-spec`:
 1. `phase('Plan')` (only when the parent is `ready-for-planner`; a re-run starts from the stored state, so a `--ruling` on a planner ESCALATE re-runs the planner with the ruling in its input): first clerk `factory plan whole-spec PARENT` (B), with three outcomes: a refusal → park the parent `harness-bug: plan whole-spec: <stderr>`, return; `"planner": "skipped"` → no planner run, `transition --to planned`; any other success → the planner as follows. `runRole('planner')` with the pinned spec; `PLANNED` → clerk `factory spec tasks PARENT --run RUN` (B), then `subticket add` per sub-ticket (`depends_on`, `parallel_safe`); `ESCALATE` → park, return.
-2. `phase('Build')`: `while` any sub-ticket is not `merged|parked|closed`: `ready = ` clerk `factory ticket ready-implementers PARENT` (JSON: sub-tickets in `ready-for-implementer` whose deps are merged, minus any with a run in flight on its branch; a `parallel_safe: false` sub-ticket runs alone: it is listed only when no sibling of the same parent is in flight — any role: `in_flight` non-empty or `checks-in-flight` — and nothing else is listed with it, and while it is in flight no sibling is listed; doc §Routing table, Planner row; item 79; its `subtickets` lists every sub-ticket id of the parent in id order); when the first `ready` of a build run has an empty `subtickets` (a parent planned with none), clerk `factory subticket add PARENT` with no `--run`, once per build run: it takes the planner run named by the parent's latest `plan.added` event; on its refusal park the parent `no sub-tickets, and none could be created from the recorded plan: <stderr>` and return, on success continue the loop; `await parallel(ready.map(st => () => buildOne(st)))`; if `ready` is empty and nothing is in flight, return (the rest is parked or waiting on a human). When nothing is left to build, clerk `factory ticket parent-check PARENT`; a refusal parks the parent `parent-check refused: <stderr>` and returns. When the parent reaches `ready-for-parent-verify` (G), or a re-run finds it there: clerk `factory ticket parent-check PARENT` first. Its `reuse` field names a run when the parent has exactly one sub-ticket and it is merged, `main` is still at that sub-ticket's merge commit, the results row for the merged head is VERIFIED from a run whose base is the parent's `parent_base`, and the sub-ticket's text names every scenario of the pinned spec; that run stands for the parent-close run: no verifier run starts, the build goes to `factory archive PARENT` with that run id as the park outputs, and the close records it as `verified_by` (`null` → as follows). Otherwise `runRole('verifier', PARENT, <main SHA>)` — the parent-close run, whose inputs doc §Routing table (merge-gate row) declares: the pinned parent spec (every delta scenario with its `## Acceptance` label), head = current `main`, base = the parent's `parent_base`, `{gate commands}`; `run compose` supplies exactly these four (no sub-ticket text), the clerk makes the checkout of that head, and the verifier definition (rendered verbatim from the doc) checks out the head it was given and runs the base it was given; `VERIFIED` → clerk `factory archive PARENT` (K), then `closed`, or on its exit 2 `park --reason 'archive: <stderr>'`; `FAILED`/`SPEC-DEFECT` → `park --reason 'parent verify: <STATUS>'` with the output (human queue); then return.
+2. `phase('Build')`: `while` any sub-ticket is not `merged|parked|closed`: `ready = ` clerk `factory ticket ready-implementers PARENT` (JSON: sub-tickets in `ready-for-implementer` whose deps are merged, minus any with a run in flight on its branch; a `parallel_safe: false` sub-ticket runs alone: it is listed only when no sibling of the same parent is in flight — any role: `in_flight` non-empty or `checks-in-flight` — and nothing else is listed with it, and while it is in flight no sibling is listed; doc §Routing table, Planner row; item 79; its `subtickets` lists every sub-ticket id of the parent in id order; sub-tickets a later plan superseded, those not merged and planned from an earlier approved version, are listed under `superseded` and left out of every other list except `subtickets`); when the first `ready` of a build run has an empty `subtickets` (a parent planned with none), clerk `factory subticket add PARENT` with no `--run`, once per build run: it takes the planner run named by the parent's latest `plan.added` event; on its refusal park the parent `no sub-tickets, and none could be created from the recorded plan: <stderr>` and return, on success continue the loop; `await parallel(ready.map(st => () => buildOne(st)))`; if `ready` is empty and nothing is in flight, return (the rest is parked or waiting on a human). When nothing is left to build, clerk `factory ticket parent-check PARENT`; a refusal parks the parent `parent-check refused: <stderr>` and returns. When the parent reaches `ready-for-parent-verify` (G), or a re-run finds it there: clerk `factory ticket parent-check PARENT` first. Its `reuse` field names a run when the parent has exactly one sub-ticket and it is merged, `main` is still at that sub-ticket's merge commit, the results row for the merged head is VERIFIED from a run whose base is the parent's `parent_base`, and the sub-ticket's text names every scenario of the pinned spec; that run stands for the parent-close run: no verifier run starts, the build goes to `factory archive PARENT` with that run id as the park outputs, and the close records it as `verified_by` (`null` → as follows). Otherwise `runRole('verifier', PARENT, <main SHA>)` — the parent-close run, whose inputs doc §Routing table (merge-gate row) declares: the pinned parent spec (every delta scenario with its `## Acceptance` label), head = current `main`, base = the parent's `parent_base`, `{gate commands}`; `run compose` supplies exactly these four (no sub-ticket text), the clerk makes the checkout of that head, and the verifier definition (rendered verbatim from the doc) checks out the head it was given and runs the base it was given; `VERIFIED` → clerk `factory archive PARENT` (K), then `closed`, or on its exit 2 `park --reason 'archive: <stderr>'`; `FAILED`/`SPEC-DEFECT` → `park --reason 'parent verify: <STATUS>'` with the output (human queue); then return.
 3. `buildOne(st)`: loop:
    - `runRole('implementer', st, …, {isolation: 'worktree'})`; the implementer's worktree is created on current `main` at dispatch (doc §Routing table, Planner row), input = sub-ticket, pinned parent spec, AGENTS.md (+ round ≥ 2: both checker outputs, CI result, or the human ruling); `BLOCKED` → park, return; `READY-FOR-REVIEW` → clerk `factory ticket head ST` (from `git ls-remote`), `transition --to checks-in-flight --round pr:init`.
    - **Checkers in parallel, fresh contexts** (`parallel` is the join barrier, E7): `[rev, ver] = await parallel([() => runRole('reviewer', …), () => runRole('verifier', …)])` with input = `git diff main...head`, PR description, sub-ticket, parent spec (+ round ≥ 2: both prior outputs, the implementer's Responses); the clerk makes each a fresh checkout `~/factory/runs/<run_id>/wt` of the head; each result → clerk `results record` (stale rule applies; the `Commit:` line must equal the current head).
diff --git a/docs/changelog.md b/docs/changelog.md
index c0cf9e8..8507f64 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -63,5 +63,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 59. After issue #74 (2026-10-08), where the operator's replay of three past intakes (#49, #51, #57), with the same inputs and bases, found that #73's spec writer rules cut its tokens by about 37% at the same quality, but that its critic rules saved nothing (0.71M to 0.72M, 1.0M to 0.93M, 1.67M to 1.63M tokens) and made the critic check less: it missed the Nanobot `UV_PYTHON_INSTALL_DIR` risk on #51 and, on #57, the brace-list declaration bug that the earlier prompt had confirmed with a scratch git test. The critic's PROCESS drops the per-claim cap (at most two paths and one command for any one claim) and the no-build rule (no clone, worktree or prototype), and says the critic may run a small experiment in its scratch directory to confirm a finding. It keeps its minimum spot-check, the rule that it runs no test suite, the rule for picking an acceptance command, the rule that a claim needing a suite run or a build of the change is a finding or a question, and the three reading rules. `docs/principles.md` principle 2 keeps the critic's no-suite rule, and its Spiking section drops the two-path bound and says that vetting a whole approach is still the spec writer's or a spike's job. The spec writer prompt is unchanged from #73.
 60. After issue #75 (2026-10-08), where every spec writer and critic input carried all of current truth and the whole decision log, whatever its ticket touched: one spec writer input on this repo's store was 171.6 kB, of which 123.9 kB was current truth and 32.4 kB the log, and the Nanobot store adds about 480 kB to each writer input. Triage now receives the capability index, one line per current-truth capability with its size, spec path and requirement names, and names the capabilities a request touches on a new `Capabilities:` output line. The spec writer and critic receive those capabilities in full, plus each one their spec cites by path, and the capability index for the rest. They and the planner receive the decision-log lines of the ticket and of those capabilities, and a decision index for the rest: one line per other ticket, with a `grep` command that reads its lines. A ticket whose triage output has no `Capabilities:` line keeps the whole of both. The projection for the Nanobot store's last ten tickets is a mean writer input of 101 kB and a maximum of 167 kB, against 521 kB and 635 kB before; that still misses the request's 40 kB and 100 kB targets, because the rest of a writer input lies outside this change. Rejected: `factory spec show` and `factory decision show` commands, because a command run from inside a role must clear the live-store fence, the guard that refuses store commands while a role runs, and find the instance; a path needs neither.
 61. After issue #78 (2026-10-09), where #75's filter reduced every decision logged against another ticket to a line of the decision index, because no line in either store's decision log names a capability: in the operator's replay of a Nanobot ticket, the spec writer put new code in a module that another ticket's standing decision rules out, and the critic missed it. The spec writer, critic and planner receive the whole decision log again, whatever capabilities their ticket names. The decision index and its `grep` command are gone; the capability index stays. Measured on 2026-10-09, the decision part of each of their inputs grows from under 3 kB to about 36 kB on this repo's store, and from about 5 kB to about 80 kB on the Nanobot store. Rejected: the request's rule of sending in full the lines that name no capability and filtering the rest, because on today's logs it sends every line anyway, and it could still hide a cross-cutting decision that happens to name a capability.
+62. After issue #77 (2026-10-08), where Nanobot ticket T-0024 was sent back to the spec gate after planning and approved at a new version: its new plan's sub-ticket was created, but the old plan's sub-ticket that the operator had closed parked the parent at once, and only moving that sub-ticket's record out of the store's `tickets/` by hand let the build go on. Each sub-ticket now records `planned_from`, the parent's approved version when it was created, which nothing changes afterwards. Once a parent has a sub-ticket planned from a later version, its sub-tickets that have not merged and were planned from an earlier one are superseded: kept with their ids and records, but left out of `ready-implementers` (listed under `superseded`), the final check, the close, archive and `resolve --replan`. Merged ones stay merged and count. `subticket add` reports and logs the sub-tickets it supersedes, and refuses a plan whose `Depends on` names one; the planner's input names them. A record without `planned_from` falls back to its `spec.approved_version`, and a second plan at the same approved version supersedes nothing. Rejected: a superseded mark written at re-plan time, which needs a migration for stores that already hold such sub-tickets; and comparing with the parent's current approved version, which would supersede the live plan after a spec amendment that keeps it.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index c9bfdf3..2a98d97 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -106,7 +106,7 @@ Rules the table relies on:
   - A question returns to the role that asked, with the answer and that role's previous output (the output that asked it); a requester's CLARIFY answer returns to Triage the same way. When the answer is a standing decision, the human passes `--decision "<line>"` with the answer, or with the close, so that it lands in `decisions.md`.
   - BLOCKED, a critic ESCALATE, and a planner ESCALATE return to the role that emitted them with the ruling, same round, or the human re-scopes (spec gate or writer round reset) or closes.
   - A spec loop at max rounds goes to the spec gate.
-  - A parent-close FAILED or SPEC-DEFECT, an archive that does not apply, or a sub-ticket closed by the human, parks the parent: the human amends the spec and re-plans (new sub-tickets under the same parent) or closes the parent.
+  - A parent-close FAILED or SPEC-DEFECT, an archive that does not apply, or a sub-ticket closed by the human, parks the parent: the human amends the spec and re-plans (new sub-tickets under the same parent) or closes the parent. A new plan made from a later approved version supersedes the earlier plan's sub-tickets that have not merged: they keep their records and ids, are no longer dispatched, and neither park the parent nor hold back its close. Merged ones stay merged and count toward the close.
   - An archive refused for no change folder or no spec store parks the parent the same way, but its spec never entered the spec store: the human closes the parent as applied. Current truth is not updated, and archive appends nothing to `decisions.md`; the human logs any decision with `factory decision add`. If current truth should carry the spec, it is re-intaken as a new ticket.
   - A PR loop at max rounds, a SPEC-DEFECT, or a reviewer ESCALATE returns to the implementer with the round reset and the human's ruling as findings, or the ticket closes. The human may amend the sub-ticket or the pinned spec first; the amended version is what the implementer and checkers receive. There is no merge-gate override. A budget-killed run, or a ticket parked on a second EMPTY-OUTPUT, re-dispatches the same role on the same inputs, same round (the human may raise that run's budget or amend the sub-ticket first), or the ticket closes. In-flight siblings keep the spec version they received; the human decides whether to re-plan.
 
diff --git a/factory/cli.py b/factory/cli.py
index f9c54d7..2da17fa 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -449,21 +449,31 @@ def subticket_add(a, root, cfg):
         text = status.strip_trailer((d / "output.md").read_text(encoding="utf-8"))
     else:
         text = Path(a.file).read_text(encoding="utf-8")
+    existing = store.subtickets_of(root, parent["id"])
     try:
-        subs = subtickets.parse(text, parent["id"], [s["id"] for s in store.subtickets_of(root, parent["id"])])
+        subs = subtickets.parse(text, parent["id"], [s["id"] for s in existing])
     except ValueError as e:
         raise Refused(str(e)) from None
     if not subs:
         raise Refused("no sub-tickets found (a head line `<id> / Title`, id like T-0001-A, ST-1 or T-0001.1, "
                       "then `Depends on:` and `Parallel-safe:`)")
     ids = {s["id"] for s in subs}
+    av = parent["spec"]["approved_version"]
+    before = {s["id"] for s in subtickets.split_plan(existing)[1]}
+    after = subtickets.superseded_by_plan(existing, av)
     for sdef in subs:
         for dep in sdef["depends_on"]:
+            if dep in after:  # never dispatched, so the dependant would wait forever
+                raise Refused(f"{sdef['id']} ({sdef['label']}) depends on {dep}, which this plan supersedes")
             if dep not in ids and not store.ticket_path(root, dep).exists():
                 raise Refused(f"{sdef['id']} ({sdef['label']}) depends on {dep}, which is neither in this plan nor a ticket in the store")
         if store.ticket_path(root, sdef["id"]).exists():
             raise Refused(f"{sdef['id']} already exists")
-    out({"ok": True, "parent": parent["id"], "subtickets": _create_subtickets(root, parent, subs, f"plan:{a.run or a.file}")})
+    made = _create_subtickets(root, parent, subs, f"plan:{a.run or a.file}")
+    superseded = [i for i in after if i not in before]
+    if superseded:
+        store.log_event(root, "subtickets.superseded", ticket=parent["id"], subtickets=superseded, approved_version=av)
+    out({"ok": True, "parent": parent["id"], "subtickets": made, "superseded": superseded})
 
 
 def _create_subtickets(root: Path, parent: dict, subs: list[dict], source: str) -> list[dict]:
@@ -476,6 +486,7 @@ def _create_subtickets(root: Path, parent: dict, subs: list[dict], source: str)
                    "parallel_safe": sdef["parallel_safe"],
                    "status": "ready-for-implementer" if not sdef["depends_on"] else "waiting-dependencies"})
         st["spec"] = {"version": parent["spec"]["version"], "approved_version": parent["spec"]["approved_version"]}
+        st["planned_from"] = parent["spec"]["approved_version"]  # never changed afterwards, unlike `spec`
         store.write_text(root / "specs" / sdef["id"] / "subticket.md", sdef["text"])
         store.save_ticket(root, st)
         store.log_event(root, "ticket.created", ticket=sdef["id"], parent=parent["id"], status=st["status"])
@@ -547,7 +558,8 @@ def plan_whole_spec(a, root, cfg):
 
 
 def ticket_ready_implementers(a, root, cfg):
-    subs = store.subtickets_of(root, a.id)
+    every = store.subtickets_of(root, a.id)
+    subs, superseded = subtickets.split_plan(every)  # a later plan's superseded sub-tickets count nowhere
 
     def status_of(tid: str):
         p = store.ticket_path(root, tid)
@@ -560,14 +572,15 @@ def ticket_ready_implementers(a, root, cfg):
             s["history"].append({"ts": store.now(), "from": "waiting-dependencies", "to": "ready-for-implementer", "by": "ready-implementers"})
             store.save_ticket(root, s)
             store.log_event(root, "ticket.transition", ticket=s["id"], **{"from": "waiting-dependencies", "to": "ready-for-implementer", "by": "ready-implementers"})
-    out({"ok": True, "parent": a.id, "ready": ready, "subtickets": [s["id"] for s in subs],
+    out({"ok": True, "parent": a.id, "ready": ready, "subtickets": [s["id"] for s in every],
          "remaining": [s["id"] for s in subs if s["status"] not in ("merged", "parked", "closed")],
          "in_flight": [s["id"] for s in subs if s["in_flight"] or s["status"] in subtickets.IN_FLIGHT_STATES],
          "parked": [s["id"] for s in subs if s["status"] == "parked"],
          # stopped mid-check (a dispatcher that died or was stopped): no run in flight, so buildOne
          # resumes it from its stored state; the checkers re-run on its current head
          "resumable": [s["id"] for s in subs if s["status"] in subtickets.IN_FLIGHT_STATES and not s["in_flight"]],
-         "closed": [s["id"] for s in subs if s["status"] == "closed"]})
+         "closed": [s["id"] for s in subs if s["status"] == "closed"],
+         "superseded": [s["id"] for s in superseded]})
 
 
 def ticket_head(a, root, cfg):
@@ -735,11 +748,13 @@ def ticket_join(a, root, cfg):
 
 
 def ticket_parent_check(a, root, cfg):
-    """When every sub-ticket is merged, the parent moves to ready-for-parent-verify (part G)."""
+    """When every sub-ticket of the current plan is merged, the parent moves to ready-for-parent-verify
+    (part G); sub-tickets a later plan superseded do not count."""
     parent = store.load_ticket(root, a.id)
-    subs = store.subtickets_of(root, parent["id"])
-    if not subs:
+    every = store.subtickets_of(root, parent["id"])
+    if not every:
         raise Refused(f"{parent['id']} has no sub-tickets")
+    subs, superseded = subtickets.split_plan(every)
     if all(s["status"] == "merged" for s in subs) and parent["status"] == "planned":
         frm = parent["status"]
         parent["status"] = "ready-for-parent-verify"
@@ -748,7 +763,8 @@ def ticket_parent_check(a, root, cfg):
         store.log_event(root, "ticket.transition", ticket=parent["id"], **{"from": frm, "to": "ready-for-parent-verify", "by": "parent-check"})
     reuse = _reused_subticket_run(root, cfg, parent) if parent["status"] == "ready-for-parent-verify" else None
     out({"ok": True, "id": parent["id"], "state": parent["status"],
-         "subtickets": {s["id"]: s["status"] for s in subs}, "reuse": reuse})
+         "subtickets": {s["id"]: s["status"] for s in subs}, "superseded": [s["id"] for s in superseded],
+         "reuse": reuse})
 
 
 # ----- human surface (K-lite) -----------------------------------------------------
@@ -913,7 +929,7 @@ def resolve(a, root, cfg):
         subs = store.subtickets_of(root, t["id"])
         if not subs:
             raise Refused(f"--replan applies to a parent with sub-tickets; {t['id']} has none")
-        unmerged = [f"{s['id']} is {s['status']}" for s in subs if s["status"] != "merged"]
+        unmerged = [f"{s['id']} is {s['status']}" for s in subtickets.split_plan(subs)[0] if s["status"] != "merged"]
         if unmerged:
             raise Refused(f"--replan needs every sub-ticket merged: {', '.join(unmerged)}")
         dest = d / f"ruling-{_next_n(d, 'ruling')}.md"
@@ -1305,7 +1321,7 @@ def _reused_subticket_run(root: Path, cfg: dict, t: dict) -> str | None:
     (design doc routing table, Merge gate row), or None when the parent needs its own run."""
     # factory: one sub-ticket only, and scenario coverage is read from scenario names occurring in
     # the sub-ticket's text; widen only when the store can check a coverage map per sub-ticket.
-    subs = store.subtickets_of(root, t["id"])
+    subs = subtickets.split_plan(store.subtickets_of(root, t["id"]))[0]
     if len(subs) != 1 or not t.get("parent_base"):
         return None
     s = subs[0]
@@ -1333,10 +1349,11 @@ def _reused_subticket_run(root: Path, cfg: dict, t: dict) -> str | None:
 
 
 def _parent_close_verified(root: Path, cfg: dict, t: dict) -> str | None:
-    """The run that verifies the parent: every sub-ticket merged, and a finished verifier run on the
-    parent itself said VERIFIED on a head that contains every one of those merges (a run from before
-    the last merge does not count); else a sub-ticket's run that stands for it; else None."""
-    subs = store.subtickets_of(root, t["id"])
+    """The run that verifies the parent: every current sub-ticket merged (a superseded one does not
+    count), and a finished verifier run on the parent itself said VERIFIED on a head that contains
+    every one of those merges (a run from before the last merge does not count); else a
+    sub-ticket's run that stands for it; else None."""
+    subs = subtickets.split_plan(store.subtickets_of(root, t["id"]))[0]
     if any(s["status"] != "merged" for s in subs):
         return None
     repo = gitops.repo_root(cfg)
diff --git a/factory/compose.py b/factory/compose.py
index 213355c..f40d7c9 100644
--- a/factory/compose.py
+++ b/factory/compose.py
@@ -10,7 +10,7 @@ import re
 import shlex
 from pathlib import Path
 
-from factory import instance, specstore, store
+from factory import instance, specstore, store, subtickets
 
 
 def _runs_for(root: Path, ticket: str, role: str, exclude: str) -> list[str]:
@@ -297,6 +297,10 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
             parts.append(f"\n## Sub-tickets already under {tid}\n\nA new plan's sub-tickets are numbered after these. "
                          "A `Depends on:` line may name any of these ids.\n\n"
                          + "".join(f"- {s['id']} / {s['title']}: {s['status']}\n" for s in subs))
+            gone = subtickets.superseded_by_plan(subs, av)
+            if gone:
+                parts.append("\nNot merged and planned from an earlier approved version, so a new plan supersedes "
+                             f"them and may not depend on them: {', '.join(gone)}\n")
     elif role in ("implementer", "reviewer", "verifier"):
         parent = t.get("parent") or tid  # the parent-close verifier runs on the parent itself
         pt = store.load_ticket(root, parent) if parent != tid else t
diff --git a/factory/subtickets.py b/factory/subtickets.py
index 1d986d8..2d7360f 100644
--- a/factory/subtickets.py
+++ b/factory/subtickets.py
@@ -11,7 +11,8 @@ numbers them <PARENT>.1, .2, … in plan order and keeps the planner's own id as
 A later plan for the same parent (a re-plan after a failed parent-close check) continues that
 numbering: its sub-tickets take the next free ids after the parent's existing ones, its
 `Depends on:` lines may name an existing sub-ticket, and a head line that reuses an existing
-sub-ticket's id is refused.
+sub-ticket's id is refused. A plan made from a later approved spec version supersedes the earlier
+plans' sub-tickets that have not merged (`split_plan`).
 
 A field line may start with a `- ` or `* ` list bullet, before any bold marks. Every sub-ticket
 needs a `Depends on:` line (`Depends on: none` when it depends on nothing); a plan with a
@@ -138,6 +139,33 @@ def parse(planner_output: str, parent: str, existing=()) -> list[dict]:
     return subs
 
 
+def planned_from(sub: dict):
+    """The parent's approved version this sub-ticket was planned from: its `planned_from`, else (a
+    record made before that field) its `spec.approved_version`, else None."""
+    if sub.get("planned_from") is not None:
+        return sub["planned_from"]
+    return (sub.get("spec") or {}).get("approved_version")
+
+
+def split_plan(subs: list[dict]) -> tuple[list[dict], list[dict]]:
+    """(current, superseded), each in input order. A sub-ticket is superseded when it has not merged
+    and was planned from a lower approved version than the parent's latest plan; one with no
+    version counts as current. A superseded sub-ticket keeps its record but no longer counts."""
+    versions = [v for s in subs if (v := planned_from(s)) is not None]
+    top = max(versions, default=None)
+    current, superseded = [], []
+    for s in subs:
+        v = planned_from(s)
+        (superseded if s.get("status") != "merged" and v is not None and v < top else current).append(s)
+    return current, superseded
+
+
+def superseded_by_plan(subs: list[dict], version) -> list[str]:
+    """The ids split_plan marks superseded once a plan made from approved version `version` joins `subs`."""
+    plan = {"planned_from": version}
+    return [s["id"] for s in split_plan([*subs, plan])[1] if s is not plan]
+
+
 def ready_implementers(subs: list[dict], status_of=None) -> list[str]:
     """Doc §Routing table, Planner row: sub-tickets whose dependencies are merged (a dependency on
     another parent ticket: closed), minus any with a run in flight; a parallel_safe=false one runs
diff --git a/tests/factory/test_superseded_plan.py b/tests/factory/test_superseded_plan.py
new file mode 100644
index 0000000..c6ab61d
--- /dev/null
+++ b/tests/factory/test_superseded_plan.py
@@ -0,0 +1,158 @@
+"""Superseded plans (spec-factory T-0038, issue #77).
+
+Each sub-ticket records `planned_from`, the parent's approved spec version it was planned from.
+Once a parent has a sub-ticket planned from a later version, its older sub-tickets that have not
+merged are superseded: kept with their ids and records, but no longer dispatched, parking the
+parent or holding back its final check, close or re-plan. Merged ones stay merged and count.
+
+Black-box through `bin/factory` on a throwaway store (FACTORY_STATE), as test_replan.py does.
+"""
+from __future__ import annotations
+
+import json
+import os
+import subprocess
+from pathlib import Path
+
+import pytest
+import yaml
+
+REPO = Path(__file__).resolve().parents[2]
+BIN = REPO / "bin" / "factory"
+OLD_PLAN = ("ST-1 / Base\nDepends on: none\nParallel-safe: yes\n\nST-2 / Dropped\nDepends on: none\nParallel-safe: yes\n\n"
+            "ST-3 / Unstarted\nDepends on: ST-2\nParallel-safe: yes\n")
+NEW_PLAN = "ST-1 / Redo\nDepends on: T-0001.1\nParallel-safe: yes\n"
+SUPERSEDES_LINE = ("Not merged and planned from an earlier approved version, so a new plan supersedes them and may "
+                   "not depend on them: T-0001.2, T-0001.3")
+
+
+def run(store: Path, *argv: str) -> subprocess.CompletedProcess:
+    env = {**os.environ, "FACTORY_STATE": str(store), "PYTHONDONTWRITEBYTECODE": "1"}
+    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)
+
+
+def js(cp: subprocess.CompletedProcess) -> dict:
+    assert cp.returncode == 0, cp.stderr
+    return json.loads(cp.stdout.strip().splitlines()[-1])
+
+
+def ticket(store: Path, tid: str) -> dict:
+    return yaml.safe_load((store / "tickets" / f"{tid}.yaml").read_text())
+
+
+def add_plan(store: Path, tmp_path: Path, text: str, name: str) -> subprocess.CompletedProcess:
+    (tmp_path / name).write_text(text)
+    return run(store, "subticket", "add", "T-0001", "--file", str(tmp_path / name))
+
+
+def events(store: Path, name: str) -> list[dict]:
+    lines = [json.loads(ln) for p in sorted((store / "log").glob("*.jsonl")) for ln in p.read_text().splitlines()]
+    return [e for e in lines if e["event"] == name]
+
+
+@pytest.fixture
+def store(tmp_path: Path) -> Path:
+    """T-0001 past the spec gate at approved v1 (no spec store), with no sub-tickets yet."""
+    s = tmp_path / "store"
+    (tmp_path / "req.md").write_text("# Fixture\n\nThe bot should do the thing.\n")
+    (tmp_path / "spec.md").write_text("## Problem\nx\n")
+    js(run(s, "ticket", "new", "--file", str(tmp_path / "req.md")))
+    js(run(s, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t"))
+    js(run(s, "spec", "add", "T-0001", "--file", str(tmp_path / "spec.md")))
+    js(run(s, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init"))
+    js(run(s, "ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t"))
+    js(run(s, "approve-spec", "T-0001"))
+    return s
+
+
+@pytest.fixture
+def respecced(store: Path, tmp_path: Path) -> Path:
+    """Planned at v1 as T-0001.1 (merged), .2 (closed by a human) and .3 (never started), then sent
+    back to the spec gate and approved again, edited, as v2: ready for its planner again."""
+    js(add_plan(store, tmp_path, OLD_PLAN, "plan1.md"))
+    js(run(store, "ticket", "transition", "T-0001", "--to", "planned", "--by", "t"))
+    js(run(store, "ticket", "set", "T-0001.1", "status=merged"))
+    js(run(store, "ticket", "transition", "T-0001.2", "--to", "closed", "--by", "t"))
+    js(run(store, "ticket", "park", "T-0001", "--reason", "sub-ticket closed by a human: T-0001.2"))
+    js(run(store, "resolve", "T-0001", "--to", "spec-gate"))
+    (tmp_path / "spec2.md").write_text("## Problem\nx, amended\n")
+    js(run(store, "approve-spec", "T-0001", "--edit", str(tmp_path / "spec2.md")))
+    return store
+
+
+def replan(store: Path, tmp_path: Path) -> dict:
+    res = js(add_plan(store, tmp_path, NEW_PLAN, "plan2.md"))
+    js(run(store, "ticket", "transition", "T-0001", "--to", "planned", "--by", "t"))
+    return res
+
+
+def test_each_sub_ticket_records_the_approved_version_it_was_planned_from(respecced, tmp_path):
+    replan(respecced, tmp_path)
+    assert [ticket(respecced, f"T-0001.{i}")["planned_from"] for i in (1, 2, 3, 4)] == [1, 1, 1, 2]
+
+
+def test_a_re_plan_supersedes_the_old_unmerged_sub_tickets_and_keeps_their_records(respecced, tmp_path):
+    assert replan(respecced, tmp_path)["superseded"] == ["T-0001.2", "T-0001.3"]
+    r = js(run(respecced, "ticket", "ready-implementers", "T-0001"))
+    assert r["ready"] == ["T-0001.4"] and r["closed"] == [] and r["remaining"] == ["T-0001.4"]
+    assert r["superseded"] == ["T-0001.2", "T-0001.3"]
+    assert r["subtickets"] == ["T-0001.1", "T-0001.2", "T-0001.3", "T-0001.4"]
+    assert ticket(respecced, "T-0001.2")["status"] == "closed"
+    assert ticket(respecced, "T-0001.3")["status"] == "waiting-dependencies"
+    [e] = events(respecced, "subtickets.superseded")
+    assert (e["ticket"], e["subtickets"], e["approved_version"]) == ("T-0001", ["T-0001.2", "T-0001.3"], 2)
+
+
+def test_the_final_check_counts_only_the_current_plan(respecced, tmp_path):
+    replan(respecced, tmp_path)
+    assert js(run(respecced, "ticket", "parent-check", "T-0001"))["state"] == "planned"
+    js(run(respecced, "ticket", "set", "T-0001.4", "status=merged"))
+    r = js(run(respecced, "ticket", "parent-check", "T-0001"))
+    assert r["state"] == "ready-for-parent-verify"
+    assert r["subtickets"] == {"T-0001.1": "merged", "T-0001.4": "merged"}
+    assert r["superseded"] == ["T-0001.2", "T-0001.3"]
+
+
+def test_a_re_plan_past_superseded_sub_tickets_is_accepted(respecced, tmp_path):
+    replan(respecced, tmp_path)
+    js(run(respecced, "ticket", "set", "T-0001.4", "status=merged"))
+    js(run(respecced, "ticket", "parent-check", "T-0001"))
+    js(run(respecced, "ticket", "park", "T-0001", "--reason", "FAILED from parent-close verifier"))
+    (tmp_path / "note.md").write_text("Re-plan: one more fix.\n")
+    assert js(run(respecced, "resolve", "T-0001", "--replan", str(tmp_path / "note.md")))["state"] == "ready-for-planner"
+
+
+def test_a_plan_that_depends_on_a_sub_ticket_it_supersedes_is_refused_and_writes_nothing(respecced, tmp_path):
+    before = sorted(p.name for p in (respecced / "tickets").iterdir())
+    cp = add_plan(respecced, tmp_path, "ST-1 / Redo\nDepends on: T-0001.3\nParallel-safe: yes\n", "plan3.md")
+    assert cp.returncode == 2
+    assert "T-0001.4 (ST-1) depends on T-0001.3, which this plan supersedes" in cp.stderr
+    assert sorted(p.name for p in (respecced / "tickets").iterdir()) == before
+
+
+def test_the_planner_input_names_the_sub_tickets_a_new_plan_supersedes(respecced):
+    rid = js(run(respecced, "run", "start", "--role", "planner", "--ticket", "T-0001"))["run_id"]
+    js(run(respecced, "run", "compose", rid))
+    text = (respecced / "runs" / rid / "input.md").read_text()
+    assert "- T-0001.3 / Unstarted: waiting-dependencies\n\n" + SUPERSEDES_LINE + "\n" in text
+
+
+def test_a_second_plan_at_the_same_approved_version_supersedes_nothing(store, tmp_path):
+    js(add_plan(store, tmp_path, "ST-1 / First\nDepends on: none\nParallel-safe: yes\n", "plan1.md"))
+    assert js(add_plan(store, tmp_path, "ST-1 / Extra\nDepends on: none\nParallel-safe: yes\n", "plan2.md"))["superseded"] == []
+    r = js(run(store, "ticket", "ready-implementers", "T-0001"))
+    assert r["superseded"] == [] and r["ready"] == ["T-0001.1", "T-0001.2"]
+    assert events(store, "subtickets.superseded") == []
+
+
+def test_a_moved_spec_record_does_not_change_the_plan_a_sub_ticket_belongs_to(respecced, tmp_path):
+    js(run(respecced, "ticket", "set", "T-0001.3", "spec.version=2", "spec.approved_version=2"))
+    replan(respecced, tmp_path)
+    assert js(run(respecced, "ticket", "ready-implementers", "T-0001"))["superseded"] == ["T-0001.2", "T-0001.3"]
+
+
+def test_a_record_without_planned_from_falls_back_to_its_spec_version(respecced, tmp_path):
+    replan(respecced, tmp_path)
+    for i in (1, 2, 3, 4):
+        js(run(respecced, "ticket", "set", f"T-0001.{i}", "planned_from="))
+    assert js(run(respecced, "ticket", "ready-implementers", "T-0001"))["superseded"] == ["T-0001.2", "T-0001.3"]
