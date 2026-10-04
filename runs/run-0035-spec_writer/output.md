# Spec T-0009: `factory run start` reserves its run directory atomically

## Problem

`specs/build-harness.md` part B says what `factory run start` writes (`runs/<run_id>/{meta.yaml,system-prompt.txt}`) and which guards refuse it. It does not say how `<run_id>` is chosen, or that two starts on one store at the same moment must get different run directories. The spec already allows concurrent starts on different tickets: part H's build loop runs `await parallel(ready.map(st => () => buildOne(st)))`, and item 79 expects "two `parallel_safe: true` siblings both ready, nothing in flight → both listed". The `in_flight` guard only covers one ticket, so nothing in the spec stops an implementer from allocating ids the way the P0 reference did: list `runs/`, take max+1. Under that scheme, two concurrent starts can share one `runs/<id>/`, their `meta.yaml`, `input.md` and `output.md` overwrite each other, and the audit log and retro attribute one run's output to another ticket. The people affected are the operator running concurrent workflows on one store, and the retro and audit readers who depend on `runs/<run_id>/` belonging to exactly one run.

## Evidence

All commands were run on 2026-10-01. spec-factory is at `main` `b4d0f90`. The reference is `~/dev/nanobot-upstream`, read only; the code was extracted with `git archive` into a scratch directory.

E1. The spec gap. Part B's bullet is `specs/build-harness.md:201`. It ends with the guards ("`ticket/T-0001 already has run <id> in flight`.") and has no allocation rule. This command:
```
$ grep -n -i "concurren\|run id\|run_id" specs/build-harness.md docs/spec-factory.md
```
returns only the uses of `run_id` as a name (lines 186, 187, 196, 201, 202, 209, 273, 294, 295, 348, 349, 418, 459 and others). It finds no allocation rule and no concurrency requirement. Part I (`:292-299`) covers system prompt, input, isolation, tools, budget and cleanup. It does not cover allocation.

E2. The spec already contains concurrent `run start` calls:
- `:283`: `await parallel(ready.map(st => () => buildOne(st)))`, which runs starts on different tickets.
- `:286`: `[rev, ver] = await parallel([() => runRole('reviewer', …), () => runRole('verifier', …)])`, which runs two starts on the same ticket.
- `:450`: item 79, "two `parallel_safe: true` siblings both ready, nothing in flight → both listed".
- `docs/spec-factory.md:101` (Planner row): "parallel-safe ones run concurrently".

E3. The race is real in the pre-fix reference. I ran `next_run_id` from `3dc4d6149~1` and from `3dc4d6149` in 8 threads behind a barrier, 200 trials each, with the same role every time:
```
== 3dc4d6149~1
trial0 ids: ['run-0002-spec_writer' ×4, 'run-0003-spec_writer' ×4]
trials with a duplicate id among 8 concurrent starts: 200 / 200
== 3dc4d6149
trials with a duplicate id among 8 concurrent starts: 0 / 200
```

E4. The new build-spec item (part B below) was run against the reference CLI. It was adapted to P0's verbs: `factory ticket new --file` instead of `request new`, no `--head` option, `FACTORY_STATE` set to a fresh scratch store, and the `.venv` python from `~/dev/nanobot-upstream`. `git diff --stat 3dc4d6149 HEAD -- factory/` is empty, so HEAD runs the same code as the fix commit. The test makes eight tickets one after another and then starts eight `--role triage` runs at once. It passes when the ids are distinct, there are 8 run directories, and every `meta.yaml` `ticket:` matches the start that printed the id. Results over 20 rounds:
```
pre-fix (3dc4d6149~1):  round 1: exitfail=0 distinct_ids=7 dirs=7 meta_ticket_mismatches=1   rounds failing: 18 / 20
fix     (3dc4d6149):    round 1: exitfail=0 distinct_ids=8 dirs=8 meta_ticket_mismatches=0   rounds failing:  0 / 20
```
One extra round ran under zsh with the item's exact shell form (`( … ; echo $? > rc.$i ) & done; wait`):
```
pre-fix: rc: 8×0; in_flight == printed id: 8/8; run.started lines: 8, distinct runs: 4, dirs: 4
fix:     rc: 8×0; in_flight == printed id: 8/8; run.started lines: 8, distinct runs: 8, dirs: 8
```
This means exit codes and `in_flight` alone do not catch the bug. The distinct-id, directory-count and `meta.yaml` ticket checks do, so the item needs all three.

E5. The as-built fix is in `3dc4d6149`, `factory/store.py` `next_run_id`. It takes a candidate from max+1, then loops `(runs / rid).mkdir()`, adding 1 to `n` on `FileExistsError`. In `factory/cli.py` `run_start` (lines 158-180 at HEAD), the ready-state and `in_flight` guards raise before `store.next_run_id(...)`, so a refused start creates no directory. That matches item 70 (`specs/build-harness.md:438`), whose text includes "no new `runs/<id>/` directory".

