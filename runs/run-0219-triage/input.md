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
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `state/`.
  The store is tracked on `main` and the operator commits it between steps, so `main` moves even
  when no ticket merges.

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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0219-triage/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0219-triage/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Request (raw, with any answers appended)

---
title: "Roles can write the live instance store: a spec writer's 'factory init' initialised spec-factory's own store"
labels: "harness"
---
**Problem:** a role can run store-writing `factory` commands against the live instance it is working on. A role's shell starts inside the target repo, so `bin/factory` walks up to that repo's own `.factory/` and writes the live store. #36's throwaway HOME does not help, because the store is not under HOME.

**Evidence (spec-factory, 2026-10-04):** at 13:35:44Z, `factory init` ran against instance B's own store. The only role run active then was T-0023's spec writer (run-0196, 13:16–13:48), which was researching #30 (`init` on a throwaway store), and its transcript shows the command. It initialised the live store: `openspec/` and `decisions.md` were created, and six `factory-*.md` agent files were copied into `~/dev/spec-factory/.claude/agents/`. Instance B's spec (T-0012) gives it no agent files. The store log records it as `store.initialised` with no run attached. Effects:
- B silently gained a spec store, so later tickets archive into current truth instead of closing as applied.
- The agent files would have registered in the next session started in that repo. They were removed by hand.

**Proposed change:**
- A. **Only the dispatcher writes the instance's own store.** The clerk's commands carry `FACTORY_DISPATCH=1`. Any store-writing command (`ticket`, `run`, `results`, `subticket`, `merge`, `archive`, `init`, `resolve`, `approve-spec`, `decision`) on the instance's own store without it, and without a human's `--by`, is refused with exit 2: "role runs may not write the live store; use a throwaway FACTORY_STATE". Read commands (`show`, `paths`, `config`) stay open.
- B. **Preamble:** to try a `factory` command, use a throwaway store (`FACTORY_STATE=<your scratch>/store`) and a throwaway instance (`FACTORY_INSTANCE`). Never the live one.
- C. **The tripwire (#38) covers the instance's own store root** for a role run, as an escalate path. Any write there during a role run that is not a clerk command is reported.

**Decision for the operator (separate):** keep the spec store that run-0196 created on B (current truth now holds 6 capabilities from T-0023), or remove it and restore close-as-applied. Recommendation: keep it. #21 wanted current truth for B anyway, and this is a start.


---

Operator (2026-10-04): take this into intake so it is properly reviewed. The spec gate is NOT pre-approved: the spec comes to the operator. The keep-or-remove decision on instance B's accidentally created spec store belongs in the spec as an Open question for the gate, with the recommendation (keep).
