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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0344-triage/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0344-triage/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Request (raw, with any answers appended)

---
title: "#75 follow-up: decision lines that name no capability always reach the writer, critic and planner in full"
labels: "harness"
---
**Where:** `factory/compose.py`, the decision-log filter that #75 added (T-0036, merged `deedbb9`), and its current-truth requirement and docs.

**Problem:** #75 sends a decision line in full only when it was logged against this ticket, or when its text names a capability sent in full. A cross-cutting standing decision names no capability, so it reaches the spec writer, critic and planner only as a one-line entry in the per-ticket index. Examples: where code must live, or how a whole category of change is done. Writers and critics can then miss a rule every ticket must follow.

**Evidence:** the operator's replay acceptance of #75 (2026-10-09), on Nanobot T-0032 in a scratch store.
- The new writer put its new code in a new module, `nanobot/cron/session_sweep.py`.
- Standing decision T-0003 rules that module out: lionbot code goes through upstream's extension points first, and `nanobot/agent/lionbot.py` holds only plain helpers.
- The original writer, given the whole log, followed T-0003 (its D11), and the original critic confirmed it. The replay critic missed the conflict, because it did not get the decision in full either.
- Everything else held: writer input fell 518 KB → 162 KB on Nanobot and 187 KB → 100 KB on spec-factory, and the Nanobot writer's run fell from 18.4M to 8.6M tokens. Quality was the same on both tickets, and no capability conflict was missed.

**Proposed change:**
- A. A decision line whose text names no current-truth capability goes in full to every spec writer, critic and planner input, as before #75.
- B. A line that names one or more capabilities goes in full when one of them is sent in full, as #75 does. Otherwise it stays in the index.
- C. Lines logged against this ticket go in full, unchanged.
- D. Measure the decision part's size on both stores before and after, and record it.

**Then:** one runtime move ships #75 with this fix.

Operator decision 2026-10-09 ("Fix the filter first, then ship"); filed by the Green session.



Issue: https://github.com/danielphang/spec-factory/issues/78
