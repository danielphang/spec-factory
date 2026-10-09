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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0345-triage/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0345-triage/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Request (raw, with any answers appended)

---
title: "A re-specced ticket's sub-tickets from a superseded plan block the new plan: sub-tickets should record the plan they belong to"
labels: "harness"
---
**Where:** `factory/store.py` `subtickets_of` (a filename glob, `tickets/<parent>.*.yaml`); `factory/cli.py` `ticket ready-implementers` (its `closed` list) and `parent-check`; `factory/workflows/build.js` (the "sub-ticket closed by a human" park); `factory/subtickets.py` (sub-ticket creation).

**Problem:** when an approved ticket is sent back after planning, re-specced and approved again, its sub-tickets from the old plan stay attached to it. The planner's new sub-tickets take the next free ids, as designed. But `subtickets_of` returns every `T-n.*` record. So `ready-implementers` reports an old, hand-closed sub-ticket in `closed`, and `build.js` parks the parent with "sub-ticket closed by a human". No field can mark a sub-ticket as belonging to a superseded plan. The routing table has no parked → planned edge, so the runner cannot recover either. Any ticket re-specced after planning hits this.

**Evidence:** Nanobot v3.5, T-0024 (SPEC-11), 2026-10-08, reported by the Driver.
1. Planned once, producing T-0024.1.
2. Sent back by the operator. The build was stopped and T-0024.1 closed by hand, with no commits.
3. Re-specced, approved at v4.
4. The new planner created T-0024.2.
5. The build parked the parent: "sub-ticket closed by a human: T-0024.1".

**Proposed change:**
- A. Every sub-ticket records the parent's spec version it was planned against (`planned_from: v<n>`). Existing records without the field count as planned from the version approved when they were created, or as current if unknown.
- B. `ready-implementers`, `parent-check`, the merge and archive guards, and the build's "closed by a human" park consider only sub-tickets planned from the parent's current approved version. Sub-tickets from an earlier version are listed separately as `superseded` and never block.
- C. Re-planning after a re-spec marks the old plan's unmerged sub-tickets superseded. It records this in the log, never deletes them, and keeps their ids reserved.
- D. Merged sub-tickets from a superseded plan stay merged. The new plan's acceptance covers the whole spec, and the final check verifies it.
- E. Tests: re-spec after planning, with old sub-tickets closed, and also with one merged. The new plan builds and the parent closes.

**Relation:** #44 and #50 (amending a pinned spec; intent changes re-plan) create exactly this situation. Build together with #44, or before it.

Reported by the Driver (Nanobot v3.5); filed by the Green session.



## Comments

Stand-in applied on Nanobot T-0024 (2026-10-08, with the operator's go): tickets/T-0024.1.yaml moved to tickets/superseded/ (git mv on factory-store), T-0024 set back to planned, a decision logged. Design note from the Driver: `ticket set` refuses unknown keys (`note=`), so a stand-in can't be annotated on the ticket itself; the fix should record supersession as a real field.


Issue: https://github.com/danielphang/spec-factory/issues/77