E6. The acceptance commands below were dry-run. On this checkout (base), items 1 to 4 print `0` or nothing and items 5 to 7 print their REGRESSION values. On a scratch clone of `main`, I committed parts A to C exactly as written below. There, items 1 to 4 print their NEW values, items 5 to 7 still hold, and `git diff --stat main...HEAD` shows `specs/build-harness.md | 8 ++++++--`.

## Root cause

The spec defines no allocation rule for `run_id`: `specs/build-harness.md` part B, the `factory run start` bullet (`:201`). Without one, a list-then-name allocation, as in the P0 reference `factory/store.py` `next_run_id` before `3dc4d6149`, meets the spec as written and still hands one id to two concurrent starts (E3, E4).

## Proposed change

All edits are in `specs/build-harness.md`. No other file changes.

**A. Part B, the `factory run start` bullet (`:201`).** Append one space and the following text to the end of the bullet, after its final "`ticket/T-0001 already has run <id> in flight`.". The bullet stays one line.

> **Run id reservation:** after the guards pass and before anything else is written, `run start` reserves the run's directory by creating `runs/<run_id>/` create-exclusive (an mkdir that fails when the path already exists); on a collision it takes the next id and tries again. Two starts on one store at the same moment, whatever their tickets or roles, therefore never share a run directory, and the id is final before its `meta.yaml` is written. A refused start reserves nothing (item 70).

The rule says nothing about the id format. This ticket does not ask for a format, and `run-NNNN-<role>`-style ids sharing a number across roles in different directories is acceptable (triage assumption A3).

**B. Acceptance: a new heading and item.** Insert the block below directly before the line `### Gates (every seam)`, with one blank line on each side. Number the item one past the highest Acceptance item number at merge time. That is 87 on `b4d0f90`, where T-0003 holds 86. T-0008's spec v2 also claims 87 and 88, so whichever ticket merges second renumbers. The text has no other cross-reference to its own number.

```
### Run store concurrency [S1]

87. **Concurrent run starts (B) [S1]:** eight tickets `T-0001`…`T-0008`, made by `factory request new` one after another, so each is `ready-for-triage` with `in_flight: []`; then eight starts at once, all one role: `for i in 1 2 3 4 5 6 7 8; do ( factory run start --role triage --ticket T-000$i --head none > start.$i.json; echo $? > rc.$i ) & done; wait; cat rc.*` → eight lines `0`; the eight `run_id`s, one per `start.$i.json`, are pairwise distinct; `runs/` holds eight more directories than before, one per printed id, each with its own `meta.yaml` and `system-prompt.txt`; each `meta.yaml` has `role: triage` and `ticket:` equal to the ticket whose start printed that id; `factory ticket show T-000$i | grep in_flight` → `in_flight: [<the id start.$i.json printed>]`; `factory log tail --event run.started` gained eight lines, one per printed id. Repeated 20 times, each time on eight new tickets in a fresh working directory → the same every time. All eight starts share one role, so an allocation that lists `runs/` and names the next id without reserving it hands two of them one id [NEW]
```

Design notes for the item. Tickets are created one after another because concurrent `request new` is a separate race (see Out of scope). All eight starts use one role because with role-suffixed ids, mixed roles would hide a collision. The 20 repeats are there because the pre-fix reference failed 18 of 20 single rounds (E4).

**C. The marker line at the end of Acceptance.** In `Items needing the bare repo: … Items 68–72, 78, 79, 82, 85 are local-only.`, add the new item's number to the local-only list, for example `…, 82, 85, 87 are local-only.`. The item needs no bare repo and no model call.

**D. No other text changes, and why.**
- Part I is not edited. Its items cover the role's environment: system prompt, input, worktree, tools, budget and cleanup. Reserving a run directory is a store operation and belongs in B, where `run start` is defined. A second statement in I would be a copy that can drift.
- `docs/spec-factory.md` is not edited. Piece 10 already requires outputs "keyed by run id", and the Planner row already requires concurrent dispatch, so the doc implies that a store shared by concurrent runs has distinct run ids. How an id is allocated is a build detail. With no doc change there is no Changelog entry and no `prompts/` re-copy.

## Acceptance

All commands run as written from `~/dev/spec-factory`. On the base, `main...HEAD` is empty.

