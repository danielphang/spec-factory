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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0251-triage/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0251-triage/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Request (raw, with any answers appended)

---
title: "Small-change lane: gate commands scoped to the paths they cover; one-part specs skip the planner"
labels: "harness"
---
**Small-change lane: work in proportion to what a change can affect.** Pre-approved by the operator (2026-10-04), under the standing decision: "removing clearly redundant work is pre-approved, provided every refusal the pipeline gives today still fires."

**Problem:** every ticket pays the full pipeline, whatever its size or what it touches. Measured:
- T-0014 (#26) added about 140 lines of prose to `docs/writing.md`, and still ran the full harness suite at every stage.
- T-0013 (#23) and T-0015 (#20) each had a one-part spec, and each still paid a planner run (about 2 to 5 min) that split it into one sub-ticket.
- A docs-only diff cannot change any test outcome. A suite run on it is work that cannot change a verdict. A one-part plan adds nothing the spec doesn't already say.

**Proposed change:**
- A. **A gate command declares the paths it covers** (`gate_commands` entries gain an optional `paths:` glob list). When a sub-ticket's diff touches none of a command's paths, the verifier records the command as SKIPPED, with the reason, and the ci row still requires every non-skipped command to PASS. A command with no `paths:` always runs, so today's behaviour stays the default. Spec-factory: the suite covers `factory/**`, `bin/factory`, `tests/**`, `agents/**`, `docs/**` (the suite reads the prompt copies and standards), `pyproject.toml` and `uv.lock`. This repo's `docs/**` stays covered, as #31's analysis found; the saving comes on repos whose docs are not test inputs, and in `dev/`, `README.md` and the store.
- B. **One-part specs skip the planner.** When an approved spec's proposed change has exactly one lettered part and no NEEDS-SPLIT, the build creates the single sub-ticket directly from the spec (the sub-ticket text is the spec's part, its acceptance is the parent's), and records that the planner was skipped. A spec with two or more parts plans as today.
- C. **One-sub-ticket parents** already close on their sub-ticket's VERIFIED run (#31). There is no change here; it is listed so the lane is complete.

**Kept, every one:** NEW checks still run on base and head; REGRESSION checks and non-skipped gate commands still run on the head; both checkers still run; the merge gate still requires CI PASS, APPROVE and VERIFIED on the current head; protected-path approvals still apply.

**Acceptance:** a docs-only sub-ticket under a `paths:`-scoped suite records the suite SKIPPED and still merges only on PASS of the rest. A one-part spec reaches its implementer without a planner run. A two-part spec still plans. Timing: the next qualifying ticket, against T-0014's and T-0015's numbers.


---

Operator (2026-10-04): pre-approved; efficiency work goes first (`.factory/answers/operator-decisions-2026-10-04.md`).
