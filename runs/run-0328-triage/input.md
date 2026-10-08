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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0328-triage/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0328-triage/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Request (raw, with any answers appended)

---
title: "Revert #73's critic limits: drop the per-claim cap and the no-build rule; keep the no-suite line and the reading rules"
labels: "harness"
---
**Where:** `factory/prompts/critic.md`, the design doc's §3 critic block, `docs/prompts/03-spec-critic.md`, `docs/principles.md` (principle 2 and the Spiking section), `docs/changelog.md`.

**Problem:** #73 (T-0034, merged `05cf8f9`) gave the spec writer and the critic turn-economy rules. The operator's replay acceptance (2026-10-08) found that the critic half saves nothing and costs quality. The critic's cost is mostly its fixed start-up context, and limiting its checks made it verify less and miss real findings.

**Evidence (replay of three past intakes, same inputs and bases, new vs original prompts):**

| Critic | Calls | Tokens | Quality (grader) |
|---|---|---|---|
| #49 | 8 → 10 | 0.71M → 0.72M | same |
| #51 | 10 → 11 | 1.0M → 0.93M | slightly worse: missed the Nanobot `UV_PYTHON_INSTALL_DIR` risk the original found |
| #57 | 11 → 17 | 1.67M → 1.63M (old-prompt control 1.69M) | worse: missed the brace-list declaration bug the original confirmed with a scratch git test; ran fewer checks |

The writer half held up and stays: about 37% fewer tokens across the three tickets, quality the same, slightly worse and better. Replay inputs and outputs: the Green session's scratch directory `eval73/`.

**Proposed change:**
- A. Remove the critic's per-claim cap ("at most 2 paths and 1 command for any one claim") and its no-build rule (no clone, worktree or prototype). A claim the critic settles with a small scratch experiment is allowed again.
- B. Keep the critic's no-full-test-suite line, since the verifier and implementer run the suite. Keep the three reading rules and the existing minimum check (2 cited paths, 1 acceptance command).
- C. `docs/principles.md`: principle 2 keeps "no full suite" for the critic; the Spiking section says a critic may run a small scratch check to confirm a finding, and that vetting a whole approach is still the writer's or a spike's job. Record the replay result.
- D. Changelog entry.

**Acceptance:** the prompt copies stay in step; the critic prompt no longer contains the cap or the no-build sentence and still contains the no-suite line and the reading rules; the writer prompt is unchanged from #73.

**Then:** the runtime moves with #73's writer rules and this revert together.

Operator decision 2026-10-08 ("Writer only: revert critic part first"); filed by the Green session.



Issue: https://github.com/danielphang/spec-factory/issues/74
