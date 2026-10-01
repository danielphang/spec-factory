# intake/ — SCRATCH

**Scratch area, not part of the design.** A throwaway spec-factory intake instance that runs
the issue drafts in `../issues/` through intake (Triage → Spec writer ⇄ Critic → human gate →
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

| Ticket | Issue draft |
|---|---|
| T-0001 | `issues/01_status_parser.md` |
| T-0002 | `issues/02_clerk_schema.md` |
| T-0003 | `issues/03_triage_reask_input.md` |
| T-0004 | `issues/04_p0_agents_dir.md` |
| T-0005 | `issues/05_protected_live_state.md` |
| T-0006 | `issues/06_p05_grep_vs_inline_scripts.md` |
| T-0007 | `issues/07_single_target_harness.md` |
| T-0008 | `issues/08_openspec_schema.md` |

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

Nothing here is pushed or filed on GitHub; that waits for `gh auth` (see `issues/README.md`).

## Scope

This instance works on the spec factory's own documents. Nanobot is a task source and the
reference harness, read only. Nanobot-side follow-ups that come out of these tickets (for
example green's `factory/status.py` adopting T-0001's `none` + prose rule) belong to the
nanobot sessions, not to this intake.
