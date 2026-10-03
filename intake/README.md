# intake/ — SCRATCH

**Scratch area, not part of the design.** A throwaway spec-factory intake instance that runs
this repo's GitHub issues (index: `../dev/issues.md`) through intake (Triage → Spec writer ⇄ Critic → human gate →
Planner) against this repo. Delete the whole directory once the issues are filed and closed;
nothing outside it depends on it.

## Why it exists

The only built harness is the Nanobot-side P0 skeleton (`~/dev/nanobot-upstream/factory/`,
branch `feat/lionbot-v3`). Its preamble, role context and config name `nanobot` as the target,
so it cannot take tickets against this repo as-is (issue draft 07). This instance runs a
pinned copy of that harness with three files overlaid to retarget it here. Green's harness and
its live store (`knowledge_vault/spec_factory/`, T-0001 = SPEC-21 mid-intake) are untouched.

## Layout

| Path | What | Tracked |
|---|---|---|
| `HARNESS_PIN` | Commit of `feat/lionbot-v3` the harness is copied from | yes |
| `instance/` | `preamble.md`, `context.md`, `config.yaml`: the retargeting overlay | yes |
| `setup.sh` | Rebuilds `harness/` from the pin plus the overlay; idempotent | yes |
| `harness/` | The built copy (`factory/`, `bin/factory`) | no (gitignored) |
| `state/` | The store (`FACTORY_STATE`): tickets, requests, runs, specs, log | yes |

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

T-0001..T-0007: spec approved at the gate and applied on `main` (merges listed in `dev/issues.md`).
Closed 2026-10-01 as applied by hand. The Planner was run on T-0001..T-0003 anyway, as its first
real test: each run found the spec already on `main` and escalated instead of planning no-op
work, which is the right call. Lesson for the design (feeds T-0008's lifecycle): the store has no
state for "approved and applied outside the pipeline"; `closed` via `resolve --close` stands in.
T-0008: approved (v3), applied (`03d8835`), closed. All nine drafts are applied; the backlog is empty.
T-0011: approved (v2 + operator amendment), applied (`9168ce1`), closed.
T-0009: approved, applied (`f2576ca`), closed.

## Running

```
intake/setup.sh
FACTORY_STATE=$PWD/intake/state intake/harness/bin/factory ticket show T-0001
```

Dispatch is the harness's own workflow script, `intake/harness/factory/workflows/intake.js`,
run through Claude Code's Workflow tool with
`{ticket, repo: <abs>/intake/harness, state: <abs>/intake/state, inlineRoles: true}`.
One ticket at a time: the store allocates run ids without a lock. The human gate is
`bin/factory approve-spec T-000N` or `request-changes`, as on green.

A new issue enters intake as a file: `gh issue view N --json body -q .body > /tmp/N.md` then `bin/factory ticket new --file /tmp/N.md`.

## Scope

This instance works on the spec factory's own documents. Nanobot is a task source and the
reference harness, read only. Nanobot-side follow-ups that come out of these tickets (for
example green's `factory/status.py` adopting T-0001's `none` + prose rule) belong to the
nanobot sessions, not to this intake.

## green-pilot/ — the first end-to-end pilot (2026-10-03)

A second store, `intake/green-pilot/`, driven by this session through **green's own harness**
(`~/dev/nanobot-upstream/bin/factory`, `factory/workflows/intake.js` then `build.js`), not the
overlay in `harness/`: the ticket changes green's `factory/` code, so its roles need green's
context and gate commands, and its build merges into `feat/lionbot-v3`. One ticket: T-0001 =
GitHub #16. The Driver session owns green's store and stays off this one.
