# .factory/ — this repo's own instance

This directory is the spec factory's instance for this repo (instance B): the factory runs this
repo's GitHub issues through intake (Triage → Spec writer ⇄ Critic → human gate → Planner) and the
build half against this repo. The harness that runs it is the code in this repo (`factory/`,
`bin/factory`, `agents/`); see the top-level `README.md`.

## Layout

| Path | What |
|---|---|
| `instance.yaml` | This instance's config: repo name, runtime checkout, store path, protected paths, gate commands, models, routing |
| `context.md` | The role-context block: the briefing every role reads first |
| `harness.lock` | The harness revision this instance has accepted |
| `answers/` | Operator answers and gate edits, as written at the time (closed records) |
| `green-pilot/` | The closed store of the first end-to-end pilot (below) |

The live store is still `intake/state/` (tickets, requests, runs, specs, log). A post-close operator
step moves it to `.factory/state/`. Records here and in the store are kept as written: old paths
quoted inside them are history, not instructions.

Ticket ids are local to this store: T-0001 here is issue 01, not green's SPEC-21 ticket.

| Ticket | GitHub issue |
|---|---|
| T-0001 | [#1](https://github.com/danielphang/spec-factory/issues/1) |
| T-0002 | [#2](https://github.com/danielphang/spec-factory/issues/2) |
| T-0003 | [#3](https://github.com/danielphang/spec-factory/issues/3) |
| T-0004 | [#4](https://github.com/danielphang/spec-factory/issues/4) |
| T-0005 | [#5](https://github.com/danielphang/spec-factory/issues/5) |
| T-0006 | [#6](https://github.com/danielphang/spec-factory/issues/6) |
| T-0007 | [#7](https://github.com/danielphang/spec-factory/issues/7) |
| T-0008 | [#8](https://github.com/danielphang/spec-factory/issues/8) |
| T-0009 | [#9](https://github.com/danielphang/spec-factory/issues/9) |
| T-0010 | [#10](https://github.com/danielphang/spec-factory/issues/10) |
| T-0011 | [#11](https://github.com/danielphang/spec-factory/issues/11) |
| T-0012 | [#19](https://github.com/danielphang/spec-factory/issues/19) |

T-0001..T-0007: spec approved at the gate and applied on `main` (merges listed in `dev/issues.md`).
Closed 2026-10-01 as applied by hand. The Planner was run on T-0001..T-0003 anyway, as its first
real test: each run found the spec already on `main` and escalated instead of planning no-op
work, which is the right call. Lesson for the design (feeds T-0008's lifecycle): the store has no
state for "approved and applied outside the pipeline"; `closed` via `resolve --close` stands in.
T-0008: approved (v3), applied (`03d8835`), closed.
T-0011: approved (v2 + operator amendment), applied (`9168ce1`), closed.
T-0009: approved, applied (`f2576ca`), closed.

## Running

From anywhere in this repo the harness finds this instance by walking up to
`.factory/instance.yaml`. Run the runtime checkout that `instance.yaml` names
(`~/dev/spec-factory-harness`, installed with `uv sync --frozen`):

```
~/dev/spec-factory-harness/bin/factory paths
~/dev/spec-factory-harness/bin/factory ticket show T-0001
```

`paths` prints the harness checkout, its entry point, both workflow scripts, the running harness
revision, and this instance and its store. Dispatch is the harness's own workflow script (`intake_workflow` or
`build_workflow` from `paths`), run through Claude Code's Workflow tool with
`{ticket, repo: <abs ~/dev/spec-factory-harness>, instance: <abs ~/dev/spec-factory/.factory>, inlineRoles: true}`
(this repo adds no `.claude/agents/`, so roles run inline). Below, `factory` is
`~/dev/spec-factory-harness/bin/factory`. The human gate is `factory approve-spec T-000N` or
`request-changes`.

A new issue enters intake as a file: `gh issue view N --json body -q .body > /tmp/N.md` then `factory ticket new --file /tmp/N.md`.

If the runtime has moved to a harness revision this instance has not accepted, or holds uncommitted
harness edits, every store command is refused. Accept a new revision between tickets with
`factory --accept-harness <sha> <command>`; the acceptance is logged in the store. Uncommitted
harness edits cannot be accepted: commit or discard them first.

## Scope

This instance works on the spec factory's own documents and harness code. Nanobot is a task
source and the reference for green's in-tree harness, read only. Nanobot-side follow-ups that come
out of these tickets (for example green's `factory/status.py` adopting T-0001's `none` + prose
rule) belong to the nanobot sessions, not to this instance.

## green-pilot/ — the first end-to-end pilot (2026-10-03)

A second, closed store, `green-pilot/`, driven through **green's own harness**
(`~/dev/nanobot-upstream/bin/factory`, its `intake.js` then `build.js`): the tickets changed green's
`factory/` code, so their roles needed green's context and gate commands, and their builds merged
into `feat/lionbot-v3`. T-0001 = GitHub #16, T-0002 = GitHub #18. The Driver session owns green's
live store; this one is kept byte-identical as a record.
