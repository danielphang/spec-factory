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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0186-triage/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Request (raw, with any answers appended)

---
title: "Planner and spec writer: per-sub-ticket labels, sibling tests a sub-ticket invalidates, tests a decision overturns"
labels: "harness"
---
**Planner and spec writer: make each sub-ticket's acceptance and test permissions right the first time.** These are prompt changes only. Under the queue policy, the acceptance is an operator-reviewed re-plan before the runtime moves.

**Problem:** sub-tickets park for reasons the planner or spec writer could have foreseen. Each park costs a full role run, plus a human relabel or ruling.
1. **Labels copied from the parent.** The planner labels a check NEW when it already passes at that sub-ticket's own base, either because it is an invariant or because an earlier sibling already made it true. The verifier parks it as a SPEC-DEFECT. Retro trial P1: spec-factory T-0012.2, .5 and .6 (three SPEC-DEFECT parks), T-0012.4 (four vacuous NEW checks), T-0014 and T-0015 pre-dispatch relabels.
2. **A sibling's interim tests become untouchable.** An earlier sub-ticket ships tests that pin its interim behaviour. The next sub-ticket changes that behaviour as the plan intends, but has "Tests to change: none", so it BLOCKs. Evidence: Nanobot T-0002.4 → .5 ("list-edit subcommands not yet available"), 2026-10-04; spec-factory T-0012.3 → .4 (2026-10-03). Retro item 10.
3. **Existing tests pin a behaviour a decision changes.** An upstream test pins exactly the behaviour that an approved decision changes, and the spec's "Tests to change" omits it. Nanobot T-0002.2 (exact CLI metadata vs decision D22), 2026-10-04.

**Proposed change** (prompt text in `docs/design.md` §2 and §4, re-copied to `docs/prompts/` and `factory/prompts/`):
- A. **Planner: labels per sub-ticket.** Each acceptance check is labelled against that sub-ticket's own base: the integration branch with its dependencies merged. A check that already passes there, whether an invariant or something a sibling made true, is REGRESSION, not NEW.
- B. **Planner: sibling tests a sub-ticket invalidates.** For each sub-ticket, list under "Tests to change" every test an earlier sibling adds that this sub-ticket's planned change will break, with the reason. The earlier sibling's sub-ticket text names those tests as interim.
- C. **Spec writer: tests a decision overturns.** For each Decision that changes existing behaviour, find the existing tests that pin the old behaviour and list them under "Tests to change", with the decision they follow. The critic checks this, under rubric 1, grounded.

**Not proposed:** letting the implementer edit a test on its own judgement, even if declared in the PR. That loosens a guardrail, and needs the operator's decision if ever wanted.

**Acceptance:** re-plan Nanobot T-0002 from its approved spec under the new prompts. The plan must list T-0002.4's interim tests under T-0002.5's "Tests to change", and label each check against its own base. Re-run spec writing on T-0002's request, and its "Tests to change" must name the CLI-metadata tests D22 overturns. The operator reviews both side by side before the runtime moves.


---

Operator: spec gate pre-approved under the queue policy (`.factory/answers/queue-preapproval-policy.md`).
