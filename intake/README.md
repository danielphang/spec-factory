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

## Follow-ups owed outside this repo

- **Green `factory/status.py` from (c) to (b)** (`none` + prose: route as none, keep the prose on
  the run record). Owner: this intake's session, after T-0001's spec is approved at the gate;
  committing on green needs the operator's go. Tests: `tests/factory/test_p0_cli.py`
  (`test_status_parse_none_is_exact_so_real_escalations_survive` and the commentary test above
  it) flip two expectations; add `none. x` with no tail → none, prose kept (e.g. a new
  `escalations_note` key that `run finish` writes to `meta.yaml`). Until then the Driver reads any
  "none, but …" queue item on its T-0001 as none.