1. `grep -F 'factory run start --role R --ticket ID|none' specs/build-harness.md | grep -F 'create-exclusive' | grep -F 'takes the next id' | grep -F 'is final before its' | grep -cF 'A refused start reserves nothing'` → `1` [NEW. Today it prints `0` and exits 1, because the `:201` bullet ends at the in-flight guard.]
2. `grep -E '^[0-9]+\. \*\*Concurrent run starts' specs/build-harness.md | grep -F 'T-0008' | grep -F -e '--role triage' | grep -F 'pairwise distinct' | grep -F 'each with its own' | grep -cF 'Repeated 20 times'` → `1` [NEW. Today it prints `0`, because no such item exists.]
3. `n=$(grep -oE '^[0-9]+\. \*\*Concurrent run starts' specs/build-harness.md | cut -d. -f1); test -n "$n" && grep -cE "^$n\. " specs/build-harness.md && test "$n" = "$(grep -oE '^[0-9]+\. ' specs/build-harness.md | tr -d '. ' | sort -n | tail -1)" && grep -o 'Items 68.* are local-only' specs/build-harness.md | grep -cE "[ ,]$n( |,)"` → `1` then `1`. This checks three things: the item's number is used once, it is the highest item number, and it is in the local-only list. [NEW. Today it prints nothing and exits 1, because `n` is empty.]
4. `grep -B2 -E '^[0-9]+\. \*\*Concurrent run starts' specs/build-harness.md | grep -c '^### Run store concurrency \[S1\]$'` → `1` [NEW. Today it prints `0`.]
5. `git diff -U0 main...HEAD -- specs/build-harness.md | grep -E '^-' | grep -vE '^--- ' | grep -vcE '^-- .factory run start --role R |^-Items needing the bare repo'` → `0`. The only lines removed or rewritten are the `run start` bullet and the marker line, so item 70 (the guard that writes no directory), item 79, part H and part I are unchanged. [REGRESSION. Today it prints `0`.]
6. `git diff --quiet main...HEAD -- docs/ prompts/ && echo untouched` → `untouched` [REGRESSION. Today it prints `untouched`.]
7. `git diff --check main...HEAD` → no output, exit 0 [REGRESSION. Today it exits 0.]

## Tests to change

none. This repo has no test suite. No existing acceptance item in `specs/build-harness.md` is edited; item 5 checks this.

## Out of scope

These must not change:
- `docs/spec-factory.md` (and so its Changelog) and `prompts/`.
- Part I.
- Items 70 and 79.
- The guard order already in B.
- The `run_id` format.
- The reference harness `~/dev/nanobot-upstream/**`, which is read only and already fixed in `3dc4d6149`.
- `intake/**`.

Concurrency across two separate checkouts of the `tickets` branch is also out of scope. mkdir is only exclusive within one filesystem, and "one store" in A means one checkout, as in `~/factory/state`.

Out-of-scope observations (not fixed here):
- The same list-then-name race exists for ticket ids. In the reference, `factory/store.py` `next_ticket_id` (lines 81-90 at HEAD) lists `tickets/` and returns max+1 without reserving anything. Two concurrent `request new` or `intake` calls could get one ID. The spec does not say they can run concurrently, so this is a separate request if wanted. This is also why item 87 creates its tickets one after another.
- Two starts on the same ticket are part of the spec, not hypothetical: part H `:286` starts the reviewer and verifier in parallel. In the reference, `run_start` loads the ticket, appends to `in_flight` and saves, so concurrent starts on one ticket could lose an `in_flight` id. Part A keeps their directories distinct but does not cover that lost update. Triage flagged the same gap, and it deserves its own request.
- `intake/README.md:57` ("One ticket at a time: the store allocates run ids without a lock.") is stale. `intake/HARNESS_PIN` reads `3dc4d61491798af161add6471d2491653653912e`, which includes the fix. `intake/**` is protected infra, so I did not edit it.
- The spec-writer FORMAT in this run's system prompt has no `## Operator steps` section, but `prompts/02-spec-writer.md` and `docs/spec-factory.md:301` do. The pinned harness's prompt copy appears to predate T-0005. This spec needs no operator steps, so I omitted the section.

## Open questions

none.

## Risk

The change only touches text in `specs/build-harness.md`: about 6 lines added and 2 rewritten, per the dry run in E6. No protected path is touched: not `intake/**`, not `prompts/**`, not `~/dev/nanobot-upstream/**`, not `~/.nanobot/**`.

Merge-order risk: T-0008's spec also inserts items before `### Gates (every seam)` and claims 87 and 88. Part B numbers the item at merge time, and acceptance items 2 to 4 find it by content rather than by number, so either order works.

Downstream effect: an implementer of seam S1 must make `run start` reserve its directory create-exclusive. The reference already does this (E5) and passes the new item 20 of 20 rounds (E4).

STATUS: READY-FOR-CRITIC
CONFIDENCE: high, because the gap, the concurrent paths and the reference fix were each checked by grep or `git show`. The new build item was run against both the pre-fix and the fixed reference (it failed 18/20 and 0/20), and every acceptance command was dry-run on the base and on a clone with the edits applied.
ESCALATIONS: none
