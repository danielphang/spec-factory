# Spec Factory

An AI software pipeline: eight agent roles (triage, spec writer, spec critic, planner, implementer,
code reviewer, verifier, retro), a routing table, human gates, and a small program, the
**harness**, that moves each ticket from role to role, keeps the records, and enforces the wiring
rules no prompt can enforce. This repo holds the design and the harness. One harness checkout
serves many target repos; each target carries only a small `.factory/` instance.

## Install

```
git clone <this repo> ~/dev/spec-factory
cd ~/dev/spec-factory
uv sync --frozen
uv run --frozen pytest -q -p no:cacheprovider tests/factory
```

`uv sync` gives the harness its interpreter and dependencies (`pyproject.toml`, `uv.lock`);
`bin/factory` runs the `factory` package with that environment.

## Five-minute use

Run these from inside the target repo. `H` is the harness checkout you run targets from (see "How
updates work").

1. `$H/bin/factory init --repo-name NAME`. It creates `.factory/` at the repo's top level
   (`instance.yaml`, `context.md`, `harness.lock`, the store) and copies the agent definitions
   into `.claude/agents/`. It is idempotent.
2. Restart the Claude Code session, so the agents register.
3. Fill in `.factory/context.md`, the briefing every role reads first (which repo, how to run its
   tests, what kind of request to expect), and `gate_commands` in `.factory/instance.yaml`.
   Adjust `protected_paths` there too.
4. `$H/bin/factory paths` prints, as JSON, the harness, its entry point, both workflow scripts
   (`intake_workflow`, `build_workflow`), the harness revision, and the instance and store it
   found.
5. Put a request in the store, `$H/bin/factory ticket new --file "$PWD/request.md"` (an absolute
   path: `bin/factory` runs from the harness checkout), then call Claude
   Code's Workflow tool with `scriptPath` set to `intake_workflow` and the args
   `{ticket, repo: <abs path of H>, instance: <abs path of .factory/>}`.
6. At the human gate, `$H/bin/factory approve-spec T-0001` (or `request-changes T-0001 --notes …`).
   The planner then runs; `build_workflow`, called the same way, builds and merges each
   sub-ticket.

## Where things live

| Path | What |
|---|---|
| `docs/design.md` | The design document: roles, harness pieces, routing, gates. The source of truth |
| `docs/changelog.md` | The design document's changelog |
| `docs/prompts/` | Each role's prompt block, copied verbatim from the design doc by hand (nothing regenerates them); `00-preamble.md` goes at the top of every role |
| `dev/` | Working documents for building the factory itself: the build spec, its plan, the P0 walking skeleton, and the index of this repo's issues |
| `factory/` | The harness package: the store CLI, its role prompts and its two workflow scripts (`factory/workflows/`) |
| `bin/factory` | The harness entry point |
| `agents/` | The agent definition templates `factory init` copies into a target's `.claude/agents/` |
| `tests/factory/` | The harness's test suite |
| `.factory/` | This repo's own instance of the factory (see `.factory/README.md`) |

## How updates work

A target holds no harness code, only `.factory/`, and runs whatever revision the runtime checkout
named in its `instance.yaml` has checked out. The lock makes a new revision available rather than
silently adopted: each target refuses an unaccepted harness revision, and refuses uncommitted
edits to the harness's code, until you run a command with `--accept-harness <sha>` there. The
acceptance is logged in the target's store.

Develop the harness in one checkout and run targets from a separate runtime checkout (for this
repo, a detached worktree at `~/dev/spec-factory-harness`), so a merge never changes code under
a running ticket. Upgrading, done between tickets, is moving the runtime
(`git -C <runtime> checkout --detach <sha>`, then `uv sync --frozen`), then accepting the new
revision in each target that uses it.
