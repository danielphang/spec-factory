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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0309-triage/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0309-triage/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Request (raw, with any answers appended)

---
title: "Merge gate does not check protected paths; the reviewer prompt promises a check that local mode never runs"
labels: "harness"
---
**Where:** `factory/cli.py` `merge_cmd` (the merge gate); the reviewer prompt's protected-path check (`factory/prompts/reviewer.md`, `docs/design.md` §6 and `docs/prompts/06-code-reviewer.md`).

**Problem:** the code reviewer's prompt says that a declared protected-path change goes under ESCALATIONS, "the merge gate will require a human approval". The local merge gate checks none of this. It checks the ticket state, that the commit is the branch tip, the three result rows, and that the commit contains the integration branch, but never the paths the change touches. A reviewer's APPROVE with protected paths listed under ESCALATIONS merges anyway, and an undeclared protected-path change merges if both checkers pass it. The factory edits its own harness and prompts, so this is the gate that guards self-modification.

**Evidence:**
- #56 part D (independent review, 2026-10-05).
- Confirmed on 2026-10-04: T-0028.1 (#48) parked because its reviewer escalated `factory/store.py`, a 3-line change the approved spec asks for in part A.5 but whose Risk list does not declare it. The reviewer (run-0298) noted that "no merge check reads the declaration" in local mode.
- T-0029 (#49) had already recorded the same wording mismatch as out of scope.

**Proposed change:**
- A. The approved spec's Risk list is the authorization; the human approves it at the spec gate. Do not add a second approval step.
- B. At merge, the gate lists the paths changed between the parent base and the judged commit. It refuses when a changed path matches `protected_paths` and the pinned spec's Risk list does not declare it, naming each path. The refusal parks for a human ruling (accept under the approved design, or send back).
- C. The reviewer prompt's check 6 is reworded to match: declared paths are listed for the record, an undeclared one is an ESCALATE, and the sentence about the merge gate describes what the gate actually checks.
- D. Tests: an undeclared protected change is refused; a declared one merges; a declaration in a different ticket's spec does not count; a change to the factory's own rules (`instance.yaml`, prompts) is covered.

**Priority:** first after #41.

From #56 part D; filed by the Green session.



## Comments

Related gap found 2026-10-05 while applying the operator's ruling on T-0028.1 (#48): `resolve --ruling` sends any ESCALATE park whose reason doesn't name the planner to `ready-for-critic` (cli.py, `resolve`), including a sub-ticket parked by its code reviewer, which should return to its checks. The ruling had to be placed by hand in `approvals/T-0028.1/ruling-1.md`, followed by `resolve --redispatch`. Fold into this ticket: a reviewer ESCALATE on a sub-ticket resolves back to `checks-in-flight` with the ruling in the checkers' input. (The same hand placement was needed for a budget-kill park on T-0029.1; #41's spec covers that one.)


Issue: https://github.com/danielphang/spec-factory/issues/57
