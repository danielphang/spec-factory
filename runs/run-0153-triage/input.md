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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0153-triage/output.md`

## Request (raw, with any answers appended)

---
title: "Intake's Plan phase plans without sub-tickets; the build then exits silently"
labels: "harness"
---
**Where:** `factory/workflows/intake.js` Plan phase (runs when the ticket is `ready-for-planner` at launch); `factory/workflows/build.js` start-up on a `planned` parent, and its handling of a `parent-check` refusal.

**Problem:** starting intake on an approved ticket plans it without its sub-tickets, and the build then does nothing, silently. Intake's Plan phase runs the planner, `spec tasks` and `plan add`, then moves the parent to `planned`. It never runs `subticket add`. The build workflow skips its own Plan phase on a parent that is already `planned`. `ready-implementers` then returns nothing, `parent-check` refuses ("<ID> has no sub-tickets"), and the build exits after about 30 s with the parent still `planned`. Nothing is parked and no error is logged.

**Evidence:** Nanobot v3.5 store, 2026-10-04: six parents at once (T-0001, T-0004, T-0007, T-0008, T-0011, T-0012). The Driver ran `subticket add <parent> --run <planner run>` by hand for each, with run ids taken from the `plan.added` log events. The README already calls intake's Plan phase unused ("in practice the build script runs the planner"), and #21 part D lists it as dead code.

**Proposed change:**
- A. Remove intake's Plan phase. Intake ends at the spec gate; the build workflow owns planning. One planner path, no duplicate.
- B. When the build workflow starts on a `planned` parent with no sub-tickets, it runs `subticket add` from the parent's recorded planner run (the `plan.added` event) instead of exiting.
- C. When `parent-check` refuses, the build workflow parks the parent with the refusal as the reason, instead of exiting quietly.

**Out of scope:** the planner's output format (#13).

Reported by the Nanobot v3.5 Driver.


---

**Comment on the issue:**

Part D, added 2026-10-04: the verifier's gate result is misread when written as a heading. This is the second occurrence, and each one cost a full round:
- spec-factory T-0012.5 (run-0073, `## Gate suite: PASS` → ci FAIL "missing Gate suite line");
- Nanobot v3.5 T-0012.1 (run-0052; round 1 → 2 at 06:15:11, and the round-2 implementer and reviewer both escalated it).

Fix:
- (a) the gate-line parser accepts optional leading `#` characters, `*` emphasis and whitespace before `Gate suite:`;
- (b) the verifier prompt pins the exact line format.

Both are kept: the parser stays tolerant to drift, and the prompt states the contract.

---

Operator: spec gate pre-approved ("#33 just do it"; `.factory/answers/queue-preapproval-policy.md`). Part D (gate line read as a heading) is in scope. The orphaned in-flight run on an agent-call failure (comment on #24, 2026-10-04) belongs with part C: any role call that fails records the run KILLED and parks with the error.
